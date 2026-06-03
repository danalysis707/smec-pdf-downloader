import json
import re
import unicodedata

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

THEME_KEYWORDS: dict[str, dict[str, list[str]]] = {}  # loaded from theme_map.json at runtime


def load_theme_keywords() -> None:
    """theme_map.json を読み込んで THEME_KEYWORDS を初期化する。"""
    global THEME_KEYWORDS
    theme_map_path = DATA_DIR / "theme_map.json"
    with open(theme_map_path, encoding="utf-8") as f:
        THEME_KEYWORDS = json.load(f)


def assign_theme(question_text: str, subject: str) -> str:
    """問題テキストのキーワードマッチングでテーマを返す。未マッチは'その他'。"""
    if not THEME_KEYWORDS:
        load_theme_keywords()
    themes = THEME_KEYWORDS.get(subject, {})
    for theme, keywords in themes.items():
        if any(kw in question_text for kw in keywords):
            return theme
    return "その他"


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
        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    # 全角数字・記号を半角に正規化して regex マッチを確実にする
    full_text = unicodedata.normalize('NFKC', raw_text)
    def fill(pattern: str) -> None:
        """マッチした問題番号のうち未取得のものだけ answers に追加する。"""
        for m in re.finditer(pattern, full_text):
            q_num = int(m.group(1))
            if q_num not in answers:
                answers[q_num] = m.group(2)

    # パターン1: 標準形式「第N問 (-|設問N) 正解 配点」
    fill(r'第\s*(\d+)\s*問\s+(?:-|設問\d+)\s+\*?([アイウエオ])')
    # パターン2: r05形式「第N問 (-|設問N) 配点 正解」（令和5年度は列順が逆）
    fill(r'第\s*(\d+)\s*問\s+(?:-|設問\d+)\s+\d+\s+\*?([アイウエオ])')
    # パターン3: r05形式「第N問 配点 正解」（設問区切りなし）
    fill(r'第\s*(\d+)\s*問\s+\d+\s+\*?([アイウエオ])')
    # パターン4: 直接形式「第N問 正解」
    fill(r'第\s*(\d+)\s*問\s+\*?([アイウエオ])')
    # パターン5: 表形式フォールバック「N 正解」
    fill(r'(?<!\d)(\d{1,2})\s+\*?([アイウエオ])(?!\w)')
    return answers


def build_question_entry(
    ryear: str, year_label: str,
    subject: str, question_number: int,
    pages: list[str], correct_answer: str,
    answer_pages: list[str],
    question_text: str = "",
) -> dict:
    """1問分のquiz_dataエントリを生成する。"""
    subject_short = SUBJECT_SHORT[subject]
    return {
        "id": f"{ryear}_{subject_short}_q{question_number:03d}",
        "year": ryear,
        "year_label": year_label,
        "subject": subject,
        "subject_short": subject_short,
        "question_number": question_number,
        "theme": assign_theme(question_text, subject),
        "pages": pages,
        "correct_answer": correct_answer,
        "answer_pages": answer_pages,
        "search_query": f"{year_label} 中小企業診断士 {subject} 第{question_number}問 解説",
    }


def build_quiz_data() -> list[dict]:
    """全年度・全科目を処理してquiz_dataエントリのリストを返す。"""
    questions = []
    for ryear, cyear, year_label in YEARS:
        for subject, answer_letter, question_letter in SUBJECTS:
            subject_short = SUBJECT_SHORT[subject]
            q_pdf = OUTPUT_DIR / year_label / f"{year_label}_{subject}_問題.pdf"
            a_pdf = OUTPUT_DIR / year_label / f"{year_label}_{subject}_解答.pdf"
            if not q_pdf.exists():
                print(f"  スキップ（PDF未存在）: {q_pdf.name}")
                continue

            # 画像変換
            img_dir = IMAGES_DIR / ryear / subject_short
            images = convert_pdf_to_images(q_pdf, img_dir)
            img_paths = [str(p.relative_to(DOCS_DIR)).replace("\\", "/") for p in images]

            # 解答画像変換
            ans_dir = IMAGES_DIR / ryear / f"{subject_short}_answer"
            ans_paths: list[str] = []
            if a_pdf.exists():
                ans_images = convert_pdf_to_images(a_pdf, ans_dir)
                ans_paths = [str(p.relative_to(DOCS_DIR)).replace("\\", "/") for p in ans_images]

            # 設問番号検出
            page_map = detect_question_pages(q_pdf)

            # 正解抽出
            answers = extract_answers(a_pdf) if a_pdf.exists() else {}

            # 問題テキスト取得（テーマ割り当て用）
            page_texts: list[str] = []
            try:
                with pdfplumber.open(str(q_pdf)) as pdf:
                    page_texts = [p.extract_text() or "" for p in pdf.pages]
            except Exception as e:
                print(f"  WARNING: テキスト抽出失敗 {q_pdf.name}: {e}")
                page_texts = [""] * len(images)

            if not page_map:
                # 検出失敗時: 全ページを第1問として扱う
                page_map = {i + 1: [i + 1] for i in range(len(images))}

            for q_num in sorted(page_map.keys()):
                q_page_nums = page_map[q_num]
                q_img_paths = [img_paths[p - 1] for p in q_page_nums if p - 1 < len(img_paths)]
                q_text = " ".join(page_texts[p - 1] for p in q_page_nums if p - 1 < len(page_texts))
                correct = answers.get(q_num, "")
                entry = build_question_entry(
                    ryear=ryear, year_label=year_label,
                    subject=subject, question_number=q_num,
                    pages=q_img_paths, correct_answer=correct,
                    # 解答PDF全体が解答シートのため全問共通で1ページ目を使用
                    answer_pages=ans_paths[:1] if ans_paths else [],
                    question_text=q_text,
                )
                questions.append(entry)
                print(f"  [{ryear}] {subject} 第{q_num}問 → {correct or '未取得'}")

    return questions


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    print("ビルド開始...\n")
    questions = build_quiz_data()
    out_path = DATA_DIR / "quiz_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"questions": questions}, f, ensure_ascii=False, indent=2)
    print(f"\n完了: {len(questions)}問 → {out_path}")


if __name__ == "__main__":
    main()
