# Product Requirements Document

## 1. Product Overview

### Working Name
**BandarAI**

Nama bersifat sementara dan dapat diganti pada tahap branding.

### Product Description

BandarAI adalah web-based Indonesian equity research and trading intelligence platform yang membantu pengguna menganalisis saham Bursa Efek Indonesia menggunakan kombinasi:

- Broker Summary / Smart Money Analysis
- Price & Volume Analysis
- Technical Analysis
- Financial & Fundamental Analysis
- News & Catalyst Intelligence
- Market & Sector Context
- AI Research Assistant
- Evidence-based Bull vs Bear Analysis
- Interactive Research Graph

Platform tidak sekadar menghasilkan sinyal "BUY" atau "SELL".

Setiap kesimpulan harus memiliki:

1. Thesis
2. Supporting Evidence
3. Counter Evidence
4. Source
5. Confidence
6. Invalidation Condition
7. Risk
8. Suggested scenario

Tujuan utama sistem adalah membantu pengguna memahami:

> **Apa yang sedang terjadi pada suatu saham, siapa yang terlihat sedang melakukan akumulasi atau distribusi melalui data broker, katalis apa yang sedang memengaruhi saham tersebut, apa bukti yang mendukung thesis, dan apa bukti yang dapat mematahkan thesis tersebut.**

---

# 2. Product Vision

Membangun sebuah:

**AI-powered Indonesian Equity Research & Smart Money Intelligence Platform**

yang menggabungkan pengalaman:

- financial terminal
- equity research platform
- broker flow intelligence
- news intelligence
- technical analysis
- AI analyst
- visual research graph

ke dalam satu aplikasi.

Platform harus terasa seperti:

> **Koyfin information density + Linear polish + Palantir intelligence graph + Unreal Blueprint-inspired Bezier research canvas.**

---

# 3. Core Philosophy

## 3.1 Evidence First

AI tidak boleh memberikan klaim finansial penting tanpa evidence yang dapat ditampilkan kepada user.

Contoh:

**Tidak boleh:**

> ANTM sedang diakumulasi oleh smart money.

Tanpa penjelasan.

**Harus:**

> ANTM menunjukkan indikasi akumulasi broker selama 6 sesi terakhir.

Evidence:

- Broker YP: +Rp62B
- Broker AK: +Rp48B
- Broker CC: +Rp31B
- Top-3 broker concentration: 61%
- Harga relatif sideways selama periode akumulasi
- Avg accumulation cost: Rp3.110
- Current price: Rp3.220

---

# 4. Important Analytical Principle

## Broker Flow ≠ Identitas Bandar

Platform tidak boleh mengklaim mengetahui identitas sebenarnya dari "bandar".

Data broker digunakan sebagai proxy untuk:

- accumulation
- distribution
- concentration
- persistence
- cost basis
- broker behaviour
- foreign flow
- unusual flow

Terminologi yang digunakan pada aplikasi:

**Smart Money / Broker Flow / Accumulation Intelligence**

bukan klaim:

> "Bandar X pasti sedang membeli."

---

# 5. Main User Problems

Retail investor/trader sering memiliki informasi yang terpisah-pisah:

- broker summary di satu aplikasi
- chart di aplikasi lain
- berita di website berbeda
- laporan keuangan di tempat lain
- macro data di sumber lain
- analisis dilakukan manual

Masalah lainnya:

### Confirmation Bias

User sering sudah memiliki pendapat terlebih dahulu.

Contoh:

> "ANTM pasti naik karena nickel naik."

Kemudian hanya mencari data yang membenarkan pendapat tersebut.

BandarAI harus secara aktif mencari:

**evidence yang mendukung DAN evidence yang membantah thesis tersebut.**

---

# 6. Target Users

Primary:

- Indonesian retail trader
- swing trader
- active investor
- investor yang menggunakan broker summary
- investor yang mengikuti foreign flow
- data-driven retail investor

Secondary:

- finance students
- equity research learners
- quantitative finance enthusiasts
- data analysts
- independent researchers

---

# 7. Product Goals

Platform harus memungkinkan pengguna:

