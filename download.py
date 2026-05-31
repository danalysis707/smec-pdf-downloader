import requests
import time
from pathlib import Path

BASE_URL = "https://www.jf-cmca.jp"
TIMEOUT_SECONDS = 30
SLEEP_SECONDS = 1

YEARS = [
    ("r02", "2020", "令和2年度"),
    ("r03", "2021", "令和3年度"),
    ("r04", "2022", "令和4年度"),
    ("r05", "2023", "令和5年度"),
    ("r06", "2024", "令和6年度"),
    ("r07", "2025", "令和7年度"),
]

SUBJECTS = [
    ("経済学・経済政策",           "a", "A"),
    ("財務・会計",                 "b", "B"),
    ("企業経営理論",               "c", "C"),
    ("運営管理",                   "d", "D"),
    ("経営法務",                   "e", "E"),
    ("経営情報システム",           "f", "F"),
    ("中小企業経営・中小企業政策", "g", "G"),
]

OUTPUT_DIR = Path("downloads")

QUESTION_JI_MAP = {
    "r02": "ji", "r03": "ji", "r04": "ji",
    "r05": "JI", "r06": "JI", "r07": "JI",
}

# 年度ごとの解答PDFフォルダ名
ANSWER_SUBDIR = {
    "r02": "1j_seikai",
    "r03": "1j_seikai",
    "r04": "1j_seikai",
    "r05": "1ji(sai)_seikai",  # 令和5年度は再試験フォルダ
    "r06": "1ji_seikai",
    "r07": "1ji_seikai",
}

# 標準パターン（{cyear}{letter}.pdf）から外れるファイル名の上書き
ANSWER_FILENAME_OVERRIDES = {
    ("r03", "g"): "2021g_teisei.pdf",   # 令和3年度 中小企業経営：訂正版
    ("r05", "a"): "A.pdf",              # 令和5年度は年号なし大文字
    ("r05", "b"): "B.pdf",
    ("r05", "c"): "C.pdf",
    ("r05", "d"): "D.pdf",
    ("r05", "e"): "E.pdf",
    ("r05", "f"): "F.pdf",
    ("r05", "g"): "G.pdf",
    ("r06", "d"): "Dv2_20240903.pdf",  # 令和6年度 運営管理：訂正版
    ("r06", "f"): "Fv2_20240903.pdf",  # 令和6年度 経営情報システム：訂正版
    ("r07", "d"): "d_v2_20250902.pdf", # 令和7年度 運営管理：訂正版
    ("r07", "f"): "f_v2_20250902.pdf", # 令和7年度 経営情報システム：訂正版
}


def build_answer_url(ryear: str, cyear: str, letter: str) -> str:
    subdir = ANSWER_SUBDIR[ryear]
    filename = ANSWER_FILENAME_OVERRIDES.get((ryear, letter), f"{cyear}{letter}.pdf")
    return f"{BASE_URL}/attach/test/{ryear}/{subdir}/{filename}"


def build_question_url(ryear: str, cyear: str, letter: str) -> str:
    ji = QUESTION_JI_MAP[ryear]
    return f"{BASE_URL}/attach/test/shikenmondai/1ji{cyear}/{letter}1{ji}{cyear}.pdf"


def download_pdf(url: str, dest: Path) -> bool:
    if dest.exists():
        print(f"  スキップ（既存）: {dest.name}")
        return True
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(response.content)
            print(f"  完了: {dest.name}")
            return True
        else:
            print(f"  失敗 ({response.status_code}): {url}")
            return False
    except requests.RequestException as e:
        print(f"  エラー ({type(e).__name__}): {e}")
        return False


def build_download_plan():
    plan = []
    for ryear, cyear, year_label in YEARS:
        for subject, answer_letter, question_letter in SUBJECTS:
            q_url = build_question_url(ryear, cyear, question_letter)
            a_url = build_answer_url(ryear, cyear, answer_letter)
            q_dest = OUTPUT_DIR / year_label / f"{year_label}_{subject}_問題.pdf"
            a_dest = OUTPUT_DIR / year_label / f"{year_label}_{subject}_解答.pdf"
            plan.append((year_label, subject, "問題", q_url, q_dest))
            plan.append((year_label, subject, "解答", a_url, a_dest))
    return plan


def main():
    plan = build_download_plan()
    total = len(plan)
    success, failure = 0, 0

    print(f"ダウンロード開始: 全{total}件\n")
    for i, (year_label, subject, kind, url, dest) in enumerate(plan, 1):
        print(f"[{i}/{total}] {year_label} / {subject} ({kind})")
        if download_pdf(url, dest):
            success += 1
        else:
            failure += 1
        time.sleep(SLEEP_SECONDS)

    print(f"\n=== 完了: 成功 {success} 件 / 失敗 {failure} 件 / 合計 {total} 件 ===")


if __name__ == "__main__":
    main()
