# Swing Trader Daily Report — Master Instruction

這份文件總結了生成每日收市市場報告（EOD Market Summary）的完整工作流程、數據來源、格式要求以及所有必須遵守的原則。

**⚠️ AI 代理重要指示：每次開始新任務前，必須首先閱讀此文件。絕不能依賴記憶，絕不能估算數據，絕不能在未經用戶確認的情況下更改來源。Accuracy over speed — always.**

---

## 1. 核心原則與防錯機制 (Core Principles & Error Prevention)

為了避免過去發生的錯誤，必須嚴格遵守以下原則：

1. **強制重讀機制（Mandatory Re-read Before Building）**
   - **CRITICAL:** 在開始構建 HTML 報告（Phase 5）之前，AI 代理**必須**重新讀取本文件（`MASTER_INSTRUCTION.md`）和 `RULES_EVOLUTION.md`。
   - 由於上下文壓縮（Context Compression），早前讀取的規則和 URL 會丟失。絕不能依賴記憶去填寫 URL 或格式。

2. **截圖數據驗證（Verify Screenshot Data）**
   - 任何從截圖中獲取的數據（如 StockCharts 的 %、Stockbee 的 T2108），必須在截圖後使用 `file view` 工具**親眼讀取圖片上的數字**，絕不能憑空估算或使用前一日的數字。

3. **Accuracy Over Speed（準確大於速度）**
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

5. **知識誠實性（Intellectual Honesty — 唔估、唔假設、唔扮知）**
   - **區分「查到的」同「估的」**：凡係用工具、代碼、截圖直接查到的數據，才可以直接陳述。凡係推斷、假設、或「聽起來合理」的解釋，必須明確標示為「我的推斷」或「我唔確定」。
   - **遇到唔確定就直接講「我唔知道」**：唔知道排程點運作、唔知道某個系統的行為、唔知道某件事的原因 → 直接說「我唔知道，我查唔到」，而唔係用合理聽起來的解釋去填補空白。
   - **唔好用「最可能係」、「應該係」、「通常係」去解釋自己冇查過的事**：呢類措辭係估算的信號。如果冇直接證據，就唔好用有信心的語氣陳述。
   - **錯了就直接承認**：如果之前給了一個錯誤的解釋或結論，直接承認「我之前講錯了，原因係我估的而唔係查到的」，唔好繞圈子或者轉移話題。
   - **此規則適用於所有對話，不只是報告數據**：包括解釋系統行為、排程運作、技術問題等任何情況。

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

### 總覽 (Verdict Box)
- **要求：** 總結當日市場環境（Regime）。
- **標題格式：** 必須使用 "Market Summary — [Date] | Generated [Time] HKT / [Time] ET"。
- **時間戳：** 數據時間必須精確到具體時間（例如 4:00 PM ET），不能只寫 "EOD close"。
- **時區換算（重要）：** HKT = UTC+8，ET（夏令時 EDT）= UTC-4。HKT 比 ET **快 12 小時**。正確換算：07:45 HKT = 19:45 ET（前一日）。**絕不能**寫成 "19:45 HKT / 07:45 ET"（方向相反）。報告生成時間通常係香港早上 6:45–7:45 HKT，對應美東時間前一日 18:45–19:45 ET。

### Step 1: 宏觀環境 (Macro Environment)
- **來源：** `yfinance` (SPY, QQQ, IWM, DIA, VIX, GLD, USO, ^TNX, DX-Y.NYB)。
- **USD 指數：** 使用 **DXY（`DX-Y.NYB`）** 而非 UUP ETF。DXY 係美元指數本身，更直接、更標準；UUP 係 ETF，有追蹤誤差。
- **Fear & Greed：** 來源為 https://feargreedmeter.com （抓取精確數值）。
- **經濟日曆：** 來源為 https://forex.tradingcharts.com/economic_calendar/ （手動查看未來三天的重要數據）。

