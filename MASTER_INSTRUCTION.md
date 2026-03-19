# Swing Trader Daily Report — Master Instruction

這份文件總結了生成每日收市市場報告（EOD Market Summary）的完整工作流程、數據來源、格式要求以及所有必須遵守的原則。

**⚠️ AI 代理重要指示：每次開始新任務前，必須首先閱讀此文件。絕不能依賴記憶，絕不能估算數據，絕不能在未經用戶確認的情況下更改來源。Accuracy over speed — always.**

---

## 1. 核心原則與防錯機制 (Core Principles & Error Prevention)

為了避免過去發生的錯誤，必須嚴格遵守以下原則：

1. **Accuracy Over Speed（準確大於速度）**
   - 絕不估算（Estimate）任何數據。所有數值必須是來自指定來源的精確數字。
   - 報告中不允許出現 `~`（大約）符號來代替精確數據（時間戳除外）。
   - 如果遇到來源無法訪問或數據缺失，必須向用戶報告，而不是自行替換來源或捏造數據。

2. **不動結構，只換數據（Update Data, Keep Structure）**
   - 每次生成新報告時，必須使用前一日的 HTML 文件作為模板（例如 `2026-03-19.html`）。
   - 絕對禁止從頭重新編寫 HTML 結構或 CSS。
   - 只允許更新模板中的數值、日期和截圖 URL。

3. **行動前必須列出檢查清單（Checklist Before Action）**
   - 在開始收集數據和修改文件之前，必須先列出所有需要更新的 Sections 和對應的 URLs。
   - 必須等待用戶確認（"ok" 或 "go ahead"）後，才能開始執行。

4. **截圖完整性（Screenshot Integrity）**
   - 所有長網頁（如 Fullstack Investor、MarketInOut）必須滾動到底部，並將多張截圖完美拼接（Stitch）成一張完整的長圖，確保沒有任何資訊被截斷。

---

## 2. MARKET_HISTORY.md 自動更新規則 (Auto-Update Rule)

每次完成 Daily Market Summary 並推送至 GitHub 後，**必須立即更新 `MARKET_HISTORY.md`**：

1. 在 `## 📈 Trend Evolution Log` 部分的**最頂端**插入當日新記錄（最新日期在最上方）。
2. 每條記錄必須包含以下欄位（格式參考現有條目）：
   - 日期、Regime 等級、Action Guidance
   - VIX、Fear & Greed、T2108
   - SPX 收市價及與各 MA 的關係
   - $SPXA20R 廣度值
   - A/D Ratio (SPX)
   - 板塊領漲/領跌
   - 當日最重要的一句市場觀察（Key Observation）
3. 更新後將 `MARKET_HISTORY.md` 一同推送至 GitHub。
4. 同時將更新後的 `MARKET_HISTORY.md` 複製到 Manus 項目共享目錄（若可訪問）。

---

## 3. 報告觸發與發佈流程 (Workflow & Publishing)

