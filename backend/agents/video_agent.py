"""
🎬 WonderKid Video Generation Agent
A kid-friendly video generation system using Google Veo 2.0 following dd project patterns

This system creates immersive story videos with:
- Compilation of all story scenes and images
- Age-appropriate cinematic content generation
- Visual consistency across story progression
- Optimized videos for children's stories
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
from dotenv import load_dotenv
from io import BytesIO
import logging

# Load environment variables
load_dotenv()

# Configure logging with emojis
logger = logging.getLogger(__name__)

# Google AI imports following dd project pattern
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    VIDEO_GENERATION_AVAILABLE = True
    print("✅ Google GenAI SDK available for video generation")
    logger.info("✅ Video generation system initialized with Google Veo 2.0")
except ImportError:
    VIDEO_GENERATION_AVAILABLE = False
    print("⚠️ Google GenAI SDK not available. Install with: pip install google-genai pillow")
    logger.warning("⚠️ Video generation not available - Google GenAI SDK missing")

# ============================================================================
# VIDEO GENERATION STATE MANAGEMENT
# ============================================================================

@dataclass
class VideoGenerationState:
    """Manages video generation state and history"""
    generated_videos: List[str] = field(default_factory=list)
    video_generation_in_progress: bool = False
    current_video_prompt: Optional[str] = None
    last_generated_video: Optional[str] = None
    total_videos_generated: int = 0
    story_videos_metadata: Dict[str, Dict] = field(default_factory=dict)  # story_id -> video metadata

# Global video generation state
video_state = VideoGenerationState()

def inspect_operation_object(operation, context: str = ""):
    """Helper function to thoroughly inspect operation object structure"""
    logger.info(f"🔍 {context} - Inspecting operation object...")
    logger.info(f"🔍 {context} - Operation type: {type(operation)}")
    logger.info(f"🔍 {context} - Operation dir: {dir(operation)}")
    
    # Check all attributes
    for attr in dir(operation):
        if not attr.startswith('_'):
            try:
                value = getattr(operation, attr)
                logger.info(f"🔍 {context} - {attr}: {type(value)} = {value}")
            except Exception as e:
                logger.info(f"🔍 {context} - {attr}: Error accessing - {e}")
    
    # Check if it's a protobuf object
    if hasattr(operation, 'DESCRIPTOR'):
        logger.info(f"🔍 {context} - This is a protobuf object")
        logger.info(f"🔍 {context} - Protobuf fields: {[field.name for field in operation.DESCRIPTOR.fields]}")
    
    return operation

def initialize_video_client():
    """Initialize Google GenAI client for video generation following dd project pattern"""
    if not VIDEO_GENERATION_AVAILABLE:
        return None
    
    try:
        # Handle different authentication methods
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if service_account_json:
            # For Cloud Run: service account JSON is in environment variable
            import json
            import tempfile
            
            # Create temporary file with service account JSON
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(json.loads(service_account_json), temp_file)
                temp_credentials_path = temp_file.name
            
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_credentials_path
            logger.info("🔑 Using service account from environment variable")
            
        elif credentials_path and os.path.exists(credentials_path):
            # For local development: service account file path
            logger.info(f"🔑 Using service account file: {credentials_path}")
        else:
            logger.warning("⚠️ No Google Cloud credentials found")
        
        # Use v1alpha API version for latest Veo 2.0 features like in dd project
        client = genai.Client(
            api_key=os.getenv('GOOGLE_API_KEY'),
            http_options={'api_version': 'v1alpha'}
        )
        logger.info("✅ Video generation client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Video client initialization failed: {e}")
        return None

def generate_video_from_image_seed(prompt: str, seed_image_path: str, story_id: str) -> Optional[str]:
    """Generate video using image as seed for visual consistency - following dd project pattern"""
    logger.info(f"🎬 Starting video generation with image seed for story {story_id}")
    
    client = initialize_video_client()
    if not client:
        logger.error(f"❌ Video client initialization failed for story {story_id}")
        return None
    
    if not seed_image_path:
        logger.error(f"❌ No seed image path provided for story {story_id}")
        return None
        
    if not os.path.exists(seed_image_path):
        logger.error(f"❌ Seed image file not found: {seed_image_path} for story {story_id}")
        return None
    
    try:
        logger.info(f"📸 Using seed image: {seed_image_path}")
        logger.info(f"📏 Seed image size: {os.path.getsize(seed_image_path)} bytes")
        
        # Enhanced kid-friendly prompt for cinematic quality
        enhanced_prompt = f"""
        {prompt}
        
        CRITICAL: This is a children's story video for ages 5-8.
        
        Cinematic direction: 
        - Smooth, gentle camera movements
        - Bright, colorful, kid-friendly atmosphere
        - Magical particle effects and sparkles
        - Warm, inviting lighting transitions
        - Fantasy storybook cinematography
        - 8-10 second sequence
        - Professional children's film quality
        - Maintains visual consistency with story illustrations
        - Safe, positive, uplifting content only
        - No scary or dark elements
        """
        
        logger.info(f"📝 Video prompt length: {len(enhanced_prompt)} characters")
        logger.info(f"🎯 Video prompt preview: {enhanced_prompt[:200]}...")
        
        # Read and validate image
        logger.info(f"📖 Reading seed image file...")
        with open(seed_image_path, 'rb') as f:
            image_data = f.read()
        
        logger.info(f"📊 Image data size: {len(image_data)} bytes")
        
        image = types.Image(
            image_bytes=image_data,
            mime_type="image/png"
        )
        
        config = types.GenerateVideosConfig(
            # Removed person_generation parameter - using default for kids content
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=8
        )
        
        logger.info(f"⚙️ Video config: aspect_ratio={config.aspect_ratio}, duration={config.duration_seconds}s")
        logger.info("🤖 Calling Google Veo 2.0 API for video generation...")
        
        operation = client.models.generate_videos(
            model="veo-2.0-generate-001",
            prompt=enhanced_prompt,
            image=image,
            config=config
        )
        
        logger.info(f"🎬 Video generation operation started for story {story_id}")
        logger.info(f"⏳ Operation ID: {getattr(operation, 'name', 'unknown')}")
        logger.info("⏳ Video generation in progress (2-3 minutes)...")
        video_state.video_generation_in_progress = True
        
        # Poll for completion with detailed logging
        poll_count = 0
        while not operation.done:
            poll_count += 1
            logger.info(f"⏳ Poll #{poll_count}: Video still generating... (20s intervals)")
            time.sleep(20)
            
            try:
                operation = client.operations.get(operation)
                logger.info(f"📊 Operation status: {getattr(operation, 'done', 'unknown')}")
                logger.info(f"🔍 Operation object type: {type(operation)}")
                logger.info(f"🔍 Operation attributes: {dir(operation)}")
                
                # Log operation response details
                if hasattr(operation, 'response'):
                    logger.info(f"📋 Operation response type: {type(operation.response)}")
                    logger.info(f"📋 Operation response: {operation.response}")
                    if operation.response and hasattr(operation.response, 'generated_videos'):
                        logger.info(f"🎬 Generated videos count: {len(operation.response.generated_videos) if operation.response.generated_videos else 0}")
                        if operation.response.generated_videos:
                            for i, video in enumerate(operation.response.generated_videos):
                                logger.info(f"🎬 Video {i}: {type(video)} - {dir(video)}")
                else:
                    logger.warning(f"⚠️ Operation has no response attribute")
                    
            except Exception as poll_error:
                logger.error(f"❌ Error polling operation status: {poll_error}")
                logger.error(f"🔍 Poll error type: {type(poll_error)}")
                logger.error(f"📋 Poll error details: {str(poll_error)}")
                break
        
        logger.info(f"🏁 Video generation polling completed after {poll_count} attempts")
        logger.info(f"🔍 Final operation state: done={getattr(operation, 'done', 'unknown')}")
        logger.info(f"🔍 Final operation response: {getattr(operation, 'response', 'no response')}")
        
        # Thoroughly inspect the completed operation
        operation = inspect_operation_object(operation, "Completed Video Operation")
        
        if operation.response and operation.response.generated_videos:
            logger.info(f"✅ Video generation successful! Found {len(operation.response.generated_videos)} video(s)")
            
            video = operation.response.generated_videos[0].video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wonderkid_story_video_{story_id}_{timestamp}.mp4"
            
            logger.info(f"💾 Downloading video from Google servers...")
            logger.info(f"📁 Video file: {getattr(video, 'name', 'unknown')}")
            
            try:
                video_data = client.files.download(file=video)
                logger.info(f"📊 Downloaded video data size: {len(video_data)} bytes")
                
                with open(filename, 'wb') as f:
                    f.write(video_data)
                
                # Verify file was written
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    logger.info(f"✅ Video file saved successfully: {filename} ({file_size} bytes)")
                else:
                    logger.error(f"❌ Video file was not created: {filename}")
                    return None
                
            except Exception as download_error:
                logger.error(f"❌ Error downloading video: {download_error}")
                return None
            
            # Update state
            video_state.generated_videos.append(filename)
            video_state.last_generated_video = filename
            video_state.total_videos_generated += 1
            video_state.video_generation_in_progress = False
            
            logger.info(f"🎉 Video generation completed successfully for story {story_id}")
            logger.info(f"📈 Total videos generated: {video_state.total_videos_generated}")
            
            return filename
        else:
            logger.error(f"❌ No videos in operation response for story {story_id}")
            logger.error(f"📊 Operation response: {operation.response}")
            logger.error(f"🔍 Operation response type: {type(operation.response)}")
            
            # Try to get more details about the operation
            if hasattr(operation, 'error'):
                logger.error(f"❌ Operation error: {operation.error}")
            if hasattr(operation, 'metadata'):
                logger.error(f"❌ Operation metadata: {operation.metadata}")
            if hasattr(operation, 'name'):
                logger.error(f"❌ Operation name: {operation.name}")
            
            # Try alternative response access patterns
            logger.info(f"🔍 Attempting alternative response access...")
            try:
                # Check if response is in a different attribute
                for attr in ['result', 'data', 'content', 'output']:
                    if hasattr(operation, attr):
                        logger.info(f"🔍 Found {attr}: {getattr(operation, attr)}")
                        if hasattr(getattr(operation, attr), 'generated_videos'):
                            logger.info(f"🎬 Found videos in {attr}!")
                            videos = getattr(getattr(operation, attr), 'generated_videos')
                            if videos:
                                logger.info(f"✅ Alternative video access successful! Found {len(videos)} videos")
                                # Process the video using alternative access
                                video = videos[0].video if hasattr(videos[0], 'video') else videos[0]
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"wonderkid_story_video_{story_id}_{timestamp}.mp4"
                                
                                logger.info(f"💾 Downloading video from alternative access...")
                                video_data = client.files.download(file=video)
                                logger.info(f"📊 Downloaded video data size: {len(video_data)} bytes")
                                
                                with open(filename, 'wb') as f:
                                    f.write(video_data)
                                
                                if os.path.exists(filename):
                                    file_size = os.path.getsize(filename)
                                    logger.info(f"✅ Video file saved successfully: {filename} ({file_size} bytes)")
                                    
                                    # Update state
                                    video_state.generated_videos.append(filename)
                                    video_state.last_generated_video = filename
                                    video_state.total_videos_generated += 1
                                    video_state.video_generation_in_progress = False
                                    
                                    logger.info(f"🎉 Video generation completed successfully via alternative access for story {story_id}")
                                    return filename
            except Exception as alt_error:
                logger.error(f"❌ Alternative response access failed: {alt_error}")
            
            video_state.video_generation_in_progress = False
            return None
            
    except Exception as e:
        logger.error(f"❌ Video generation failed for story {story_id}: {e}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        logger.error(f"📋 Error details: {str(e)}")
        video_state.video_generation_in_progress = False
        return None

def generate_comprehensive_story_video(
    story_scenes: List[Dict],
    story_theme: str,
    story_id: str,
    age_group: str = "5-8"
) -> Dict:
    """
    Generate comprehensive video after 10 story iterations using all context
    This follows dd project's epic video generation pattern but adapted for kids
    """
    
    logger.info(f"🎬 Starting comprehensive video generation for story {story_id}")
    logger.info(f"📊 Story details: theme='{story_theme}', age_group='{age_group}', scenes={len(story_scenes)}")
    
    if not VIDEO_GENERATION_AVAILABLE:
        error_msg = "Video generation not available - Google GenAI SDK missing"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "generated_file": None
        }
    
    client = initialize_video_client()
    if not client:
        error_msg = "Failed to initialize video generation client"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "generated_file": None
        }
    
    try:
        logger.info(f"📚 Processing {len(story_scenes)} story scenes for video compilation")
        
        # Compile complete story narrative
        full_narrative = " ".join([scene.get("text", "") for scene in story_scenes])
        all_choices = [choice for scene in story_scenes for choice in scene.get("choices", [])]
        
        logger.info(f"📝 Compiled narrative length: {len(full_narrative)} characters")
        logger.info(f"🎯 Total choices made: {len(all_choices)}")
        logger.info(f"📖 Narrative preview: {full_narrative[:200]}...")
        
        # Select best seed image (most recent or most representative)
        logger.info(f"🔍 Searching for seed image from {len(story_scenes)} scenes...")
        seed_image = None
        available_images = []
        
        for i, scene in enumerate(reversed(story_scenes)):
            image_file = scene.get("image_file")
            if image_file:
                available_images.append(image_file)
                if os.path.exists(image_file):
                    seed_image = image_file
                    logger.info(f"✅ Found valid seed image: {seed_image} (from scene {len(story_scenes) - i})")
                    break
                else:
                    logger.warning(f"⚠️ Image file referenced but not found: {image_file}")
        
        logger.info(f"📊 Available images: {len(available_images)}")
        logger.info(f"🖼️ Images found: {available_images}")
        
        if not seed_image:
            logger.warning("⚠️ No valid seed image found, attempting direct video generation")
            logger.info(f"🎬 Falling back to direct video generation for story {story_id}")
            return generate_direct_story_video(story_scenes, story_theme, story_id, age_group)
        
        # Create comprehensive video prompt with full story context
        video_prompt = f"""
        CHILDREN'S STORY VIDEO: {story_theme}
        
        Complete Story Journey (10 scenes):
        {full_narrative}
        
        Story Choices Made by the Young Reader:
        {', '.join(all_choices[:10])}
        
        Visual Requirements:
        - Compilation of all 10 story scenes in sequence
        - Smooth transitions between each story moment
        - Maintain character consistency throughout
        - Kid-friendly, bright, colorful animation
        - Storybook quality for ages {age_group}
        - Magical, whimsical atmosphere
        - Educational and inspiring content
        - 8-10 second cinematic sequence
        - Show story progression from beginning to current point
        
        CRITICAL SAFETY: 
        - Absolutely no scary, violent, or inappropriate content
        - Only positive, uplifting, educational themes
        - Safe for young children to watch
        """
        
        logger.info(f"📝 Video prompt created: {len(video_prompt)} characters")
        logger.info(f"🎯 Video prompt preview: {video_prompt[:300]}...")
        
        # Store metadata
        video_state.story_videos_metadata[story_id] = {
            "story_theme": story_theme,
            "scenes_count": len(story_scenes),
            "generation_started": datetime.now().isoformat(),
            "age_group": age_group,
            "seed_image": seed_image,
            "available_images": available_images,
            "narrative_length": len(full_narrative),
            "choices_count": len(all_choices)
        }
        
        logger.info(f"💾 Video metadata stored for story {story_id}")
        
        # Generate the video using the seed image for consistency
        logger.info(f"🎨 Using seed image: {seed_image}")
        logger.info(f"🚀 Calling generate_video_from_image_seed...")
        
        generated_file = generate_video_from_image_seed(video_prompt, seed_image, story_id)
        
        if generated_file:
            # Update metadata
            video_state.story_videos_metadata[story_id].update({
                "generated_file": generated_file,
                "generation_completed": datetime.now().isoformat(),
                "status": "success"
            })
            
            logger.info(f"✅ Comprehensive story video generated: {generated_file}")
            logger.info(f"📈 Video generation stats: {video_state.total_videos_generated} total videos")
            
            return {
                "status": "success",
                "generated_file": generated_file,
                "story_id": story_id,
                "story_theme": story_theme,
                "scenes_included": len(story_scenes),
                "video_type": "comprehensive_story",
                "age_group": age_group,
                "seed_image_used": seed_image,
                "timestamp": datetime.now().isoformat(),
                "message": "🎬 Your story video is ready! All 10 scenes combined into one magical journey!"
            }
        else:
            logger.error(f"❌ Video generation failed for story {story_id}")
            logger.error(f"📊 Seed image used: {seed_image}")
            logger.error(f"📝 Prompt length: {len(video_prompt)}")
            
            return {
                "status": "error",
                "error": "Video generation failed",
                "generated_file": None,
                "story_id": story_id
            }
            
    except Exception as e:
        error_msg = f"Comprehensive video generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        logger.error(f"📋 Error details: {str(e)}")
        logger.error(f"📊 Story context: theme='{story_theme}', scenes={len(story_scenes)}")
        
        return {
            "status": "error",
            "error": error_msg,
            "generated_file": None,
            "story_id": story_id
        }

def generate_direct_story_video(
    story_scenes: List[Dict],
    story_theme: str,
    story_id: str,
    age_group: str = "5-8"
) -> Dict:
    """Generate video directly without image seed as fallback - following dd pattern"""
    
    logger.info(f"🎬 Starting direct video generation (no seed image) for story {story_id}")
    
    client = initialize_video_client()
    if not client:
        logger.error(f"❌ Video client not available for story {story_id}")
        return {
            "status": "error",
            "error": "Video client not available",
            "generated_file": None
        }
    
    try:
        logger.info(f"📚 Processing {len(story_scenes)} story scenes for direct video generation")
        
        # Compile story narrative
        full_narrative = " ".join([scene.get("text", "") for scene in story_scenes[:10]])
        logger.info(f"📝 Compiled narrative length: {len(full_narrative)} characters")
        logger.info(f"📖 Narrative preview: {full_narrative[:200]}...")
        
        enhanced_prompt = f"""
        CHILDREN'S ANIMATED STORY: {story_theme}
        
        Story Content (10 magical scenes):
        {full_narrative}
        
        Animation Style:
        - Colorful children's book illustration come to life
        - Pixar-quality kid-friendly animation
        - Bright, vibrant colors with warm lighting
        - Cute, friendly characters
        - Magical storybook atmosphere
        - Smooth scene transitions
        - Age-appropriate for {age_group}
        - Educational and fun
        - 8-10 second sequence showing story highlights
        
        SAFETY: Kid-friendly content only, no scary elements
        """
        
        logger.info(f"📝 Direct video prompt created: {len(enhanced_prompt)} characters")
        logger.info(f"🎯 Prompt preview: {enhanced_prompt[:300]}...")
        
        config = types.GenerateVideosConfig(
            # Removed person_generation parameter - using default for kids content  
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=8
        )
        
        logger.info(f"⚙️ Direct video config: aspect_ratio={config.aspect_ratio}, duration={config.duration_seconds}s")
        logger.info("🤖 Calling Google Veo 2.0 for direct video generation...")
        
        # Generate video without image seed
        operation = client.models.generate_videos(
            model="veo-2.0-generate-001",
            prompt=enhanced_prompt,
            config=config
        )
        
        logger.info(f"🎬 Direct video generation operation started for story {story_id}")
        logger.info(f"⏳ Operation ID: {getattr(operation, 'name', 'unknown')}")
        logger.info("⏳ Direct video generation in progress (2-3 minutes)...")
        video_state.video_generation_in_progress = True
        
        # Poll for completion with detailed logging
        poll_count = 0
        while not operation.done:
            poll_count += 1
            logger.info(f"⏳ Direct video poll #{poll_count}: Still generating... (20s intervals)")
            time.sleep(20)
            
            try:
                operation = client.operations.get(operation)
                logger.info(f"📊 Direct video operation status: {getattr(operation, 'done', 'unknown')}")
                logger.info(f"🔍 Direct operation object type: {type(operation)}")
                logger.info(f"🔍 Direct operation attributes: {dir(operation)}")
                
                # Log operation response details
                if hasattr(operation, 'response'):
                    logger.info(f"📋 Direct operation response type: {type(operation.response)}")
                    logger.info(f"📋 Direct operation response: {operation.response}")
                    if operation.response and hasattr(operation.response, 'generated_videos'):
                        logger.info(f"🎬 Direct generated videos count: {len(operation.response.generated_videos) if operation.response.generated_videos else 0}")
                        if operation.response.generated_videos:
                            for i, video in enumerate(operation.response.generated_videos):
                                logger.info(f"🎬 Direct video {i}: {type(video)} - {dir(video)}")
                else:
                    logger.warning(f"⚠️ Direct operation has no response attribute")
                    
            except Exception as poll_error:
                logger.error(f"❌ Error polling direct video operation: {poll_error}")
                logger.error(f"🔍 Direct poll error type: {type(poll_error)}")
                logger.error(f"📋 Direct poll error details: {str(poll_error)}")
                break
        
        logger.info(f"🏁 Direct video generation polling completed after {poll_count} attempts")
        logger.info(f"🔍 Final direct operation state: done={getattr(operation, 'done', 'unknown')}")
        logger.info(f"🔍 Final direct operation response: {getattr(operation, 'response', 'no response')}")
        
        # Thoroughly inspect the completed direct operation
        operation = inspect_operation_object(operation, "Completed Direct Video Operation")
        
        if operation.response and operation.response.generated_videos:
            logger.info(f"✅ Direct video generation successful! Found {len(operation.response.generated_videos)} video(s)")
            
            video = operation.response.generated_videos[0].video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wonderkid_direct_video_{story_id}_{timestamp}.mp4"
            
            logger.info(f"💾 Downloading direct video from Google servers...")
            logger.info(f"📁 Video file: {getattr(video, 'name', 'unknown')}")
            
            try:
                video_data = client.files.download(file=video)
                logger.info(f"📊 Downloaded direct video data size: {len(video_data)} bytes")
                
                with open(filename, 'wb') as f:
                    f.write(video_data)
                
                # Verify file was written
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    logger.info(f"✅ Direct video file saved successfully: {filename} ({file_size} bytes)")
                else:
                    logger.error(f"❌ Direct video file was not created: {filename}")
                    return {
                        "status": "error",
                        "error": "Video file creation failed",
                        "generated_file": None
                    }
                
            except Exception as download_error:
                logger.error(f"❌ Error downloading direct video: {download_error}")
                return {
                    "status": "error",
                    "error": f"Video download failed: {download_error}",
                    "generated_file": None
                }
            
            video_state.generated_videos.append(filename)
            video_state.last_generated_video = filename
            video_state.video_generation_in_progress = False
            
            logger.info(f"✅ Direct story video saved: {filename}")
            logger.info(f"📈 Total videos generated: {video_state.total_videos_generated}")
            
            return {
                "status": "success",
                "generated_file": filename,
                "story_id": story_id,
                "video_type": "direct_generation",
                "message": "🎬 Story video created without seed image!"
            }
        else:
            logger.error(f"❌ No videos in direct video operation response for story {story_id}")
            logger.error(f"📊 Operation response: {operation.response}")
            logger.error(f"🔍 Operation response type: {type(operation.response)}")
            
            # Try to get more details about the operation
            if hasattr(operation, 'error'):
                logger.error(f"❌ Direct operation error: {operation.error}")
            if hasattr(operation, 'metadata'):
                logger.error(f"❌ Direct operation metadata: {operation.metadata}")
            if hasattr(operation, 'name'):
                logger.error(f"❌ Direct operation name: {operation.name}")
            
            # Try alternative response access patterns
            logger.info(f"🔍 Attempting alternative response access for direct video...")
            try:
                # Check if response is in a different attribute
                for attr in ['result', 'data', 'content', 'output']:
                    if hasattr(operation, attr):
                        logger.info(f"🔍 Found direct {attr}: {getattr(operation, attr)}")
                        if hasattr(getattr(operation, attr), 'generated_videos'):
                            logger.info(f"🎬 Found direct videos in {attr}!")
                            videos = getattr(getattr(operation, attr), 'generated_videos')
                            if videos:
                                logger.info(f"✅ Alternative direct video access successful! Found {len(videos)} videos")
                                # Process the video using alternative access
                                video = videos[0].video if hasattr(videos[0], 'video') else videos[0]
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"wonderkid_direct_video_{story_id}_{timestamp}.mp4"
                                
                                logger.info(f"💾 Downloading direct video from alternative access...")
                                video_data = client.files.download(file=video)
                                logger.info(f"📊 Downloaded direct video data size: {len(video_data)} bytes")
                                
                                with open(filename, 'wb') as f:
                                    f.write(video_data)
                                
                                if os.path.exists(filename):
                                    file_size = os.path.getsize(filename)
                                    logger.info(f"✅ Direct video file saved successfully: {filename} ({file_size} bytes)")
                                    
                                    video_state.generated_videos.append(filename)
                                    video_state.last_generated_video = filename
                                    video_state.video_generation_in_progress = False
                                    
                                    logger.info(f"🎉 Direct video generation completed successfully via alternative access for story {story_id}")
                                    return {
                                        "status": "success",
                                        "generated_file": filename,
                                        "story_id": story_id,
                                        "video_type": "direct_generation_alternative",
                                        "message": "🎬 Story video created via alternative access!"
                                    }
            except Exception as alt_error:
                logger.error(f"❌ Alternative direct response access failed: {alt_error}")
            
            video_state.video_generation_in_progress = False
            return {
                "status": "error",
                "error": "No video generated in response",
                "generated_file": None
            }
            
    except Exception as e:
        logger.error(f"❌ Direct video generation failed for story {story_id}: {e}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        logger.error(f"📋 Error details: {str(e)}")
        video_state.video_generation_in_progress = False
        return {
            "status": "error",
            "error": str(e),
            "generated_file": None
        }

def get_video_generation_status() -> Dict:
    """Get current video generation status and statistics"""
    return {
        "video_generation_available": VIDEO_GENERATION_AVAILABLE,
        "generation_in_progress": video_state.video_generation_in_progress,
        "total_videos_generated": video_state.total_videos_generated,
        "last_generated_video": video_state.last_generated_video,
        "generated_videos": video_state.generated_videos[-5:],  # Last 5 videos
        "story_videos": len(video_state.story_videos_metadata),
        "current_prompt": video_state.current_video_prompt[:100] if video_state.current_video_prompt else None,
        "status": "generating" if video_state.video_generation_in_progress else "ready"
    }

def clear_video_generation_state():
    """Clear video generation state for new story"""
    global video_state
    video_state = VideoGenerationState()
    logger.info("🧹 Video generation state cleared for new story")
    return {"status": "cleared", "message": "Video generation state reset"}
