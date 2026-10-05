# Catatan riset: perhitungan broker summary dan bandarmology

Tanggal riset: 5 Oktober 2026. Fokus: kontrak data dan aritmetika yang dapat diuji untuk saham BEI. Ini bukan bukti bahwa sinyal broker tertentu memprediksi return. Sumber di bawah adalah BEI, dokumentasi penyedia data, dan dokumentasi fitur milik broker/platform sendiri.

## 1. Apa unit observasinya?

Unit dasar yang diperlukan untuk analisis per saham ialah **tanggal perdagangan × ticker × segmen pasar × kode broker × jenis investor (jika tersedia)**. Simpan `source`, waktu publikasi/ketersediaan, waktu ingest, dan versi data. Endpoint Index Alpha `/stocks/broker-summary` meminta ticker, rentang tanggal, `investor=all|f|d`, dan `market=RG|NG|ALL` (default `RG`). Responsnya memuat `buy_volume`/`sell_volume` dalam **lembar**, `buy_value`/`sell_value` dalam **rupiah**, frekuensi transaksi, serta rata-rata harga tertimbang dalam rupiah. [Index Alpha — API endpoints](https://indexalpha.id/docs/endpoints); [Index Alpha — quick start](https://indexalpha.id/docs/quickstart).

Jangan salah menganggap berkas BEI bernama `Brok-Summary_YYYYMMDD.csv` sebagai data per ticker. Spesifikasi publik BEI menyebutnya rekap transaksi **anggota bursa** EOD dan memetakan `participantcode`, `dailyvolume`, `dailyvalue`, `dailyfreq`; mapping yang dipublikasikan tidak mempunyai kolom kode saham atau sisi beli/jual. Jadi berkas itu berguna untuk aktivitas broker seluruh pasar, tetapi tidak cukup untuk menghitung flow broker di BBCA atau ticker tertentu. Ini kesimpulan dari skema yang dipublikasikan, bukan klaim bahwa BEI tidak punya produk data lain. [BEI — PUBLIK Report Specification, bagian Broker Summary](https://www.idxdata3.co.id/IDX%20Reporting%20PSPP/Revitalisasi/Specification%20Document-Report%20Revitalization_PUBLIK%20v1.0.pdf). BEI memang menawarkan data transaksi yang mencantumkan stock code, board code, trade price/volume, buyer/seller code, dan investor type melalui produk data tersendiri. [BEI — IDX Data Services](https://testing3.idx.id/en/products/idx-data-services/).

**Unit dan segmen tidak boleh bercampur.** BEI menetapkan 1 lot = 100 efek untuk Pasar Reguler dan Tunai; Pasar Negosiasi tidak harus round lot. Jika UI menampilkan lot dari data Index Alpha, `lot = shares / 100`; jangan mengalikan lagi nilai transaksi dengan 100. Pasar Reguler (RG), Tunai (TN), dan Negosiasi (NG) punya mekanisme berbeda; negosiasi adalah kesepakatan individual, sehingga blok NG bisa mendistorsi dugaan akumulasi di pasar reguler. Gunakan RG sebagai analisis utama dan tampilkan NG terpisah. Index Alpha mendokumentasikan RG/NG/ALL, tetapi tidak TN sebagai opsi sendiri; `ALL` menurut docs-nya ialah kedua segmen RG dan NG, sehingga jangan menyebutnya seluruh pasar BEI. [BEI — Jam dan Mekanisme Perdagangan](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/); [Index Alpha — API endpoints](https://indexalpha.id/docs/endpoints).

## 2. Rumus aritmetika yang dapat dipastikan

Untuk broker `i`, ticker `s`, hari `t`, dan segmen `m`, setelah unit disamakan:

| Metrik | Rumus | Makna |
| --- | --- | --- |
| Beli bersih lembar | `net_shares_i = buy_shares_i - sell_shares_i` | Perubahan bersih lembar melalui broker, **bukan** kepemilikan nasabah. |
| Beli bersih rupiah | `net_value_i = buy_value_i - sell_value_i` | Selisih nilai beli dan jual, bisa berbeda tanda dari `net_shares`. |
| Rata-rata beli tertimbang | `buy_vwap_i = buy_value_i / buy_shares_i` bila penyebut > 0 | Harga rata-rata transaksi beli dalam cakupan baris. |
| Rata-rata jual tertimbang | `sell_vwap_i = sell_value_i / sell_shares_i` bila penyebut > 0 | Harga rata-rata transaksi jual dalam cakupan baris. |
| Total transaksi satu sisi | `traded_shares = Σ_i buy_shares_i = Σ_i sell_shares_i` | Jika daftar broker lengkap dan definisi pasar sama. Nilai rupiah juga harus seimbang. |

Definisi volume/nilai/rata-rata di atas konsisten dengan skema Index Alpha. Untuk volume atau value nol, rata-rata harga adalah **null**, bukan nol. Hitung rata-rata gabungan dari total value dibagi total shares, bukan rata-rata sederhana angka `buy_avg` harian yang telah dibulatkan. Frekuensi beli dan jual, bila lengkap, juga merepresentasikan dua sisi transaksi yang match; validasi terhadapnya perlu toleransi bila vendor mendefinisikan `freq` berbeda. [Index Alpha — API endpoints](https://indexalpha.id/docs/endpoints); [BEI — Jam dan Mekanisme Perdagangan](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/).

Contoh tiga broker dalam satu saham dan satu hari (angka ilustratif, 1 unit = 1 lembar untuk memudahkan pembacaan; kalikan setiap kuantitas dengan 100 untuk contoh transaksi RG yang sah per lot): A membeli 100 dari B pada Rp100, membeli 100 dari C pada Rp100, menjual 150 ke B pada Rp110, dan menjual 40 ke C pada Rp120.

| Broker | Beli lembar | Beli Rp | Jual lembar | Jual Rp | Net lembar | Net Rp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 200 | 20.000 | 190 | 21.300 | +10 | −1.300 |
| B | 150 | 16.500 | 100 | 10.000 | +50 | +6.500 |
| C | 40 | 4.800 | 100 | 10.000 | −60 | −5.200 |
| Total | 390 | 41.300 | 390 | 41.300 | 0 | 0 |

A memiliki `buy_vwap = 20.000/200 = Rp100`, namun net lembar positif sementara net rupiah negatif. Jadi tanda keduanya tidak dapat saling menggantikan. `net_value/net_shares = −Rp130` di sini jelas **bukan** harga modal. Contoh lain: beli 10 juta lembar senilai Rp10 miliar lalu jual 2 juta lembar senilai Rp2,2 miliar memberi `buy_vwap=Rp1.000` dan `net_value/net_shares=Rp975`; Rp975 bukan biaya per lembar yang tersisa. Bahkan VWAP beli Rp1.000 sendiri hanya rata-rata transaksi beli dalam jendela, bukan biaya portofolio riil karena stok awal, urutan jual, dan banyak nasabah di satu broker tidak diketahui.

## 3. Agregasi waktu dan waktu ketersediaan

Index Alpha mengembalikan **satu baris agregat per broker untuk seluruh rentang tanggal**, bukan satu baris per hari. Multi-day: jumlahkan lembar, rupiah, dan frekuensi masing-masing sisi; hitung ulang VWAP dari jumlah tersebut. Dari satu respons 5 hari kita **tidak bisa** tahu apakah broker beli bersih tiap hari atau hanya satu hari besar. Persistensi dan perubahan arah memerlukan permintaan `from=to` per hari atau sumber yang memberi record harian. Endpoint batch tetap menghitung satu unit kuota per ticker. [Index Alpha — API endpoints](https://indexalpha.id/docs/endpoints); [Index Alpha — quick start](https://indexalpha.id/docs/quickstart).

Index Alpha menyatakan pembaruan setiap hari bursa pukul **19.00 WIB**. Stockbit menyatakan fitur Broker Flow-nya diperbarui setelah perdagangan, **17.00–18.00 WIB**, meskipun grafiknya berinterval satu menit. Berkas BEI di atas juga berlabel EOD. Waktu tepatnya bergantung provider; simpan `available_at` dari provider dan waktu ingest aktual. Untuk keputusan BPJS/BSJP pada hari `t`, broksum EOD hari `t` belum menjadi bukti yang tersedia saat pagi atau sore `t`. Backtest hanya boleh memakai snapshot dengan `available_at <= decision_at`; bila terlambat atau hilang, tandai missing dan jangan forward-fill sebagai data hari itu. [Index Alpha — API endpoints](https://indexalpha.id/docs/endpoints); [Stockbit — Broker Flow](https://help.stockbit.com/id/article/broker-flow-bagaimana-cara-menggunakan-dan-apa-fungsinya-vbvjo1/); [BEI — PUBLIK Report Specification](https://www.idxdata3.co.id/IDX%20Reporting%20PSPP/Revitalisasi/Specification%20Document-Report%20Revitalization_PUBLIK%20v1.0.pdf).

## 4. Metrik usulan BandarAI — hipotesis, belum tervalidasi

Semua rumus di bagian ini **pilihan desain** untuk diuji secara historis, bukan formula resmi BEI atau jaminan prediksi.

| Komponen usulan | Definisi yang eksplisit | Penanganan tepi |
| --- | --- | --- |
| Intensitas net buy broker | `net_value_i / stock_traded_value`, dengan stock value satu sisi, ticker/hari/segmen yang sama. | Jangan gunakan nilai transaksi seluruh BEI atau beda segmen. Null bila denominator nol/tidak tersedia. Nilai dapat negatif. |
| Konsentrasi top `k` net buyer | `Σ_{i in top-k} max(net_value_i,0) / Σ_all_i max(net_value_i,0)`; top `k` dipilih menurut **net value positif**. | Null jika tidak ada net buyer atau daftar broker tidak lengkap. `Σ_i net_value_i ≈ 0`, sehingga **jangan** pakai signed total itu sebagai denominator. Laporkan k dan cakupan broker. |
| Persistensi broker | `jumlah hari eligible dengan net_value_i>0 / jumlah hari eligible` dalam N hari bursa; tampilkan juga jumlah hari teramati. | Butuh record harian; jangan menyamakan hari missing dengan netral/negatif. Sinyal 1 dari 1 hari terlalu rapuh. |
| Tekanan beli bersih grup | `Σ_{i∈G} net_value_i / stock_traded_value` untuk grup broker yang ditetapkan **sebelum** melihat hasil hari tersebut. | Jika G dipilih ex post sebagai broker yang paling untung, backtest bias. Hindari identitas “bandar”. |
| Turnover dan likuiditas | Nilai transaksi RG harian dan rasio terhadap median historis (jika data tersedia). | Kalender hari bursa, suspensi, dan corporate action perlu diperhitungkan. |

Contoh konsentrasi: empat broker pembeli bersih mempunyai +Rp40 juta, +Rp30 juta, +Rp20 juta, +Rp10 juta; denominator Rp100 juta, top-2 = 70%. Semua broker penjual bersih bersama-sama bernilai −Rp100 juta jika data lengkap. Indikator 70% hanya menyatakan konsentrasi flow bersih di sisi beli, tidak membuktikan satu pihak mengendalikan empat broker tersebut. Stockbit memakai pengelompokan top 3/5/10 dalam fiturnya, tetapi definisi matematis di tabel adalah usulan BandarAI sendiri. [Stockbit — Bandar Detector](https://help.stockbit.com/id/article/bandar-detector-bagaimana-cara-menggunakan-dan-apa-fungsinya-gocgkc/).

Jangan beri bobot, ambang, atau label “strong accumulation” sebelum ada backtest walk-forward pada data yang benar-benar tersedia saat keputusan, pembanding sederhana, biaya/slippage, dan pemeriksaan stabilitas per periode/likuiditas. Pelaporan harus mencakup hit rate, distribusi return bersih, drawdown, jumlah sinyal, coverage, dan ketidakpastian; jika data broker berbayar terbatas, sampaikan keterbatasan sampelnya.

## 5. Hal yang tidak bisa disimpulkan dari broksum

- **Identitas investor dan biaya posisi riil.** BEI menyebut Anggota Bursa bertanggung jawab atas transaksi sendiri maupun nasabah. Satu kode broker dapat mewakili banyak orang dengan arah transaksi berbeda. Kode broker asing pada klasifikasi UI Stockbit merujuk kategori sekuritas; itu tidak sama dengan investor asing. Foreign flow harus mengikuti tag `investor=f` atau field foreign yang jelas definisinya, bukan dijumlah dari daftar kode broker “asing”. BEI menyediakan buyer/seller type terpisah dari buyer/seller code; Index Alpha memisahkan filter investor dan endpoint foreign flow. [BEI — Jam dan Mekanisme Perdagangan](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/); [BEI — IDX Data Services](https://testing3.idx.id/en/products/idx-data-services/); [Stockbit — Bandar Detector](https://help.stockbit.com/id/article/bandar-detector-bagaimana-cara-menggunakan-dan-apa-fungsinya-gocgkc/); [Index Alpha — API endpoints](https://indexalpha.id/docs/endpoints).
- **“Average cost bandar.”** Penyedia IDXAlpha mempublikasikan model ledger proksi: beli menambah saham/nilai, jual mengurangi pada rata-rata berjalan, reset saat posisi net flat. Itu dapat direproduksi sebagai **model broker-flow implied average**, tetapi asumsi satu broker = satu posisi dan saldo awal yang diketahui tidak dipenuhi oleh rekap broker umum. Bahkan `buy_vwap` hanya rata-rata harga transaksi beli, bukan biaya kepemilikan tersisa. Label UI yang aman ialah “rata-rata harga beli broker dalam periode”, dan model ledger harus diberi label proksi beserta jendela awalnya. [IDXAlpha — API dan campaign ledger](https://idxalpha.com/api); [BEI — Jam dan Mekanisme Perdagangan](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/).
- **Konsistensi harga lintas stock split.** Index Alpha menyatakan OHLCV-nya as-traded dan tidak disesuaikan untuk stock split. Untuk membandingkan harga atau VWAP melintasi split, gunakan faktor corporate action yang berlaku pada tanggal efektif untuk harga dan lembar, atau putus/reset jendela analisis; jangan campur skala pra/pasca split. Simpan harga asli serta transformasi dan sumber faktor. [Index Alpha — API endpoints, Daily OHLCV](https://indexalpha.id/docs/endpoints); [BEI — Stock Splits and Reverse Stocks](https://www.idx.id/en/market-data/statistical-reports/digital-statistic/monthly/corporate-action-of-listed-companies/stock-splits-and-reverse-stocks).

## 6. Invariant untuk tes ingestion/perhitungan

1. Untuk satu ticker, tanggal, segmen, dan jenis investor **all** dengan semua broker: `Σ buy_shares ≈ Σ sell_shares`, `Σ buy_value ≈ Σ sell_value`, `Σ net_shares ≈ 0`, `Σ net_value ≈ 0`. Toleransi nilai hanya untuk pembulatan/rekonsiliasi provider; ketidakseimbangan besar berarti cakupan tidak lengkap atau unit salah. Jangan wajibkan balance untuk subset `investor=f` karena lawan transaksi dapat domestik.
2. Setiap baris: nilai/lembar/frekuensi nonnegatif; `net_value` dan `net_shares` hasil pengurangan sisi yang benar; VWAP null jika shares = 0; VWAP hasil bagi value/shares cocok dengan field provider dalam toleransi pembulatan harga.
3. Agregasi waktu: `buy_value(window) = Σ_day buy_value(day)` dan demikian pula untuk sell/volume; `VWAP(window) = Σ value / Σ shares`. Bila provider merevisi data, bandingkan versi/snapshot, bukan diam-diam mengubah backtest lampau.
4. Invariant satuan: 100 lembar RG = 1 lot; nilai rupiah = harga per lembar × lembar. Jangan kalikan Rp dengan jumlah lot tanpa faktor 100. NG boleh bukan kelipatan 100.
5. Invariant ketersediaan: setiap evidence yang dipakai sinyal harus punya `available_at <= decision_at`; missing market/ticker/day tetap missing. Simpan waktu berita terbit dan waktu pertama kali ditemukan terpisah.
6. Invariant cakupan: perbandingan antarhari memakai segmen dan definisi investor sama; perubahan ticker/stock split, suspensi, dan hari bursa tidak boleh diam-diam menjadi nol transaksi atau harga sintetis.

## 7. Keputusan praktis sebelum implementasi

Data yang cukup untuk versi pertama ialah broksum **per ticker per hari RG**, harga harian, metadata corporate action, dan waktu ketersediaan. Tampilkan metrik yang aritmetikanya pasti terlebih dulu: gross buy/sell, net shares/value, buy/sell VWAP, persentase terhadap turnover, dan coverage sumber. Hitung persistensi hanya saat data harian berurutan tersedia. Tampilkan NG dan investor asing sebagai dimensi tersendiri ketika provider memang menyediakan datanya. Istilah “bandar” dalam produk adalah hipotesis perilaku flow broker, bukan identitas pelaku yang terverifikasi.
