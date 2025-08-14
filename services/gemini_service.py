import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable is required")
            return
            
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
    
    def is_available(self):
        """Check if Gemini service is available"""
        return self.client is not None
    
    def generate_response(self, text: str) -> str:
        """Generate response using Gemini AI"""
        if not self.client:
            return "❌ Gemini AI service is not available. Please check API key configuration."
        
        try:
            # Create a conversational prompt
            prompt = f"""You are a helpful AI assistant. Please provide a clear, informative, and friendly response to the following message:

{text}

Keep your response concise but comprehensive. Use emojis appropriately to make the conversation engaging."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                return response.text
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return "❌ I encountered an error while processing your message. Please try again later."
    
    def analyze_image(self, image_path: str) -> str:
        """Analyze image using Gemini's multimodal capabilities"""
        if not self.client:
            return "❌ Gemini AI service is not available."
        
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg",
                    ),
                    """Analyze this image in detail. Please describe:
                    1. Main subjects and objects
                    2. Setting and environment
                    3. Colors, lighting, and composition
                    4. Any text visible in the image
                    5. Overall mood or atmosphere
                    6. Notable details or interesting aspects
                    
                    Provide a comprehensive but concise analysis.""",
                ],
            )
            
            if response.text:
                return response.text
            else:
                return "I couldn't analyze this image. Please try with a different image."
                
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {e}")
            return "❌ Error analyzing image with AI. Please try again."
    
    def summarize_text(self, text: str) -> str:
        """Summarize long text content"""
        if not self.client:
            return "❌ Gemini AI service is not available."
        
        try:
            prompt = f"Please provide a clear and concise summary of the following text, highlighting the key points:\n\n{text}"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text or "Could not generate summary."
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return "❌ Error generating summary."