1. Menemukan saham dengan pola broker accumulation yang menarik.
2. Melihat broker yang dominan membeli dan menjual.
3. Mengidentifikasi silent accumulation.
4. Mengidentifikasi distribution.
5. Menghubungkan broker behaviour dengan price action.
6. Menghubungkan news dengan ticker terkait.
7. Menghubungkan commodity/macro event dengan saham terkait.
8. Mendapatkan AI explanation dari setiap signal.
9. Mendapatkan argument yang berlawanan dengan thesis.
10. Melihat evidence secara visual.
11. Menilai apakah opportunity bagus.
12. Menilai apakah timing entry bagus.
13. Melihat risiko dan invalidation condition.
14. Melakukan historical validation/backtesting terhadap strategy.

---

# 8. Non Goals

Versi awal tidak bertujuan menjadi:

- broker saham
- automated execution platform
- high-frequency trading platform
- robo advisor
- guaranteed stock prediction system
- copy trading platform
- financial advisory service

Platform tidak mengeksekusi transaksi secara otomatis.

---

# 9. Core Product Modules

Navigasi utama:

- Overview
- Daily Opportunities
- Smart Money
- Screener
- Stocks
- News Intelligence
- AI Research
- Strategy Lab
- Watchlist

---

# 10. Overview Dashboard

Halaman utama memberikan gambaran cepat market Indonesia.

## Components

### Market Overview

Menampilkan:

- IHSG
- daily change
- trading value
- market breadth
- foreign net flow
- USD/IDR
- strongest sector
- weakest sector

### Today's Opportunities

Contoh:

ANTM

Opportunity: 89  
Smart Money: 94  
Technical: 83  
Catalyst: 87  
Entry Quality: 72  

Signal:

**Silent Accumulation**

### Smart Money Radar

Top saham berdasarkan broker accumulation score.

### Market Sector Rotation

Contoh:

Mining ↑  
Energy ↑  
Banking →  
Technology ↓

### Important News

Berita yang memiliki market impact tertinggi.

### AI Morning Brief

Contoh:

> Broker accumulation meningkat pada beberapa saham basic materials sementara sector momentum ikut menguat. Namun foreign flow pada large-cap banking masih negatif.

---

# 11. Daily Opportunities

Platform melakukan ranking saham setiap trading day.

Namun platform tidak menampilkan:

**"Top Stocks To Buy Today."**

Terminologi:

**Today's Opportunities**

Setiap ticker memiliki beberapa score.

## Main Scores

### Opportunity Score

Menjawab:

> Seberapa menarik setup saham ini?

### Entry Quality

Menjawab:

> Apakah sekarang merupakan entry yang menarik?

### Smart Money Score

Menjawab:

> Seberapa kuat indikasi broker accumulation?

### Catalyst Score

Menjawab:

> Seberapa kuat katalis yang mendukung?

### Technical Score

Menjawab:

> Seberapa sehat struktur harga?

### Fundamental Quality

Menjawab:

> Seberapa sehat bisnis/perusahaan?

### Risk Score

Menilai risiko setup.

---

# 12. Important Score Separation

Platform harus membedakan:

**Good Company**

dengan

**Good Opportunity**

dan

**Good Entry**

Contoh:

BBCA dapat memiliki:

Fundamental Quality: 94

Opportunity: 82

Entry Quality: 52

Artinya:

Perusahaan berkualitas dan saham menarik untuk diamati, namun harga sekarang belum memberikan entry yang ideal.

---

# 13. Smart Money / Bandarmology Module

Ini merupakan salah satu fitur utama platform.

Menu:

## Smart Money Radar

Menampilkan saham yang menunjukkan:

- accumulation
- silent accumulation
- increasing accumulation
- distribution
- increasing distribution
- accumulation breakout
- possible re-accumulation

---

# 14. Broker Summary Analysis

Untuk setiap saham sistem menganalisis:

- broker buy value
- broker sell value
- broker net value
- buy volume
- sell volume
- average buy price
- average sell price
- transaction frequency
- foreign/domestic classification jika tersedia

Timeframe:

- 1D
- 3D
- 5D
- 10D
- 20D
- custom

---

# 15. Accumulation Persistence

Sistem tidak hanya melihat net buy satu hari.

Contoh:

Broker YP:

Day 1: +12B  
Day 2: +18B  
Day 3: +14B  
Day 4: +21B  
Day 5: +17B  

lebih menarik daripada:

Day 1: +100B  
Day 2: -95B

Sistem harus memberikan persistence score.

---

# 16. Broker Concentration

