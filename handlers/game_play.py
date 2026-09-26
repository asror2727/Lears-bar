import random

from aiogram import Router, F
from aiogram.types import CallbackQuery

import keyboards as kb
from bot_instance import bot
from database import add_result, update_balance
from game_manager import PendingPlay, games, selections

router = Router()


@router.callback_query(F.data.startswith("toggle:"))
async def cb_toggle(call: CallbackQuery):
    _, chat_id_str, idx_str = call.data.split(":")
    chat_id, idx = int(chat_id_str), int(idx_str)
    session = games.get(chat_id)
    if not session or session.state != "playing":
        await call.answer("O'yin faol emas.", show_alert=True)
        return
    player = session.current_player()
    if player.user_id != call.from_user.id:
        await call.answer("Hozir sizning navbatingiz emas.", show_alert=True)
        return

    sel = selections.setdefault(call.from_user.id, set())
    if idx in sel:
        sel.remove(idx)
    else:
        if len(sel) >= 4:
            await call.answer("Bir yo'la ko'pi bilan 4 ta karta tashlash mumkin.", show_alert=True)
            return
        sel.add(idx)

    await call.message.edit_reply_markup(reply_markup=kb.hand_keyboard(session, sel))
    await call.answer()


@router.callback_query(F.data.startswith("submit_play:"))
async def cb_submit(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    session = games.get(chat_id)
    player = session.current_player()
    if player.user_id != call.from_user.id:
        await call.answer("Navbat sizda emas.", show_alert=True)
        return

    sel = selections.get(call.from_user.id, set())
    if not sel:
        await call.answer("Kamida 1 ta karta tanlang.", show_alert=True)
        return

    await call.message.edit_text(
        f"Tanlangan kartalar soni: {len(sel)}\n"
        "Endi qaysi darajani (rank) e'lon qilasiz? (Haqiqiy yoki yolg'on bo'lishi mumkin 😉)",
        reply_markup=kb.declare_keyboard(chat_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("declare:"))
async def cb_declare(call: CallbackQuery):
    _, chat_id_str, rank = call.data.split(":")
    chat_id = int(chat_id_str)
    session = games.get(chat_id)
    player = session.current_player()
    if player.user_id != call.from_user.id:
        await call.answer("Navbat sizda emas.", show_alert=True)
        return

    sel = sorted(selections.get(call.from_user.id, set()), reverse=True)
    cards = [player.hand[i] for i in sel]
    for i in sel:
        player.hand[i] = None
    player.hand = [c for c in player.hand if c is not None]
    selections.pop(call.from_user.id, None)

    session.pending = PendingPlay(player.user_id, cards, rank)

    await call.message.edit_text(f"✅ Siz {len(cards)} ta \"{rank}\" tashladingiz (deb e'lon qildingiz).")
    await bot.send_message(chat_id, f"🎴 {player.username} {len(cards)} ta \"{rank}\" tashladi.")

    next_uid = session.next_alive_after(player.user_id)
    next_player = session.players[next_uid]
    try:
        await bot.send_message(
            next_uid,
            f"{player.username} {len(cards)} ta \"{rank}\" tashladi.\nIshonasizmi?",
            reply_markup=kb.believe_keyboard(chat_id),
        )
    except Exception:
        await bot.send_message(chat_id, f"⚠️ {next_player.username}, botga shaxsiy /start bosing — qaror sizda!")

    await call.answer()


@router.callback_query(F.data.startswith("believe:"))
async def cb_believe(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    session = games.get(chat_id)
    if not session or not session.pending:
        await call.answer("Hech narsa kutilmayapti.", show_alert=True)
        return

    await call.message.edit_text("Siz ishondingiz. ✅")
    await bot.send_message(chat_id, f"{call.from_user.first_name} ishondi. O'yin davom etadi.")
    session.pending = None
    session.advance_turn()
    await proceed_or_finish(session)
    await call.answer()


@router.callback_query(F.data.startswith("challenge:"))
async def cb_challenge(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    session = games.get(chat_id)
    pending = session.pending if session else None
    if not pending:
        await call.answer("Hech narsa kutilmayapti.", show_alert=True)
        return

    liar = session.players[pending.player_id]
    challenger = session.players[call.from_user.id]
    truthful = all(c == pending.claimed_rank for c in pending.cards)
    reveal = ", ".join(pending.cards)

    if truthful:
        challenger.lives -= 1
        result_text = (
            f"😱 {liar.username} rost aytgan ekan! Kartalar: {reveal}\n"
            f"{challenger.username} jon yo'qotdi. Qolgan jon: {challenger.lives}"
        )
        if challenger.lives <= 0:
            challenger.alive = False
    else:
        liar.lives -= 1
        result_text = (
            f"🤥 {liar.username} yolg'on gapirgan ekan! Kartalar: {reveal}\n"
            f"{liar.username} jon yo'qotdi. Qolgan jon: {liar.lives}"
        )
        if liar.lives <= 0:
            liar.alive = False

    await bot.send_message(chat_id, result_text)
    session.pending = None
    session.advance_turn()
    await call.message.edit_text("Qaror qabul qilindi.")
    await proceed_or_finish(session)
    await call.answer()


@router.callback_query(F.data.startswith("risk:"))
async def cb_risk(call: CallbackQuery):
    _, mult_str, base_str = call.data.split(":")
    if mult_str == "skip":
        await call.message.edit_text("👍 Yutuqni saqlab qoldingiz.")
        await call.answer()
        return

    mult = float(mult_str)
    base = int(base_str)
    win_chance = 0.5 if mult <= 1 else max(0.15, 0.5 - (mult - 1) * 0.15)
    won = random.random() < win_chance

    if won:
        amount = int(base * mult)
        update_balance(call.from_user.id, dollars=amount)
        await call.message.edit_text(f"🎉 Risk yutdingiz! +{amount}$")
    else:
        update_balance(call.from_user.id, dollars=-base)
        await call.message.edit_text(f"💥 Risk yutqazdingiz. -{base}$")
    await call.answer()


async def proceed_or_finish(session):
    winner_id = session.check_winner()
    if winner_id:
        session.state = "finished"
        winner = session.players[winner_id]
        reward = 100
        update_balance(winner_id, dollars=reward)
        add_result(winner_id, win=True)
        for uid in session.order:
            if uid != winner_id:
                add_result(uid, win=False)

        await bot.send_message(session.chat_id, f"🏆 G'olib: {winner.username}!\n💵 Yutuqqa {reward}$ qo'shildi.")
        try:
            await bot.send_message(
                winner_id,
                "🎲 Yutuqni ko'paytirmoqchimisiz? Risk qiling!",
                reply_markup=kb.risk_keyboard(reward),
            )
        except Exception:
            pass

        games.pop(session.chat_id, None)
        return

    from handlers.registration import announce_turn

    await announce_turn(session)
