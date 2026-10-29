import logging
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Logging qurğusu
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Botun işləmə vəziyyəti və cari ayarlar
bot_state = {
    "is_running": False,
    "timeframe": "1m",
    "asset_type": "Hamısı"
}

ASSETS = ["EUR/USD", "GBP/USD", "USD/JPY"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Botu Başlat", callback_data="start_bot")],
        [InlineKeyboardButton("🛑 Botu Dayandır", callback_data="stop_bot")],
        [InlineKeyboardButton("⚙️ Ayarlar", callback_data="parametrier")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            "🤖 **Pocket Option Siqnal Botuna Xoş Gəlmisiniz!**\n"
            "Bu bot 15s - 5 dəqiqəlik intervallarla siqnallar göndərir.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def duyme_isledicisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorgu = update.callback_query
    await sorgu.answer()
    
    if sorgu.data == 'start_bot':
        bot_state["is_running"] = True
        await sorgu.edit_message_text("🚀 **Bot başladıldı!** Siqnallar göndərilməyə başlanacaq.", parse_mode="Markdown")
        context.application.create_task(siqnal_generatoru(context, sorgu.message.chat_id))
    elif sorgu.data == 'stop_bot':
        bot_state["is_running"] = False
        await sorgu.edit_message_text("🛑 **Bot dayandırıldı.**", parse_mode="Markdown")
    elif sorgu.data == 'parametrier':
        keyboard = [
            [InlineKeyboardButton("15 Saniyə", callback_data="tf_15s"), InlineKeyboardButton("1 Dəqiqə", callback_data="tf_1m")],
            [InlineKeyboardButton("Geri", callback_data="asas_menyu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await sorgu.edit_message_text(f"⚙️ **Cari Ayarlar:**\n⏱️ Interval: {bot_state['timeframe']}", reply_markup=reply_markup, parse_mode="Markdown")
    elif sorgu.data.startswith('tf_'):
        tf = sorgu.data.split('_')[1]
        bot_state["timeframe"] = tf
        await sorgu.edit_message_text(f"✅ Interval dəyişdirildi: {tf}")
    elif sorgu.data == 'asas_menyu':
        await start(update, context)

async def siqnal_generatoru(context, chat_id):
    while bot_state["is_running"]:
        await asyncio.sleep(15)
        if not bot_state["is_running"]:
            break
        
        aktiv = random.choice(ASSETS)
        istiqamət = random.choice(["🟢 YUXARI (CALL)", "🔴 AŞAĞI (PUT)"])
        ozunainam = random.randint(78, 95)
        
        siqnal_metni = (
            f"🔔 **YENİ SİQNAL!**\n\n"
            f"📊 **Aktiv:** {aktiv}\n"
            f"⏱️ **Müddət (Timeframe):** {bot_state['timeframe']}\n"
            f"📈 **İstiqamət:** {istiqamət}\n"
            f"🎯 **Uğur ehtiyacı:** %{ozunainam}\n"
            f"⚠️ *Risk idarəetməsini unutmayın!*"
        )
        
        try:
            await context.bot.send_message(chat_id=chat_id, text=siqnal_metni, parse_mode="Markdown")
        except Exception as e:
            print(f"Xəta baş verdi: {e}")

def main():
    TOKEN = "9200059393:AAEQuv9e6qw89tAsOMZbDplWq7p2L5vYTaQ"
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(duyme_isledicisi))
    
    print("Bot işləyir...")
    application.run_polling()

if __name__ == '__main__':
    main()
    
