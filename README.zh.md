<div align="center">

<div style="margin: 20px 0;">
  <img src="./assets/logo.png" height="60" alt="Weave Logo" >
</div>

# Weave

**用 AI 將投影片編織成結構完整的 Markdown 學習講義。**

*再也不會遺漏投影片裡的任何細節。*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)

[English](README.md) | [繁體中文](README.zh.md)

</div>

---

**Weave** 是一個 AI 驅動的命令列工具，能將 PDF 投影片自動轉換為結構化的 Markdown 學習講義。就像織布一樣，將零散的投影片內容編織成一份完整的學習資料。

## 解決的痛點

- 📋 投影片只有關鍵字，缺乏完整脈絡
- 📊 重要圖表沒有文字解釋
- 🔗 跨多份投影片尋找關聯概念極度耗時
- 📑 需要可列印的 PDF 版本方便複習

## 功能特色

- **兩階段 AI 分析** — 先產生結構化大綱，再逐章擴展完整內容
- **PDF 轉講義** — 將多頁 PDF 投影片轉換為一份結構清晰的 Markdown 文件
- **智慧圖片嵌入** — 自動辨識並嵌入重要的圖表、示意圖與公式
- **覆蓋率驗證** — 確保每一頁投影片都被納入最終講義
- **多語言輸出** — 可選擇任何語言產生講義（預設：繁體中文）
- **零資訊遺失** — 完整保留投影片所有內容，包括註腳與小字說明
- **PDF 匯出** — 一鍵將 Markdown 講義轉為排版精美的 PDF
- **Gemini 驅動** — 使用 Google 的多模態 AI，支援大量上下文

## 快速開始

### 系統需求

- Python 3.10+
- [Poppler](https://poppler.freedesktop.org/)（`pdf2image` 的 PDF 渲染依賴）
- [Pango](https://www.gtk.org/docs/architecture/pango)（`weasyprint` 的 PDF 匯出依賴）
- 一組 [Google Gemini API 金鑰](https://aistudio.google.com/apikey)

```bash
# macOS
brew install poppler pango

# Ubuntu / Debian
sudo apt-get install poppler-utils libpango-1.0-0 libpangoft2-1.0-0

# Windows (chocolatey)
choco install poppler
# Pango/GTK 安裝請參考 https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
```

### 安裝

```bash
# 複製專案
git clone https://github.com/ReeveWu/weave.git
cd weave

# 以可編輯模式安裝（開發用）
pip install -e .

# 或同時安裝開發依賴
pip install -e ".[dev]"
```

### 設定

```bash
# 複製範例環境設定檔，填入你的 API Key
cp .env.example .env
# 編輯 .env，將 your_api_key_here 改為實際的 Gemini API Key
```

### 基本用法

```bash
# 將 PDF 投影片放入 ./data/ 後執行
weave

# 指定輸入輸出目錄
weave -i ./我的投影片 -o ./筆記

# 使用 Pro 模型（更高品質）
weave -m gemini-2.5-pro

# 只產生大綱（先檢視結構再決定是否展開）
weave --outline-only

# 產生英文講義
weave --language English

# 同時輸出 PDF
weave --pdf

# 如果 Gemini 503/high demand，拉長重試等待時間
weave --unavailable-retry-delay 60 --max-retries 6

# 將已產生的 Markdown 單獨轉成 PDF
weave-pdf output/20260325_160828/handout.md
weave-pdf handout.md -o my_handout.pdf
```

也可以直接傳入 API Key：

```bash
weave -k "your-api-key" -i ./slides
```

> 📖 完整 CLI 參數說明請參考 [CLI Reference](docs/cli-reference.md)

## 運作原理

### 兩階段提示策略

1. **第一階段 — 大綱生成**：將所有投影片圖片送至 AI，產生帶有頁碼參照的樹狀章節大綱，讓 AI 先全覽整份講義的結構。

2. **第二階段 — 章節展開**：逐章搭配對應的投影片圖片與完整大綱作為上下文進行展開，確保內容詳盡、前後連貫，且不遺漏任何細節。

3. **後處理**：複製引用的圖片至輸出資料夾、驗證覆蓋率（確保沒有遺漏任何投影片），並清理暫存檔案。

## 輸出結構

每次執行會在輸出目錄下建立時間戳子資料夾：

```
output/
└── 20260325_160828/        # 時間戳資料夾 (YYYYMMDD_HHMMSS)
    ├── handout.md          # 完整的 Markdown 講義
    ├── handout.pdf          # PDF 版本（使用 --pdf 時產生）
    └── images/             # 嵌入的投影片圖片（圖表、示意圖等）
        ├── slide_01_page_005.jpg
        ├── slide_01_page_012.jpg
        └── ...
```

## 更多資訊

- [CLI 完整參數](docs/cli-reference.md)
- [程式化使用方式](docs/programmatic-usage.md)
- [疑難排解](docs/troubleshooting.md)
- [貢獻指南](CONTRIBUTING.md)

## 授權

本專案採用 MIT 授權 — 詳見 [LICENSE](LICENSE)。
