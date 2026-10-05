# BandarAI MVP design

Date: 2026-10-05
Status: working design

## Intended outcome

Build a local-first, end-to-end Indonesian equity research application for a retail trader who checks real news, price/volume, and broker summary to research two workflows:

- **BPJS**: buy in the morning, sell in the afternoon of the same trading day.
- **BSJP**: buy in the afternoon, sell the next morning.

The application presents candidates, source data, counter-evidence, and a possible invalidation condition. It does not execute orders or imply a guaranteed return. Broker codes represent intermediaries and cannot identify the beneficial owner or a particular "bandar". A broker's average transaction price is not an investor's actual cost basis.

## Data reality and product decision

1. Broker summary is an end-of-day input. A broker's completed flow on trading day `D` can only inform a decision after the provider's publication time on `D`. It cannot be used to justify an entry earlier on `D`. A securities firm's user guide says broker transaction data is available after market close, approximately 18:00 WIB at the earliest: https://www.mncsekuritas.id/dl/MNCTradeNew/MNCTradeNew-UserGuide-id.pdf (p. 42).
2. The public IDX website offers a broker summary page, but its terms prohibit web scraping/crawling and restrict commercial redistribution: https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-broker and https://www.idx.co.id/id/syarat-penggunaan. The MVP will not crawl that site.
3. Yahoo Finance shows `.JK` prices as delayed and disallows redistribution of displayed information: https://help.yahoo.com/kb/SLN2352.html and https://finance.yahoo.com/quote/BBRI.JK/. A Yahoo adapter can support a personal/local development instance, but it must be disabled for a public deployment unless rights are confirmed.
4. The free tier of Index Alpha offers five API requests per day for real broker summary, with a server-side API key: https://indexalpha.id/docs/quickstart. That is useful for a small personal watchlist but insufficient for scanning every listed share daily. Its terms must be checked before any public redistribution.
5. IDXAlpha exposes a no-key BBRI sample; its broad broker dataset is paid and redistribution is separately licensed: https://idxalpha.com/api. This is a connector smoke-test source, not a market-wide free feed.
6. GDELT DOC API can discover real published articles with title, URL and time: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/. The MVP stores source metadata and links to the publisher. An article headline alone is weak evidence; claims about the article body require readable, permitted source text. Official BI and OJK announcements can be linked as primary sources: https://www.bi.go.id/id/Publikasi/Ruang-Media/news-release/Default.aspx and https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/default.aspx.

## MVP scope

The first useful version contains authentication, stock search, watchlist, daily and available intraday prices, broker summary import/API adapter, news discovery, a stock research page, and BPJS/BSJP candidate views. Every displayed observation has provider, `observed_at`, `published_at` where available, and `ingested_at`. Missing provider data is shown as unavailable; scores depending on it are withheld.

The app supports two broker summary paths:

- Upload a legitimately obtained CSV/Excel export for any ticker/date. Validate columns, units, timestamps, duplicates and market type before importing.
- Configure the Index Alpha free API key server-side for a small watchlist, obeying its published quota. The connector is optional. A single `BrokerFlowProvider` interface makes a licensed provider replaceable later.

There is no promise of automatic full-market broker screening on a zero-cost data budget. Price-only candidate lists remain possible without broker data, labeled accordingly.

## Trading workflows and time boundaries

### BPJS morning research

Before the morning session, form a candidate list from the latest available broker summary through the previous session, price/volume history, and news published before the decision timestamp. During the session, delayed intraday price/volume can update the setup status. The system must display the delayed quote time and must not treat that quote as executable. Same-day broker summary is unavailable for the morning decision.

### BSJP afternoon research

Before the close, form a candidate list from broker summaries through the previous session, price/volume behavior observed by then, and news published by then. The completed broker summary for the current day is added to the next research cycle after publication. Show overnight event and gap risk alongside the setup.

### Retrospective evaluation

Save each candidate with a frozen `decision_at` and the exact evidence visible then. Measure outcomes using prices after that time. A historical backtest must enforce the same availability rules, include brokerage fees and slippage assumptions, and report sample size. No strategy performance claim appears before this evaluation exists.

