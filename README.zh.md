<div align="center">

<div style="margin: 20px 0;">
  <img src="./assets/logo.png" height="60" alt="Weave Logo" >
</div>

# Weave

**用 AI 將投影片編織成結構完整的 Markdown 學習講義。**

*再也不會遺漏投影片裡的任何細節。*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-339933.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)

[English](README.md) | [繁體中文](README.zh.md)

</div>

---

**Weave** 是一個 AI 驅動的工具，能將 PDF 投影片自動轉換為結構化的 Markdown 學習講義。提供**現代化網頁介面**讓你點幾下就能完成，同時也支援 **CLI** 供腳本與自動化使用。

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

---

## 快速開始（網頁介面）

### 系統需求

- **Python 3.10+** 與 **Node.js 18+**
- [Poppler](https://poppler.freedesktop.org/)（PDF 渲染依賴）
- [Pango](https://www.gtk.org/docs/architecture/pango)（PDF 匯出依賴）
- 一組 [Google Gemini API 金鑰](https://aistudio.google.com/apikey)

```bash
# macOS
brew install poppler pango

# Ubuntu / Debian
sudo apt-get install poppler-utils libpango-1.0-0 libpangoft2-1.0-0
```

### 1. 複製專案

```bash
git clone https://github.com/ReeveWu/weave.git
cd weave
```

### 2. 安裝所有依賴

執行一次，完成 Python 虛擬環境建立與前後端套件安裝：

```bash
npm run setup
```

這個指令會：
- 在 `.venv/` 建立 Python 虛擬環境
- 安裝 `weave` Python 套件與所有後端依賴
- 安裝前端（`client/`）npm 套件

### 3. 啟動應用程式

```bash
npm run start
```

同時啟動前後端：
- **後端 API**：`http://localhost:8000`
- **網頁介面**：`http://localhost:3000`

在瀏覽器開啟 [http://localhost:3000](http://localhost:3000)。

### 4. 使用網頁介面

1. **上傳 PDF** — 拖放或點擊選取一或多個 PDF 投影片檔案
2. **設定** — 輸入 Gemini API 金鑰、選擇模型與輸出語言，可選擇是否同時匯出 PDF
3. **執行** — 點擊「開始」，即時觀看每個處理階段的進度
4. **取得結果** — 瀏覽渲染後的 Markdown 講義，可複製、下載或匯出為 PDF

---

## 進階：CLI 使用方式

> CLI 適合用於腳本、自動化或批次處理。需先完成上方的 Python 環境安裝。

先啟動虛擬環境：

```bash
source .venv/bin/activate
```

將 PDF 投影片放入 `./data/` 後執行：

```bash
# 完整流程 — PDF 投影片 → Markdown 講義
weave

# 指定輸入輸出目錄
weave -i ./我的投影片 -o ./筆記

# 使用 Pro 模型（更高品質）
weave -m gemini-2.5-pro

# 只產生大綱（先檢視結構再決定是否展開）
weave --outline-only

# 產生英文講義
weave --language English

# 完整流程 + 匯出 PDF
weave --pdf

# 直接傳入 API Key（不需要 .env 檔）
weave -k "your-api-key" -i ./slides

# 如果 Gemini 503 / 高負載，拉長重試等待時間
weave --unavailable-retry-delay 60 --max-retries 6

# 將已產生的 Markdown 單獨轉成 PDF
weave-pdf output/20260325_160828/handout.md
weave-pdf handout.md -o my_handout.pdf
```

#### 設定 CLI 環境變數

使用 `.env` 儲存 API Key，就不用每次傳 `-k`：

```bash
cp .env.example .env
# 編輯 .env，設定 GEMINI_API_KEY=your_actual_key
```

> 📖 完整 CLI 參數說明請參考 [CLI Reference](docs/cli-reference.md)

---

## 運作原理

### 兩階段提示策略

1. **第一階段 — 大綱生成**：將所有投影片圖片送至 AI，產生帶有頁碼參照的樹狀章節大綱，讓 AI 先全覽整份講義的結構。

2. **第二階段 — 章節展開**：逐章搭配對應的投影片圖片與**完整大綱**作為上下文進行展開，確保內容詳盡、前後連貫，且不遺漏任何細節。

3. **後處理**：複製引用的圖片至輸出資料夾、驗證覆蓋率（確保沒有遺漏任何投影片），並清理暫存檔案。

## 輸出結構

每次執行會在輸出目錄下建立時間戳子資料夾：

```
output/
└── 20260325_160828/        # 時間戳資料夾 (YYYYMMDD_HHMMSS)
    ├── handout.md          # 完整的 Markdown 講義
    ├── handout.pdf         # PDF 版本（啟用 PDF 匯出時產生）
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
