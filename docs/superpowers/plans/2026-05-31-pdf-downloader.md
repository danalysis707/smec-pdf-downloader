# 中小企業診断士 第1次試験 全科目 PDFダウンローダー 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** jf-cmca.jp から中小企業診断士 第1次試験 全7科目（令和2〜6年度）の問題PDF・解答PDFをダウンロードして年度別フォルダに整理保存するPythonスクリプトを作成する。

**Architecture:** 単一の Python スクリプト `download.py` が、jf-cmca.jp の公開URLから各科目・各年度のPDFをダウンロードし `downloads/令和X年度/科目名_種別.pdf` の形で保存する。最初のタスクでURLパターンを調査・確定し、その結果を元にスクリプトを実装する。

**Tech Stack:** Python 3.x, requests, pathlib, pytest

---

### Task 1: 環境セットアップ・URLパターン調査

**Files:**
- Create: `requirements.txt`
- Create: `url_investigation.py`（調査専用スクリプト、調査後削除）

- [ ] **Step 1: git を初期化**

```bash
git init
git commit --allow-empty -m "chore: initial commit"
```

- [ ] **Step 2: requests・pytest をインストール**

```bash
pip install requests pytest
```

- [ ] **Step 3: requirements.txt を作成**

`requirements.txt`:
```
requests
pytest
```

- [ ] **Step 4: 解答PDF URLパターン調査スクリプトを作成**

`url_investigation.py`:
```python
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
```

- [ ] **Step 5: 調査スクリプトを実行して結果を確認**

```bash
python url_investigation.py
```

出力から以下2点を確定する:
1. **解答PDFの letter と科目の対応表**（どのアルファベットがどの科目か）
2. **問題PDFの正しいURLパターン**（`[HIT]` と表示されたパターン）

結果をメモしておく。次のタスクで `download.py` の定数に反映する。

- [ ] **Step 6: 調査スクリプトをコミット**

```bash
git add requirements.txt url_investigation.py
git commit -m "chore: add URL investigation script and requirements"
```

---

### Task 2: コア実装（TDD）

**Files:**
- Create: `tests/__init__.py`（空ファイル）
- Create: `tests/test_download.py`
- Create: `download.py`

- [ ] **Step 1: tests フォルダを作成**

PowerShell:
```powershell
New-Item -ItemType Directory -Name tests
New-Item -ItemType File -Path tests/__init__.py
```

- [ ] **Step 2: URL構築関数のテストを書く**

`tests/test_download.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from download import build_answer_url, build_question_url, download_pdf


def test_build_answer_url():
    url = build_answer_url(ryear="r03", cyear="2021", letter="a")
    assert url == "https://www.jf-cmca.jp/attach/test/r03/1j_seikai/2021a.pdf"


def test_build_answer_url_r05():
    url = build_answer_url(ryear="r05", cyear="2023", letter="b")
    assert url == "https://www.jf-cmca.jp/attach/test/r05/1j_seikai/2023b.pdf"


def test_build_question_url_contains_year_and_letter():
    url = build_question_url(ryear="r03", cyear="2021", letter="a")
    assert "r03" in url
    assert "2021" in url
    assert url.endswith(".pdf")
```

- [ ] **Step 3: テストが失敗することを確認**

```bash
pytest tests/test_download.py -v
```

期待出力: `ImportError: cannot import name 'build_answer_url' from 'download'`

- [ ] **Step 4: download.py を作成してURL構築関数を実装**

`download.py`:

> **注意:** `QUESTION_URL_PATTERN` と `SUBJECTS` の letter は Task 1 Step 5 の調査結果で確定した値に書き換えること。

```python
import requests
import time
from pathlib import Path

BASE_URL = "https://www.jf-cmca.jp"

# Task 1 の調査結果で確定した問題PDFのURLパターンに書き換える
# 例: "/attach/test/{ryear}/mondai/{cyear}{letter}.pdf"
QUESTION_URL_PATTERN = "/attach/test/{ryear}/mondai/{cyear}{letter}.pdf"

YEARS = [
    ("r02", "2020", "令和2年度"),
    ("r03", "2021", "令和3年度"),
    ("r04", "2022", "令和4年度"),
    ("r05", "2023", "令和5年度"),
    ("r06", "2024", "令和6年度"),
]

# Task 1 の調査結果で各科目の letter を確定して書き換える
SUBJECTS = [
    ("経済学・経済政策",         "a"),
    ("財務・会計",               "b"),
    ("企業経営理論",             "c"),
    ("運営管理",                 "d"),
    ("経営法務",                 "e"),
    ("経営情報システム",         "f"),
    ("中小企業経営・中小企業政策", "g"),
]

OUTPUT_DIR = Path("downloads")


def build_answer_url(ryear: str, cyear: str, letter: str) -> str:
    return f"{BASE_URL}/attach/test/{ryear}/1j_seikai/{cyear}{letter}.pdf"


def build_question_url(ryear: str, cyear: str, letter: str) -> str:
    path = QUESTION_URL_PATTERN.format(ryear=ryear, cyear=cyear, letter=letter)
    return BASE_URL + path
```

