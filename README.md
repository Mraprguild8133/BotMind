# AI Assistant Telegram Bot 🤖

A sophisticated Telegram bot powered by multiple AI services for intelligent conversations, image analysis, and background removal capabilities.

## Features

### 🧠 AI-Powered Conversations
- **Gemini AI Integration**: Natural language processing using Google's Gemini 2.5 Flash model
- **Multi-language Support**: Responds in user's preferred language (English, Tamil, etc.)
- **Context Awareness**: Maintains conversation context for better responses

### 🖼️ Advanced Image Processing
- **Image Analysis**: Detailed analysis using Google Gemini's vision capabilities
- **Background Removal**: Professional background removal using Background.bg API
- **Computer Vision**: Optional Google Cloud Vision API integration for enhanced image understanding

### 📊 Monitoring & Health Checks
- **Web Dashboard**: Real-time status monitoring at `/`
- **Health Endpoints**: Service availability checks at `/health`
- **Service Status**: Individual service monitoring at `/status`

## Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token
- Gemini API Key
- Optional: Google Vision API Key, Background.bg API Key

### 1. Environment Setup
Create environment variables or add to Replit Secrets:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_VISION_API_KEY=your_google_vision_key  # Optional
BACKGROUNDBG_API_KEY=your_background_api_key  # Optional
RENDER_PORT=5000  # For deployment
```

### 2. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or use the package manager
python -m pip install flask python-telegram-bot google-genai gunicorn
```

### 3. Run the Bot
```bash
# Development
python simple_app.py

# Production (Gunicorn)
gunicorn --bind 0.0.0.0:5000 main:app
```

## Bot Commands

- `/start` - Welcome message and bot introduction
- `/help` - Display available commands and features
- `/status` - Check bot and service status
- Send any text - Get AI-powered responses
- Send images - Get detailed image analysis
- Send images with "remove background" - Background removal

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Status dashboard |
| `/health` | GET | Health check (JSON) |
| `/status` | GET | Service availability |
| `/webhook` | POST | Telegram webhook endpoint |

## Deployment

### Replit (Current)
Already configured and running! The bot is live and operational.

### Docker Deployment
```bash
# Build and run
docker build -t telegram-ai-bot .
docker run -d --env-file .env -p 5000:5000 telegram-ai-bot

# Or use Docker Compose
docker-compose up -d
```

### Cloud Platforms

#### Render.com
1. Connect GitHub repository
2. Set environment variables in dashboard
3. Automatic deployment with Dockerfile

#### Railway/Heroku
1. Connect repository
2. Add environment variables
3. Deploy with provided configuration

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed deployment instructions.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Telegram API   │───▶│   Flask WebApp   │───▶│  Service Layer  │
│   (Webhook)     │    │   (Port 5000)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Web Dashboard  │    │   AI Services   │
                       │   Monitoring    │    │                 │
                       └─────────────────┘    │ • Gemini AI     │
                                              │ • Google Vision │
                                              │ • Background.bg │
                                              └─────────────────┘
```

## Project Structure

```
├── services/                 # AI service modules
│   ├── gemini_service.py    # Gemini AI integration
│   ├── vision_service.py    # Google Vision API
│   └── background_service.py # Background removal
├── templates/               # Web dashboard templates
│   └── index.html          # Status dashboard
├── static/                 # Static web assets
│   └── style.css          # Dashboard styling
├── simple_app.py          # Main Flask application
├── main.py               # Gunicorn entry point
├── bot.py               # Alternative bot implementation
├── docker-requirements.txt # Docker dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
└── DOCKER_DEPLOYMENT.md # Deployment guide
```

## Service Integration

### Gemini AI
- **Model**: gemini-2.5-flash for conversations
- **Model**: gemini-2.5-pro for image analysis
- **Features**: Text generation, image understanding, multi-language support

### Google Cloud Vision (Optional)
- **Features**: Label detection, text recognition, face detection, landmark recognition
- **Note**: Requires billing enabled on Google Cloud project

### Background Removal (Optional)
- **Provider**: Background.bg or Remove.bg API
- **Features**: Professional background removal with automatic image compression

## Configuration

### Required Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `GEMINI_API_KEY`: Google AI Studio API key

### Optional Environment Variables
- `GOOGLE_VISION_API_KEY`: Google Cloud Vision API key
- `BACKGROUNDBG_API_KEY`: Background removal service key
- `RENDER_PORT`: Port number (default: 5000)
- `WEBHOOK_URL`: Custom webhook URL (auto-detected if not set)

## Monitoring

### Health Checks
The bot includes comprehensive health monitoring:
- Service availability checks
- API connectivity verification  
- Real-time status updates
- Error logging and reporting

### Dashboard Features
- Service status indicators
- Uptime tracking
- Message processing statistics
- Error rate monitoring

## Development

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd telegram-ai-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export GEMINI_API_KEY=your_key

# Run development server
python simple_app.py
```

### Adding New Services
1. Create service module in `services/` directory
2. Implement service class with availability check
3. Register in main application
4. Update health monitoring

## Troubleshooting

### Common Issues

**Bot not responding:**
- Check TELEGRAM_BOT_TOKEN is valid
- Verify webhook URL is accessible
- Check application logs for errors

**AI responses failing:**
- Verify GEMINI_API_KEY is correct
- Check API quota and billing status
- Review service initialization logs

**Image analysis not working:**
- Ensure GOOGLE_VISION_API_KEY is set
- Enable billing on Google Cloud project
- Check image format compatibility

### Debug Mode
Set environment variable `DEBUG=true` for detailed logging.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check troubleshooting section
2. Review logs for error details
3. Open GitHub issue with detailed description

---

**Status**: ✅ Active and operational  
**Last Updated**: August 14, 2025  
**Version**: 1.0.0