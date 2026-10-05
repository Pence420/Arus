import Link from "next/link";

export default function Home() {
  return <main className="home">
    <div className="brand"><span className="brand-mark">B</span><span>BandarAI</span></div>
    <section className="home-intro">
      <p className="kicker">Meja riset saham Indonesia</p>
      <h1>Yang penting bukan cuma angkanya. <em>Kapan angkanya tersedia?</em></h1>
      <p>Periksa harga, berita, dan broksum dengan sumber serta jejak waktu yang bisa diaudit. Bukan mesin sinyal beli otomatis.</p>
      <form action="/search" className="search-form"><label htmlFor="ticker">Mulai dari kode saham</label><div><input id="ticker" name="ticker" placeholder="Contoh: BBRI" maxLength={5} required pattern="[A-Za-z]{4,5}" /><button type="submit">Buka riset</button></div></form>
    </section>
    <footer>Data bisa tertunda dan tidak selalu lengkap. <Link href="/stocks/BBRI">Lihat halaman BBRI</Link></footer>
  </main>;
}
