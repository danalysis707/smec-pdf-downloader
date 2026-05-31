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

QUESTION_JI_MAP = {"r02": "ji", "r03": "ji", "r04": "ji", "r05": "JI", "r06": "JI"}


def build_answer_url(ryear: str, cyear: str, letter: str) -> str:
    return f"{BASE_URL}/attach/test/{ryear}/1j_seikai/{cyear}{letter}.pdf"


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
            q_dest = OUTPUT_DIR / year_label / f"{subject}_問題.pdf"
            a_dest = OUTPUT_DIR / year_label / f"{subject}_解答.pdf"
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
