# 中小企業診断士 第1次試験 過去問クイズアプリ 設計書

## 概要

令和2〜7年度 全7科目の過去問PDFを使ったスマホ対応問題集アプリ。  
ローカルでビルドしてGitHub Pagesに静的デプロイする2ステップ構成。

---

## 要件

| 項目 | 内容 |
|------|------|
| 対象問題 | 令和2〜7年度 × 7科目 × 問題PDF 全約1,470問 |
| 問題表示 | PDFページ画像をそのまま表示（図・表・数式含む） |
| 出典表示 | 年度・科目名・設問番号を常時表示 |
| テーマ分類 | 7科目 × 各5テーマ（手動定義） |
| 解説 | 正解表示 ＋ Google検索リンク ＋ テーマ一致YouTube動画リンク（特定動画） ＋ ユーザーメモ |
| メモ機能 | 問題ごとにメモ記入・localStorage保存（永続） |
| ホスティング | GitHub Pages（無料・どこでもアクセス可能） |
| 著作権 | PDFは非公開リポジトリに保管、個人学習用途のみ |

---

## アーキテクチャ

```
[ローカルPC - 初回のみ]
downloads/（既存84 PDF）
    ↓
fetch_youtube.py                         ← YouTubeデータ取得（yt-dlp使用）
    ├─ youtube_config.json を読む（チャンネル定義）
    ├─ yt-dlp で各チャンネルの動画タイトル+URLを取得
    ├─ theme_map.json のキーワードで動画タイトルをマッチング
    └─ docs/data/youtube_data.json を生成

build.py
    ├─ PDF → JPEG画像変換（PyMuPDF）
    ├─ 解答PDF解析 → 正解JSON（pdfplumber）
    └─ quiz_data.json 生成

git push
    ↓
[GitHub Pages - 常時公開]
https://danalysis707.github.io/smec-pdf-downloader
    ├─ index.html + app.js + style.css
    ├─ data/quiz_data.json
    ├─ data/theme_map.json
    ├─ data/youtube_data.json            ← テーマ別マッチング済み動画一覧
    └─ images/{ryear}/{subject}/page_{NNN}.jpg
```

---

## ファイル構成

```
quiz/
├── download.py             # 既存PDFダウンローダー
├── build.py                # ビルドスクリプト（PDF→画像＋JSON）
├── fetch_youtube.py        # YouTube動画データ取得スクリプト（yt-dlp使用）
├── youtube_config.json     # YouTubeチャンネル定義（手動メンテ）
├── docs/                   # GitHub Pages 公開ルート
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── data/
│       ├── quiz_data.json     # 全問題メタデータ（build.py生成）
│       ├── theme_map.json     # テーマ分類定義
│       └── youtube_data.json  # テーマ別動画一覧（fetch_youtube.py生成）
├── downloads/              # gitignore済み（元PDF）
└── requirements.txt
```

---

## データ構造

### quiz_data.json

```json
{
  "questions": [
    {
      "id": "r02_keizai_q01",
      "year": "r02",
      "year_label": "令和2年度",
      "subject": "経済学・経済政策",
      "subject_short": "keizai",
      "question_number": 1,
      "theme": "ミクロ経済学",
      "pages": ["images/r02/keizai/page_001.jpg"],
      "correct_answer": "ウ",
      "answer_page": "images/r02/keizai_answer/page_001.jpg",
      "search_query": "令和2年度 中小企業診断士 経済学 第1問 解説"
    }
  ]
}
```

### youtube_config.json（手動メンテ・gitに含める）

チャンネル定義ファイル。`fetch_youtube.py` の入力として使用する。

```json
{
  "channels": [
    {
      "name": "はじめよう経済学",
      "url": "https://www.youtube.com/@hajimeyou-keizaigaku"
    },
    {
      "name": "ほらっちチャンネル",
      "url": "https://www.youtube.com/@Horacchichannel"
    },
    {
      "name": "たかぴーの中小企業診断士試験 攻略チャンネル",
      "url": "https://www.youtube.com/@takapi-shindanshi"
    }
  ]
}
```

### youtube_data.json（fetch_youtube.py 生成・gitに含める）

`fetch_youtube.py` がチャンネルの全動画タイトルを `theme_map.json` のキーワードでマッチングして生成する。アプリは問題の `subject` + `theme` でこのJSONを引いて該当動画を表示する。

