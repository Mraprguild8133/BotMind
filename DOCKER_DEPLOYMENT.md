# Docker Deployment Guide for AI Assistant Telegram Bot

## Quick Start

### 1. Copy Requirements File
```bash
# Copy the Docker requirements to requirements.txt
cp docker-requirements.txt requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with your API keys:
```bash
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_VISION_API_KEY=your_google_vision_api_key_here
BACKGROUNDBG_API_KEY=your_background_removal_api_key_here

# Port Configuration
RENDER_PORT=5000

# Optional
WEBHOOK_URL=https://your-domain.com
SESSION_SECRET=your-session-secret-key
```

### 3. Build and Run with Docker

#### Option A: Using Docker directly
```bash
# Build the image
docker build -t telegram-ai-bot .

# Run the container
docker run -d \
  --name telegram-bot \
  --env-file .env \
  -p 5000:5000 \
  telegram-ai-bot
```

#### Option B: Using Docker Compose (Recommended)
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Deployment Platforms

### Render.com
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Use the provided Dockerfile for automatic builds
4. Port will be automatically configured via RENDER_PORT

### Railway
1. Connect repository to Railway
2. Add environment variables
3. Railway will automatically detect and use the Dockerfile

### DigitalOcean App Platform
1. Create new app from GitHub repository
2. Configure environment variables
3. Set build command: `docker build -t app .`
4. Set run command: `gunicorn --bind 0.0.0.0:$PORT main:app`

### AWS ECS / Azure Container Instances / Google Cloud Run
Use the provided Dockerfile with your preferred container orchestration platform.

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI conversations and image analysis
- `TELEGRAM_BOT_TOKEN`: Required for Telegram bot functionality
- `GOOGLE_VISION_API_KEY`: Optional for advanced image analysis
- `BACKGROUNDBG_API_KEY`: Optional for background removal features
- `RENDER_PORT`: Port number (default: 5000)
- `WEBHOOK_URL`: External URL for Telegram webhooks (auto-detected if not set)
- `SESSION_SECRET`: Flask session security key

### Port Configuration
The application dynamically uses the port specified in `RENDER_PORT` environment variable, making it compatible with most cloud platforms.

## Health Monitoring
- Health check endpoint: `/health`
- Status dashboard: `/`
- API status: `/status`

## Logs
Application logs are available through:
- `docker logs telegram-bot` (Docker)
- `docker-compose logs -f` (Docker Compose)
- Your platform's logging interface

## Troubleshooting

### Common Issues
1. **Bot not responding**: Check `TELEGRAM_BOT_TOKEN` and webhook setup
2. **AI not working**: Verify `GEMINI_API_KEY`
3. **Port issues**: Ensure `RENDER_PORT` matches your platform requirements
4. **Image analysis failing**: Check `GOOGLE_VISION_API_KEY` and billing status

### Debug Mode
Set `DEBUG=true` environment variable for detailed logging.

## Security Notes
- Never commit API keys to version control
- Use environment variables or secrets management
- Consider running as non-root user (included in Dockerfile)
- Enable HTTPS in production deployments