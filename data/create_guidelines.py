"""헌혈 판정기준 PDF 3개 생성 (reportlab + 한국어 폰트)"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 한국어 폰트 등록
FONT_PATH = os.path.expanduser("~/Library/Fonts/NanumGothic-Regular.ttf")
FONT_BOLD_PATH = os.path.expanduser("~/Library/Fonts/NanumGothic-Bold.ttf")
pdfmetrics.registerFont(TTFont("NanumGothic", FONT_PATH))
pdfmetrics.registerFont(TTFont("NanumGothicBold", FONT_BOLD_PATH))

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

styles = getSampleStyleSheet()
style_title = ParagraphStyle("KorTitle", parent=styles["Title"], fontName="NanumGothicBold", fontSize=18)
style_heading = ParagraphStyle("KorHeading", parent=styles["Heading2"], fontName="NanumGothicBold", fontSize=13)
style_body = ParagraphStyle("KorBody", parent=styles["Normal"], fontName="NanumGothic", fontSize=10, leading=14)
style_table = ParagraphStyle("KorTable", fontName="NanumGothic", fontSize=9, leading=12)


def _p(text):
    """테이블 셀용 Paragraph"""
    return Paragraph(text, style_table)


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "NanumGothicBold"),
        ("FONTNAME", (0, 1), (-1, -1), "NanumGothic"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])


def create_drug_guideline():
    """약물 판정기준 PDF 생성"""
    path = os.path.join(DATA_DIR, "guideline_drug.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    elements.append(Paragraph("헌혈 판정기준 — 약물 복용", style_title))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph("1. 일반의약품 복용 시 헌혈 판정기준", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "헌혈 희망자가 약물을 복용한 경우, 약물의 종류와 복용 목적에 따라 헌혈 가능 여부를 판정합니다. "
        "아래 표는 주요 일반의약품의 헌혈 유예기간을 정리한 것입니다.",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))

    data = [
        [_p("약물명"), _p("성분"), _p("채혈 가능 여부"), _p("유예기간"), _p("판정 사유")],
        [_p("아스피린<br/>(Aspirin)"), _p("아세틸살리실산"), _p("조건부 가능"),
         _p("복용 후 36시간 경과 시<br/>전혈헌혈 가능"),
         _p("비가역적 혈소판 기능 억제.<br/>혈소판성분헌혈은 3일 경과 필요.")],
        [_p("타이레놀<br/>(Tylenol)"), _p("아세트아미노펜"), _p("즉시 가능"),
         _p("유예기간 없음"),
         _p("혈소판 기능에 영향 없음.<br/>해열·진통 목적 복용 시 즉시 헌혈 가능.")],
        [_p("이부프로펜<br/>(Ibuprofen)"), _p("이부프로펜"), _p("조건부 가능"),
         _p("복용 후 24시간 경과 시"),
         _p("가역적 혈소판 기능 억제.<br/>24시간 후 기능 회복.")],
        [_p("항히스타민제<br/>(세티리진 등)"), _p("세티리진/로라타딘"), _p("즉시 가능"),
         _p("유예기간 없음"),
         _p("알레르기 치료 목적.<br/>혈액 성분에 영향 없음.")],
        [_p("항생제<br/>(아목시실린 등)"), _p("아목시실린/세팔렉신"), _p("조건부 가능"),
         _p("투약 완료 후 증상 소실 시"),
         _p("감염 치료 목적 항생제는 투약 완료 및<br/>증상 소실 확인 후 헌혈 가능.")],
    ]
    t = Table(data, colWidths=[55*mm, 35*mm, 30*mm, 45*mm, 55*mm])  # 수정된 너비
    t.setStyle(_table_style())
    elements.append(t)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("2. 고혈압 치료제 복용 시 판정기준", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "고혈압 치료를 위해 약물을 복용 중인 경우, 약물 자체보다 혈압 수치가 판정의 핵심입니다. "
        "혈압이 정상 범위 내에서 안정적으로 조절되고 있다면 헌혈이 가능합니다.",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))

    data2 = [
        [_p("약물 계열"), _p("대표 약물"), _p("채혈 가능 여부"), _p("조건"), _p("비고")],
        [_p("ACE 억제제"), _p("에날라프릴, 라미프릴"), _p("조건부 가능"),
         _p("수축기 90~179mmHg<br/>이완기 100mmHg 미만"),
         _p("혈압이 기준 범위 내이고<br/>합병증 없으면 가능")],
        [_p("ARB"), _p("로사르탄, 발사르탄"), _p("조건부 가능"),
         _p("수축기 90~179mmHg<br/>이완기 100mmHg 미만"),
         _p("단일제 복용, 혈압 안정 시 가능")],
        [_p("베타차단제"), _p("아테놀올, 메토프롤올"), _p("조건부 가능"),
         _p("수축기 90~179mmHg<br/>이완기 100mmHg 미만"),
         _p("맥박 50회/분 이상 확인 필요")],
        [_p("칼슘채널차단제"), _p("암로디핀, 니페디핀"), _p("조건부 가능"),
         _p("수축기 90~179mmHg<br/>이완기 100mmHg 미만"),
         _p("혈압 안정 조절 확인")],
    ]
    t2 = Table(data2, colWidths=[35*mm, 40*mm, 30*mm, 45*mm, 55*mm])  # 수정된 너비
    t2.setStyle(_table_style())
    elements.append(t2)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("3. 헌혈 절대 금지 약물", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "다음 약물을 복용 중인 경우 헌혈이 절대 불가합니다:",
        style_body
    ))
    elements.append(Spacer(1, 3*mm))

    data3 = [
        [_p("약물명"), _p("유예기간"), _p("사유")],
        [_p("이소트레티노인 (로아큐탄)"), _p("투약 중단 후 1개월"),
         _p("태아 기형 유발 위험. 혈액 내 잔류 가능.")],
        [_p("피나스테리드 (프로페시아)"), _p("투약 중단 후 1개월"),
         _p("태아 기형 유발 위험.")],
        [_p("두타스테리드 (아보다트)"), _p("투약 중단 후 6개월"),
         _p("긴 반감기로 혈액 내 장기 잔류.")],
        [_p("아시트레틴 (소리아탄)"), _p("투약 중단 후 3년"),
         _p("극히 긴 반감기. 태아 기형 유발.")],
        [_p("에트레티네이트 (테기손)"), _p("영구 헌혈 금지"),
         _p("체내 영구 잔류 가능.")],
    ]
    t3 = Table(data3, colWidths=[55*mm, 50*mm, 80*mm])
    t3.setStyle(_table_style())
    elements.append(t3)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        "※ 위 기준은 대한적십자사 헌혈기록카드 판정기준 제22판을 기반으로 작성되었습니다. "
        "최종 판정은 문진 간호사의 종합적 판단에 따릅니다.",
        style_body
    ))

    doc.build(elements)
    print(f"생성 완료: {path}")


def create_malaria_guideline():
    """말라리아 위험지역 판정기준 PDF 생성"""
    path = os.path.join(DATA_DIR, "guideline_malaria.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    elements.append(Paragraph("헌혈 판정기준 — 말라리아 위험지역", style_title))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph("1. 말라리아 위험지역 방문 시 헌혈 유예기간", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "말라리아 위험지역을 방문한 헌혈 희망자는 방문 지역의 WHO 위험등급에 따라 유예기간이 적용됩니다. "
        "증상 유무와 관계없이 유예기간은 반드시 준수해야 합니다.",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))

    data = [
        [_p("지역"), _p("국가"), _p("WHO 위험등급"), _p("유예기간"), _p("비고")],
        [_p("동남아시아"), _p("인도네시아 (발리)"), _p("저위험"),
         _p("귀국 후 1개월"),
         _p("발리는 저위험 지역으로 분류.<br/>증상 없고 1개월 경과 시 헌혈 가능.")],
        [_p("동남아시아"), _p("인도네시아 (파푸아)"), _p("고위험"),
         _p("귀국 후 1년"),
         _p("파푸아는 고위험 지역.<br/>1년 유예 및 말라리아 검사 권장.")],
        [_p("동남아시아"), _p("태국 (방콕)"), _p("저위험"),
         _p("귀국 후 1개월"),
         _p("방콕 시내는 저위험.<br/>북부 국경지역은 중위험 적용.")],
        [_p("동남아시아"), _p("베트남 (하노이/호치민)"), _p("저위험"),
         _p("귀국 후 1개월"),
         _p("주요 도시는 저위험.<br/>중부 고원지대는 중위험.")],
        [_p("남아시아"), _p("인도 (델리/뭄바이)"), _p("중위험"),
         _p("귀국 후 6개월"),
         _p("도시 지역도 중위험 적용.<br/>농촌 방문 시 고위험.")],
        [_p("아프리카"), _p("케냐"), _p("고위험"),
         _p("귀국 후 1년"),
         _p("사하라 이남 아프리카 전역 고위험.")],
        [_p("아프리카"), _p("나이지리아"), _p("고위험"),
         _p("귀국 후 1년"),
         _p("세계 최다 말라리아 발생국 중 하나.")],
        [_p("아프리카"), _p("탄자니아"), _p("고위험"),
         _p("귀국 후 1년"),
         _p("잔지바르 포함 전역 고위험.")],
        [_p("중남미"), _p("브라질 (아마존)"), _p("중위험"),
         _p("귀국 후 6개월"),
         _p("아마존 유역 중위험.<br/>상파울루 등 도시는 저위험.")],
        [_p("중남미"), _p("멕시코"), _p("저위험"),
         _p("귀국 후 1개월"),
         _p("관광지역 대부분 저위험.")],
    ]
    t = Table(data, colWidths=[30*mm, 40*mm, 30*mm, 35*mm, 60*mm])
    t.setStyle(_table_style())
    elements.append(t)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("2. 말라리아 예방약 복용 시 추가 유예", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "말라리아 예방약(메플로퀸, 독시사이클린, 아토바쿠온-프로구아닐 등)을 복용한 경우, "
        "지역 유예기간과 별도로 약물 복용 완료 후 추가 유예기간이 적용될 수 있습니다. "
        "예방약 복용 시 최소 3개월의 추가 유예기간을 권장합니다.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("3. 말라리아 감염 이력이 있는 경우", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "과거 말라리아에 감염된 적이 있는 경우, 완치 판정 후 3년간 헌혈이 유예됩니다. "
        "3년 경과 후에도 말라리아 항체 검사에서 양성이면 헌혈이 불가합니다.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("4. 국내 말라리아 위험지역", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "경기북부(파주, 연천, 철원 등) 및 강원북부(철원, 화천, 양구 등) 지역은 "
        "국내 말라리아 위험지역으로 지정되어 있습니다. 해당 지역 거주자 또는 "
        "군 복무자는 전역/퇴소 후 2년간 헌혈이 유예됩니다.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        "※ 위 기준은 대한적십자사 헌혈기록카드 판정기준 제22판 및 WHO 말라리아 보고서(2024)를 "
        "기반으로 작성되었습니다.",
        style_body
    ))

    doc.build(elements)
    print(f"생성 완료: {path}")


def create_main_guideline():
    """일반 판정기준 PDF 생성"""
    path = os.path.join(DATA_DIR, "guideline_main.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    elements.append(Paragraph("헌혈 판정기준 — 일반 기준", style_title))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph("1. 헌혈 기본 자격 요건", style_heading))
    elements.append(Spacer(1, 5*mm))

    data_basic = [
        [_p("항목"), _p("전혈헌혈 (320/400mL)"), _p("혈소판성분헌혈"), _p("혈장성분헌혈")],
        [_p("연령"), _p("만 16세 ~ 69세"), _p("만 17세 ~ 59세"), _p("만 17세 ~ 69세")],
        [_p("체중"), _p("남 50kg / 여 45kg 이상"), _p("남 50kg / 여 45kg 이상"), _p("남 50kg / 여 45kg 이상")],
        [_p("혈압 (수축기)"), _p("90 ~ 179 mmHg"), _p("90 ~ 179 mmHg"), _p("90 ~ 179 mmHg")],
        [_p("혈압 (이완기)"), _p("100 mmHg 미만"), _p("100 mmHg 미만"), _p("100 mmHg 미만")],
        [_p("맥박"), _p("60 ~ 100회/분"), _p("60 ~ 100회/분"), _p("60 ~ 100회/분")],
        [_p("체온"), _p("37.5°C 이하"), _p("37.5°C 이하"), _p("37.5°C 이하")],
        [_p("헤모글로빈"), _p("남 13.0 / 여 12.5 g/dL 이상"), _p("남 13.0 / 여 12.5 g/dL 이상"), _p("남 13.0 / 여 12.5 g/dL 이상")],
        [_p("헌혈 간격"), _p("전혈 후 8주"), _p("성분헌혈 후 2주"), _p("성분헌혈 후 2주")],
    ]
    t1 = Table(data_basic, colWidths=[40*mm, 50*mm, 45*mm, 45*mm])
    t1.setStyle(_table_style())
    elements.append(t1)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("2. 혈압 판정 세부 기준", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "헌혈 시 측정한 혈압이 다음 기준을 벗어나면 헌혈이 불가합니다:",
        style_body
    ))
    elements.append(Spacer(1, 3*mm))

    data_bp = [
        [_p("혈압 구분"), _p("정상 범위"), _p("헌혈 가능"), _p("헌혈 불가")],
        [_p("수축기 혈압"), _p("90 ~ 139 mmHg"), _p("90 ~ 179 mmHg"),
         _p("180 mmHg 이상 또는 90 mmHg 미만")],
        [_p("이완기 혈압"), _p("60 ~ 89 mmHg"), _p("100 mmHg 미만"),
         _p("100 mmHg 이상")],
    ]
    t2 = Table(data_bp, colWidths=[40*mm, 45*mm, 45*mm, 55*mm])
    t2.setStyle(_table_style())
    elements.append(t2)

    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "혈압이 경계 수치(수축기 140~179mmHg)인 경우, 고혈압 치료제 복용 여부와 "
        "합병증 유무를 추가로 확인합니다. 치료 중이며 혈압이 안정적으로 조절되고 있다면 "
        "헌혈이 가능합니다. 다만, 수축기 180mmHg 이상이면 치료 여부와 관계없이 당일 헌혈이 불가합니다.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("3. 헌혈 영구 부적격 사유", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "다음 항목에 해당하는 경우 영구적으로 헌혈이 불가합니다:",
        style_body
    ))
    elements.append(Spacer(1, 3*mm))

    data_perm = [
        [_p("사유"), _p("세부 내용")],
        [_p("HIV/AIDS 감염"), _p("확진 또는 양성 판정자")],
        [_p("B형/C형 간염 보균"), _p("HBsAg 양성 또는 HCV 항체 양성")],
        [_p("인간광우병(vCJD) 위험"), _p("1980~1996년 영국 체류 3개월 이상,<br/>1980~2004년 유럽 체류 5년 이상")],
        [_p("마약 주사 사용 이력"), _p("정맥주사 약물 사용 경험자")],
        [_p("장기/조직 이식 수혜"), _p("이종 또는 동종 장기이식 수혜자")],
        [_p("혈우병/혈액응고장애"), _p("선천성 혈액응고인자 결핍증")],
    ]
    t3 = Table(data_perm, colWidths=[55*mm, 120*mm])
    t3.setStyle(_table_style())
    elements.append(t3)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("4. 문진 절차 요약 (간호사용)", style_heading))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "① 헌혈기록카드 전자문진 확인 → ② 신분증 확인 및 본인 여부 확인 → "
        "③ 혈압·맥박·체온 측정 → ④ 헤모글로빈 측정 (핑거스틱) → "
        "⑤ 문진 항목 대면 확인 (여행력, 약물, 수술, 질환 등) → "
        "⑥ 최종 판정 및 헌혈 동의서 서명 → ⑦ 채혈 진행",
        style_body
    ))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        "문진 간호사는 전자문진 결과를 기반으로 추가 질문을 진행하며, "
        "판정기준에 명시되지 않은 케이스는 의료담당자(의사)에게 판정을 의뢰합니다.",
        style_body
    ))

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("5. 임시 부적격 사유 (주요 항목)", style_heading))
    elements.append(Spacer(1, 5*mm))

    data_temp = [
        [_p("사유"), _p("유예기간"), _p("비고")],
        [_p("감기/독감 증상"), _p("증상 소실 후 1주"),
         _p("발열, 기침, 인후통 등")],
        [_p("치과 치료 (발치)"), _p("시술 후 72시간"),
         _p("단순 스케일링은 당일 가능")],
        [_p("문신(타투)/피어싱"), _p("시술 후 6개월"),
         _p("의료기관 외 시술 시")],
        [_p("수혈 경험"), _p("수혈 후 1년"),
         _p("수혈 받은 날로부터 기산")],
        [_p("내시경 (조직검사 포함)"), _p("시술 후 6개월"),
         _p("단순 내시경은 1주")],
        [_p("예방접종 (생백신)"), _p("접종 후 4주"),
         _p("불활화 백신은 24시간")],
        [_p("임신/출산"), _p("출산 후 6개월"),
         _p("수유 중에도 6개월 적용")],
    ]
    t4 = Table(data_temp, colWidths=[50*mm, 45*mm, 80*mm])
    t4.setStyle(_table_style())
    elements.append(t4)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        "※ 위 기준은 대한적십자사 헌혈기록카드 판정기준 제22판을 기반으로 작성되었습니다. "
        "모든 판정은 문진 간호사의 종합적 판단에 따르며, 불확실한 경우 의료담당자에게 의뢰합니다.",
        style_body
    ))

    doc.build(elements)
    print(f"생성 완료: {path}")


if __name__ == "__main__":
    create_drug_guideline()
    create_malaria_guideline()
    create_main_guideline()
    print("\n모든 PDF 생성 완료!")
