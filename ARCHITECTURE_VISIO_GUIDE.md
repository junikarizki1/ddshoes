                                                                                                                    # Panduan Membuat Diagram Arsitektur DD Shoes di Microsoft Visio

Dokumen ini berisi deskripsi teks lengkap dari diagram arsitektur dan langkah-langkah membuat ulangnya di Visio, mengikuti format seperti contoh gambar.

---

## BAGIAN 1 — DESKRIPSI TEKS DIAGRAM

Berikut isi lengkap diagram arsitektur DD Shoes dalam format teks terstruktur.

---

### AKTOR (sisi kiri, di luar kotak utama)

Dua aktor berada di sebelah kiri diagram, di luar kotak besar:

1. **Web Browser** — kotak persegi panjang
2. **User (Konsumen)** — ikon orang/stick figure di bawah Web Browser

Keduanya dihubungkan dengan panah ke kanan menuju kotak utama Django Project.

---

### KOTAK BESAR UTAMA — "Frontend DD Shoes Store (Django Templates)"

Ini adalah kotak terluar berwarna oranye muda (seperti di gambar contoh). Di dalamnya terdapat semua komponen frontend dan backend Django.

**Judul kotak:** `Frontend DD Shoes Store (Django Templates)`

---

#### BAGIAN ATAS DALAM KOTAK UTAMA (alur routing)

Dua kotak berurutan dari kiri ke kanan, dihubungkan panah:

**Kotak 1 — Global Layout**
- Label: `Global Layout (base.html)`
- Posisi: kiri atas
- Warna: biru muda
- Berisi: template master dengan Navbar, Footer, Tawk.to script

**Kotak 2 — URL Router**
- Label: `URL Router (ddshoes/urls.py)`
- Posisi: di kanan Kotak 1, dihubungkan panah dari Browser
- Warna: biru muda
- Berisi route: `/ · /cart/ · /order/ · /account/ · /admin/`

**Kotak 3 — Pages**
- Label: `Pages (Django Templates)`
- Posisi: di kanan URL Router, dihubungkan panah dari URL Router
- Warna: putih/abu muda
- Merupakan simpul tengah yang terhubung ke Fitur & Komponen dan ke Parts

**Kotak 4 — Parts**
- Label: `Parts (Partials / Include)`
- Posisi: di kanan Pages, dihubungkan panah dari Pages
- Warna: putih/abu muda
- Berisi: `alerts.html`, potongan template yang diinclude

---

#### KOTAK DALAM — "Fitur & Komponen" (kotak kuning/hijau muda besar)

Di bawah Pages, terdapat satu kotak besar berlabel **"Fitur & Komponen"** dengan border berwarna biru/hijau. Di dalamnya terdapat grid kotak-kotak fitur yang disusun 3 kolom.

**Kolom Kiri:**

| No | Label Kotak |
|----|------------|
| 1 | Autentikasi (Register & Login & Reset Password) |
| 2 | Filter & Pencarian (Kategori, Brand, Keyword) |
| 3 | Rekomendasi Produk (Content-Based + Cold Start) |
| 4 | Transaksi (Checkout & Bayar via Midtrans) |
| 5 | Program Loyalitas (Poin → Voucher LOYAL-) |
| 6 | Live Chat (Tawk.to Widget) |
| 7 | Tracking Pesanan (Resi Manual) |

**Kolom Tengah:**

| No | Label Kotak |
|----|------------|
| 1 | Beranda (Home — Banner, Rekomendasi, Top Brand) |
| 2 | Katalog Produk (Listing + Pagination) |
| 3 | Keranjang Belanja |
| 4 | Notifikasi Email (Gmail SMTP) |
| 5 | Riwayat Pesanan + Auto-Sync Midtrans |
| 6 | Pusat Bantuan / Terms |
| 7 | Ulasan Produk (Rating 1–5) |

**Kolom Kanan:**

| No | Label Kotak |
|----|------------|
| 1 | Produk & Detail Produk |
| 2 | Profil & Alamat User (Maks 3 Alamat) |
| 3 | Klaim Voucher (Manual & Loyalty) |
| 4 | Riwayat Pesanan Detail |
| 5 | Invoice PDF (Download / Preview) |
| 6 | Tentang / Terms |
| 7 | Retur Produk (Purna Jual) |

