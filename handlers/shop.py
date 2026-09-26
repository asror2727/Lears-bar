from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

import keyboards as kb
from bot_instance import bot
from database import update_balance

router = Router()


@router.message(Command("shop"))
async def cmd_shop(message: Message):
    await message.answer(
        "💎 <b>Olmos do'koni</b>\nTelegram Stars orqali xohlagan paketni tanlang:",
        reply_markup=kb.shop_keyboard(),
    )


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(call: CallbackQuery):
    _, diamonds_str, stars_str = call.data.split(":")
    diamonds, stars = int(diamonds_str), int(stars_str)

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f"{diamonds} 💎 Olmos",
        description=f"O'yin uchun {diamonds} ta olmos sotib olish",
        payload=f"diamonds:{diamonds}",
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label=f"{diamonds} olmos", amount=stars)],
    )
    await call.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    diamonds = int(payload.split(":")[1])
    update_balance(message.from_user.id, diamonds=diamonds)
    await message.answer(f"✅ To'lov qabul qilindi! +{diamonds} 💎 hisobingizga qo'shildi.")
