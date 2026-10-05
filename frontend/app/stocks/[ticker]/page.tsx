import Link from "next/link";
import DecisionPicker from "./DecisionPicker";

type Price = { provider: string; observed_at: string; available_at: string; close: string; volume_shares: number; source_url: string | null };
type Article = { title: string; url: string; domain: string; published_at: string | null; source_seen_at: string; available_at: string; confidence: string };
type Broker = { trading_date: string; broker: string; net_shares: number; net_value_idr: number; available_at: string; source_ref: string };
type Report = {
  ticker: string; decision_at: string;
  price: { status: string; bar: Price | null };
  news: { status: string; items: Article[] };
  broker_flow: { status: string; rows: Broker[] };
};

function time(value: string) {
  return new Intl.DateTimeFormat("id-ID", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Jakarta" }).format(new Date(value)) + " WIB";
}
function number(value: number) { return new Intl.NumberFormat("id-ID").format(value); }
function statusText(status: string) {
  if (status === "not_configured") return "Sumber belum diaktifkan";
  if (status === "unavailable_at_decision") return "Belum tersedia pada jam keputusan";
  if (status === "available") return "Data tersedia";
  return "Data belum tersedia";
}

export default async function StockPage({ params, searchParams }: {
  params: Promise<{ ticker: string }>;
  searchParams: Promise<{ decision_at?: string }>;
}) {
  const { ticker: raw } = await params;
  const { decision_at } = await searchParams;
  const ticker = raw.toUpperCase();
  if (!/^[A-Z]{4,5}$/.test(ticker)) return <main className="shell"><p>Kode saham tidak valid.</p><Link href="/">Kembali</Link></main>;
  const query = decision_at ? `?decision_at=${encodeURIComponent(decision_at)}` : "";
  let report: Report | null = null;
  try {
    const response = await fetch(`${process.env.API_URL || "http://127.0.0.1:8000"}/api/stocks/${ticker}/research${query}`, { cache: "no-store" });
    if (response.ok) report = await response.json();
  } catch { /* API offline is an explicit UI state below. */ }
  return <main className="shell">
    <header className="topbar"><Link href="/" className="brand"><span className="brand-mark">B</span><span>BandarAI</span></Link><span>Riset saham BEI</span></header>
    <section className="stock-head"><div><p className="kicker">Lembar riset</p><h1>{ticker}</h1><p>Harga, berita, dan aliran broker yang tersedia pada waktu keputusan.</p></div><div className="decision"><span>Jam keputusan</span><strong>{report ? time(report.decision_at) : "API belum tersambung"}</strong><small>Bukti setelah jam ini disembunyikan.</small><DecisionPicker ticker={ticker} /></div></section>
    {!report ? <section className="notice"><h2>API riset belum tersambung</h2><p>Jalankan backend dan PostgreSQL lokal, lalu muat ulang halaman ini. Tidak ada data contoh yang ditampilkan sebagai data pasar.</p></section> : <>
      <div className="source-strip"><span>Harga: {statusText(report.price.status)}</span><span>Berita: {statusText(report.news.status)}</span><span>Broksum: {statusText(report.broker_flow.status)}</span></div>
      <section className="grid">
        <article className="panel price-panel"><div className="panel-head"><h2>Harga terakhir</h2><span>Observasi, bukan harga eksekusi</span></div>{report.price.bar ? <><div className="big-price">Rp {number(Number(report.price.bar.close))}</div><p>Volume {number(report.price.bar.volume_shares)} lembar</p><div className="meta"><span>Teramati {time(report.price.bar.observed_at)}</span><span>Tersedia {time(report.price.bar.available_at)}</span><span>Sumber {report.price.bar.provider}</span></div>{report.price.bar.source_url && <a href={report.price.bar.source_url} target="_blank" rel="noreferrer">Buka sumber harga</a>}</> : <p className="empty">{statusText(report.price.status)}. Aktifkan sumber harga pribadi dan jalankan refresh untuk mengisinya.</p>}</article>
        <article className="panel news-panel"><div className="panel-head"><h2>Berita terkait</h2><span>Judul dan tautan, bukan analisis isi</span></div>{report.news.items.length ? <ul className="news-list">{report.news.items.map((item) => <li key={item.url}><a href={item.url} target="_blank" rel="noreferrer">{item.title}</a><div className="meta"><span>{item.domain}</span><span>{item.published_at ? `Terbit ${time(item.published_at)}` : `Terdeteksi ${time(item.source_seen_at)}`}</span><span>{item.confidence === "corroborated" ? "Ticker terkonfirmasi" : "Kecocokan perlu diperiksa"}</span></div></li>)}</ul> : <p className="empty">{statusText(report.news.status)}. Jalankan refresh berita untuk ticker ini.</p>}</article>
      </section>
      <section className="panel broker-panel"><div className="panel-head"><div><h2>Aliran broker</h2><p>Ringkasan transaksi per broker, bukan identitas bandar atau biaya posisi investor.</p></div><span>Pasar reguler · semua investor</span></div>{report.broker_flow.rows.length ? <div className="table-wrap"><table><thead><tr><th>Tanggal</th><th>Broker</th><th>Net lembar</th><th>Net nilai</th><th>Tersedia</th><th>Asal</th></tr></thead><tbody>{report.broker_flow.rows.map((row) => <tr key={`${row.trading_date}-${row.broker}`}><td>{row.trading_date}</td><td>{row.broker}</td><td className={row.net_shares < 0 ? "negative" : "positive"}>{number(row.net_shares)}</td><td className={row.net_value_idr < 0 ? "negative" : "positive"}>Rp {number(row.net_value_idr)}</td><td>{time(row.available_at)}</td><td>{row.source_ref}</td></tr>)}</tbody></table></div> : <p className="empty">Data broksum belum tersedia pada jam keputusan ini. Impor CSV harian dari sumber yang sah untuk melihatnya.</p>}</section>
      <aside className="disclaimer">BPJS/BSJP memerlukan evaluasi waktu masuk, likuiditas, biaya, dan risiko. Halaman ini hanya menyajikan bukti, bukan rekomendasi transaksi.</aside>
    </>}
  </main>;
}