Execution assumptions must also reflect the BEI trading schedule, pre-close matching, order priority, price limits and special-monitoring call auctions. Broker fees must be configured from the user's actual trade confirmation; the published exchange/tax components must not be charged a second time if already included in that fee. The source-backed trading note is in `docs/research/2026-10-05-indonesian-short-horizon-trading.md`.

## Architecture

- **Frontend:** Next.js, TypeScript, Tailwind and shadcn/ui. Main pages: dashboard, stock detail, BPJS candidates, BSJP candidates, watchlist, source/evidence inspection, and data import/status.
- **API:** FastAPI with modules for market data, broker flow, news, evidence, research, watchlists, and authentication. The API validates ticker symbols and returns freshness metadata with every dataset.
- **Database:** PostgreSQL with migrations. Core tables: `stocks`, `price_bars`, `broker_flow_rows`, `news_items`, `news_ticker_links`, `evidence`, `research_snapshots`, `watchlists`, `provider_runs`, `users`. Source rows retain their original provider identifier and import batch.
- **Jobs:** Scheduled ingestion for permitted news and configured market data, broker API quota scheduling, normalization, evidence calculation and stale-data checks. An explicit manual import endpoint handles CSV/Excel. Jobs are idempotent by provider/source key and market date.
- **AI:** An optional server-side model adapter receives only retrieved evidence objects. It produces thesis, supporting evidence, counter-evidence, unknowns, invalidation, risk and confidence with source IDs. Without a configured model key, the deterministic evidence report remains usable; the interface does not present templated text as AI output.
- **Deployment:** Docker Compose for local Next.js, FastAPI, PostgreSQL and worker. Secrets come from environment variables and are excluded from Git. Hosted deployment and data redistribution require source-rights review.

## Evidence and scoring

Each evidence object includes ticker, type, direction, value, unit, source URL or import reference, observed time, available time, and reliability. The scorer uses only evidence with `available_at <= decision_at`. Broker calculations use per-ticker, per-day, regular-market rows with shares and IDR kept as distinct units. `net_value = buy_value - sell_value`; the sum of signed broker net values is approximately zero for complete two-sided data, so concentration uses the sum of positive net values as its denominator. Persistence requires separate daily observations, not a multi-day aggregate. A high-concentration risk flag is shown separately. These concentration and persistence definitions are proposed indicators, not validated predictive scores; see `docs/research/2026-10-05-broker-summary-calculation-notes.md` for worked examples and test invariants. News matching requires ticker/company alias checks and stores match confidence. If broker data, news, or intraday price is absent, that dimension is omitted instead of being assigned a neutral score.

The first release uses transparent component values and explanations instead of a single opaque Opportunity Score. Scores can be calibrated only after enough historical outcomes have been collected and evaluated.

## Failure handling and checks

- Provider timeout, quota exhaustion, stale data or schema change: record a failed provider run, preserve the last valid timestamp, show a warning and never label old data as current.
- CSV validation failure: reject the batch with line-level errors; do not partially import ambiguous units or dates.
- Duplicate article or broker row: upsert by stable source key and market date.
- AI response missing citations or contradicting numeric evidence: reject it and show the deterministic report.
- Tests: provider contract parsing, CSV validation, `available_at` look-ahead prevention, BPJS/BSJP candidate construction, evidence citation integrity, and end-to-end stock research with unavailable-source states.

## Delivery order

1. Repository scaffold, local infrastructure, migrations, stock and evidence contracts.
2. One vertical slice: real price/news retrieval, broker CSV import and a sourced stock research page.
3. BPJS/BSJP candidate snapshots and watchlists, with time-safe evaluation.
4. Optional Index Alpha adapter and AI explanation behind server-side configuration.
5. Broader PRD modules after the core data flow is reliable.

## Explicit exclusions in the first release

Full-market automatic broker coverage, live broker tape, trade execution, guaranteed entry signals, Research Graph, strategy performance claims, and public redistribution of restricted provider data.
