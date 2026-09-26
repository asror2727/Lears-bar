from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import keyboards as kb
from bot_instance import bot
from config import ADMIN_IDS
from database import all_user_ids, set_ban, top_players, update_balance

router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🛠 <b>Admin panel</b>\n\n"
        "Qo'shimcha buyruqlar:\n"
        "/grant <code>&lt;user_id&gt; &lt;dollars&gt; [diamonds]</code>\n"
        "/broadcast <code>&lt;matn&gt;</code>\n"
        "/ban <code>&lt;user_id&gt;</code>  /unban <code>&lt;user_id&gt;</code>",
        reply_markup=kb.admin_panel_keyboard(),
    )


@router.callback_query(F.data == "admin:stats")
async def cb_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return await call.answer()
    ids = all_user_ids()
    await call.message.answer(f"👥 Jami ro'yxatdan o'tgan foydalanuvchilar: {len(ids)}")
    await call.answer()


@router.callback_query(F.data == "admin:top")
async def cb_top(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return await call.answer()
    top = top_players()
    if not top:
        await call.message.answer("Hali o'yinchilar yo'q.")
    else:
        text = "🏆 <b>TOP o'yinchilar</b>\n\n" + "\n".join(
            f"{i+1}. {u['username']} — {u['rating']} ball ({u['wins']}/{u['games']})"
            for i, u in enumerate(top)
        )
        await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "admin:broadcast")
async def cb_broadcast_prompt(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return await call.answer()
    await call.message.answer("📢 Xabar yuborish uchun: /broadcast <matn>")
    await call.answer()


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return
    text = message.text.replace("/broadcast", "", 1).strip()
    if not text:
        await message.answer("Foydalanish: /broadcast <matn>")
        return
    ids = all_user_ids()
    sent = 0
    for uid in ids:
        try:
            await bot.send_message(uid, f"📢 {text}")
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ {sent} ta foydalanuvchiga yuborildi.")


@router.message(Command("grant"))
async def cmd_grant(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Foydalanish: /grant <user_id> <dollars> [diamonds]")
        return
    try:
        uid = int(parts[1])
        dollars = int(parts[2])
        diamonds = int(parts[3]) if len(parts) > 3 else 0
    except ValueError:
        await message.answer("Raqamlarni to'g'ri kiriting.")
        return
    update_balance(uid, dollars=dollars, diamonds=diamonds)
    await message.answer(f"✅ {uid} ga {dollars}$ va {diamonds}💎 qo'shildi.")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /ban <user_id>")
        return
    set_ban(int(parts[1]), True)
    await message.answer("🚫 Bloklandi.")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /unban <user_id>")
        return
    set_ban(int(parts[1]), False)
    await message.answer("✅ Blokdan chiqarildi.")
