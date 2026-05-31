import fitz  # PyMuPDF
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
