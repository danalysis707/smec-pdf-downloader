import re

import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path

from download import YEARS, SUBJECTS, OUTPUT_DIR

DOCS_DIR = Path("docs")
IMAGES_DIR = DOCS_DIR / "images"
DATA_DIR = DOCS_DIR / "data"

SUBJECT_SHORT = {
    "経済学・経済政策":           "keizai",
    "財務・会計":                 "zaimu",
    "企業経営理論":               "keiei",
    "運営管理":                   "unei",
    "経営法務":                   "houmu",
    "経営情報システム":           "joho",
    "中小企業経営・中小企業政策": "chusho",
}

IMAGE_DPI = 150
IMAGE_QUALITY = 85
PDF_BASE_DPI = 72  # PDF standard resolution in points


def convert_pdf_to_images(pdf_path: Path, output_dir: Path) -> list[Path]:
    """PDFの各ページをJPEG画像に変換して保存し、画像パスのリストを返す。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    mat = fitz.Matrix(IMAGE_DPI / PDF_BASE_DPI, IMAGE_DPI / PDF_BASE_DPI)
    image_paths = []
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            image_path = output_dir / f"page_{page_num + 1:03d}.jpg"
            if not image_path.exists():
                page = doc[page_num]
                pix = page.get_pixmap(matrix=mat)
                image_path.write_bytes(pix.tobytes("jpeg", jpg_quality=IMAGE_QUALITY))
            image_paths.append(image_path)
    return image_paths


def detect_question_pages(pdf_path: Path) -> dict[int, list[int]]:
    """PDFから「第N問」の出現ページを検出し {問題番号: [ページ番号]} を返す（1始まり）。"""
    question_pages: dict[int, list[int]] = {}
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            for match in re.finditer(r'第\s*(\d+)\s*問', text):
                q_num = int(match.group(1))
                if q_num not in question_pages:
                    question_pages[q_num] = []
                if page_num not in question_pages[q_num]:
                    question_pages[q_num].append(page_num)
    return question_pages


def extract_answers(answer_pdf_path: Path) -> dict[int, str]:
    """解答PDFから {問題番号: 正解記号} を抽出する。"""
    answers: dict[int, str] = {}
    with pdfplumber.open(str(answer_pdf_path)) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        # パターン1: 「第1問　ウ」形式
        for match in re.finditer(r'第\s*(\d+)\s*問\s*([アイウエオ])', full_text):
            answers[int(match.group(1))] = match.group(2)
        # パターン2: 表形式「1　ウ」形式（パターン1で取れなかった場合のフォールバック）
        # 注: 境界アサーションで誤検出を抑制するが、PDFレイアウトによっては限界がある
        if not answers:
            for match in re.finditer(r'(?<!\d)(\d{1,2})\s+([アイウエオ])(?!\w)', full_text):
                answers[int(match.group(1))] = match.group(2)
    return answers