---

#### KOTAK "Utilities, Scripts & Styling" (kotak merah muda kecil)

Berada di bawah tengah diagram, di dalam kotak utama. Berisi 4 kotak kecil disusun 2 kolom:

| Kotak | Isi |
|-------|-----|
| Kiri atas | Bootstrap 5 (Grid / Theme) |
| Kanan atas | main.css (Custom Style) |
| Kiri bawah | jQuery 2.2.4 (AJAX & DOM Manipulation) |
| Kanan bawah | Owl Carousel · Magnific Popup · Nice Select · noUiSlider |

---

#### KOTAK "Metode Rendering" (kotak di pojok kanan atas, di dalam kotak utama)

Berisi 2 kotak kecil vertikal:

| Kotak | Isi |
|-------|-----|
| Atas | Client-Side Interactivity (jQuery & Fetch AJAX) — Dropdown wilayah, hitung ongkir, apply kupon, cart badge |
| Bawah | Server-Side Rendering / SSR (Diproses oleh Django Template Engine) |

---

### KOTAK DI KANAN LUAR — "Controller (Views + Models)"

Di sebelah kanan kotak utama, sejajar tengah. Dihubungkan panah dari AJAX dan dari Pages.

- Label: `Views + Models (Logika Bisnis)`
- Sub-label kecil: `store · cart · order · account`
- Warna: putih, border biasa

Panah dari Controller ke bawah menuju dua komponen:

1. **Database** — simbol silinder (cylinder), label: `Database PostgreSQL (Prod) / SQLite (Dev)`
2. **Admin Panel** — kotak label: `Django Admin + Jazzmin` dengan catatan: kelola Produk, Order, User, ReturnRequest, Coupon

---

### KOTAK DI KANAN LUAR — "Layanan Eksternal" (kotak kuning)

Di sebelah kanan Controller, berlabel **"Layanan Eksternal"**. Berisi 4 kotak kecil:

| Kotak | Isi |
|-------|-----|
| 1 | Midtrans — Payment Gateway (Snap UI + CoreApi, 17+ metode) |
| 2 | Komerce / RajaOngkir — Shipping API (JNE, SiCepat, J&T, dll.) |
| 3 | Gmail SMTP — Notifikasi Email (Shipping, Produk Baru, Reset Password) |
| 4 | Tawk.to — Live Chat Widget |

---

### KOTAK DI BAWAH — "Infrastruktur Deployment"

Di bagian bawah kanan diagram. Berisi:

| Kotak | Isi |
|-------|-----|
| 1 | Docker Container + Gunicorn WSGI |
| 2 | WhiteNoise (Static Files Server) |
| 3 | Docker Volume /app/media (Persistent Media) |
| 4 | Coolify (Self-Hosted PaaS) |

---

### PANAH-PANAH KONEKSI ANTAR KOMPONEN

Berikut semua koneksi yang perlu digambar sebagai panah:

| Dari | Ke | Label Panah |
|------|-----|-------------|
| User / Browser | URL Router | HTTP Request |
| Admin | Django Admin | HTTP Request |
| URL Router | Pages | routing |
| URL Router | Admin Panel | /admin/ |
| Pages | Parts | include |
| Pages | Fitur & Komponen | render |
| Fitur & Komponen | AJAX (jQuery) | request dinamis |
| AJAX | Controller (Views) | AJAX Request |
| Pages | Controller (Views) | SSR Request |
| Controller | Database | ORM Query |
| Controller | Layanan Eksternal | API Call |
| order/Views | Midtrans | Snap Token + Status Check |
| order/Views | Komerce | AJAX Ongkir & Wilayah |
| order/Views | Gmail | Email Resi Pengiriman |
| store/Views | Gmail | Email Produk Baru (Signal) |
| account/Views | Gmail | Email Reset Password |
| base.html | Tawk.to | Embed JS Widget |
| Controller | Infrastruktur | Deploy |

---

## BAGIAN 2 — PANDUAN LANGKAH DEMI LANGKAH DI MICROSOFT VISIO

### Persiapan Awal