```json
{
  "経済学・経済政策": {
    "ミクロ経済学": [
      {
        "title": "需要曲線と供給曲線の基礎",
        "url": "https://www.youtube.com/watch?v=XXXXXXXXX",
        "channel": "はじめよう経済学"
      },
      {
        "title": "需要の価格弾力性をわかりやすく解説",
        "url": "https://www.youtube.com/watch?v=YYYYYYYYY",
        "channel": "たかぴーの中小企業診断士試験 攻略チャンネル"
      }
    ],
    "マクロ経済学": [...]
  },
  "財務・会計": { ... }
}
```

### theme_map.json

```json
{
  "経済学・経済政策": [
    "ミクロ経済学",
    "マクロ経済学",
    "金融政策・財政政策",
    "国際経済・貿易・為替",
    "経済指標・景気動向"
  ],
  "財務・会計": [
    "財務諸表（B/S・P/L・CF）",
    "財務分析（収益性・安全性）",
    "管理会計・原価計算",
    "企業価値評価・投資",
    "資金調達・資本構成"
  ],
  "企業経営理論": [
    "経営戦略論",
    "組織論・人的資源管理",
    "マーケティング",
    "技術経営・イノベーション",
    "国際経営"
  ],
  "運営管理": [
    "生産管理・IE",
    "在庫管理・SCM",
    "品質管理・QC",
    "店舗・販売管理",
    "物流管理"
  ],
  "経営法務": [
    "会社法",
    "知的財産法（特許・商標等）",
    "民法・契約法",
    "資本市場・証券法",
    "独占禁止法・その他"
  ],
  "経営情報システム": [
    "ハードウェア・OS基礎",
    "ネットワーク・セキュリティ",
    "データベース",
    "経営情報システム（ERP等）",
    "統計・データ分析"
  ],
  "中小企業経営・中小企業政策": [
    "中小企業の現状・統計",
    "中小企業政策・支援制度",
    "中小企業金融",
    "創業・ベンチャー支援",
    "事業承継・M&A"
  ]
}
```

---

## 画面仕様

### 画面① 科目・テーマ・年度選択

- 科目リスト（7科目）をタップして選択
- テーマチップ（各5個）で絞り込み（複数選択可）
- 年度チップ（全年度 / 令和2〜7年度）で絞り込み
- 「▶ 学習開始（N問）」ボタンで出題開始

### 画面② 問題表示・解答

**ヘッダー（常時表示）:**
```
[令和4年度] [経済学・経済政策] [第3問]
```

**本文:**
- PDFページのJPEG画像を全幅表示（ピンチズーム対応）
- テーマバッジ・進捗表示（3 / 28問）
- 解答ボタン: ア / イ / ウ / エ（または ① 〜 ⑤）をタップ
- 「🔍 この問題を検索」ボタン（解答前でも押せる）

### 画面③ 正解・解説・メモ

**ヘッダー（常時表示・同上）**

**本文:**
- 正誤バッジ（✅ 正解！ / ❌ 不正解）
- 正解記号・自分の解答を並べて表示
- 「📄 解答PDFで確認」ボタン（解答ページ画像を表示）
- 「🔍 解説をネット検索（令和4年 経済学 第3問）」ボタン
- 📺 YouTube関連動画セクション（`youtube_data.json` から `subject` + `theme` で引いた動画を最大3件表示）  
  表示形式: `📺 [動画タイトル]（[チャンネル名]）`（タップでYouTube動画を開く）  
  例: `📺 需要曲線と供給曲線の基礎（はじめよう経済学）`  
  　　`📺 ミクロ経済学 需要の弾力性（たかぴーの中小企業診断士試験 攻略チャンネル）`  
  該当動画なしの場合はセクション自体を非表示にする。
- 📝 メモ欄（テキストエリア）：入力内容はlocalStorageに自動保存
- 「次の問題へ →」ボタン

---

## fetch_youtube.py 仕様

### 処理フロー

1. `youtube_config.json` からチャンネルURLを読み込む
2. `docs/data/theme_map.json` からキーワード辞書を読み込む
3. 各チャンネルに対して `yt-dlp --flat-playlist` で動画タイトル・URLを取得
4. 各動画のタイトルに対して `theme_map.json` のキーワードでマッチング
5. マッチした動画を `{subject: {theme: [{title, url, channel}]}}` 形式で集約
6. `docs/data/youtube_data.json` に出力

### キーワードマッチング

`theme_map.json` と共通のキーワード辞書を使用する。動画タイトルに科目・テーマのキーワードが含まれれば、そのテーマに分類する。1つの動画が複数テーマにマッチした場合は最初にマッチしたテーマに分類する。

```python
def match_video_to_theme(title: str, theme_keywords: dict) -> tuple[str, str] | None:
    """動画タイトルをキーワードマッチし (subject, theme) を返す。未マッチはNone。"""
    for subject, themes in theme_keywords.items():
        for theme, keywords in themes.items():
            if any(kw in title for kw in keywords):
                return subject, theme
    return None
```

