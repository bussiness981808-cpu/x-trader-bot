import os
import qrcode
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
import uvicorn

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, WebAppInfo
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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

WAITING_SCREENSHOT = 1

api = FastAPI()
telegram_app = None

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
        [InlineKeyboardButton(
            "🚀 Open Number Hack App",
            web_app=WebAppInfo(url=f"{WEBHOOK_URL}/miniapp")
        )],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

# ---------- Mini App route ----------
@api.get("/miniapp", response_class=HTMLResponse)
async def serve_miniapp():
    try:
        with open("miniapp.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Mini App file not found</h1>", status_code=404)

# ---------- Webhook route ----------
@api.post("/webhook")
async def telegram_webhook(request: Request):
    if telegram_app is None:
        return Response(status_code=503)
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return Response(status_code=200)

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

# ---------- Setup bot handlers ----------
def setup_handlers(app: Application):
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
    app.add_handler(CallbackQueryHandler(package_selected, pattern="^pkg_"))
    app.add_handler(CallbackQueryHandler(package_selected, pattern="^back$"))
    app.add_handler(conv)

# ---------- Startup / Shutdown ----------
@api.on_event("startup")
async def on_startup():
    global telegram_app
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN nahi mila!")
        return
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL nahi mila!")
        return

    telegram_app = Application.builder().token(BOT_TOKEN).build()
    setup_handlers(telegram_app)

    await telegram_app.initialize()
    await telegram_app.start()

    webhook_endpoint = f"{WEBHOOK_URL}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_endpoint)
    print(f"✅ Bot started. Webhook set: {webhook_endpoint}")

@api.on_event("shutdown")
async def on_shutdown():
    global telegram_app
    if telegram_app:
        await telegram_app.stop()
        await telegram_app.shutdown()
        print("🛑 Bot stopped.")

# ---------- Run ----------
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", "8443"))
    uvicorn.run(api, host="0.0.0.0", port=PORT)