### Step 3: 市場情緒 (Market Sentiment)
- **要求：** 包含 VIX、Fear & Greed、T2108 和 **NAAIM Exposure Index** 的計分卡（Scorecard）。
- **T2108 來源：** 必須使用 Stockbee 的實際數據，絕不能估算。
- **NAAIM Exposure Index：**
  - **來源：** NAAIM 官網每週三發布 Excel 文件，直接下載解析。URL 格式：`https://naaim.org/wp-content/uploads/[YYYY]/[MM]/USE_Data-since-Inception_[YYYY-MM-DD].xlsx`
  - **更新頻率：** 每週三更新，其餘日子顯示最近一次的數值並標明日期。
  - **解讀：** 0–100% 代表機構主動管理人的平均股票倉位；>75% 偏多，<50% 偏空，<25% 極度悲觀。
  - **加入 Scorecard：** 在 Step 3 的 Scorecard 中加入 NAAIM 數值，與 VIX、Fear & Greed、T2108 並列顯示。

### Step 4: 技術分析 (Technical Analysis)
- **4A Index vs MAs：** 使用 `yfinance` 數據。**特別注意：不需要 SPY 日線圖（已刪除）**。
  - **只使用以下 4 個指數：SPY、QQQ、DIA（道瓊斯 ETF）、IWM**。不需要 SPX 或 NDX 指數本身。
  - **MA 顏色規則（必須嚴格執行）：** 若某指數收市價低於某條 MA，該欄位必須顯示**紅色**；若高於，顯示**綠色**。絕不能因為照搬模板而顯示錯誤顏色。Signal badge 亦必須根據實際 MA 位置自動判斷（ABOVE / BELOW / BREACHED）。
- **4B % of Stocks Above MAs：**
  - **正確來源：** **StockCharts.com**。絕對不能使用 TradingView 或 MarketInOut。
  - **所需截圖（共 9 張）：** 
    - S&P 500: $SPXA20R, $SPXA50R, $SPXA200R
    - Nasdaq 100: $NDXA20R, $NDXA50R, $NDXA200R
    - NYSE: $NYA20R, $NYA50R, $NYA200R
  - **要求：** 必須顯示這 9 個指標的精確數值和截圖，不能有任何 "estimated" 標籤。**注意：截圖大小必須是原來的兩倍（Double the size of current screenshots）。**
- **4C Sector ETF Rotation：** 
  - 必須包含 11 個板塊 ETF 和 SPY。
  - **必須增加 RSI 14 欄位**。
  - **排序規則：** 必須按 **RSI 14 由高至低排序**（不是按 1D% 排序）。SPY 需按照其 RSI 數值插入到正確的排名位置。
  - **RSI 計算方法：** 必須使用 **Wilder's Smoothed Moving Average（SMMA / RMA）** 計算 RSI 14，而非簡單 rolling mean。使用 `pandas_ta` 庫的 `ta.rsi()` 或手動實現 SMMA：`smma = (prev_smma * 13 + current_value) / 14`。簡單 rolling mean 會導致 RSI 數值偏低，與 Yahoo Finance / TradingView 顯示的數值不符。

