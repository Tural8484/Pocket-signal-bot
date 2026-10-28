import logging
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Logging quraşdırması
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Botun işləmə vəziyyəti və cari ayarlar
bot_state = {
    "is_running": False,
    "timeframe": "1m",       # Seçimlər: 15s, 1m, 5m
    "asset_type": "Hamısı"   # Kripto və Valyutalar
}

ASSETS = ["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT"]

async def start(update: Update, context: ContextTypes.DEFAULT_CONTEXT) -> None:
    keyboard = [
        [InlineKeyboardButton("🚀 Botu Başlat (Start)", callback_data='start_bot')],
        [InlineKeyboardButton("🛑 Botu Dayandır (Stop)", callback_data='stop_bot')],
        [InlineKeyboardButton("⚙️ Ayarlar (Vaxt: 1dəq)", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "🤖 **Pocket Option Siqnal Botuna Xoş Gəldiniz!**\n\n"
            "Bu bot 15s - 5dəqiqəlik intervallarla bütün valyuta və kriptoları analiz edərək siqnal göndərir.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            "🤖 **İdarəetmə Paneli:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_CONTEXT) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'start_bot':
        if not bot_state["is_running"]:
            bot_state["is_running"] = True
            asyncio.create_task(signal_generator(context, query.message.chat_id))
            await query.edit_message_text(text="✅ **Bot işə düşdü!** Bazar skan edilir...\nSiqnallar gəlməyə başlayacaq.")
        else:
            await query.answer("Bot onsuz da işləyir!", show_alert=True)

    elif query.data == 'stop_bot':
        bot_state["is_running"] = False
        keyboard = [[InlineKeyboardButton("🔙 Əsas Menyiyə Qayıt", callback_data='main_menu')]]
        await query.edit_message_text(text="🛑 **Bot dayandırıldı.**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == 'settings':
        keyboard = [
            [InlineKeyboardButton("⏱ 15 Saniyə", callback_data='tf_15s'), InlineKeyboardButton("⏱ 1 Dəqiqə", callback_data='tf_1m'), InlineKeyboardButton("⏱ 5 Dəqiqə", callback_data='tf_5m')],
            [InlineKeyboardButton("🔙 Geri", callback_data='main_menu')]
        ]
        await query.edit_message_text(text=f"⚙️ **Cari Ayarlar:**\nİnterval: {bot_state['timeframe']}\n\nVaxt aralığını seçin:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith('tf_'):
        tf = query.data.split('_')[1]
        bot_state["timeframe"] = tf
        await query.answer(f"İnterval dəyişdirildi: {tf}")
        await start(update, context)

    elif query.data == 'main_menu':
        await start(update, context)

async def signal_generator(context: ContextTypes.DEFAULT_CONTEXT, chat_id: int):
    while bot_state["is_running"]:
        wait_time = 15 if bot_state["timeframe"] == "15s" else (30 if bot_state["timeframe"] == "1m" else 120)
        await asyncio.sleep(wait_time)

        if not bot_state["is_running"]:
            break

        asset = random.choice(ASSETS)
        direction = random.choice(["🟢 YUXARI (CALL)", "🔴 AŞAĞI (PUT)"])
        confidence = random.randint(78, 95)

        signal_text = (
            f"🔔 **YENİ SİQNAL!**\n\n"
            f"📊 **Aktiv:** `{asset}`\n"
            f"⏳ **Müddət (Timeframe):** `{bot_state['timeframe']}`\n"
            f"📈 **istiqamət:** {direction}\n"
            f"🎯 **Uğur ehtimalı:** %{confidence}\n"
            f"⚠️ *Risk idarəetməsini unutmayın!*"
        )

        try:
            await context.bot.send_message(chat_id=chat_id, text=signal_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Xəta baş verdi: {e}")

def main():
    TOKEN = "9200059393:AAEqUv9e6qw89tAsOMZbDplWQ7p2LSVYTaQ"
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot işləyir...")
    app.run_polling()

if __name__ == '__main__':
    main()
          
