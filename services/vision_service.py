import os
import logging
from google.cloud import vision
from google.cloud.vision_v1 import types as vision_types

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_VISION_API_KEY")
        self.client = None
        
        if not self.api_key:
            logger.error("GOOGLE_VISION_API_KEY environment variable is required")
            return
        
        try:
            # Use API key directly with client options
            from google.api_core.client_options import ClientOptions
            client_options = ClientOptions(api_key=self.api_key)
            self.client = vision.ImageAnnotatorClient(client_options=client_options)
            logger.info("Google Vision service initialized successfully with API key")
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision service: {e}")
    
    def is_available(self):
        """Check if Vision service is available"""
        return self.client is not None
    
    def analyze_image(self, image_path: str) -> str:
        """Analyze image using Google Vision API"""
        if not self.client:
            return "❌ Google Vision service is not available. Please check API configuration."
        
        try:
            with open(image_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Detect labels, text, objects, faces, and landmarks
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION, max_results=5),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.FACE_DETECTION, max_results=5),
                vision.Feature(type_=vision.Feature.Type.LANDMARK_DETECTION, max_results=5),
                vision.Feature(type_=vision.Feature.Type.LOGO_DETECTION, max_results=5),
                vision.Feature(type_=vision.Feature.Type.SAFE_SEARCH_DETECTION),
            ]
            
            request = vision.AnnotateImageRequest(image=image, features=features)
            response = self.client.annotate_image(request=request)
            
            if response.error.message:
                logger.error(f"Vision API error: {response.error.message}")
                return f"❌ Vision API error: {response.error.message}"
            
            # Process results
            analysis_parts = []
            
            # Labels
            if response.label_annotations:
                labels = [f"{label.description} ({label.score:.2f})" for label in response.label_annotations[:5]]
                analysis_parts.append(f"🏷️ **Labels:** {', '.join(labels)}")
            
            # Text detection
            if response.text_annotations:
                text_content = response.text_annotations[0].description.strip()
                if text_content:
                    # Limit text to first 200 characters
                    if len(text_content) > 200:
                        text_content = text_content[:200] + "..."
                    analysis_parts.append(f"📝 **Text found:** {text_content}")
            
            # Objects
            if response.localized_object_annotations:
                objects = [f"{obj.name} ({obj.score:.2f})" for obj in response.localized_object_annotations[:3]]
                analysis_parts.append(f"🎯 **Objects:** {', '.join(objects)}")
            
            # Faces
            if response.face_annotations:
                face_count = len(response.face_annotations)
                analysis_parts.append(f"👥 **Faces detected:** {face_count}")
            
            # Landmarks
            if response.landmark_annotations:
                landmarks = [landmark.description for landmark in response.landmark_annotations[:3]]
                analysis_parts.append(f"🏛️ **Landmarks:** {', '.join(landmarks)}")
            
            # Logos
            if response.logo_annotations:
                logos = [logo.description for logo in response.logo_annotations[:3]]
                analysis_parts.append(f"🏢 **Logos:** {', '.join(logos)}")
            
            # Safe search
            if response.safe_search_annotation:
                safe_search = response.safe_search_annotation
                safety_levels = {
                    1: "Very unlikely",
                    2: "Unlikely", 
                    3: "Possible",
                    4: "Likely",
                    5: "Very likely"
                }
                
                safety_info = []
                if safe_search.adult >= 3:
                    safety_info.append(f"Adult: {safety_levels.get(safe_search.adult, 'Unknown')}")
                if safe_search.violence >= 3:
                    safety_info.append(f"Violence: {safety_levels.get(safe_search.violence, 'Unknown')}")
                
                if safety_info:
                    analysis_parts.append(f"⚠️ **Safety:** {', '.join(safety_info)}")
            
            if analysis_parts:
                return "\n".join(analysis_parts)
            else:
                return "No significant features detected in this image."
                
        except Exception as e:
            logger.error(f"Error analyzing image with Vision API: {e}")
            return "❌ Error analyzing image. Please try again."
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        if not self.client:
            return "❌ Google Vision service is not available."
        
        try:
            with open(image_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            request = vision.AnnotateImageRequest(
                image=image,
                features=[vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)]
            )
            response = self.client.annotate_image(request=request)
            
            if response.error.message:
                return f"❌ OCR error: {response.error.message}"
            
            if response.text_annotations:
                return response.text_annotations[0].description
            else:
                return "No text found in image."
                
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return "❌ Error extracting text from image."
