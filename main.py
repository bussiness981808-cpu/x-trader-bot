import os
import qrcode
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
)
from telegram.ext import (
    Application,
    CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7142188619"))
UPI_ID = os.getenv("UPI_ID", "BHARATPE2G0W0I1W6R16196@unitype")
UPI_NAME = os.getenv("UPI_NAME", "X Trader AI")

WAITING_SCREENSHOT = 1

# ---------- QR Generator ----------
def generate_qr(amount: int, note: str) -> BytesIO:
    upi_link = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amount}&cu=INR&tn={note}"
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    text = (
        "🤖 *X TRADER AI* 🤖\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔥 *Premium Packages* 🔥\n\n"
        "📦 *Package 1:* 3 Days – ₹499\n"
        "📦 *Package 2:* 7 Days – ₹999\n"
        "📦 *Package 3:* Private Server – ₹1999\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Demo dekhe bina mat kharido!\n"
        "👇 Niche button se Demo dekho\n"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 3 Days – ₹499", callback_data="pkg_499")],
        [InlineKeyboardButton("📦 7 Days – ₹999", callback_data="pkg_999")],
        [InlineKeyboardButton("🚀 Private Server – ₹1999", callback_data="pkg_1999")],
        [InlineKeyboardButton("🎬 Watch Demo (Free)", callback_data="demo")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

# ---------- Demo ----------
async def demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    demo_url = "https://youtu.be/XXXXXXX"   # 👉 apna demo video link yahan daal
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Open Demo Video", url=demo_url)],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])
    await q.message.reply_text(
        "🎬 *Hack Demo Video*\n\nYeh demo dekhne ke baad hi purchase karein!",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ---------- Package selected ----------
async def package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "back":
        await start(update, context)
        return

    amount = int(q.data.split("_")[1])
    context.user_data["amount"] = amount

    buf = generate_qr(amount, f"XTraderAI_{amount}")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ I have paid – Upload Screenshot", callback_data="paid")]
    ])
    await q.message.reply_photo(
        photo=InputFile(buf, filename=f"qr_{amount}.png"),
        caption=(
            f"💳 *Payment QR*\n\n"
            f"💰 Amount: *₹{amount}*\n"
            f"📱 UPI ID: `{UPI_ID}`\n"
            f"👤 Name: {UPI_NAME}\n\n"
            f"1️⃣ Scan QR / Pay on UPI ID\n"
            f"2️⃣ Niche wale button se screenshot bhejo\n\n"
            f"⚠️ Amount exact hona chahiye!"
        ),
        parse_mode="Markdown",
        reply_markup=kb
    )

# ---------- Ask Screenshot ----------
async def ask_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(
        "📤 *Please send payment screenshot now.*\n\n"
        "Screenshot clearly dikhna chahiye (amount + UTR + date)."
    )
    return WAITING_SCREENSHOT

# ---------- Receive Screenshot ----------
async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if not msg.photo:
        await msg.reply_text("❌ Please send a *screenshot image* only.", parse_mode="Markdown")
        return WAITING_SCREENSHOT

    amount = context.user_data.get("amount", "N/A")
    photo = msg.photo[-1]

    await msg.reply_text(
        "✅ *Screenshot received!*\n\n"
        "Admin will verify and contact you within 5-10 minutes.\n"
        "⏳ Please wait...",
        parse_mode="Markdown"
    )

    admin_caption = (
        "🔔 *NEW PAYMENT PROOF* 🔔\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name: *{user.full_name}*\n"
        f"🆔 User ID: `{user.id}`\n"
        f"📛 Username: @{user.username if user.username else 'N/A'}\n"
        f"💰 Amount: *₹{amount}*\n"
        f"🕐 Time: {msg.date}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ Verify & deliver package."
    )

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=admin_caption,
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 Reply to user: [Click here](tg://user?id={user.id})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await msg.reply_text(f"⚠️ Admin ko bhejne me error: {e}")
        return ConversationHandler.END

    context.user_data.clear()
    return ConversationHandler.END

# ---------- Cancel ----------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled. /start dobara dabaye.")
    return ConversationHandler.END

# ---------- Main (Webhook mode for Render) ----------
def main():
    PORT = int(os.environ.get("PORT", "8443"))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL environment variable nahi mila!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_screenshot, pattern="^paid$")],
        states={
            WAITING_SCREENSHOT: [
                MessageHandler(filters.PHOTO, receive_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               lambda u, c: u.message.reply_text("📸 Screenshot bhejo, text nahi."))
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(demo, pattern="^demo$"))
    app.add_handler(CallbackQueryHandler(package_selected, pattern="^pkg_"))
    app.add_handler(CallbackQueryHandler(package_selected, pattern="^back$"))
    app.add_handler(conv)

    print(f"✅ Bot webhook mode par start ho raha hai: {WEBHOOK_URL}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
