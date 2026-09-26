# 🎴 Bluff Karta — Telegram guruh o'yin boti

2–4 kishilik "rost yoki yolg'on" karta o'yini: guruhda ro'yxatdan o'tasiz, botning
shaxsiy xabarlari orqali karta tashlaysiz va boshqalarni aldashga (yoki ularni
ushlab olishga) harakat qilasiz. Dollar/Olmos ekonomikasi, admin panel va
Telegram Stars orqali olmos do'koni bilan birga.

## Qanday ishlaydi

1. Guruhda `/game` — ro'yxat ochiladi, "Qo'shilish" tugmasi chiqadi.
2. 4 kishi bo'lganda o'yin avtomatik boshlanadi (2-3 kishida `/startgame` bilan
   qo'lda ham boshlash mumkin).
3. Har bir o'yinchiga 5 ta karta beriladi (`10, J, Q, K, A`).
4. Navbatdagi o'yinchiga bot shaxsiy xabarda kartalarini yuboradi — u 1-4 ta
   kartani tanlab, "qaysi daraja"ligini e'lon qiladi (bu haqiqiy yoki yolg'on
   bo'lishi mumkin).
5. Guruhda e'lon ko'rinadi, keyingi o'yinchiga esa shaxsiyda "Ishonaman /
   Ishonmayman" tugmasi chiqadi.
6. Yolg'on ushlansa — yolg'onchi jon yo'qotadi. Noto'g'ri challenge qilinsa —
   challenge qilgan jon yo'qotadi (har kimda 3 jon bor).
7. Oxirgi tirik qolgan yoki qo'lidagi barcha kartalarni tashlab ulgurgan
   o'yinchi g'olib bo'ladi va $ yutadi. Xohласа "Risk" tugmasi bilan yutug'ini
   ko'paytirishga (yoki yo'qotishga) urinishi mumkin.

## Fayllar tuzilishi

```
mafia_bluff_bot/
├── main.py            # ishga tushirish nuqtasi (long polling)
├── bot_instance.py     # Bot/Dispatcher obyektlari
├── config.py           # token, admin ID, o'yin sozlamalari
├── database.py         # SQLite: profil, dollar/olmos, statistika
├── game_manager.py     # o'yin holati (kartalar, navbat, jonlar)
├── keyboards.py        # barcha inline tugmalar
├── handlers/
│   ├── common.py       # /start, /profile
│   ├── registration.py # /game, qo'shilish, o'yinni boshlash
│   ├── game_play.py     # karta tashlash, ishonish/challenge, risk
│   ├── shop.py          # /shop — Telegram Stars orqali olmos sotib olish
│   └── admin.py         # /admin panel, /grant, /broadcast, /ban
├── requirements.txt
└── Procfile
```

## O'rnatish (lokal)

```bash
pip install -r requirements.txt
export BOT_TOKEN="123456:AA...sizning_tokeningiz"
export ADMIN_IDS="7651404790"
python main.py
```

## GitHub'ga yuklash

```bash
git init
git add .
git commit -m "Bluff karta boti"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/mafia-bluff-bot.git
git push -u origin main
```

## Render'ga deploy qilish

1. Render'da **New → Background Worker** tanlang, GitHub repo'ni ulang.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `python main.py` (Procfile ham buni avtomatik oladi)
4. **Environment → Environment Variables** bo'limida qo'shing:
   - `BOT_TOKEN` — @BotFather'dan olingan token
   - `ADMIN_IDS` — sizning Telegram ID'ingiz (vergul bilan bir nechtasi)
5. Deploy qiling — bot polling rejimida 24/7 ishlay boshlaydi.

> Eslatma: bu "Background Worker" bo'lgani uchun tashqi HTTP so'rov qabul
> qilmaydi — bu odatiy holat, chunki bot Telegram serveridan o'zi so'rab
> (polling) ishlaydi.

## Olmos do'koni haqida

`/shop` — Telegram'ning o'z ichki valyutasi **Telegram Stars (XTR)** orqali
ishlaydi. Bu usulda alohida to'lov provayderi (Stripe va h.k.) kerak emas —
Telegram buni o'zi qo'llab-quvvatlaydi. `config.py` ichidagi
`DIAMOND_PACKAGES` ro'yxatidan narxlarni o'zgartira olasiz.

## Kengaytirish g'oyalari

- Premium emojilar bilan kartalarni chiroyliroq ko'rsatish (aiogram
  `MessageEntity` orqali maxsus emoji ID'lar bilan).
- `Bluff / Risk / Joker / Tekshiruv / Omad` maxsus qobiliyatlarni profilga
  qo'shish va har birini alohida narx evaziga sotib olish tugmalari.
- Har bir guruh uchun "Premium guruh" holatini `database.py`da alohida
  jadvalda saqlash.
- Karta rasmlari yoki animatsion GIF bilan boyitish (Telegram
  `send_photo`/`send_animation`).

Bu — ishlaydigan, kengaytirsa bo'ladigan asos. Butun o'yin mantig'i (kartalar,
navbat, jon, yolg'on/challenge, mukofot, risk) real ishlaydi; tashqi ko'rinish
(rasmlar, premium emoji, dizayn) ustida keyin ishlashingiz mumkin.
