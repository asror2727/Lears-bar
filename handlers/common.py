from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from database import get_or_create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    get_or_create_user(message.from_user.id, message.from_user.username or message.from_user.first_name)
    await message.answer(
        "👋 Salom! Bu <b>Bluff Karta</b> o'yin boti.\n\n"
        "Meni guruhga qo'shing va u yerda <b>/game</b> deb yozing — 2 dan 4 gacha o'yinchi ro'yxatdan o'tadi "
        "va o'yin avtomatik boshlanadi.\n\n"
        "🎴 /profile — profilingiz\n"
        "💎 /shop — olmos sotib olish"
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username or message.from_user.first_name)
    text = (
        "🏆 <b>PROFIL</b>\n\n"
        f"⭐ ID: <code>{user['user_id']}</code>\n"
        f"👤 {user['username']}\n\n"
        f"💵 Dollar: {user['dollars']}\n"
        f"💎 Olmos: {user['diamonds']}\n\n"
        f"🎯 G'alabalar: {user['wins']}\n"
        f"🎲 Jami o'yinlar: {user['games']}\n\n"
        f"🏆 Reyting: {user['rating']}"
    )
    await message.answer(text)
