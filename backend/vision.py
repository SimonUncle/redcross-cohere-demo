"""Command A Vision + Translate — 영문 처방전 이미지 분석 + 한국어 번역"""

import base64
import cohere
from dotenv import load_dotenv

load_dotenv()

MODEL_VISION = "command-a-vision-07-2025"
MODEL_TRANSLATE = "command-a-translate-08-2025"


def analyze_prescription(image_bytes: bytes) -> str:
    """영문 처방전 이미지에서 약물명/용량을 추출"""
    co = cohere.ClientV2()
    img_b64 = base64.standard_b64encode(image_bytes).decode()
    response = co.chat(
        model=MODEL_VISION,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Read all text visible in this prescription label image. "
                    "List each medication with its name, dosage, and instructions. "
                    "Format as a structured list."
                )},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            ]
        }],
        safety_mode="CONTEXTUAL",
    )
    return response.message.content[0].text


def translate_to_korean(text: str) -> str:
    """Translate 모델로 영문 텍스트를 한국어로 번역"""
    co = cohere.ClientV2()
    response = co.chat(
        model=MODEL_TRANSLATE,
        messages=[{
            "role": "user",
            "content": f"Translate the following English text to Korean:\n\n{text}",
        }],
    )
    return response.message.content[0].text


def translate_to_english(text: str) -> str:
    """Translate 모델로 한국어 텍스트를 영어로 번역"""
    co = cohere.ClientV2()
    response = co.chat(
        model=MODEL_TRANSLATE,
        messages=[{
            "role": "user",
            "content": f"Translate the following Korean text to English:\n\n{text}",
        }],
    )
    return response.message.content[0].text


def analyze_and_translate(image_bytes: bytes) -> dict:
    """Vision OCR + Translate 파이프라인: 영문 처방전 → 한국어 번역"""
    ocr_result = analyze_prescription(image_bytes)
    translated = translate_to_korean(ocr_result)
    return {
        "ocr_english": ocr_result,
        "translated_korean": translated,
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/sample_en_prescription.jpg"
    with open(path, "rb") as f:
        result = analyze_and_translate(f.read())
    print("=== OCR (English) ===")
    print(result["ocr_english"])
    print("\n=== Translated (Korean) ===")
    print(result["translated_korean"])