Mengukur apakah accumulation terkonsentrasi pada beberapa broker tertentu.

Contoh:

Top 3 broker mengontrol:

64% total net accumulation.

Semakin tinggi concentration, semakin menarik untuk dianalisis.

Tetapi concentration ekstrem juga harus diberikan risk flag.

---

# 17. Broker Cost Basis

Sistem menghitung approximate average accumulation cost.

Contoh:

YP Avg Cost: Rp3.105  
AK Avg Cost: Rp3.128  
CC Avg Cost: Rp3.092

Current Price:

Rp3.230

User dapat melihat apakah current price:

- below estimated cost
- near cost
- moderately above cost
- significantly above cost

---

# 18. Broker Cost Map

Visualisasi:

Current Price  
Rp3.400

YP ● Rp3.250

AK ● Rp3.170

CC ● Rp3.110

Tujuan:

Mempermudah pengguna memahami cost basis broker.

---

# 19. Accumulation Matrix

Contoh:

| Broker | 1D | 3D | 5D | 10D | 20D |
|---|---:|---:|---:|---:|---:|
| YP | +12B | +34B | +61B | +102B | +151B |
| AK | +8B | +19B | +42B | +76B | +94B |
| CC | -2B | +4B | +16B | +31B | +72B |
| PD | +1B | -8B | -21B | -36B | -81B |

UI menggunakan heatmap.

---

# 20. Smart Money Divergence

Salah satu signal penting.

## Positive Divergence

Harga:

sideways / turun sedikit.

Broker accumulation:

terus meningkat.

Signal:

**Possible Silent Accumulation**

## Negative Divergence

Harga:

masih naik.

Broker accumulation:

berubah menjadi distribution.

Signal:

**Possible Distribution Into Strength**

---

# 21. Silent Accumulation Detection

Signal muncul ketika beberapa kondisi terpenuhi:

- price consolidation
- volatility relatively low
- accumulation persistence high
- broker concentration increasing
- volume structurally increasing
- large negative distribution tidak ditemukan

Output:

**Silent Accumulation Candidate**

Bukan:

**Guaranteed Buy**

---

# 22. Distribution Detection

Mendeteksi kondisi:

- harga naik tetapi broker besar net sell
- concentration of selling meningkat
- previous accumulator mulai menjual
- volume tinggi saat distribution
- price gagal breakout

Signal:

**Distribution Risk**

---

# 23. Broker Explorer

User dapat membuka broker tertentu.

Contoh:

**Broker YP**

Menampilkan:

Largest Accumulation:

ANTM +62B  
MDKA +38B  
INCO +26B  
PTBA +11B

Tujuan:

Mendeteksi kemungkinan sector-level accumulation.

---

# 24. Broker Network Graph

Interactive graph.

Contoh:

YP → ANTM  
YP → MDKA  
YP → INCO

Ketebalan edge menunjukkan magnitude flow.

Color:

Green = accumulation  
Red = distribution

---

# 25. Technical Analysis Engine

Technical tidak boleh menjadi sekumpulan indikator tanpa konteks.

Core indicator:

- EMA 20
- EMA 50
- EMA 200
- VWAP
- RSI
- MACD
- ATR
- Relative Volume
- OBV
- Support
- Resistance
- Swing High
- Swing Low
- Breakout
- Breakdown
- 52-week position

---

# 26. Technical Structure Analysis

Sistem mencoba mengidentifikasi:

- uptrend
- downtrend
- consolidation
- accumulation range
- breakout
- failed breakout
- pullback
- momentum continuation
- reversal candidate

---

# 27. Price + Broker Confirmation

Contoh setup:

Price breakout  
+  
Relative Volume > 1.5x  
+  
Broker accumulation increasing

Signal:

**Smart Breakout**

Sebaliknya:

Price breakout  
+  
high volume  
+  
dominant brokers distributing

Signal:

**Breakout Quality Warning**

---

# 28. News Intelligence Engine

News bukan sekadar feed berita.

Pipeline:

News Source  
→ Article Extraction  
→ Entity Detection  
→ Ticker Mapping  
→ Event Classification  
→ Sentiment  
→ Expected Impact  
→ Time Horizon  
→ Evidence Graph

---

# 29. News Sources

Prioritas sumber:

Tier 1:

- IDX disclosures
- company announcements
- Bank Indonesia
- OJK
- BPS
- government regulatory sources

Tier 2:

- Reuters
- Bloomberg jika tersedia
- CNBC Indonesia
- Kontan
- Bisnis Indonesia
- Investor Daily
- other reputable finance publications

---

# 30. News Event Classification

News dikategorikan menjadi:

### Corporate

- earnings
- dividend
- acquisition
- merger
- contract win
- expansion
- capex
- management change
- debt issuance
- rights issue
- buyback
- stock split

### Macro

- interest rate
- inflation
- GDP
- currency
- regulation
- fiscal policy

### Commodity

- nickel
- coal
- oil
- gas
- gold
- CPO
- copper

### Risk

- lawsuit
- fraud investigation
- operational issue
- regulatory sanction
- governance issue

---

# 31. News Impact Model

Setiap news memiliki:

- affected ticker
- affected sector
- direction
- magnitude
- time horizon
- confidence
- source quality

Contoh:

Event:

Nickel supply disruption

Affected Sector:

Basic Materials

Affected:

ANTM  
INCO  
NCKL

Direction:

Potential Positive

Impact:

Medium-High

Horizon:

Short-Medium Term

---

# 32. Evidence Engine

Evidence Engine merupakan pusat reasoning sistem.

Evidence categories:

- broker
- price
- volume
- technical
- news
- financial
- macro
- sector
- foreign flow

Setiap evidence memiliki:

- source
- timestamp
- value
- interpretation
- reliability
- related ticker
- related thesis

---

# 33. Evidence Conflict Detection

Sistem harus mendeteksi ketika evidence bertentangan.

Contoh:

Technical: Bullish

Broker Flow: Bullish

News: Bearish

Foreign Flow: Bearish

Output:

**Conflict Detected**

Confidence diturunkan.

User dapat melihat alasan penurunan confidence tersebut.

---

# 34. AI Research System

AI tidak boleh menjawab pertanyaan finansial berdasarkan memory model saja.

AI harus menggunakan internal tools.

Contoh tools:

get_market_data()

get_broker_summary()

get_accumulation_history()

get_financials()

get_technical_signals()

search_news()

get_company_disclosures()

get_sector_context()

get_macro_context()

build_bull_case()

build_bear_case()

---

# 35. AI Modes

## Analyst

Mencari evidence yang mendukung thesis.

Pertanyaan:

> Kenapa ANTM menarik?

Output:

Bullish evidence.

---

## Devil's Advocate

Mencari evidence yang dapat mematahkan thesis.

Pertanyaan:

> Apa yang bisa membuat analisis ANTM ini salah?

Output:

- resistance dekat
- accumulation weakening
- negative commodity catalyst
- foreign distribution
- valuation risk

---

## Judge

Membandingkan:

Bull Case

vs

Bear Case

dan memberikan evidence-weighted conclusion.

---

# 36. Debate My Thesis

User dapat menulis:

> Menurut gue BBRI akan naik karena BI menurunkan suku bunga.

Sistem membuat:

## Supporting Arguments

Evidence yang mendukung.

## Counter Arguments

Evidence yang membantah.

## Unknown Factors

Hal yang belum memiliki evidence cukup.

## Invalidation

Kondisi yang membuat thesis tidak lagi valid.

---

# 37. AI Output Format

Setiap analisis penting memiliki struktur:

### Thesis

### Supporting Evidence

### Counter Evidence

### Risks

### Unknowns

### Invalidation Condition

### Confidence

### Source

AI tidak boleh menyembunyikan conflicting evidence.

---

# 38. AI Research Graph

Salah satu differentiator utama aplikasi.

Visual:

Interactive node graph.

Style:

**Unreal Blueprint-inspired Bezier research canvas.**

Technology:

React Flow / XYFlow.

---

# 39. Research Graph Node Types

Node:

- Stock
- Broker
- News
- Commodity
- Sector
- Technical Signal
- Fundamental
- Macro Event
- Bull Thesis
- Bear Thesis
- Risk
- AI Conclusion

---

# 40. Graph Edge Types

Relationships:

supports

contradicts

affects

accumulates

distributes

correlates

derived_from

belongs_to_sector

Edge menggunakan Bezier curve.

Magnitude dapat direpresentasikan melalui thickness.

Confidence dapat direpresentasikan melalui opacity.

