import requests
import time

BASE = "https://www.jf-cmca.jp"

years = [
    ("r02", "2020"),
    ("r03", "2021"),
    ("r04", "2022"),
    ("r05", "2023"),
    ("r06", "2024"),
]
letters = ["a", "b", "c", "d", "e", "f", "g"]

print("=== 解答PDF URLパターン調査 ===")
for ryear, cyear in years:
    for letter in letters:
        url = f"{BASE}/attach/test/{ryear}/1j_seikai/{cyear}{letter}.pdf"
        try:
            r = requests.head(url, timeout=10)
            status = "OK " if r.status_code == 200 else f"{r.status_code}"
            print(f"  [{status}] {ryear} {letter}: {url}")
        except Exception as e:
            print(f"  [ERR] {ryear} {letter}: {e}")
        time.sleep(0.3)
    print()

print("=== 問題PDF URLパターン候補調査 (r03のみ) ===")
ryear, cyear = "r03", "2021"
candidates = [
    "/attach/test/{r}/mondai/{y}{l}.pdf",
    "/attach/test/{r}/{y}{l}.pdf",
    "/attach/test/{r}/1ji_mondai/{y}{l}.pdf",
    "/attach/test/{r}/mondai/1ji_{y}{l}.pdf",
]
for pat in candidates:
    for letter in ["a", "b", "c"]:
        url = BASE + pat.format(r=ryear, y=cyear, l=letter)
        try:
            r = requests.head(url, timeout=10)
            if r.status_code == 200:
                print(f"  [HIT] {url}")
            else:
                print(f"  [{r.status_code}] {url}")
        except Exception as e:
            print(f"  [ERR] {url} -> {e}")
        time.sleep(0.3)
    print()

print("=== 問題PDF 確認済みパターン検証 ===")
verified_cases = [
    # r02-r04: 小文字ji
    ("r02", "2020", "ji"),
    ("r03", "2021", "ji"),
    ("r04", "2022", "ji"),
    # r05-r06: 大文字JI
    ("r05", "2023", "JI"),
    ("r06", "2024", "JI"),
]
for ryear, cyear, ji_case in verified_cases:
    for letter in ["A", "B", "C", "D", "E", "F", "G"]:
        url = f"{BASE}/attach/test/shikenmondai/1ji{cyear}/{letter}1{ji_case}{cyear}.pdf"
        try:
            r = requests.head(url, timeout=10)
            status = "HIT" if r.status_code == 200 else str(r.status_code)
            print(f"  [{status}] {ryear} {letter}: {url}")
        except Exception as e:
            print(f"  [ERR] {ryear} {letter}: {e}")
        time.sleep(0.3)
    print()