1. Buka **Microsoft Visio**
2. Pilih template: **Blank Drawing** (bukan template otomatis, agar bebas mengatur layout)
3. Atur ukuran halaman: **Landscape A3** atau **Landscape A4** (lebih lebar)
   - File → Page Setup → ukuran kertas → A3 Landscape
4. Aktifkan **gridlines**: View → Show → Grid ✓
5. Aktifkan **Snap to Grid**: View → Snap & Glue → centang Snap to Grid

---

### Langkah 1 — Buat Kotak Aktor (Sisi Kiri)

1. Dari panel **Shapes** di kiri, pilih shape **Rectangle** (persegi panjang)
2. Gambar kotak di posisi paling kiri, ukuran kecil ±2 x 1 cm
3. Klik dua kali → ketik: `Web Browser`
4. Format warna fill: putih, border: abu gelap

5. Di bawahnya, pilih shape **Ellipse** atau gunakan shape **User/Person** dari stencil
   - Jika tidak ada, gambar lingkaran kecil + garis vertikal + dua garis diagonal (ikon orang manual)
   - Atau: Insert → Icons → ketik "person" → insert
6. Di bawah ikon orang, tambah **Text Box**: `User (Konsumen)`

---

### Langkah 2 — Buat Kotak Utama (Kotak Besar Oranye)

1. Pilih **Rectangle** besar, gambar memenuhi hampir seluruh halaman (menyisakan ruang untuk koneksi ke kanan)
2. Ukuran: kira-kira 70% lebar halaman, 85% tinggi halaman
3. Format fill: **oranye muda** (warna hex: `#FFE6CC` atau theme color Orange, 60% lighter)
4. Border: **oranye tua** atau `#FF8C00`, ketebalan 2pt
5. Klik dua kali → ketik judul di sudut kiri atas:
   `Frontend DD Shoes Store (Django Templates)`
   Format: Bold, font 12pt, warna hitam

---

### Langkah 3 — Buat Alur Routing di Bagian Atas

Masih di dalam kotak besar, bagian atas:

**Kotak "Global Layout":**
1. Buat **Rectangle** kecil, posisi kiri atas dalam kotak besar
2. Fill: **biru muda** (`#DAE8FC`), border biru tua
3. Label (2 baris): `Global Layout` (baris 1), `(base.html)` (baris 2, italic kecil)

**Kotak "URL Router":**
1. Buat Rectangle sejajar di kanannya
2. Fill: biru muda, border biru tua
3. Label: `URL Router` (baris 1), `(ddshoes/urls.py)` (baris 2)

**Kotak "Pages":**
1. Buat Rectangle di kanan URL Router
2. Fill: putih, border abu
3. Label: `Pages` (baris 1), `(Django Templates)` (baris 2)

**Kotak "Parts":**
1. Buat Rectangle di kanan Pages
2. Fill: putih, border abu
3. Label: `Parts` (baris 1), `(Partials / Include)` (baris 2)

**Hubungkan dengan panah:**
- Dari Web Browser → URL Router: panah biasa, label `HTTP Request`
- Dari Global Layout → ke Pages: panah ke bawah (Global Layout memengaruhi semua halaman)
- Dari URL Router → Pages: panah ke kanan
- Dari Pages → Parts: panah ke kanan

---

### Langkah 4 — Buat Kotak "Fitur & Komponen" (Kotak Besar Kuning)

1. Di dalam kotak utama, di bawah alur routing, buat **Rectangle besar** kedua
2. Ukuran: lebar ±60% dari kotak utama, tinggi ±70%
3. Fill: **kuning sangat muda** (`#FFF2CC`) atau hijau muda (`#D5E8D4`)
4. Border: biru tua atau hijau tua, ketebalan 1.5pt, style **dashed** (putus-putus)
5. Judul di kiri atas dalam kotak ini: `Fitur & Komponen`, Bold

**Buat 21 kotak kecil di dalamnya (3 kolom × 7 baris):**

Gunakan ukuran seragam tiap kotak kecil: ±3.5 x 1.5 cm

