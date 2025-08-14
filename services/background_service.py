import os
import logging
import requests
from PIL import Image
import io

logger = logging.getLogger(__name__)

class BackgroundService:
    def __init__(self):
        self.api_key = os.environ.get("BACKGROUNDBG_API_KEY", os.environ.get("REMOVE_BG_API_KEY"))
        self.api_url = "https://api.remove.bg/v1.0/removebg"
        
        if not self.api_key:
            logger.error("BACKGROUNDBG_API_KEY or REMOVE_BG_API_KEY environment variable is required")
    
    def is_available(self):
        """Check if background removal service is available"""
        return self.api_key is not None
    
    def remove_background(self, image_path: str) -> str:
        """Remove background from image using Background.bg API"""
        if not self.api_key:
            raise Exception("Background removal service is not available. Please check API key configuration.")
        
        try:
            # Read and validate image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Check file size (API usually has limits around 12MB)
            if len(image_data) > 12 * 1024 * 1024:  # 12MB
                # Compress image if too large
                image_data = self._compress_image(image_data)
            
            # Prepare API request
            headers = {
                'X-Api-Key': self.api_key,
            }
            
            files = {
                'image_file': ('image.jpg', image_data, 'image/jpeg'),
            }
            
            data = {
                'size': 'auto',  # or 'preview', 'full'
                'format': 'png'  # PNG supports transparency
            }
            
            # Make API request
            logger.info("Sending request to background removal API...")
            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Save processed image
                processed_path = f"processed_{os.path.basename(image_path)}.png"
                with open(processed_path, 'wb') as output_file:
                    output_file.write(response.content)
                
                logger.info(f"Background removed successfully, saved as {processed_path}")
                return processed_path
            
            else:
                error_msg = f"API error {response.status_code}"
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        error_msg = error_data['errors'][0].get('title', error_msg)
                except:
                    pass
                
                logger.error(f"Background removal failed: {error_msg}")
                raise Exception(f"Background removal failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            logger.error("Background removal API timeout")
            raise Exception("Background removal service timed out. Please try again.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Background removal API request error: {e}")
            raise Exception("Background removal service is temporarily unavailable.")
            
        except Exception as e:
            logger.error(f"Background removal error: {e}")
            raise Exception(f"Background removal failed: {str(e)}")
    
    def _compress_image(self, image_data: bytes, max_size: int = 10 * 1024 * 1024) -> bytes:
        """Compress image to reduce file size"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Calculate new size (maintain aspect ratio)
            width, height = image.size
            if width > 2048 or height > 2048:
                # Resize if too large
                ratio = min(2048/width, 2048/height)
                new_size = (int(width * ratio), int(height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Compress and save to bytes
            output = io.BytesIO()
            quality = 85
            
            while quality > 10:
                output.seek(0)
                output.truncate()
                image.save(output, format='JPEG', quality=quality, optimize=True)
                
                if output.tell() <= max_size:
                    break
                    
                quality -= 10
            
            compressed_data = output.getvalue()
            logger.info(f"Image compressed from {len(image_data)} to {len(compressed_data)} bytes")
            return compressed_data
            
        except Exception as e:
            logger.error(f"Image compression error: {e}")
            return image_data  # Return original if compression fails
    
    def get_account_info(self):
        """Get account information from Background.bg API"""
        if not self.api_key:
            return None
        
        try:
            headers = {'X-Api-Key': self.api_key}
            response = requests.get(
                "https://api.remove.bg/v1.0/account",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get account info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