- [ ] **Step 5: URL構築テストが通ることを確認**

```bash
pytest tests/test_download.py -v
```

期待出力: `3 passed`

- [ ] **Step 6: download_pdf 関数のテストを追加**

`tests/test_download.py` に追記:
```python
def test_download_pdf_success(tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"%PDF-fake-content"

    with patch("download.requests.get", return_value=mock_response):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/test.pdf", dest)
        assert result is True
        assert dest.exists()
        assert dest.read_bytes() == b"%PDF-fake-content"


def test_download_pdf_not_found(tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("download.requests.get", return_value=mock_response):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/missing.pdf", dest)
        assert result is False
        assert not dest.exists()


def test_download_pdf_skip_if_exists(tmp_path):
    dest = tmp_path / "existing.pdf"
    dest.write_bytes(b"already here")

    with patch("download.requests.get") as mock_get:
        result = download_pdf("https://example.com/test.pdf", dest)
        mock_get.assert_not_called()
        assert result is True
```

- [ ] **Step 7: テストが失敗することを確認**

```bash
pytest tests/test_download.py -v
```

期待出力: `ImportError: cannot import name 'download_pdf'`

- [ ] **Step 8: download_pdf 関数を download.py に追記**

```python
def download_pdf(url: str, dest: Path) -> bool:
    if dest.exists():
        print(f"  スキップ（既存）: {dest.name}")
        return True
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(response.content)
            print(f"  完了: {dest.name}")
            return True
        else:
            print(f"  失敗 ({response.status_code}): {url}")
            return False
    except requests.RequestException as e:
        print(f"  エラー: {e}")
        return False
```

- [ ] **Step 9: テストが全て通ることを確認**

```bash
pytest tests/test_download.py -v
```

期待出力: `6 passed`

- [ ] **Step 10: コミット**

```bash
git add download.py tests/
git commit -m "feat: add URL builders and download_pdf with tests"
```

---

### Task 3: メインループ実装・全件ダウンロード

**Files:**
- Modify: `download.py`（`build_download_plan` と `main` を追加）

- [ ] **Step 1: build_download_plan のテストを追加**

`tests/test_download.py` の冒頭 import 行を以下に更新する:
```python
from download import build_answer_url, build_question_url, download_pdf, build_download_plan
```

続けて以下のテストを追記:
```python
def test_build_download_plan_count():
    plan = build_download_plan()
    # 5年度 × 7科目 × 2種類（問題・解答）= 70件
    assert len(plan) == 70


def test_build_download_plan_entry_structure():
    plan = build_download_plan()
    year_label, subject, kind, url, dest = plan[0]
    assert kind in ("問題", "解答")
    assert url.startswith("https://")
    assert url.endswith(".pdf")
    assert isinstance(dest, Path)
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
pytest tests/test_download.py::test_build_download_plan_count -v
```

期待出力: `ImportError: cannot import name 'build_download_plan'`

- [ ] **Step 3: build_download_plan と main を download.py に追記**

```python
def build_download_plan():
    plan = []
    for ryear, cyear, year_label in YEARS:
        for subject, letter in SUBJECTS:
            q_url = build_question_url(ryear, cyear, letter)
            a_url = build_answer_url(ryear, cyear, letter)
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
        time.sleep(1)

    print(f"\n=== 完了: 成功 {success} 件 / 失敗 {failure} 件 / 合計 {total} 件 ===")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 全テストが通ることを確認**

```bash
pytest tests/test_download.py -v
```

期待出力: `8 passed`

- [ ] **Step 5: 1件だけ試しにダウンロードして動作確認**

令和3年度の解答a（アクセス確認済みのURL）で動作確認:

```bash
python -c "
from download import download_pdf, build_answer_url
from pathlib import Path
url = build_answer_url('r03', '2021', 'a')
dest = Path('downloads/_test/r03a_test.pdf')
print('URL:', url)
result = download_pdf(url, dest)
print('結果:', '成功' if result else '失敗')
"
```

期待: `downloads/_test/r03a_test.pdf` が作成される（数KB以上のPDFファイル）。

- [ ] **Step 6: テスト用フォルダを削除**

```powershell
Remove-Item -Recurse -Force downloads\_test
```

- [ ] **Step 7: 調査スクリプトを削除してコミット**

```bash
git rm url_investigation.py
git add download.py tests/
git commit -m "feat: add main loop and build_download_plan"
```

- [ ] **Step 8: 全件ダウンロードを実行**

```bash
python download.py
```

期待: `downloads/` 以下に令和2〜6年度 × 7科目 × 2種類のPDFが保存される。失敗件数も表示される（問題PDFのURLパターンが異なる場合は失敗になる）。

- [ ] **Step 9: 問題PDFが取得できなかった場合の対処**

Step 8 で問題PDFが全件失敗した場合は、Task 1 の調査結果を再確認し、`download.py` の `QUESTION_URL_PATTERN` を修正して再実行する。

- [ ] **Step 10: 最終コミット**

```bash
git add .
git commit -m "feat: complete PDF downloader - all 7 subjects, 5 years"
```
