from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import RANKS, DIAMOND_PACKAGES, RISK_MULTIPLIERS


def join_keyboard(chat_id):
    b = InlineKeyboardBuilder()
    b.button(text="➕ Qo'shilish", callback_data=f"join:{chat_id}")
    return b.as_markup()


def hand_keyboard(session, selected=None):
    selected = selected or set()
    player = session.current_player()
    b = InlineKeyboardBuilder()
    for i, card in enumerate(player.hand):
        mark = "✅ " if i in selected else ""
        b.button(text=f"{mark}{card}", callback_data=f"toggle:{session.chat_id}:{i}")
    b.adjust(3)
    b.row()
    b.button(text="🎯 Tashlash", callback_data=f"submit_play:{session.chat_id}")
    return b.as_markup()


def declare_keyboard(chat_id):
    b = InlineKeyboardBuilder()
    for rank in RANKS:
        b.button(text=rank, callback_data=f"declare:{chat_id}:{rank}")
    b.adjust(5)
    return b.as_markup()


def believe_keyboard(chat_id):
    b = InlineKeyboardBuilder()
    b.button(text="✅ Ishonaman", callback_data=f"believe:{chat_id}")
    b.button(text="❌ Ishonmayman (Challenge)", callback_data=f"challenge:{chat_id}")
    b.adjust(1)
    return b.as_markup()


def risk_keyboard(base_reward):
    b = InlineKeyboardBuilder()
    for m in RISK_MULTIPLIERS:
        b.button(text=f"x{m}", callback_data=f"risk:{m}:{base_reward}")
    b.button(text="🚫 Yo'q, olib qolaman", callback_data="risk:skip:0")
    b.adjust(len(RISK_MULTIPLIERS), 1)
    return b.as_markup()


def shop_keyboard():
    b = InlineKeyboardBuilder()
    for pkg in DIAMOND_PACKAGES:
        b.button(text=f"💎 {pkg['diamonds']} — ⭐ {pkg['stars']}", callback_data=f"buy:{pkg['diamonds']}:{pkg['stars']}")
    b.adjust(1)
    return b.as_markup()


def admin_panel_keyboard():
    b = InlineKeyboardBuilder()
    b.button(text="📊 Statistika", callback_data="admin:stats")
    b.button(text="🏆 TOP o'yinchilar", callback_data="admin:top")
    b.button(text="📢 Xabar yuborish", callback_data="admin:broadcast")
    b.adjust(1)
    return b.as_markup()