Kolom 1 (paling kiri), dari atas ke bawah:
- `Autentikasi (Register & Login & Reset Password)`
- `Filter & Pencarian (Kategori, Brand, Keyword)`
- `Rekomendasi Produk (Content-Based + Cold Start)`
- `Transaksi (Checkout & Bayar via Midtrans)`
- `Program Loyalitas (Poin → Voucher LOYAL-)`
- `Live Chat (Tawk.to Widget)`
- `Tracking Pesanan (Resi Manual)`

Kolom 2 (tengah), dari atas ke bawah:
- `Beranda (Banner, Rekomendasi, Top Brand)`
- `Katalog Produk (Listing + Pagination)`
- `Keranjang Belanja`
- `Notifikasi Email (Gmail SMTP)`
- `Riwayat Pesanan + Auto-Sync Midtrans`
- `Pusat Bantuan / Terms`
- `Ulasan Produk (Rating 1–5)`

Kolom 3 (paling kanan), dari atas ke bawah:
- `Produk & Detail Produk`
- `Profil & Alamat User (Maks 3 Alamat)`
- `Klaim Voucher (Manual & Loyalty)`
- `Riwayat Pesanan Detail`
- `Invoice PDF (Download / Preview)`
- `Tentang / Terms`
- `Retur Produk (Purna Jual)`

> TIP VISIO: Setelah buat satu kotak kecil, tekan Ctrl+D untuk duplicate. Atur ulang posisinya. Gunakan Align dan Distribute (Home → Arrange) untuk meratakan otomatis.

---

### Langkah 5 — Buat Kotak "Utilities, Scripts & Styling"

1. Di dalam kotak utama, di bawah Fitur & Komponen (atau di pojok kanan bawah dalam kotak utama)
2. Buat **Rectangle sedang**, judul: `Utilities, Scripts & Styling`
3. Fill: **merah muda sangat muda** (`#FFE6E6`) atau abu muda
4. Border: merah/pink, dashed

Di dalamnya buat 4 kotak kecil (2×2 grid):
- Kiri atas: `Bootstrap 5 (Grid / Theme)`
- Kanan atas: `main.css (Custom Style)`
- Kiri bawah: `jQuery 2.2.4 (AJAX & DOM)`
- Kanan bawah: `Owl Carousel · Popup · noUiSlider`

---

### Langkah 6 — Buat Kotak "Metode Rendering" (Pojok Kanan Atas)

1. Di luar kotak utama, di pojok kanan atas
2. Buat **Rectangle sedang**, judul: `Metode Rendering`
3. Fill: putih, border abu, shadow ringan

Di dalamnya 2 kotak vertikal:
- Atas: `Client-Side Interactivity (jQuery & Fetch AJAX)` — subtitle: `Dropdown wilayah · Hitung ongkir · Apply kupon · Cart badge`
- Bawah: `Server-Side Rendering / SSR` — subtitle: `(Diproses Django Template Engine)`

---

### Langkah 7 — Buat "Controller (Views + Models)"

1. Di sebelah kanan kotak utama, posisi tengah
2. Buat **Rectangle sedang**
3. Fill: putih, border abu gelap, shadow
4. Label: `Views + Models` (baris 1, Bold), `(Logika Bisnis)` (baris 2), `store · cart · order · account` (baris 3, kecil)

---

### Langkah 8 — Buat "Database"

1. Di bawah Controller
2. Gunakan shape **Cylinder** (Database)
   - Di Shapes panel: cari "cylinder" atau buka stencil **Network** / **Database**
   - Atau: Insert → Shape → Database
3. Label: `Database` (baris 1), `PostgreSQL (Prod)` (baris 2), `SQLite (Dev)` (baris 3)
4. Fill: merah muda atau kuning muda (warna berbeda agar menonjol)

---

### Langkah 9 — Buat "Admin Panel"

1. Di bawah Database (atau di samping Database)
2. Buat **Rectangle**
3. Fill: abu muda, border abu tua
4. Label: `Django Admin + Jazzmin` (baris 1), `Kelola: Produk, Order, User` (baris 2), `ReturnRequest, Coupon` (baris 3)

---

### Langkah 10 — Buat Kotak "Layanan Eksternal" (Kotak Kuning Kanan)