---

# 41. Research Graph Example

Nickel News

↓

Basic Materials

↓

ANTM

ANTM menerima hubungan lain dari:

Broker YP  
Broker AK  
Relative Volume  
Technical Breakout

Kemudian:

ANTM

→ Bull Case

ANTM

→ Bear Case

Keduanya menuju:

AI Judge

---

# 42. Node Interaction

User dapat:

- drag node
- zoom
- pan
- collapse group
- expand evidence
- click source
- inspect raw data
- highlight relation
- filter relation type

Klik node membuka right side panel.

---

# 43. Research Graph Design

Background:

Dark grid.

Nodes:

Minimal institutional cards.

Bezier edges:

Smooth animated connectors.

Animation harus subtle.

Bukan cyberpunk berlebihan.

---

# 44. Stock Detail Page

Header:

Ticker  
Company  
Price  
Daily Change

Main Score:

Opportunity Score

Subscores:

Smart Money  
Technical  
Catalyst  
Fundamental  
Entry  
Risk

---

# 45. Stock Detail Tabs

- Overview
- Smart Money
- Chart
- Financials
- News
- Evidence
- AI Research

---

# 46. Stock Overview

Menampilkan:

- AI summary
- current thesis
- major catalyst
- major risk
- broker status
- technical status
- foreign flow
- valuation overview

---

# 47. Financial Analyst Module

Financial analysis mencakup:

### Growth

- Revenue Growth
- Net Income Growth
- EPS Growth

### Profitability

- ROE
- ROA
- Gross Margin
- Operating Margin
- Net Margin

### Balance Sheet

- Debt
- Cash
- Debt-to-Equity
- Interest Coverage

### Cash Flow

- Operating Cash Flow
- Free Cash Flow
- Capex

### Valuation

- PER
- PBV
- EV/EBITDA
- Dividend Yield

---

# 48. Financial AI Analysis

AI menjelaskan:

- strength
- weakness
- trend
- anomaly
- peer comparison

Contoh:

> Revenue tumbuh 18%, namun operating margin turun selama dua kuartal berturut-turut sehingga kualitas pertumbuhan perlu diperhatikan.

---

# 49. Screener

Filter:

### Market

- sector
- market cap
- liquidity
- price

### Smart Money

- accumulation score
- accumulation persistence
- broker concentration
- foreign flow
- silent accumulation

### Technical

- trend
- RSI
- breakout
- volume
- EMA

### Fundamental

- PE
- PBV
- ROE
- revenue growth
- earnings growth

### Catalyst

- positive news
- earnings
- corporate action
- commodity sensitivity

---

# 50. Strategy Library

Initial strategies:

## Silent Accumulation

Broker accumulation ketika harga belum bergerak signifikan.

## Smart Breakout

Breakout + volume + accumulation.

## Re-Accumulation

Trend naik → consolidation → broker accumulation kembali.

## Distribution Warning

Price strength + broker distribution.

## Catalyst + Flow

Positive catalyst + confirming smart-money flow.

---

# 51. Strategy Lab

User dapat melakukan backtest strategy.

Metrics:

- number of trades
- win rate
- average return
- median return
- average winner
- average loser
- profit factor
- max drawdown
- Sharpe ratio
- expectancy
- average holding period

---

# 52. No Strategy Claim Without Backtest

Platform tidak boleh menyatakan strategy:

"high-performing"

"excellent"

"profitable"

tanpa historical evidence.

---

# 53. Watchlist

User dapat membuat watchlist.

Watchlist mendeteksi:

- new accumulation
- distribution
- breakout
- catalyst
- negative news
- unusual volume
- foreign activity

---

# 54. Alert System — Later Phase

Contoh alert:

ANTM

**Silent Accumulation Detected**

Broker accumulation meningkat selama 5 sesi sementara harga masih berada dalam consolidation range.

---

# 55. UI / UX Direction

Design philosophy:

## Institutional Dark Intelligence

Karakter:

- professional
- technical
- premium
- dense
- readable
- data-first
- modern

Bukan:

- neon cyberpunk
- excessive gradients
- oversized SaaS cards
- generic AI dashboard

---

# 56. Design Inspiration

Core combination:

**Koyfin information density**

+

**Linear polish**

+

**Palantir intelligence graph**

+

**Unreal Blueprint-inspired Bezier research canvas**

