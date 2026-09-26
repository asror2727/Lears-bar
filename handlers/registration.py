from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import keyboards as kb
from bot_instance import bot
from config import MAX_PLAYERS, MIN_PLAYERS
from database import get_or_create_user
from game_manager import GameSession, active_game_for_user, games

router = Router()


@router.message(Command("game"))
async def cmd_game(message: Message):
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhda ishlaydi. Meni guruhga qo'shib, /game deb yozing.")
        return

    chat_id = message.chat.id
    existing = games.get(chat_id)
    if existing and existing.state != "finished":
        await message.answer("Bu guruhda allaqachon ro'yxat ochiq yoki o'yin ketmoqda.")
        return

    session = GameSession(chat_id)
    games[chat_id] = session
    uname = message.from_user.username or message.from_user.first_name
    get_or_create_user(message.from_user.id, uname)
    session.add_player(message.from_user.id, uname)
    active_game_for_user[message.from_user.id] = chat_id

    await message.answer(
        "🎴 <b>Ro'yxatdan o'tish boshlandi!</b>\n"
        "Qo'shilish uchun bosing 👇🏻\n\n"
        f"Ro'yxatdan o'tganlar:\n1. {uname}\n\n"
        f"Jami 1 ta odam. ({MIN_PLAYERS}-{MAX_PLAYERS} kishi kerak, {MAX_PLAYERS} ta bo'lsa avtomatik boshlanadi)",
        reply_markup=kb.join_keyboard(chat_id),
    )


@router.callback_query(F.data.startswith("join:"))
async def cb_join(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    session = games.get(chat_id)
    if not session or session.state != "registration":
        await call.answer("Ro'yxat yopilgan.", show_alert=True)
        return
    if session.player_count >= MAX_PLAYERS:
        await call.answer("Joy yo'q, o'yin to'lgan.", show_alert=True)
        return

    user = call.from_user
    uname = user.username or user.first_name
    get_or_create_user(user.id, uname)
    added = session.add_player(user.id, uname)
    if not added:
        await call.answer("Siz allaqachon ro'yxatdasiz.", show_alert=True)
        return
    active_game_for_user[user.id] = chat_id

    names = "\n".join(f"{i+1}. {session.players[uid].username}" for i, uid in enumerate(session.order))
    await call.message.edit_text(
        "🎴 <b>Ro'yxatdan o'tish davom etmoqda</b>\n"
        "Qo'shilish uchun bosing 👇🏻\n\n"
        f"Ro'yxatdan o'tganlar:\n{names}\n\nJami {session.player_count} ta odam.",
        reply_markup=kb.join_keyboard(chat_id),
    )
    await call.answer("Siz o'yinga qo'shildingiz! ✅")

    if session.player_count >= MAX_PLAYERS:
        await start_game(chat_id)


@router.message(Command("startgame"))
async def cmd_startgame(message: Message):
    chat_id = message.chat.id
    session = games.get(chat_id)
    if not session or session.state != "registration":
        await message.answer("Faol ro'yxat topilmadi. Avval /game yozing.")
        return
    if session.player_count < MIN_PLAYERS:
        await message.answer(f"Kamida {MIN_PLAYERS} kishi kerak.")
        return
    await start_game(chat_id)


async def start_game(chat_id):
    session = games[chat_id]
    session.start()
    names = ", ".join(p.username for p in session.players.values())
    await bot.send_message(
        chat_id,
        f"🎮 <b>O'yin boshlandi!</b>\n👥 {names}\n\n"
        "Har biriga kartalar tarqatildi. Navbat botning shaxsiy xabarlari orqali ketadi — "
        "botga /start bosishni unutmang, aks holda navbatingizni ko'ra olmaysiz!",
    )
    await announce_turn(session)


async def announce_turn(session):
    player = session.current_player()
    hand_text = ", ".join(player.hand)
    try:
        await bot.send_message(
            player.user_id,
            f"🎴 <b>Sizning navbatingiz!</b>\nQo'lingizdagi kartalar: {hand_text}\n\n"
            "Tashlamoqchi bo'lgan kartalaringizni tanlang (1-4 ta), so'ng qaysi darajani "
            "e'lon qilishni tanlaysiz — bu haqiqiy yoki yolg'on bo'lishi mumkin 😉",
            reply_markup=kb.hand_keyboard(session),
        )
    except Exception:
        await bot.send_message(
            session.chat_id,
            f"⚠️ {player.username}, botga shaxsiy xabarda /start bosing — navbat sizda!",
        )
