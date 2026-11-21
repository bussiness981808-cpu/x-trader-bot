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

# ==========================================
# MINI APP KA HTML CODE (Directly embedded)
# ==========================================
MINIAPP_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Number Hack — Mini App</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#060816; --card:#0f1729; --card2:#111c33;
  --primary:#7c4dff; --secondary:#00e5ff; --pink:#ff4dbe;
  --soft:#9aa4c7; --green:#00e676;
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html,body{height:100%;}
body{
  background:radial-gradient(circle at top left,#1b1040 0%,transparent 35%),
             radial-gradient(circle at bottom right,#001f3f 0%,transparent 35%),
             var(--bg);
  min-height:100vh; display:flex; justify-content:center; align-items:center;
  font-family:Inter,sans-serif; color:white; padding:15px;
  overflow-x:hidden;
}
.phone{
  width:360px; max-width:100%; border-radius:28px; padding:18px;
  background:rgba(16,22,40,.95);
  border:1px solid rgba(255,255,255,.08);
  box-shadow:0 0 40px rgba(124,77,255,.35), inset 0 0 30px rgba(255,255,255,.02);
  backdrop-filter:blur(18px);
}
.header{display:flex; justify-content:center; margin-bottom:18px;}
.server-status{
  display:flex; align-items:center; gap:9px; padding:13px 22px;
  border-radius:13px; background:rgba(0,230,118,.10);
  border:1px solid rgba(0,230,118,.4); color:#00e676;
  font-family:Orbitron,sans-serif; font-size:18px; font-weight:800;
  letter-spacing:1px; box-shadow:0 0 20px rgba(0,230,118,.2);
  white-space:nowrap;
}
.online-dot{width:9px;height:9px;flex-shrink:0;border-radius:50%;background:#00e676;
  box-shadow:0 0 12px #00e676;animation:onlinePulse 1.2s infinite;}
@keyframes onlinePulse{0%,100%{opacity:1;box-shadow:0 0 10px #00e676}50%{opacity:.35;box-shadow:0 0 2px #00e676}}
.panel{background:linear-gradient(180deg,var(--card),var(--card2));
  border-radius:24px; padding:20px; border:1px solid rgba(255,255,255,.05);}
.toprow{display:flex; justify-content:space-between; align-items:center; gap:8px;}
.period{font-family:Orbitron,sans-serif; font-size:12px; color:var(--secondary);}
.period span{display:block; color:white; font-size:15px; margin-top:6px; word-break:break-all;}
.timer{font-family:Orbitron,sans-serif; font-size:22px; color:var(--pink);
  text-shadow:0 0 15px rgba(255,77,190,.8); white-space:nowrap;}
.circle-wrap{margin:28px 0; display:flex; flex-direction:column; align-items:center;}
.ring{width:220px; height:220px; border-radius:50%; position:relative;
  background:linear-gradient(var(--card),var(--card)) padding-box,
             linear-gradient(135deg,var(--primary),var(--secondary),var(--pink)) border-box;
  border:4px solid transparent; display:flex; justify-content:center; align-items:center;
  box-shadow:0 0 25px rgba(124,77,255,.5),0 0 60px rgba(0,229,255,.15);
  transition:.25s; animation:rotateGlow 5s linear infinite;}
@keyframes rotateGlow{0%{filter:hue-rotate(0deg)}100%{filter:hue-rotate(360deg)}}
.ring::before{content:""; position:absolute; inset:14px; border-radius:50%;
  background:#09101f; box-shadow:inset 0 0 25px rgba(0,0,0,.7);}
.digit{position:relative; z-index:2; font-size:48px; font-family:Orbitron,sans-serif;
  font-weight:800; letter-spacing:2px;
  background:linear-gradient(180deg,var(--secondary),white);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.label-pill{margin-top:18px; padding:10px 18px; border-radius:999px;
  background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08);
  color:var(--soft); font-size:12px; font-weight:600; letter-spacing:1px;
  text-align:center; transition:color .3s;}
.actions{display:flex; flex-direction:column; gap:14px;}
.predict{padding:14px; border:none; border-radius:16px; font-weight:800;
  font-size:15px; cursor:pointer; color:white;
  background:linear-gradient(135deg,var(--primary),var(--pink));
  box-shadow:0 0 20px rgba(124,77,255,.5),0 0 25px rgba(255,77,190,.35);
  transition:.25s; font-family:Inter,sans-serif;}
.predict:active{transform:scale(.97);}
.small-row{display:flex; gap:12px;}
.auto,.clear{flex:1; padding:12px; border-radius:14px;
  border:1px solid rgba(255,255,255,.08);
  background:rgba(255,255,255,.04); color:white; font-weight:700; cursor:pointer;
  transition:.25s; font-family:Inter,sans-serif;}
.auto.on{background:linear-gradient(135deg,#7c4dff,#00e5ff);}
.history{margin-top:18px; padding:16px;
  background:linear-gradient(180deg,#111c33,#0b1223);
  border:1px solid rgba(0,229,255,.18); border-radius:20px;
  box-shadow:0 0 20px rgba(0,229,255,.06);}
.history-title{font-family:Orbitron,sans-serif; font-size:14px; font-weight:800;
  text-align:center; color:#00e5ff; margin-bottom:16px; letter-spacing:1px;}
.history-head,.history-row{display:grid; grid-template-columns:1fr 75px;
  align-items:center; gap:8px; padding:12px 8px;}
.history-head{color:#9aa4c7; font-size:10px; font-weight:800;
  border-bottom:1px solid #26334d;}
.history-row{color:white; font-size:11px; font-weight:600;
  border-bottom:1px solid rgba(255,255,255,.06);}
.history-row:last-child{border-bottom:none;}
.history-row span:last-child{color:#00e5ff; font-family:Orbitron,sans-serif;
  font-size:16px; text-align:center;}
.loading{padding:20px 5px; text-align:center; color:#9aa4c7; font-size:12px;}
.history-status{text-align:center; font-size:10px; color:#9aa4c7; margin-top:12px;}
.footer{text-align:center; margin-top:16px; color:var(--soft); font-size:10px;}
@media(max-width:420px){.phone{width:100%}.ring{width:200px;height:200px}}
@media(max-width:350px){.server-status{font-size:15px;padding:11px 15px}}
</style>
</head>
<body>

<div class="phone">
  <div class="header">
    <div class="server-status">
      <span class="online-dot"></span> NUMBER SERVER
    </div>
  </div>

  <div class="panel">
    <div class="toprow">
      <div class="period">PERIOD: <span id="period">WAITING...</span></div>
      <div class="timer" id="timer">00:60</div>
    </div>

    <div class="circle-wrap">
      <div class="ring" id="ring">
        <div class="digit" id="digit">?</div>
      </div>
      <div class="label-pill" id="label">WAITING</div>
    </div>

    <div class="actions">
      <button class="predict" id="predictBtn">PREDICT NUMBER</button>
      <div class="small-row">
        <button class="auto" id="autoBtn">AUTO MODE</button>
        <button class="clear" id="clearBtn">CLEAR</button>
      </div>
    </div>
  </div>

  <div class="history">
    <div class="history-title">LAST 10 RESULT</div>
    <div class="history-head">
      <span>PERIOD NUMBER</span>
      <span style="text-align:center">RESULT</span>
    </div>
    <div id="historyList"><div class="loading">Loading results...</div></div>
    <div class="history-status" id="historyStatus">CONNECTING TO SERVER...</div>
  </div>

  <div class="footer">TELEGRAM : @DESIBILLAL1</div>
</div>

<script>
try {
  if (window.Telegram && window.Telegram.WebApp) {
    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
  }
} catch(e) { console.log("Telegram WebApp not available"); }

const digitEl   = document.getElementById("digit");
const timerEl   = document.getElementById("timer");
const periodEl  = document.getElementById("period");
const labelEl   = document.getElementById("label");
const ringEl    = document.getElementById("ring");
const predictBtn= document.getElementById("predictBtn");
const autoBtn   = document.getElementById("autoBtn");
const clearBtn  = document.getElementById("clearBtn");
const historyList  = document.getElementById("historyList");
const historyStatus= document.getElementById("historyStatus");

let autoMode = false;
let lastAutoMinute = -1;

function makePrediction(){
  digitEl.innerText = "🔒";
  labelEl.innerText = "LOCKED — PURCHASE TO UNLOCK";
  labelEl.style.color = "#ff4dbe";
  ringEl.style.transform = "scale(1.05)";
  setTimeout(()=>{ ringEl.style.transform = "scale(1)"; }, 250);
}

predictBtn.addEventListener("click", makePrediction);

autoBtn.addEventListener("click", ()=>{
  autoMode = !autoMode;
  if(autoMode){
    autoBtn.innerText = "AUTO ON";
    autoBtn.classList.add("on");
    makePrediction();
  }else{
    autoBtn.innerText = "AUTO MODE";
    autoBtn.classList.remove("on");
  }
});

clearBtn.addEventListener("click", ()=>{
  digitEl.innerText = "?";
  labelEl.innerText = "WAITING";
  labelEl.style.color = "#9aa4c7";
});

function updateTimer(){
  const now = new Date();
  const seconds = now.getSeconds();
  const remaining = 60 - seconds;
  timerEl.innerText = `00:${String(remaining).padStart(2,"0")}`;
  const Y = now.getUTCFullYear();
  const M = String(now.getUTCMonth()+1).padStart(2,"0");
  const D = String(now.getUTCDate()).padStart(2,"0");
  const totalMinutes = now.getUTCHours()*60 + now.getUTCMinutes();
  periodEl.innerText = `${Y}${M}${D}1000${10001+totalMinutes}`;
  const currentMinute = now.getUTCHours()*60 + now.getUTCMinutes();
  if(autoMode && seconds === 0 && lastAutoMinute !== currentMinute){
    lastAutoMinute = currentMinute;
    makePrediction();
  }
}
setInterval(updateTimer, 1000);
updateTimer();

const API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json";
let isFetching = false;

async function fetchHistory(){
  if(isFetching) return;
  isFetching = true;
  try{
    const response = await fetch(`${API_URL}?ts=${Date.now()}`, { method: "GET", cache: "no-store" });
    if(!response.ok) throw new Error("HTTP " + response.status);
    const data = await response.json();
    const results = data?.data?.list || data?.data?.records || data?.list || [];
    if(!Array.isArray(results) || results.length === 0) throw new Error("No result data found");
    historyList.innerHTML = results.slice(0,10).map(item=>{
      const period = item.issueNumber ?? item.issue ?? item.period ?? item.periodNumber ?? "--";
      const result = item.number ?? item.result ?? item.openNumber ?? item.winNumber ?? "--";
      return `<div class="history-row"><span>${escapeHTML(period)}</span><span>${escapeHTML(result)}</span></div>`;
    }).join("");
    historyStatus.innerText = "● LIVE DATA CONNECTED";
    historyStatus.style.color = "#00e676";
  }catch(error){
    console.error("History API Error:", error);
    historyStatus.innerText = "API CONNECTION ERROR";
    historyStatus.style.color = "#ff4dbe";
    if(!historyList.children.length){
      historyList.innerHTML = '<div class="loading">Unable to load results</div>';
    }
  }finally{
    isFetching = false;
  }
}

function escapeHTML(v){
  return String(v).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  })[c]);
}

fetchHistory();
setInterval(fetchHistory, 5000);
</script>
</body>
</html>
"""

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

# ---------- Mini App Route ----------
@api.get("/miniapp", response_class=HTMLResponse)
async def serve_miniapp():
    # Ab file ki zaroorat nahi, seedha HTML return karega
    return HTMLResponse(content=MINIAPP_HTML)

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
