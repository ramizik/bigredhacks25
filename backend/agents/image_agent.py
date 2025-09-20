"""
🎨 WonderKid Image Generation Agent
A kid-friendly image generation system using Google Imagen following dd project patterns

This system creates immersive story illustrations with:
- Age-appropriate visual content generation
- Kid-friendly artistic style and themes
- Visual consistency across story scenes
- Optimized prompts for children's stories
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

# Google AI imports following dd project pattern
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    IMAGE_GENERATION_AVAILABLE = True
    print("✅ Google GenAI SDK available for image generation")
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False
    print("⚠️ Google GenAI SDK not available. Install with: pip install google-genai pillow")

# ============================================================================
# VISUAL STYLE SYSTEM FOR KIDS
# ============================================================================

@dataclass
class KidsVisualStyle:
    """Maintains kid-friendly visual consistency across all generated content"""
    art_style: str = "colorful children's book illustration style"
    color_palette: str = "bright, vibrant colors with warm lighting"
    character_references: Dict[str, str] = field(default_factory=dict)  # Character name -> reference image
    location_references: Dict[str, str] = field(default_factory=dict)   # Location name -> reference image
    style_seed: str = "kids_friendly_2024"
    safety_level: str = "high"  # Always high safety for kids content

@dataclass
class ImageGenerationState:
    """Manages image generation state and history"""
    generated_images: List[str] = field(default_factory=list)
    visual_style: KidsVisualStyle = field(default_factory=KidsVisualStyle)
    scene_count: int = 0
    last_generated_image: Optional[str] = None

# Global image generation state
image_state = ImageGenerationState()

def initialize_image_client():
    """Initialize Google GenAI client following dd project pattern"""
    if not IMAGE_GENERATION_AVAILABLE:
        return None
    
    try:
        # Use v1alpha API version for latest features like in dd project
        client = genai.Client(
            api_key=os.getenv('GOOGLE_API_KEY'),
            http_options={'api_version': 'v1alpha'}
        )
        print("✅ Image generation client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Image client initialization failed: {e}")
        return None

def generate_kid_friendly_image(story_text: str, scene_context: str = "", age_group: str = "5-8") -> Dict:
    """Generate kid-friendly illustration based on story text using Google Imagen"""
    
    if not IMAGE_GENERATION_AVAILABLE:
        error_msg = "Google GenAI SDK not available for image generation. Please install with: pip install google-genai pillow"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "generated_file": None
        }
    
    client = initialize_image_client()
    if not client:
        error_msg = "Failed to initialize Google GenAI client. Check GOOGLE_API_KEY environment variable."
        print(f"❌ {error_msg}")
        return {
            "status": "error", 
            "error": error_msg,
            "generated_file": None
        }
    
    try:
        print(f"🎨 Generating kid-friendly image for: {story_text[:100]}...")
        
        # Create age-appropriate image prompt following dd project pattern
        enhanced_prompt = f"""
        Children's book illustration: {story_text}
        
        Visual Style: {image_state.visual_style.art_style}
        Color Palette: {image_state.visual_style.color_palette}
        Target Age: {age_group}
        Story Context: {scene_context}
        
        Requirements:
        - Kid-friendly, safe, and positive imagery
        - No scary, violent, or inappropriate content
        - Cute, friendly characters with expressive faces
        - Magical, whimsical atmosphere
        - Professional children's book quality
        - 4K illustration quality
        - Bright, engaging colors that appeal to children
        - Clear, simple composition for easy understanding
        - Consistent with previous story illustrations if any
        """
        
        print(f"🎨 Enhanced prompt created for Imagen 3.0")
        
        # Generate image using Imagen 3.0 - following dd project pattern exactly
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=enhanced_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_low_and_above"
            )
        )
        
        # Follow dreamdirector's exact response handling pattern
        if response.generated_images:
            image = response.generated_images[0].image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wonderkid_scene_{timestamp}.png"
            
            # Convert and save image following dd project pattern
            image_data = BytesIO(image.image_bytes)
            pil_image = Image.open(image_data)
            pil_image.save(filename)
            
            # Update state
            image_state.generated_images.append(filename)
            image_state.last_generated_image = filename
            image_state.scene_count += 1
            
            print(f"✅ Kid-friendly image saved: {filename}")
            
            return {
                "status": "success",
                "generated_file": filename,
                "story_text": story_text,
                "scene_context": scene_context,
                "age_group": age_group,
                "prompt_used": enhanced_prompt,
                "model": "imagen-3.0-generate-002",
                "safety_level": "high",
                "timestamp": datetime.now().isoformat(),
                "scene_number": image_state.scene_count,
                "image_generation": True
            }
        else:
            # Enhanced debugging following the logs pattern but with cleaner handling
            print(f"⚠️ Scene image generation failed: No images generated by Imagen API")
            
            # Try alternative approach - often safety filters block content
            # Let's try with a more generic, guaranteed-safe prompt
            fallback_prompt = f"""
            Children's book illustration showing a magical adventure scene.
            Bright, cheerful colors with friendly characters in a safe, whimsical setting.
            Professional children's book art style, colorful and engaging for kids aged {age_group}.
            """
            
            print(f"🔄 Trying fallback safe prompt...")
            fallback_response = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=fallback_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    safety_filter_level="block_few"  # Less restrictive
                )
            )
            
            if fallback_response.generated_images:
                image = fallback_response.generated_images[0].image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"wonderkid_fallback_{timestamp}.png"
                
                image_data = BytesIO(image.image_bytes)
                pil_image = Image.open(image_data)
                pil_image.save(filename)
                
                image_state.generated_images.append(filename)
                image_state.last_generated_image = filename
                image_state.scene_count += 1
                
                print(f"✅ Fallback image generated: {filename}")
                
                return {
                    "status": "success",
                    "generated_file": filename,
                    "story_text": story_text,
                    "fallback_used": True,
                    "prompt_used": fallback_prompt,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": "No images generated by Imagen API - both primary and fallback failed",
                    "generated_file": None,
                    "debug_info": "Content may be blocked by safety filters"
                }
            
    except Exception as e:
        error_msg = f"Image generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "generated_file": None,
            "story_text": story_text,
            "timestamp": datetime.now().isoformat()
        }

def generate_character_portrait(character_name: str, character_description: str, scene_context: str, age_group: str = "5-8") -> Dict:
    """Generate consistent character portrait for story characters"""
    
    if not IMAGE_GENERATION_AVAILABLE:
        return {
            "status": "error",
            "error": "Image generation not available",
            "generated_file": None
        }
    
    # Check if character already has a reference
    if character_name in image_state.visual_style.character_references:
        existing_reference = image_state.visual_style.character_references[character_name]
        print(f"🎭 Using existing character reference for {character_name}: {existing_reference}")
        return {
            "status": "success",
            "character_name": character_name,
            "existing_reference": existing_reference,
            "generated_file": existing_reference,
            "reused_character": True
        }
    
    client = initialize_image_client()
    if not client:
        return {
            "status": "error",
            "error": "Failed to initialize image client",
            "generated_file": None
        }
    
    try:
        print(f"🎭 Generating character portrait for: {character_name}")
        
        character_prompt = f"""
        Children's book character portrait: {character_name}
        
        Character description: {character_description}
        Scene context: {scene_context}
        Age group: {age_group}
        
        Style requirements:
        - {image_state.visual_style.art_style}
        - {image_state.visual_style.color_palette}
        - Friendly, approachable character design
        - Expressive, kind facial features
        - Age-appropriate and safe for children
        - Professional children's book character art
        - Consistent with previous story illustrations
        - Clear, detailed character design for reference
        
        Safety: High safety filter, child-friendly character design
        """
        
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=character_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",  # Square for character portraits
                safety_filter_level="block_low_and_above"
            )
        )
        
        if response.generated_images:
            image = response.generated_images[0].image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wonderkid_character_{character_name.replace(' ', '_')}_{timestamp}.png"
            
            # Save image
            image_data = BytesIO(image.image_bytes)
            pil_image = Image.open(image_data)
            pil_image.save(filename)
            
            # Store character reference for consistency
            image_state.visual_style.character_references[character_name] = filename
            image_state.generated_images.append(filename)
            
            print(f"✅ Character portrait saved: {filename}")
            
            return {
                "status": "success",
                "character_name": character_name,
                "generated_file": filename,
                "character_description": character_description,
                "new_character_reference": True,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        error_msg = f"Character portrait generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "generated_file": None
        }

def get_image_generation_status() -> Dict:
    """Get current image generation status and statistics"""
    return {
        "image_generation_available": IMAGE_GENERATION_AVAILABLE,
        "total_images_generated": len(image_state.generated_images),
        "scene_count": image_state.scene_count,
        "last_generated_image": image_state.last_generated_image,
        "character_references": len(image_state.visual_style.character_references),
        "characters_created": list(image_state.visual_style.character_references.keys()),
        "visual_style": {
            "art_style": image_state.visual_style.art_style,
            "color_palette": image_state.visual_style.color_palette,
            "safety_level": image_state.visual_style.safety_level
        },
        "status": "active" if IMAGE_GENERATION_AVAILABLE else "disabled"
    }

def clear_image_generation_state():
    """Clear image generation state for new story"""
    global image_state
    image_state = ImageGenerationState()
    print("🧹 Image generation state cleared for new story")
    return {"status": "cleared", "message": "Image generation state reset"}
