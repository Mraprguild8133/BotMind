import os
import logging
import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
from services.gemini_service import GeminiService
from services.vision_service import VisionService
from services.background_service import BackgroundService

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Bot status tracking
bot_status = {
    "status": "initializing",
    "last_update": datetime.utcnow(),
    "messages_processed": 0,
    "images_processed": 0,
    "errors": 0,
    "uptime": datetime.utcnow()
}

# Initialize services
gemini_service = GeminiService()
vision_service = VisionService()
background_service = BackgroundService()

# Telegram bot configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app.replit.dev")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
    bot_status["status"] = "error"
    bot_status["error_message"] = "Missing Telegram bot token"

# Initialize Telegram Application
application = None
if TELEGRAM_TOKEN:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start_command(update: Update, context):
    """Handle /start command"""
    welcome_message = """
🤖 Welcome to AI Assistant Bot!

I can help you with:
• 💬 Text conversations using Gemini AI
• 🖼️ Image analysis with Google Vision
• 🎨 Background removal from images

Commands:
/start - Show this welcome message
/help - Get help information
/status - Check bot status

Just send me a message or image to get started!
    """
    await update.message.reply_text(welcome_message)
    bot_status["messages_processed"] += 1

async def help_command(update: Update, context):
    """Handle /help command"""
    help_message = """
🔧 How to use this bot:

📝 Text Messages:
Send any text message and I'll respond using Gemini AI.

📸 Images:
Send an image and I'll:
• Analyze it using Google Vision API
• Provide detailed description
• Optionally remove background (use caption "remove background")

⚠️ Supported formats: JPEG, PNG, WebP
📏 Max file size: 20MB

Need more help? Contact support!
    """
    await update.message.reply_text(help_message)
    bot_status["messages_processed"] += 1

async def status_command(update: Update, context):
    """Handle /status command"""
    uptime = datetime.utcnow() - bot_status["uptime"]
    status_message = f"""
📊 Bot Status: {bot_status["status"]}
⏰ Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m
📨 Messages processed: {bot_status["messages_processed"]}
🖼️ Images processed: {bot_status["images_processed"]}
❌ Errors: {bot_status["errors"]}
🕐 Last update: {bot_status["last_update"].strftime("%Y-%m-%d %H:%M:%S")} UTC
    """
    await update.message.reply_text(status_message)
    bot_status["messages_processed"] += 1

async def handle_text_message(update: Update, context):
    """Handle text messages with Gemini AI"""
    try:
        user_message = update.message.text
        logger.info(f"Processing text message: {user_message[:50]}...")
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Get response from Gemini
        response = gemini_service.generate_response(user_message)
        
        # Send response
        await update.message.reply_text(response)
        
        bot_status["messages_processed"] += 1
        bot_status["last_update"] = datetime.utcnow()
        logger.info("Text message processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        await update.message.reply_text("Sorry, I encountered an error processing your message. Please try again.")
        bot_status["errors"] += 1

async def handle_image_message(update: Update, context):
    """Handle image messages with Vision API and optional background removal"""
    try:
        logger.info("Processing image message...")
        
        # Send processing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
        
        # Get the largest photo
        photo = update.message.photo[-1]
        
        # Download image
        file = await context.bot.get_file(photo.file_id)
        image_path = f"temp_{photo.file_id}.jpg"
        await file.download_to_drive(image_path)
        
        # Check if background removal is requested
        caption = update.message.caption or ""
        remove_bg = "remove background" in caption.lower()
        
        response_parts = []
        
        # Analyze image with Vision API
        vision_analysis = vision_service.analyze_image(image_path)
        if vision_analysis:
            response_parts.append(f"🔍 **Image Analysis:**\n{vision_analysis}")
        
        # Analyze with Gemini (multimodal)
        gemini_analysis = gemini_service.analyze_image(image_path)
        if gemini_analysis:
            response_parts.append(f"🤖 **AI Analysis:**\n{gemini_analysis}")
        
        # Remove background if requested
        if remove_bg:
            try:
                processed_image_path = background_service.remove_background(image_path)
                if processed_image_path:
                    # Send processed image
                    with open(processed_image_path, 'rb') as processed_file:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=processed_file,
                            caption="✨ Background removed!"
                        )
                    os.remove(processed_image_path)
                    response_parts.append("✅ Background removal completed!")
            except Exception as bg_error:
                logger.error(f"Background removal error: {bg_error}")
                response_parts.append("❌ Background removal failed. Please try again.")
        
        # Send analysis response
        if response_parts:
            full_response = "\n\n".join(response_parts)
            await update.message.reply_text(full_response)
        else:
            await update.message.reply_text("I couldn't analyze this image. Please try with a different image.")
        
        # Cleanup
        if os.path.exists(image_path):
            os.remove(image_path)
        
        bot_status["images_processed"] += 1
        bot_status["last_update"] = datetime.utcnow()
        logger.info("Image message processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing image message: {e}")
        await update.message.reply_text("Sorry, I couldn't process your image. Please try again with a different image.")
        bot_status["errors"] += 1

# Add handlers to application
if application:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image_message))
    bot_status["status"] = "running"

@app.route('/')
def index():
    """Render status dashboard"""
    return render_template('index.html', bot_status=bot_status)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    try:
        if not application:
            return jsonify({"error": "Bot not initialized"}), 500
            
        # Get update from Telegram
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({"error": "No data received"}), 400
        
        # Create Update object
        update = Update.de_json(update_data, application.bot)
        
        # Process update asynchronously
        asyncio.create_task(application.process_update(update))
        
        bot_status["last_update"] = datetime.utcnow()
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        bot_status["errors"] += 1
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def get_status():
    """API endpoint for bot status"""
    return jsonify(bot_status)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "telegram": TELEGRAM_TOKEN is not None,
            "gemini": gemini_service.is_available(),
            "vision": vision_service.is_available(),
            "background": background_service.is_available()
        }
    })

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set webhook URL for Telegram bot"""
    try:
        if not TELEGRAM_TOKEN:
            return jsonify({"error": "Bot token not configured"}), 500
            
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # Set webhook
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            json={"url": webhook_url}
        )
        
        if response.json().get("ok"):
            return jsonify({"status": "webhook set", "url": webhook_url})
        else:
            return jsonify({"error": response.json()}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