---

# 57. Color System

Background:

near-black.

Panel:

dark charcoal.

Border:

subtle neutral.

Functional colors:

Green  
= positive / accumulation

Red  
= negative / distribution

Amber  
= warning / uncertainty

Blue  
= AI / intelligence

Purple  
= news / catalyst

Color harus memiliki semantic meaning.

---

# 58. Typography

Primary:

Modern sans-serif.

Characteristics:

- highly readable
- compact
- numeric-friendly
- professional

Use monospaced/tabular numeric styling pada:

- price
- percentage
- financial data
- broker flow

---

# 59. Desktop Layout

Left Sidebar

↓

Main Workspace

↓

Contextual Right Panel

Research Graph dapat menggunakan full canvas mode.

---

# 60. Frontend Stack

### Framework

Next.js

React

TypeScript

### Styling

Tailwind CSS

shadcn/ui

### Research Graph

@xyflow/react / React Flow

### Financial Chart

TradingView Lightweight Charts

### General Visualization

Apache ECharts

### State

Zustand

### Server State

TanStack Query

---

# 61. Backend Stack

Python

FastAPI

Pydantic

SQLAlchemy

---

# 62. Database

PostgreSQL.

MVP deployment:

Supabase PostgreSQL.

Supabase juga dapat digunakan untuk:

- authentication
- storage
- user data

---

# 63. Data Processing

Recommended:

Polars

Pandas

NumPy

SciPy

scikit-learn

---

# 64. Background Jobs

Worker bertanggung jawab terhadap:

- market ingestion
- broker ingestion
- news ingestion
- financial updates
- technical calculation
- scoring
- news NLP
- alert generation

Technology:

Celery / equivalent job queue.

---

# 65. Cache

Redis.

Digunakan untuk:

- dashboard
- stock snapshot
- ranking
- frequently requested analytics

---

# 66. System Architecture

External Data

↓

Ingestion Layer

↓

Raw Database

↓

Normalization

↓

Analytics Engines

↓

Evidence Engine

↓

Scoring Engine

↓

AI Research Layer

↓

FastAPI

↓

Next.js Frontend

---

# 67. Analytics Engines

Independent services/modules:

Market Engine

Broker Flow Engine

Technical Engine

Financial Engine

News Intelligence Engine

Sector Engine

Macro Engine

Risk Engine

---

# 68. Evidence Graph Architecture

Data tidak langsung diberikan ke LLM.

Flow:

Raw Data

↓

Deterministic Analytics

↓

Evidence Objects

↓

Relationship Graph

↓

LLM Reasoning

↓

User Explanation

Ini mengurangi hallucination.

---

# 69. Suggested Main Database Entities

users

stocks

companies

daily_prices

intraday_prices

brokers

broker_transactions

broker_daily_summary

broker_accumulation

financial_statements

financial_metrics

news_articles

news_entities

news_ticker_relations

technical_signals

market_signals

sector_metrics

evidence

theses

thesis_evidence

ai_analysis

strategies

backtest_results

watchlists

alerts

---

# 70. Evidence Object Example

Evidence:

ID

Type

Ticker

Value

Description

Source

Source URL

Timestamp

Confidence

Direction

Impact

Raw Reference

---

# 71. API Structure

Example:

GET /market/overview

GET /stocks

GET /stocks/{ticker}

GET /stocks/{ticker}/brokers

GET /stocks/{ticker}/technical

GET /stocks/{ticker}/financials

GET /stocks/{ticker}/news

GET /stocks/{ticker}/evidence

GET /brokers/{code}

GET /smart-money/radar

GET /opportunities

POST /ai/research

POST /ai/debate

GET /research-graph/{ticker}

---

# 72. Security

API key tidak boleh berada pada client.

Secrets disimpan server-side.

Implement:

- authentication
- request validation
- rate limiting
- input sanitization
- audit logs

---

# 73. AI Safety & Financial UX

Platform harus menampilkan:

- uncertainty
- confidence
- conflicting evidence
- source timestamp

Tidak boleh menggunakan wording:

"Guaranteed profit."

"Pasti naik."

"100% buy."

Sebaliknya:

"Potential opportunity."

"Evidence currently favors..."

"Setup remains valid while..."

---

# 74. Data Freshness

Setiap data penting harus memiliki timestamp.

