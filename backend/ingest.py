"""PDF 파싱 → Embed v4 임베딩 → ChromaDB 저장 파이프라인"""

import os
import pdfplumber
import cohere
import chromadb
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
COLLECTION_NAME = "blood_donation_guidelines"

PDF_FILES = [
    "guideline_drug.pdf",
    "guideline_malaria.pdf",
    "guideline_main.pdf",
]


def parse_pdf(file_path: str) -> list[dict]:
    """pdfplumber로 PDF를 페이지 단위로 파싱하여 청크 리스트 반환.
    발표 멘트: North/온프레미스 환경에서는 Compass SDK가 이 과정을 자동화합니다.
    """
    chunks = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                chunks.append({
                    "text": text.strip(),
                    "source": os.path.basename(file_path),
                    "page": i + 1,
                })
    return chunks


def embed_chunks(co: cohere.ClientV2, chunks: list[dict], batch_size: int = 96) -> list[list[float]]:
    """Embed v4로 청크 임베딩 (배치 처리)"""
    all_embeddings = []
    texts = [c["text"] for c in chunks]

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = co.embed(
            texts=batch,
            model="embed-v4.0",
            input_type="search_document",
            embedding_types=["float"],
        )
        all_embeddings.extend(response.embeddings.float_)

    return all_embeddings


def store_to_chromadb(chunks: list[dict], embeddings: list[list[float]]):
    """ChromaDB에 청크와 임베딩 저장"""
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # 기존 컬렉션 삭제 후 재생성
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"{c['source']}_p{c['page']}_{i}" for i, c in enumerate(chunks)]
    documents = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "page": c["page"]} for c in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return collection


def run():
    """전체 인제스트 파이프라인 실행"""
    co = cohere.ClientV2()

    all_chunks = []
    for pdf_file in PDF_FILES:
        path = os.path.join(DATA_DIR, pdf_file)
        chunks = parse_pdf(path)
        all_chunks.extend(chunks)
        print(f"파싱 완료: {pdf_file} → {len(chunks)}개 청크")

    print(f"\n총 {len(all_chunks)}개 청크 임베딩 중...")
    embeddings = embed_chunks(co, all_chunks)
    print(f"임베딩 완료: {len(embeddings)}개 벡터 (차원: {len(embeddings[0])})")

    collection = store_to_chromadb(all_chunks, embeddings)
    print(f"\nChromaDB 저장 완료: {collection.count()}개 문서")
    print(f"저장 경로: {CHROMA_DIR}")


if __name__ == "__main__":
    run()