1. Di sebelah kanan Controller / Database
2. Buat **Rectangle besar**, judul: `Layanan Eksternal`
3. Fill: **kuning muda** (`#FFFACD`), border: oranye/kuning tua
4. Border style: solid, ketebalan 2pt

Di dalamnya 4 kotak kecil vertikal:
- `Midtrans — Payment Gateway` + subtitle: `Snap UI + CoreApi, 17+ metode`
- `Komerce / RajaOngkir — Shipping API` + subtitle: `JNE, SiCepat, J&T, Ninja, TIKI, dll.`
- `Gmail SMTP — Notifikasi Email` + subtitle: `Shipping · Produk Baru · Reset Password`
- `Tawk.to — Live Chat Widget` + subtitle: `Embed JS di base.html`

---

### Langkah 11 — Buat Kotak "Infrastruktur Deployment" (Bawah)

1. Di bagian bawah diagram, di bawah Layanan Eksternal atau Controller
2. Buat **Rectangle**, judul: `Infrastruktur (Coolify — Self-hosted)`
3. Fill: biru sangat muda (`#EBF3FB`), border biru

Di dalamnya 3–4 kotak kecil horizontal:
- `Docker Container + Gunicorn WSGI`
- `WhiteNoise (Static Files)`
- `Docker Volume /app/media`
- `Coolify PaaS`

---

### Langkah 12 — Hubungkan Semua Panah

Gunakan tool **Connector** (shortcut: Ctrl+Shift+3 atau klik ikon panah di toolbar).

Buat panah sesuai tabel berikut:

| Dari | Ke | Cara panah | Label |
|------|-----|-----------|-------|
| User (Konsumen) | Web Browser | → biasa | |
| Web Browser | URL Router | → biasa | HTTP Request |
| Admin | Django Admin | → biasa | HTTP Request |
| URL Router | Pages | → biasa | routing |
| URL Router | Admin Panel | → biasa | /admin/ |
| Pages | Parts | → biasa | include |
| Pages | Fitur & Komponen | → ke bawah | render |
| Fitur & Komponen | Utilities | → ke bawah | digunakan oleh |
| Fitur & Komponen | AJAX (dalam Metode Rendering) | → ke kanan | request dinamis |
| AJAX | Controller | → ke kanan | AJAX Request |
| Pages | Controller | → ke kanan | SSR Request |
| Controller | Database | → ke bawah | ORM Query |
| Controller | Layanan Eksternal | → ke kanan | API Call |
| (order) Controller | Midtrans | ↗ panah ke kanan | Snap Token |
| (order) Controller | Komerce | ↗ panah ke kanan | Cek Ongkir |
| (order) Controller | Gmail | ↗ panah ke kanan | Email Resi |
| (store) Controller | Gmail | ↗ panah ke kanan | Email Produk Baru |
| (account) Controller | Gmail | ↗ panah ke kanan | Email Reset |
| base.html | Tawk.to | ↗ panah ke kanan | Embed JS |
| Controller | Infrastruktur | → ke bawah | deployed on |

> TIP VISIO: Untuk menambahkan label pada panah, klik dua kali pada garis panah → ketik label. Atur posisi label dengan drag.

---

### Langkah 13 — Finishing dan Polishing

**Warna yang disarankan (konsisten dengan gambar referensi):**

| Elemen | Warna Fill | Warna Border |
|--------|-----------|--------------|
| Kotak utama besar | Oranye muda `#FFE6CC` | Oranye tua `#D6790A` |
| Kotak routing (Global Layout, URL Router) | Biru muda `#DAE8FC` | Biru tua `#6C8EBF` |
| Kotak Fitur & Komponen | Kuning muda `#FFF2CC` | Kuning tua `#D6B656` |
| Kotak-kotak fitur kecil | Putih `#FFFFFF` | Abu `#AAAAAA` |
| Utilities | Merah muda muda `#FFE6E6` | Merah muda `#D60000` |
| Layanan Eksternal | Kuning `#FFFACD` | Oranye `#D6930A` |
| Database (silinder) | Merah muda `#F8CECC` | Merah `#B85450` |
| Infrastruktur | Biru sangat muda `#EBF3FB` | Biru `#5B9BD5` |
| Controller | Putih | Abu gelap |