Contoh:

Broker Summary

Last updated:

5 Oct 2026  
18:15 WIB

News:

13 minutes ago

Financials:

Q2 2026

---

# 75. Source Transparency

Setiap analysis harus bisa ditelusuri ke source.

User harus dapat membuka:

**View Evidence**

**View Source**

**View Raw Data**

---

# 76. MVP Scope

## Phase 1 — MVP

Build:

- authentication
- overview dashboard
- stock database
- stock search
- stock detail
- basic technical analysis
- broker summary ingestion
- Smart Money Radar
- accumulation score
- accumulation matrix
- news feed
- news ticker mapping
- Opportunity Score
- AI Assistant
- Bull Case
- Bear Case
- basic Research Graph
- watchlist

---

# 77. Phase 2

Add:

- advanced broker behaviour
- broker network
- cost basis modelling
- financial analyst
- catalyst scoring
- market regime
- sector rotation
- Debate My Thesis
- evidence conflict engine
- improved Research Graph

---

# 78. Phase 3

Add:

- Strategy Lab
- backtesting
- alerts
- personalized strategy
- paper trading
- portfolio analytics
- realtime notification

---

# 79. Phase 4

Possible:

Mobile companion app.

Mobile fokus pada:

- daily opportunities
- watchlist
- alerts
- stock analysis
- AI assistant

Research Graph tetap optimal pada desktop.

---

# 80. MVP Priority

Priority 1:

**Reliable Broker Summary Analytics**

Priority 2:

**Evidence Engine**

Priority 3:

**News Intelligence**

Priority 4:

**AI Explanation**

Priority 5:

**Research Graph**

Visual tidak boleh mengorbankan kualitas analytics.

---

# 81. Success Metrics

Product metrics:

- daily active users
- watchlist usage
- stock research sessions
- evidence opened
- AI questions
- research graph interactions

Analytical metrics:

- signal precision
- false positive rate
- strategy expectancy
- data freshness
- news classification accuracy
- ticker mapping accuracy

---

# 82. Quality Requirements

Platform dianggap berhasil jika user dapat menjawab:

### Apa yang sedang terjadi?

Price / market.

### Siapa yang tampaknya sedang aktif?

Broker flow.

### Kenapa?

News / catalyst / financial context.

### Apa bukti pendukungnya?

Evidence.

### Apa yang bisa membuat saya salah?

Counter Evidence.

### Kapan thesis ini invalid?

Invalidation.

---

# 83. Core Product Principle

Setiap stock analysis harus memiliki bentuk:

**Observe**

↓

**Explain**

↓

**Support With Evidence**

↓

**Challenge The Thesis**

↓

**Assess Risk**

↓

**Conclude With Uncertainty**

---

# 84. Example Final Stock Analysis

## ANTM

Opportunity Score:

87 / 100

Smart Money:

92 / 100

Technical:

82 / 100

Catalyst:

86 / 100

Entry Quality:

71 / 100

### Thesis

Possible silent accumulation with improving sector catalyst.

### Supporting Evidence

- Multiple brokers accumulated over 5 sessions.
- Top broker concentration increased.
- Price remained inside consolidation.
- Relative volume started increasing.
- Nickel-related sentiment improved.

### Counter Evidence

- Resistance remains close.
- Foreign investors remain net sellers.
- One major accumulator reduced buying during the latest session.

### Invalidation

Thesis weakens if price breaks support accompanied by significant broker distribution.

### Conclusion

Current evidence favors the bullish thesis, but entry quality remains moderate and confirmation is still required.

---

# 85. Product Differentiation

BandarAI bukan hanya:

- stock screener
- stock charting app
- broker summary app
- news aggregator
- ChatGPT wrapper

BandarAI menggabungkan:

**Market Data**

+

**Broker Intelligence**

+

**News**

+

**Financial Analysis**

+

**Evidence Reasoning**

+

**Counter-Thesis AI**

+

**Visual Research Graph**

dalam satu research workflow.

---

# 86. Final Product Identity

The platform should feel like:

> An institutional research terminal built for Indonesian equities, combining broker-flow intelligence, financial analysis, news catalysts, and evidence-grounded AI reasoning inside a visual research workspace.

Primary differentiator:

> **Every conclusion can be traced back to evidence — and the system actively searches for evidence that could prove itself wrong.**