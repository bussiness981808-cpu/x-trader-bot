import os
# ... aapke baaki imports ...

# ... aapke saare functions (start, demo, package_selected, etc.) ...

def main():
    # Render PORT environment variable deta hai
    PORT = int(os.environ.get("PORT", "8443"))
    
    # Render aapko ek external URL deta hai
    # Isko Render dashboard ke "Environment" tab mein set karna hoga
    # Example: https://aapka-bot-name.onrender.com
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 
    
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL environment variable nahi mila!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # ... aapke saare handlers add karein (jo pehle code mein the) ...
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

    # Webhook mode mein chalayein
    print(f"✅ Bot webhook mode par start ho raha hai: {WEBHOOK_URL}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,  # URL path mein token daalna zaroori hai
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()