### 実行例

```bash
python fetch_youtube.py
# Fetching: はじめよう経済学 ... 142 videos
# Fetching: ほらっちチャンネル ... 87 videos
# Fetching: たかぴーの中小企業診断士試験 攻略チャンネル ... 210 videos
# Matched: 経済学・経済政策/ミクロ経済学 → 8 videos
# ...
# Done: docs/data/youtube_data.json (47 subjects/theme entries, 124 videos total)
```

---

## build.py 仕様

### 処理フロー

1. `downloads/` 以下の問題PDFを年度・科目ごとに列挙
2. PyMuPDFで各ページをJPEG変換（解像度150dpi・品質85）
3. pdfplumberで解答PDFのテキストを抽出し正解記号をパース
4. 設問番号と正解のマッピングを生成
5. `data/quiz_data.json` を出力
6. `data/theme_map.json` を出力（手動定義済みデータをコピー）

### テーマ割り当て方法

各問題のテーマはキーワードマッチングで自動割り当て:

```python
THEME_KEYWORDS = {
    "経済学・経済政策": {
        "ミクロ経済学":      ["需要", "供給", "弾力性", "消費者余剰", "独占", "寡占", "ゲーム理論"],
        "マクロ経済学":      ["GDP", "国民所得", "乗数", "IS-LM", "消費関数", "投資"],
        "金融政策・財政政策": ["日本銀行", "金融政策", "財政政策", "公開市場操作", "準備率"],
        "国際経済・貿易・為替": ["為替", "貿易", "比較優位", "経常収支", "国際収支"],
        "経済指標・景気動向": ["景気", "物価", "CPI", "GDP成長率", "景気循環"],
    },
    # 他科目も同様に定義
}
```

マッチしない問題は「その他」に分類。

### 設問番号の検出方法（Approach B）

- `第N問` パターンでテキスト検索し、出現ページを記録
- 各設問の開始ページ〜次の設問の前ページを画像セットとする
- 検出できない問題はページ番号順でフォールバック

### 正解抽出

解答PDFのテキストから以下パターンを正規表現でパース:

```
第1問　ウ　第2問　ア　第3問　イ ...
```

年度・科目ごとにパターンが異なる場合は個別対応。

---

## app.js 仕様

### 主要機能

| 機能 | 実装方法 |
|------|---------|
| フィルタリング | quiz_data.jsonをJS側でフィルター |
| 解答管理 | セッション内はメモリ、メモはlocalStorage |
| 進捗表示 | 正答数/出題数をリアルタイム更新 |
| メモ保存 | `localStorage.setItem(questionId, memo)` |
| 検索リンク | `https://www.google.com/search?q=${searchQuery}` |
| YouTube動画リンク | `youtube_data.json` を init 時に fetch し、解答後に `question.subject` + `question.theme` で引いた動画を最大3件表示。マッチなしの場合は非表示。 |
| 画像ズーム | CSS `touch-action: pinch-zoom` + max-width 100% |

### localStorage キー設計

```
memo_{question_id}   → メモテキスト
result_{question_id} → 最終解答結果 (correct/wrong)
```

---

## 非機能要件

| 項目 | 要件 |
|------|------|
| スマホ対応 | レスポンシブ、タップ操作、ピンチズーム |
| オフライン | 画像はGitHub Pagesからキャッシュ（初回要ネット） |
| ページ速度 | 画像は150dpi JPEG圧縮で1枚あたり約80〜150KB |
| ブラウザ | iOS Safari / Android Chrome / PC Chrome |
| データ永続 | メモ・進捗はlocalStorage（端末ごと） |

---

## デプロイ手順

```bash
# 1. YouTube動画データ取得（初回 or チャンネル更新時）
pip install yt-dlp
python fetch_youtube.py
# → docs/data/youtube_data.json を生成

# 2. ビルド（初回 or PDF更新時）
pip install pymupdf pdfplumber
python build.py

# 2. GitHub Pagesにデプロイ
git add data/ images/ app/
git commit -m "build: update quiz data and images"
git push

# 3. アクセス
# https://danalysis707.github.io/smec-pdf-downloader
```

---

## 実装タスク概要

1. **build.py**: PDF→画像変換・正解抽出・JSON生成
2. **data/theme_map.json**: テーマ分類定義ファイル
3. **app/index.html + style.css**: スマホ対応UI骨格
4. **app/app.js**: フィルター・解答・メモ・進捗ロジック
5. **GitHub Pages設定**: リポジトリのPages設定を有効化