- **觸發時間：** 美股收市後（美東時間下午 4:00 = 香港時間凌晨 4:00）。
- **自動執行時間：** 香港時間早上 **6:45 AM HKT**（即美東時間前一晚 6:45 PM ET），周一至周五，美股非假日。
- **發佈目標時間：** 香港時間早上 **6:45 AM HKT**。
- **觸發方式：** 用戶會在新對話中發送 "Clone the swing-trader-daily repo and read WORKFLOW.md, then make today's report" 或 "開始"。
- **發佈平台：** GitHub Pages (https://matt-manus.github.io/swing-trader-daily/)。
- **Git 操作：** 報告生成後，必須將新的 `index.html` 和歸檔文件（如 `2026-03-20.html`）推送到 `main` 分支。

---

## 3. 數據來源與具體要求 (Data Sources & Specific Requirements)

報告分為多個固定的 Steps，每個 Step 都有嚴格指定的數據來源和格式要求。

### 總覽與關鍵水平 (Verdict Box & Key Levels)
- **要求：** 總結當日市場環境（Regime）。
- **標題格式：** 必須使用 "Market Summary — [Date] | Generated [Time] HKT / [Time] ET"。
- **時間戳：** 數據時間必須精確到具體時間（例如 4:00 PM ET），不能只寫 "EOD close"。
- **MA 數值：** SPX 的 20MA、50MA、200MA 必須通過 `yfinance` 精確計算，不能使用約數。

### Step 1: 宏觀環境 (Macro Environment)
- **來源：** `yfinance` (SPY, QQQ, IWM, DIA, VIX, GLD, USO, ^TNX, UUP)。
- **Fear & Greed：** 來源為 https://feargreedmeter.com （抓取精確數值）。
- **經濟日曆：** 來源為 https://forex.tradingcharts.com/economic_calendar/ （手動查看未來三天的重要數據）。

### Step 2: Fullstack Investor
- **正確 URL：** **https://fullstackinvestor.co/market-model** （注意是 `.co`，不是 `.com`）。
- **要求：** **只放截圖，不作任何解讀**。不需要提取數據表，不需要寫 "Positive" 或 "Neutral" 的文字總結。
- **截圖技術：** 必須使用 Playwright/Selenium 等工具進行整頁截圖（Full-page screenshot），並加入滾動等待（Scroll-and-wait）以觸發懶加載（Lazy loading），**絕對不能出現黑色空隙（Black gap）**。

### Step 3: 市場情緒 (Market Sentiment)
- **要求：** 包含 VIX、Fear & Greed 和 T2108 的計分卡（Scorecard）。
- **T2108 來源：** 必須使用 Stockbee 的實際數據，絕不能估算。

### Step 4: 技術分析 (Technical Analysis)
- **4A Index vs MAs：** 使用 `yfinance` 數據。**特別注意：不需要 SPY 日線圖（已刪除）**。
- **4B Sector ETF Rotation：** 
  - 必須包含 11 個板塊 ETF 和 SPY。
  - **必須增加 RSI 14 欄位**。
  - **排序規則：** 必須按 **RSI 14 由高至低排序**（不是按 1D% 排序）。SPY 需按照其 RSI 數值插入到正確的排名位置。
- **4C % of Stocks Above MAs：**
  - **正確來源：** **StockCharts.com**。絕對不能使用 TradingView 或 MarketInOut。
  - **所需截圖（共 9 張）：** 
    - S&P 500: $SPXA20R, $SPXA50R, $SPXA200R
    - Nasdaq 100: $NDXA20R, $NDXA50R, $NDXA200R
    - NYSE: $NYA20R, $NYA50R, $NYA200R
  - **要求：** 必須顯示這 9 個指標的精確數值和截圖，不能有任何 "estimated" 標籤。

### Step 5: 板塊與行業強度 (Sector & Industry Strength)
- **5A Sector Performance：** 來源為 Finviz (https://finviz.com/groups.ashx?g=sector&o=-change) 的數據與截圖。
- **5B Industry Leaders：** 來源為 Finviz (https://finviz.com/groups.ashx?g=industry&o=-change)。
  - **要求：** 必須列出當日表現最好的 **Top 10** 行業，並且**必須包含其所屬的母板塊（Parent Sector）**。
  - **刪除：** 不需要列出表現最差的 Laggards（Bottom 5）。

### Step 6: 市場廣度 (Market Breadth)
- **6A Advance/Decline Ratio：** 
  - **正確 URL：** https://www.marketinout.com/chart/market.php?breadth=advance-decline-ratio （不需要登入）。
  - **要求：** 必須提供一張包含所有主要指數（S&P 500, Dow, NYSE, Nasdaq）的完整 MarketInOut 截圖。
- **6B Stockbee Market Monitor：**
  - **正確 URL：** **https://stockbee.blogspot.com/p/mm.html** （不需要登入，不是 `.biz`）。
  - **要求：** 截圖**必須包含 T2108 欄位**。
  - **截圖技術：** 由於 T2108 在 iframe 中，截圖時必須確保滾動到 iframe 內部或直接訪問 Google Sheets 來源 URL 進行截圖，確保 T2108 數據清晰可見。
  - **數據：** 需讀取 Up/Down 4%+ 和 5-day/10-day ratio 的精確數據填入報告。

### 已刪除的內容 (Removed Content)
以下內容在之前的版本中存在，但**已被明確要求刪除，絕不能出現在未來的報告中**：
- Step 7: UFO / Breakout Watchlist
- Report Comparison Notes (與其他報告的比較)
- SPY 日線圖 (Step 4A-ii)

---

## 4. 常見錯誤檢查清單 (Common Mistakes to Avoid)

在推送至 GitHub 前，必須進行以下自我檢查：

- [ ] Fullstack 網址是否正確（`.co` 而非 `.com`）？
- [ ] Stockbee 網址是否正確（`blogspot.com` 而非 `.biz`）？
- [ ] 報告中是否含有任何 `~` 符號或 "estimated" 字眼（時間戳除外）？
- [ ] Step 4B 是否已按 RSI 14 排序？
- [ ] Step 4C 是否使用了 StockCharts（$SPXA20R 等）的截圖？
- [ ] Step 6B 的 Stockbee 截圖是否包含了 T2108 數據？
- [ ] 是否已刪除 Step 7 和 Report Comparison？

嚴格遵守以上所有指示，確保每日報告的結構穩定和數據絕對準確。
