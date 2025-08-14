# AI Assistant Bot

## Overview

An AI-powered Telegram bot that provides intelligent text responses, image analysis, and background removal capabilities. The bot integrates multiple AI services including Google Gemini for conversational AI, Google Cloud Vision for image analysis, and Background.bg/Remove.bg for background removal. Built with Flask for web interface and monitoring, the bot serves as a comprehensive AI assistant accessible through Telegram.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### August 14, 2025
- Fixed Telegram import conflicts by creating simplified webhook-based implementation
- Application successfully running on port 5000 with gunicorn (Render compatible)
- All services operational with provided API keys:
  * Gemini AI: Working (conversations and image analysis)
  * Telegram Bot: Active with webhook configured
  * Background removal: API connected and ready
  * Google Vision: API key valid but requires billing enablement
- Bot actively processing user messages and images via webhook
- Port configuration supports both Replit (5000) and Render deployment
- Status dashboard and health monitoring fully functional

## System Architecture

### Web Framework
- **Flask Application**: Main web server handling HTTP requests, webhook endpoints, and serving a status dashboard
- **Template Rendering**: HTML templates for web interface with Bootstrap dark theme
- **Static Assets**: CSS styling with custom bot-specific themes and Font Awesome icons

### Messaging Platform Integration
- **Telegram Bot Integration**: Uses python-telegram-bot library for handling Telegram API interactions
- **Webhook Architecture**: Designed to receive updates via webhooks rather than polling
- **Bot Status Tracking**: Real-time monitoring of bot operations including message counts, uptime, and error tracking

### AI Service Layer
The application implements a modular service architecture with three core AI capabilities:

- **Gemini Service**: Handles conversational AI using Google's Gemini 2.5 Flash model for generating intelligent text responses
- **Vision Service**: Provides image analysis using Google Cloud Vision API with comprehensive feature detection (labels, text, objects, faces, landmarks, logos, safe search)
- **Background Service**: Removes backgrounds from images using Background.bg or Remove.bg APIs with automatic image compression for large files

### Configuration Management
- **Environment Variables**: All sensitive data (API keys, tokens, webhook URLs) stored as environment variables
- **Graceful Degradation**: Services check availability and provide user-friendly error messages when APIs are unavailable
- **Fallback Mechanisms**: Bot continues operating even if individual services fail

### Error Handling and Monitoring
- **Comprehensive Logging**: Debug-level logging throughout the application for troubleshooting
- **Service Health Checks**: Each service has availability checking methods
- **Status Dashboard**: Web interface displaying bot status, service availability, and operational metrics
- **Exception Management**: Try-catch blocks with user-friendly error messages

### File Processing
- **Image Handling**: Supports various image formats with automatic compression for API size limits
- **Temporary File Management**: Handles file uploads and processing for image analysis and background removal

## External Dependencies

### AI and Machine Learning Services
- **Google Gemini API**: Conversational AI and text generation (requires GEMINI_API_KEY)
- **Google Cloud Vision API**: Image analysis and computer vision (requires GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_VISION_API_KEY)
- **Background.bg/Remove.bg API**: Background removal service (requires BACKGROUNDBG_API_KEY or REMOVE_BG_API_KEY)

### Messaging Platform
- **Telegram Bot API**: Core messaging functionality (requires TELEGRAM_BOT_TOKEN)

### Python Libraries
- **Flask**: Web framework for HTTP server and dashboard
- **python-telegram-bot**: Telegram API wrapper
- **google-generativeai**: Google Gemini API client
- **google-cloud-vision**: Google Cloud Vision API client
- **Pillow (PIL)**: Image processing and manipulation
- **requests**: HTTP client for API calls

### Infrastructure
- **Replit Hosting**: Designed for deployment on Replit platform
- **Webhook URL**: External webhook endpoint for receiving Telegram updates (WEBHOOK_URL)
- **Environment Variables**: Configuration through Replit secrets or environment variables

### Web Frontend
- **Bootstrap**: UI framework with dark theme variant
- **Font Awesome**: Icon library for dashboard interface
- **CDN Dependencies**: External CSS and JavaScript libraries loaded from CDNs