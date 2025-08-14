import os
import logging
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
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
    "status": "running",
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
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", f"https://{os.environ.get('REPLIT_DOMAINS', 'your-app.replit.dev')}")

if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN environment variable not set")
    bot_status["status"] = "configuration_needed"

def send_telegram_message(chat_id, text, reply_to_message_id=None):
    """Send a message via Telegram Bot API"""
    if not TELEGRAM_TOKEN:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json().get("ok", False)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def send_telegram_photo(chat_id, photo_path, caption=""):
    """Send a photo via Telegram Bot API"""
    if not TELEGRAM_TOKEN:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption
            }
            response = requests.post(url, files=files, data=data, timeout=30)
            return response.json().get("ok", False)
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return False

def handle_start_command(chat_id):
    """Handle /start command"""
    welcome_message = """
🤖 *Welcome to AI Assistant Bot!*

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
    return send_telegram_message(chat_id, welcome_message)

def handle_help_command(chat_id):
    """Handle /help command"""
    help_message = """
🔧 *How to use this bot:*

📝 *Text Messages:*
Send any text message and I'll respond using Gemini AI.

📸 *Images:*
Send an image and I'll:
• Analyze it using Google Vision API
• Provide detailed description
• Optionally remove background (use caption "remove background")

⚠️ Supported formats: JPEG, PNG, WebP
📏 Max file size: 20MB

Need more help? Contact support!
    """
    return send_telegram_message(chat_id, help_message)

def handle_status_command(chat_id):
    """Handle /status command"""
    uptime = datetime.utcnow() - bot_status["uptime"]
    status_message = f"""
📊 *Bot Status:* {bot_status["status"]}
⏰ *Uptime:* {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m
📨 *Messages processed:* {bot_status["messages_processed"]}
🖼️ *Images processed:* {bot_status["images_processed"]}
❌ *Errors:* {bot_status["errors"]}
🕐 *Last update:* {bot_status["last_update"].strftime("%Y-%m-%d %H:%M:%S")} UTC
    """
    return send_telegram_message(chat_id, status_message)

def handle_text_message(chat_id, message_text, message_id):
    """Handle text messages with Gemini AI"""
    try:
        logger.info(f"Processing text message: {message_text[:50]}...")
        
        # Get response from Gemini
        response = gemini_service.generate_response(message_text)
        
        # Send response
        success = send_telegram_message(chat_id, response, message_id)
        
        if success:
            bot_status["messages_processed"] += 1
            bot_status["last_update"] = datetime.utcnow()
            logger.info("Text message processed successfully")
        else:
            logger.error("Failed to send response")
            bot_status["errors"] += 1
            
    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        send_telegram_message(chat_id, "Sorry, I encountered an error processing your message. Please try again.")
        bot_status["errors"] += 1

def handle_photo_message(chat_id, photo_file_id, caption, message_id):
    """Handle photo messages with Vision API and optional background removal"""
    try:
        logger.info("Processing photo message...")
        
        # Download image
        if not TELEGRAM_TOKEN:
            return
            
        # Get file info
        file_info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile"
        response = requests.get(file_info_url, params={"file_id": photo_file_id})
        
        if not response.json().get("ok"):
            send_telegram_message(chat_id, "❌ Could not download image. Please try again.")
            return
            
        file_path = response.json()["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        
        # Download image
        image_response = requests.get(download_url)
        image_path = f"temp_{photo_file_id}.jpg"
        
        with open(image_path, 'wb') as f:
            f.write(image_response.content)
        
        # Check if background removal is requested
        remove_bg = caption and "remove background" in caption.lower()
        
        response_parts = []
        
        # Analyze image with Vision API
        vision_analysis = vision_service.analyze_image(image_path)
        if vision_analysis and not vision_analysis.startswith("❌"):
            response_parts.append(f"🔍 *Image Analysis:*\n{vision_analysis}")
        
        # Analyze with Gemini (multimodal)
        gemini_analysis = gemini_service.analyze_image(image_path)
        if gemini_analysis and not gemini_analysis.startswith("❌"):
            response_parts.append(f"🤖 *AI Analysis:*\n{gemini_analysis}")
        
        # Remove background if requested
        if remove_bg and background_service.is_available():
            try:
                processed_image_path = background_service.remove_background(image_path)
                if processed_image_path:
                    # Send processed image
                    if send_telegram_photo(chat_id, processed_image_path, "✨ Background removed!"):
                        response_parts.append("✅ Background removal completed!")
                    os.remove(processed_image_path)
            except Exception as bg_error:
                logger.error(f"Background removal error: {bg_error}")
                response_parts.append("❌ Background removal failed. Please try again.")
        
        # Send analysis response
        if response_parts:
            full_response = "\n\n".join(response_parts)
            send_telegram_message(chat_id, full_response, message_id)
        else:
            send_telegram_message(chat_id, "I couldn't analyze this image. Please try with a different image.")
        
        # Cleanup
        if os.path.exists(image_path):
            os.remove(image_path)
        
        bot_status["images_processed"] += 1
        bot_status["last_update"] = datetime.utcnow()
        logger.info("Photo message processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing photo message: {e}")
        send_telegram_message(chat_id, "Sorry, I couldn't process your image. Please try again with a different image.")
        bot_status["errors"] += 1

@app.route('/')
def index():
    """Render status dashboard"""
    return render_template('index.html', bot_status=bot_status)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    try:
        if not TELEGRAM_TOKEN:
            return jsonify({"error": "Bot token not configured"}), 500
            
        # Get update from Telegram
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({"error": "No data received"}), 400
        
        logger.info(f"Received update: {json.dumps(update_data, indent=2)}")
        
        # Handle different types of updates
        if "message" in update_data:
            message = update_data["message"]
            chat_id = message["chat"]["id"]
            message_id = message["message_id"]
            
            # Handle commands
            if "text" in message and message["text"].startswith("/"):
                command = message["text"].split()[0]
                if command == "/start":
                    handle_start_command(chat_id)
                elif command == "/help":
                    handle_help_command(chat_id)
                elif command == "/status":
                    handle_status_command(chat_id)
                else:
                    send_telegram_message(chat_id, "Unknown command. Use /help to see available commands.")
            
            # Handle text messages
            elif "text" in message:
                handle_text_message(chat_id, message["text"], message_id)
            
            # Handle photos
            elif "photo" in message:
                # Get the largest photo
                photo = message["photo"][-1]
                caption = message.get("caption", "")
                handle_photo_message(chat_id, photo["file_id"], caption, message_id)
        
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
            bot_status["status"] = "running"
            return jsonify({"status": "webhook set", "url": webhook_url})
        else:
            return jsonify({"error": response.json()}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("RENDER_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)