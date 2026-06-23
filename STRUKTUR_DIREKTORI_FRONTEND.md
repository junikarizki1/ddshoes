# DD Shoes Store (Struktur Direktori Frontend — Konsumen)

## Panduan Membuat di Visio

Format: Kotak-kotak grid berlapis, seperti gambar referensi.
Judul besar di atas: **DD Shoes Store (Struktur Direktori Frontend — Konsumen)**

---

## LAPISAN 1 — Folder Utama Django Apps
*(Baris kotak biru muda — 4 kotak sejajar)*

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     store/      │  │     account/    │  │     cart/       │  │     order/      │
│  (App Produk)   │  │  (App Akun)     │  │  (App Keranjang)│  │  (App Pesanan)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Warna:** Biru muda — `#DAE8FC`, border biru `#6C8EBF`

---

## LAPISAN 2 — File Konfigurasi Utama
*(Baris kotak oranye/kuning — 4 kotak sejajar)*

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   settings.py   │  │    urls.py      │  │   .env.example  │  │ requirements.txt│
│  (Konfigurasi)  │  │ (URL Router)    │  │  (Environment)  │  │  (Dependencies) │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Warna:** Oranye muda — `#FFE6CC`, border oranye `#D6790A`

---

## LAPISAN 3 — Views (Logika Frontend / Konsumen)
*Label section (teks abu di atas kotak): "isi folder views.py — Logika Frontend Konsumen"*
*(Kotak merah muda — grid 3 kolom × 4 baris)*

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│     store/views.py   │  │   account/views.py   │  │    cart/views.py     │
│        home()        │  │       login()        │  │      cart()          │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/views.py     │  │   account/views.py   │  │    cart/views.py     │
│     product()        │  │      register()      │  │     add_cart()       │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/views.py     │  │   account/views.py   │  │    order/views.py    │
│  product_detail()    │  │    edit_profile()    │  │     checkout()       │
│     search()         │  │   address CRUD()     │  │    place_order()     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/views.py     │  │   account/views.py   │  │    order/views.py    │
│   submit_review()    │  │  loyalty_program()   │  │     payments()       │
│ update_user_interest │  │     tracking()       │  │   confirmation()     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

**Warna:** Merah muda — `#FFD6D6`, border merah muda tua `#B85450`

---

## LAPISAN 4 — Templates (Tampilan Frontend / Konsumen)
*Label section: "isi folder templates/ — Tampilan Frontend Konsumen"*
*(Kotak hijau muda — grid 4 kolom × 3 baris)*

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  base.html   │  │  home.html   │  │ alerts.html  │  │  terms.html  │
│(Global Layout│  │(Beranda)     │  │(Flash Msg)   │  │(Syarat & Ket)│
│ Navbar+Footer│  │              │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ store/       │  │ account/     │  │ cart/        │  │ order/       │
│product.html  │  │ login.html   │  │ cart.html    │  │checkout.html │
│product_detail│  │register.html │  │              │  │payments.html │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ account/     │  │ account/     │  │ order/       │  │ order/       │
│edit_profile  │  │address_form  │  │confirmation  │  │my_orders.html│
│loyalty_prog  │  │address_list  │  │submit_return │  │invoice_pdf   │
│tracking.html │  │password_reset│  │shipping_email│  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**Warna:** Hijau muda — `#D5E8D4`, border hijau `#82B366`

---

## KETERANGAN WARNA UNTUK VISIO

| Lapisan | Warna Fill | Warna Border | Isi |
|---------|-----------|--------------|-----|
| Baris 1 — Folder Apps | Biru muda `#DAE8FC` | Biru `#6C8EBF` | store/ · account/ · cart/ · order/ |
| Baris 2 — File Config | Oranye muda `#FFE6CC` | Oranye `#D6790A` | settings.py · urls.py · .env · requirements.txt |
| Baris 3 — Views | Merah muda `#FFD6D6` | Merah muda tua `#B85450` | Semua file views.py per app |
| Baris 4 — Templates | Hijau muda `#D5E8D4` | Hijau `#82B366` | Semua folder & file template |

---

## PANDUAN CEPAT VISIO

1. Buat **Rectangle besar** sebagai kotak luar (border abu, fill putih)
2. Tambah judul di atas: **DD Shoes Store (Struktur Direktori Frontend — Konsumen)** — Bold, 14pt, tengah
3. **Baris 1 (Biru):** 4 kotak sejajar horizontal, ukuran sama (~4 x 1.5 cm)
4. **Baris 2 (Oranye):** 4 kotak sejajar di bawah baris 1, ukuran sama
5. **Teks label section** antara baris 2 dan 3: teks italic abu kecil — "isi folder views.py — Logika Frontend Konsumen"
6. **Baris 3 (Merah Muda):** 12 kotak (3 kolom × 4 baris), ukuran sama (~4 x 2 cm karena ada 2 baris teks)
7. **Teks label section** antara baris 3 dan 4: "isi folder templates/ — Tampilan Frontend Konsumen"
8. **Baris 4 (Hijau):** 12 kotak (4 kolom × 3 baris), ukuran sama (~3.5 x 2 cm)
9. Gunakan **Home → Arrange → Distribute Horizontally** untuk meratakan jarak antar kotak otomatis