**Font:**
- Judul kotak besar: **Bold, 11–12pt, Arial atau Calibri**
- Label kotak fitur: Regular, 9–10pt
- Sub-label/keterangan: Italic, 8pt, warna abu gelap

**Panah:**
- Panah utama (antar section besar): ketebalan 1.5pt, warna hitam
- Panah AJAX/API: ketebalan 1pt, warna biru atau abu, style dashed

**Tambahan estetik:**
- Tambahkan **shadow** ringan pada Controller dan Layanan Eksternal
- Pastikan semua kotak dalam satu section memiliki ukuran yang seragam
- Gunakan **Align Center** dan **Distribute Vertically/Horizontally** untuk merapikan grid

---

### Tips Tambahan

- **Gunakan Layer:** View → Layer Properties → buat layer terpisah untuk "Aktor", "Routing", "Fitur", "Eksternal", "Panah" — memudahkan editing per bagian
- **Group komponen:** Setelah selesai satu section, select semua elemennya → Ctrl+G untuk group, agar mudah dipindah
- **Page scale:** Jika terlalu penuh, gunakan View → Zoom → Fit Page untuk melihat keseluruhan
- **Export:** File → Save As → PDF atau PNG untuk presentasi/skripsi
- **Print:** File → Print → pastikan "Fit to page" aktif agar tidak terpotong

---

## BAGIAN 3 — LAYOUT POSISI VISUAL (Peta Kasar)

Berikut peta posisi kasar elemen di kanvas (bayangkan halaman A3 landscape):

```
┌─────────────────────────────────────────────────────────────────────┐ ← Kotak Metode Rendering (pojok kanan atas, DI LUAR kotak utama)
│  Client-Side (AJAX)                                                  │
│  Server-Side (SSR/SSR)                                               │
└─────────────────────────────────────────────────────────────────────┘

[User]   ┌────────────────────────────────────────────────────────────────────────┐
         │  Frontend DD Shoes Store (Django Templates) ← JUDUL KOTAK ORANYE      │
[Web  ]→ │                                                                        │
[Browser]│  [Global Layout]→[URL Router]→[Pages]→[Parts]                         │  →[Controller]→[Database]
         │       (base.html)  (urls.py)                                           │       (Views+Models)  (Silinder)
         │                        ↓                                               │              ↓
         │  ┌────────────────────────────────────────────────────┐                │        [Admin Panel]
         │  │ Fitur & Komponen (kotak kuning besar)              │                │
         │  │                                                    │                │
         │  │ [Autentikasi] [Beranda]   [Produk & Detail]        │                │  ┌─────────────────────┐
         │  │ [Filter/Cari] [Katalog]   [Profil & Alamat]        │                │  │ Layanan Eksternal   │
         │  │ [Rekomendasi] [Keranjang] [Klaim Voucher]          │                │  │ (kotak kuning)      │
         │  │ [Transaksi]   [Notifikasi][Riwayat Detail]         │  →AJAX→       │  │ · Midtrans          │
         │  │ [Loyalitas]   [Riwayat]   [Invoice PDF]            │               │  │ · Komerce/RajaOngkir│
         │  │ [Live Chat]   [FAQ/Terms] [Tentang]                │               │  │ · Gmail SMTP        │
         │  │ [Tracking]    [Ulasan]    [Retur Produk]           │               │  │ · Tawk.to           │
         │  └────────────────────────────────────────────────────┘               │  └─────────────────────┘
         │                                                                        │
         │  ┌────────────────────────────────────┐                               │
         │  │ Utilities, Scripts & Styling        │                               │  ┌─────────────────────┐
         │  │ [Bootstrap 5]  [main.css]           │                               │  │ Infrastruktur       │
         │  │ [jQuery 2.2.4] [Owl·Popup·Slider]   │                               │  │ Docker + Gunicorn   │
         │  └────────────────────────────────────┘                               │  │ WhiteNoise          │
         └────────────────────────────────────────────────────────────────────────┘  │ /app/media Volume   │
                                                                                     └─────────────────────┘
```

---

Dokumen ini cukup sebagai acuan lengkap untuk membangun diagram di Visio dari nol tanpa bergantung pada kode apapun.