### Step 5: 板塊與行業強度 (Sector & Industry Strength)
- **5A Sector Performance：** 來源為 Finviz (https://finviz.com/groups.ashx?g=sector&o=-change) 的數據與截圖。

**注意：原 Step 5B 已移至 Step 4D。**

**4D Industry Leaders：** 來源為 Finviz (https://finviz.com/groups.ashx?g=industry&o=-change)。
  - **要求：** 必須列出當日表現最好的 **Top 10** 行業，並且**必須包含其所屬的母板塊（Parent Sector）**。
  - **刪除：** 不需要列出表現最差的 Laggards（Bottom 5）。

### Step 6: 市場廣度 (Market Breadth)
- **6B Stockbee Market Monitor：**
  - **正確 URL：** **https://stockbee.blogspot.com/p/mm.html** （不需要登入，不是 `.biz`）。
  - **要求：** 截圖**必須包含 T2108 欄位**。
  - **截圖技術：** 由於 T2108 在 iframe 中，截圖時必須確保滾動到 iframe 內部或直接訪問 Google Sheets 來源 URL 進行截圖，確保 T2108 數據清晰可見。
  - **數據：** 需讀取 Up/Down 4%+ 和 5-day/10-day ratio 的精確數據填入報告。
  - **截圖時機：** 必須在美股**收市後**（4:00 PM ET 之後）重新截圖，確保數據係當日收市數據。不能使用早上截的圖標示為 LIVE。

### Step 7: 每日市場評論 (Daily Market Commentary — Bull vs Bear)
- **目的：** 根據當日所有數據，從多頭（Bullish）和空頭（Bearish）兩個角度各自列出論點，幫助投資者做出更平衡的判斷。
- **格式：** 固定分為三部分：
  1. **🐻 空頭論點（Bearish Case）** — 列出 4–6 條當日最重要的看空理由，每條需引用具體數據（如 VIX 數值、RSI、MA 關係等）。
  2. **🐂 多頭論點（Bullish Case）** — 列出 3–5 條當日最重要的看多理由，同樣需引用具體數據。
  3. **⚖️ 多空力量對比表** — 用表格列出各維度（長期趨勢、市場廣度、情緒面、機構倉位、宏觀環境、短期技術、基本面）的多空勝負，並給出「多空比分」及一句總結交易指引。
- **數據來源：** 完全基於當日報告的實際數據（Steps 1–6），不得引入報告以外的估算或主觀判斷。
- **語言：** 繁體中文為主，技術術語保留英文（如 RSI、VIX、MA、T2108）。
- **位置：** 放在 Step 6 市場廣度之後，Regime Box（市場環境判定）之前。
- **長度：** 空頭論點每條 2–3 句，多頭論點每條 2–3 句，總長度控制在 600–900 字。

### 已刪除的內容 (Removed Content)
以下內容在之前的版本中存在，但**已被明確要求刪除，絕不能出現在未來的報告中**：
- Step 7: UFO / Breakout Watchlist
- Report Comparison Notes (與其他報告的比較)
- SPY 日線圖 (Step 4A-ii)

---

## 4. 常見錯誤檢查清單 (Common Mistakes to Avoid)

在推送至 GitHub 前，必須進行以下自我檢查：

- [ ] Stockbee 網址是否正確（`blogspot.com` 而非 `.biz`）？
- [ ] 報告中是否含有任何 `~` 符號或 "estimated" 字眼（時間戳除外）？
- [ ] Step 4B 是否使用了 StockCharts（$SPXA20R 等）的截圖，並且尺寸為兩倍大？
- [ ] Step 4C 是否已按 RSI 14 排序？
- [ ] Step 6B 的 Stockbee 截圖是否包含了 T2108 數據？
- [ ] 是否已刪除 Step 7 UFO 和 Report Comparison？
- [ ] Step 3 Scorecard 是否已包含 NAAIM Exposure Index 數值（並標明數據日期）？
- [ ] Step 1 USD 是否使用 DXY（`DX-Y.NYB`）而非 UUP？
- [ ] Step 4A 是否只有 SPY/QQQ/DIA/IWM 四個指數？MA 顏色是否根據實際位置正確顯示（低於 MA = 紅色）？
- [ ] Step 4C RSI 是否使用 Wilder's SMMA 算法計算？排序是否正確（由高至低）？
- [ ] Step 6B Stockbee 截圖是否在收市後（4:00 PM ET 後）重新截取？
- [ ] 所有描述文字（如 VIX 漲跌描述）是否根據當日實際數據更新，而非照搬昨日模板？
- [ ] Step 7 市場評論是否包含空頭論點、多頭論點及多空對比表？所有論點是否引用報告內的具體數據？

嚴格遵守以上所有指示，確保每日報告的結構穩定和數據絕對準確。
