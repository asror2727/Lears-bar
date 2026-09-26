import os

# Botni @BotFather'dan olingan token bilan to'ldiring (Render'da Environment Variable qilib qo'ying)
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# Admin panelga kira oladigan Telegram ID'lar (vergul bilan ajratib bir nechta qo'shish mumkin)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7651404790").split(",") if x.strip()]

# O'yin sozlamalari
MIN_PLAYERS = 2
MAX_PLAYERS = 4
CARDS_PER_PLAYER = 5
STARTING_LIVES = 3

# Yangi foydalanuvchiga beriladigan boshlang'ich balans
STARTING_DOLLARS = 100
STARTING_DIAMONDS = 0

# O'yinda ishlatiladigan karta darajalari (soddalashtirilgan)
RANKS = ["10", "J", "Q", "K", "A"]

# Olmos do'koni paketlari (Telegram Stars - XTR valyutasida)
DIAMOND_PACKAGES = [
    {"diamonds": 10, "stars": 50},
    {"diamonds": 50, "stars": 200},
    {"diamonds": 120, "stars": 400},
    {"diamonds": 300, "stars": 900},
]

# Yutuqni "Risk" qilib ko'paytirish uchun multiplikatorlar
RISK_MULTIPLIERS = [0.5, 1, 1.5, 2, 3]
