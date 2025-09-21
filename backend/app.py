from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import logging
import os
import sys
import glob
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import asyncio
import threading

# Add the agents directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

# Import reading agent
try:
    from agents.reading_agent import (
        generate_kid_story,
        continue_story_with_choice,
        get_story_status,
        story_state,
        generate_story_video_async,
        reset_story_state
    )
    AGENT_AVAILABLE = True
    print("✅ Reading agent loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not import reading agent: {e}")
    AGENT_AVAILABLE = False

# Import image agent
try:
    from agents.image_agent import (
        generate_kid_friendly_image,
        get_image_generation_status,
        clear_image_generation_state
    )
    IMAGE_AGENT_AVAILABLE = True
    print("✅ Image agent loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not import image agent: {e}")
    IMAGE_AGENT_AVAILABLE = False

# Import video agent
try:
    from agents.video_agent import (
        generate_comprehensive_story_video,
        get_video_generation_status,
        clear_video_generation_state,
        VIDEO_GENERATION_AVAILABLE
    )
    VIDEO_AGENT_AVAILABLE = True
    print("✅ Video agent loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not import video agent: {e}")
    VIDEO_AGENT_AVAILABLE = False
    VIDEO_GENERATION_AVAILABLE = False

# Configure comprehensive logging with emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('wonderkid_startup.log')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# COMPREHENSIVE COLD START LOGGING
# ============================================================================

def log_environment_variables():
    """Log all environment variables for debugging (excluding sensitive data)"""
    logger.info("🔧 Environment Variables Check")
    logger.info("=" * 50)
    
    # Critical environment variables
    critical_vars = [
        'GOOGLE_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS', 
        'GOOGLE_SERVICE_ACCOUNT_JSON',
        'MONGODB_URI',
        'PORT',
        'HOST'
    ]
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'CREDENTIALS' in var or 'URI' in var:
                # Mask sensitive values
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                logger.info(f"✅ {var}: {masked_value}")
            else:
                logger.info(f"✅ {var}: {value}")
        else:
            logger.warning(f"⚠️ {var}: NOT SET")
    
    # Optional environment variables
    optional_vars = [
        'NODE_ENV',
        'PYTHONPATH',
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_APPLICATION_CREDENTIALS_PATH'
    ]
    
    logger.info("📋 Optional Environment Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {value}")
        else:
            logger.info(f"⚪ {var}: not set (optional)")

def test_google_ai_connection():
    """Test Google AI services connection"""
    logger.info("🤖 Testing Google AI Services Connection")
    logger.info("=" * 50)
    
    try:
        # Test Gemini API
        from google import genai
        from google.genai import types
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.error("❌ GOOGLE_API_KEY not found")
            return False
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        logger.info("✅ Google GenAI client initialized")
        
        # Test basic API call
        try:
            # Simple test request
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Hello, this is a test"
            )
            logger.info("✅ Gemini API connection successful")
            return True
        except Exception as api_error:
            logger.error(f"❌ Gemini API test failed: {api_error}")
            return False
            
    except ImportError as import_error:
        logger.error(f"❌ Google GenAI SDK not available: {import_error}")
        return False
    except Exception as e:
        logger.error(f"❌ Google AI connection test failed: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    logger.info("🍃 Testing MongoDB Connection")
    logger.info("=" * 50)
    
    try:
        from pymongo import MongoClient
        import urllib.parse
        
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            logger.error("❌ MONGODB_URI not found")
            return False
        
        # Parse URI to mask password
        parsed_uri = urllib.parse.urlparse(mongodb_uri)
        masked_uri = f"{parsed_uri.scheme}://{parsed_uri.netloc.split('@')[0]}@***"
        logger.info(f"🔗 Connecting to MongoDB: {masked_uri}")
        
        # Test connection
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        
        # Test database access
        db = client.get_default_database()
        collections = db.list_collection_names()
        logger.info(f"📊 Available collections: {collections}")
        
        client.close()
        return True
        
    except ImportError:
        logger.error("❌ PyMongo not available")
        return False
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

def test_video_generation_setup():
    """Test video generation setup"""
    logger.info("🎬 Testing Video Generation Setup")
    logger.info("=" * 50)
    
    try:
        from agents.video_agent import (
            VIDEO_GENERATION_AVAILABLE,
            initialize_video_client,
            get_video_generation_status
        )
        
        if not VIDEO_GENERATION_AVAILABLE:
            logger.error("❌ Video generation not available - missing dependencies")
            return False
        
        logger.info("✅ Video generation dependencies available")
        
        # Test client initialization
        client = initialize_video_client()
        if client:
            logger.info("✅ Video generation client initialized")
        else:
            logger.warning("⚠️ Video generation client initialization failed")
        
        # Get status
        status = get_video_generation_status()
        logger.info(f"📊 Video generation status: {status}")
        
        return client is not None
        
    except Exception as e:
        logger.error(f"❌ Video generation setup test failed: {e}")
        return False

def comprehensive_startup_check():
    """Run comprehensive startup checks for all services"""
    logger.info("🚀 WonderKid API Cold Start Initialization")
    logger.info("=" * 60)
    logger.info(f"⏰ Startup time: {datetime.now().isoformat()}")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    # Check environment variables
    log_environment_variables()
    logger.info("")
    
    # Test service connections
    services_status = {
        "Google AI": test_google_ai_connection(),
        "MongoDB": test_mongodb_connection(), 
        "Video Generation": test_video_generation_setup()
    }
    
    logger.info("📊 Service Connection Summary")
    logger.info("=" * 50)
    for service, status in services_status.items():
        if status:
            logger.info(f"✅ {service}: Connected")
        else:
            logger.error(f"❌ {service}: Failed")
    
    # Overall health
    all_services_healthy = all(services_status.values())
    if all_services_healthy:
        logger.info("🎉 All services are healthy and ready!")
    else:
        logger.warning("⚠️ Some services are not available - check logs above")
    
    logger.info("=" * 60)
    return all_services_healthy

# Run comprehensive startup check
startup_health = comprehensive_startup_check()

app = FastAPI(
    title="WonderKid Reading Game API",
    description="📚 AI-Powered Interactive Reading Experience for Kids with Video Generation",
    version="2.0.0"
)

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Run additional checks on server startup"""
    logger.info("🚀 FastAPI server starting up...")
    logger.info(f"📊 Startup health status: {'✅ Healthy' if startup_health else '❌ Issues detected'}")
    
    if not startup_health:
        logger.warning("⚠️ Server starting with degraded functionality - check startup logs")
    
    logger.info("🎉 WonderKid API server is ready to accept requests!")

# Shutdown event handler  
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    logger.info("🛑 WonderKid API server shutting down...")
    logger.info("🧹 Cleaning up resources...")
    logger.info("👋 Goodbye!")

# CORS middleware for React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://*.expo.dev",  # Expo development
        "exp://192.168.*",     # Expo local network
        "exp://localhost:*",   # Expo localhost
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class StoryThemeRequest(BaseModel):
    theme: str
    age_group: str = "5-8"
    reading_level: str = "beginner"

class StoryChoiceRequest(BaseModel):
    choice: str
    story_id: str
    current_paragraph: int

class StoryResponse(BaseModel):
    story_id: str
    paragraphs: List[str]
    current_paragraph: int
    choices: Optional[List[str]] = None
    illustration_prompt: str = ""
    mood: str = "adventure"
    is_complete: bool = False
    progress_percentage: float = 0.0
    image_url: Optional[str] = None
    image_generated: bool = False
    scene_count: int = 0
    video_trigger: Optional[Dict] = None

class VideoGenerationRequest(BaseModel):
    story_id: str
    manual_trigger: bool = False

class VideoStatusResponse(BaseModel):
    status: str
    generation_in_progress: bool
    video_url: Optional[str] = None
    scenes_included: int = 0
    message: str = ""
    gcs_url: Optional[str] = None  # Direct GCS URL for video persistence

class UserProgressRequest(BaseModel):
    user_id: str
    story_id: str
    completed_paragraphs: int
    total_paragraphs: int
    reading_time: int  # in seconds

class UserProgressResponse(BaseModel):
    user_id: str
    stories_read: int
    total_reading_time: int
    current_streak: int
    achievements: List[Dict[str, Any]]
    level: int

# User progress tracking (will be replaced with MongoDB)
USER_PROGRESS = {}

# Background video generation tracking
VIDEO_GENERATION_TASKS = {}

def trigger_background_video_generation(story_id: str):
    """Trigger video generation in background thread"""
    def generate_video():
        try:
            # Handle empty story_id by using current story ID or generating one
            actual_story_id = story_id
            if not story_id or story_id == "":
                if AGENT_AVAILABLE:
                    try:
                        story_status = get_story_status()
                        actual_story_id = story_status.get('story_id', '')
                        if not actual_story_id:
                            actual_story_id = "current_story"
                        logger.info(f"⚠️ Empty story_id provided, using: {actual_story_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to get story status in background generation: {e}")
                        actual_story_id = "current_story"
                else:
                    actual_story_id = "current_story"

            logger.info(f"🎬 === BACKGROUND VIDEO GENERATION START ===")
            logger.info(f"🎬 Story ID: {actual_story_id}")

            # Get story context for logging
            if AGENT_AVAILABLE:
                try:
                    story_status = get_story_status()
                    logger.info(f"📊 Current story state: {story_status}")
                    logger.info(f"📚 Story context: scenes={story_status.get('scene_count', 0)}, images={story_status.get('images_generated', 0)}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not get story status for logging: {e}")
            else:
                logger.info(f"📊 Reading agent not available, skipping story state logging")
            
            result = generate_story_video_async()
            
            # Ensure story_id is included in the result
            result['requested_story_id'] = actual_story_id
            
            # Check if video was uploaded to GCS and add the URL
            if result.get("status") == "success" and result.get("generated_file"):
                try:
                    from gcs_helper import get_gcs_manager
                    gcs = get_gcs_manager()
                    gcs_url = gcs.get_video_url(result["generated_file"])
                    if gcs_url:
                        result['gcs_url'] = gcs_url
                        logger.info(f"☁️ Video available on GCS: {gcs_url}")
                except Exception as e:
                    logger.error(f"❌ Failed to get GCS URL: {str(e)}")
            
            VIDEO_GENERATION_TASKS[actual_story_id] = result
            
            # Also store by the actual story_id from the result (might be different format)
            if result.get('story_id') and result['story_id'] != actual_story_id:
                logger.info(f"🔄 Also mapping video to story_id: {result['story_id']}")
                VIDEO_GENERATION_TASKS[result['story_id']] = result
            
            if result.get("status") == "success":
                logger.info(f"✅ Background video generation completed successfully")
                logger.info(f"📁 Generated file: {result}")
                logger.info(f"📊 Updated task mappings: {list(VIDEO_GENERATION_TASKS.keys())}")
            else:
                logger.error(f"❌ Background video generation failed: {result.get('error', 'unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Background video generation exception for {story_id}: {e}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            logger.error(f"📋 Exception details: {str(e)}")
            VIDEO_GENERATION_TASKS[story_id] = {
                "status": "error",
                "error": str(e),
                "exception_type": type(e).__name__
            }
    
    # Start video generation in background thread
    logger.info(f"🚀 === TRIGGERING VIDEO GENERATION ===")
    logger.info(f"🚀 Story ID: {story_id}")
    logger.info(f"🚀 Current tasks: {list(VIDEO_GENERATION_TASKS.keys())}")

    # Only add task if story_id is not empty
    if story_id and story_id.strip():
        thread = threading.Thread(target=generate_video, daemon=True)
        thread.start()
        VIDEO_GENERATION_TASKS[story_id] = {"status": "processing", "message": "Video generation started"}
        logger.info(f"📊 Active video generation tasks after trigger: {list(VIDEO_GENERATION_TASKS.keys())}")
    else:
        logger.warning(f"⚠️ Cannot trigger video generation with empty story_id: '{story_id}'")

# API Health Check
@app.get("/api/health")
async def health_check():
    logger.info("🏥 Health check requested")
    
    # Get current service status
    current_services = {
        "reading_agent": AGENT_AVAILABLE,
        "image_agent": IMAGE_AGENT_AVAILABLE,
        "video_agent": VIDEO_AGENT_AVAILABLE,
        "video_generation": VIDEO_GENERATION_AVAILABLE
    }
    
    # Check if all services are still healthy
    all_healthy = all(current_services.values()) and startup_health
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "WonderKid Reading Game API",
        "startup_health": startup_health,
        "services": current_services,
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "environment_variables_loaded": len([k for k in os.environ.keys() if k.startswith(('GOOGLE_', 'MONGODB_'))])
        }
    }

# Test image endpoint for debugging
@app.get("/api/test-image")
async def test_image():
    """Test endpoint to verify image serving works"""
    logger.info("🧪 Testing image serving capability")
    
    # Check if any images exist
    import glob
    image_files = glob.glob("wonderkid_*.png")
    
    if image_files:
        latest_image = max(image_files, key=os.path.getctime)
        return {
            "status": "success",
            "message": "Image serving test",
            "available_images": image_files,
            "latest_image": latest_image,
            "test_url": f"/api/images/{latest_image}",
            "full_url": f"https://bigredhacks25-331813490179.us-east4.run.app/api/images/{latest_image}"
        }
    else:
        return {
            "status": "no_images",
            "message": "No images found for testing",
            "available_images": []
        }

# Generate new story based on theme using AI
@app.post("/api/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryThemeRequest):
    logger.info(f"📚 Generating story for theme: {request.theme}")
    
    if not AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Reading Agent system not available")
    
    try:
        # Reset story state for new story
        logger.info(f"🔄 Resetting story state for new story")
        reset_story_state()
        logger.info(f"📊 Story state after reset - ID: '{story_state.story_id}'")

        # Use AI agent to generate story
        logger.info(f"🤖 Generating AI story for: {request.theme}")
        agent_result = generate_kid_story(request.theme, request.age_group)

        story_data = agent_result["story_data"]

        # Use story_id from agent_result (more reliable than global story_state)
        story_id = agent_result.get("story_id") or story_state.story_id

        # CRITICAL: Validate story_id is not empty - generate fallback if needed
        if not story_id or story_id.strip() == "":
            from datetime import datetime
            fallback_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.error(f"❌ Both agent_result and story_state story_id are empty! Using fallback: {fallback_id}")
            story_id = fallback_id
            story_state.story_id = fallback_id  # Update story state with fallback
        else:
            # Ensure story_state is synchronized with the agent result
            story_state.story_id = story_id

        logger.info(f"📊 Agent result story_id: '{agent_result.get('story_id')}'")
        logger.info(f"📊 Story state story_id: '{story_state.story_id}'")
        logger.info(f"📊 Final story_id being returned: '{story_id}'")
        logger.info(f"✅ AI story generated: {story_data.get('story_title', 'Untitled')}")
        
        # Check if image was generated
        image_url = None
        image_generated = False
        if agent_result.get("image_generation") and agent_result["image_generation"].get("status") == "success":
            generated_file = agent_result["image_generation"].get("generated_file")
            if generated_file:
                image_url = f"/api/images/{generated_file}"
                image_generated = True
                logger.info(f"🎨 Image generated and available at: {image_url}")
        
        # Get story progress info
        story_progress = agent_result.get("story_progress", {})
        
        logger.info(f"📚 Returning initial story with ID: {story_id}")
        
        return StoryResponse(
            story_id=story_id,
            paragraphs=story_data.get("paragraphs", []),
            current_paragraph=0,
            choices=story_data.get("choices", []),
            illustration_prompt=story_data.get("illustration_prompts", [""])[0],
            mood=story_data.get("mood", "happy"),
            is_complete=False,
            progress_percentage=story_progress.get("progress_percentage", 0),
            image_url=image_url,
            image_generated=image_generated,
            scene_count=story_progress.get("scene_count", 0),
            video_trigger=None
        )
        
    except Exception as e:
        error_msg = f"AI story generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Story generation failed",
                "message": "Unable to generate story. Please check AI service configuration.",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Generate story using AI agent
@app.post("/api/create-story")
async def create_story(request: StoryThemeRequest):
    logger.info(f"📝 Received story request: {request.theme}")
    
    if not AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Reading Agent system not available")
    
    try:
        # Reset story state for new story
        reset_story_state()
        
        # Use AI agent to generate story
        logger.info(f"🤖 Generating AI story for: {request.theme}")
        agent_result = generate_kid_story(request.theme, request.age_group)
        
        story_data = agent_result["story_data"]
        story_progress = agent_result.get("story_progress", {})
        
        # Check if image was generated
        image_info = {}
        if agent_result.get("image_generation"):
            image_result = agent_result["image_generation"]
            if image_result.get("status") == "success":
                generated_file = image_result.get("generated_file")
                image_info = {
                    "image_generated": True,
                    "image_url": f"/api/images/{generated_file}" if generated_file else None,
                    "image_file": generated_file,
                    "scene_number": image_result.get("scene_number", 1)
                }
            else:
                image_info = {
                    "image_generated": False,
                    "image_error": image_result.get("error", "Unknown error")
                }
        else:
            image_info = {"image_generated": False}

        response = {
            "message": f"✨ {agent_result['message']}",
            "user_input": request.theme,
            "story_title": story_data.get("story_title", "Your Adventure"),
            "paragraphs": story_data.get("paragraphs", []),
            "choices": story_data.get("choices", []),
            "illustration_prompts": story_data.get("illustration_prompts", []),
            "mood": story_data.get("mood", "happy"),
            "educational_theme": story_data.get("educational_theme", ""),
            "ai_powered": agent_result.get("ai_powered", True),
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "story_progress": story_progress,
            "story_id": story_state.story_id,
            **image_info  # Include image information
        }
        
        logger.info(f"✅ AI story generated: {story_data.get('story_title', 'Untitled')}")
        logger.info(f"📚 Returning continued story with ID: {story_state.story_id}")
        return response
        
    except Exception as e:
        error_msg = f"AI story generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Story generation failed",
                "message": "Unable to generate story. Please check AI service configuration.",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Continue story with user choice using AI
@app.post("/api/continue-story", response_model=StoryResponse)
async def continue_story(request: StoryChoiceRequest):
    logger.info(f"🎭 Processing choice for story {request.story_id}: {request.choice}")
    
    if not AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Reading Agent system not available")
    
    try:
        # Validate story ID consistency between frontend and backend session
        backend_story_id = ''
        if AGENT_AVAILABLE:
            try:
                current_story_status = get_story_status()
                backend_story_id = current_story_status.get('story_id', '')
            except Exception as e:
                logger.warning(f"⚠️ Could not get story status for ID validation: {e}")
                backend_story_id = ''

        if backend_story_id and request.story_id != 'current_story' and request.story_id != backend_story_id:
            logger.warning(f"⚠️ Story ID mismatch! Frontend: {request.story_id}, Backend: {backend_story_id}")
            logger.info(f"🔄 Using backend story ID for session consistency: {backend_story_id}")

        # Use AI agent to continue story with choice
        logger.info(f"🤖 Continuing story with AI choice: {request.choice}")
        agent_result = continue_story_with_choice(request.choice)
        
        continuation_data = agent_result["continuation_data"]
        updated_story = agent_result["updated_story"]
        story_progress = agent_result.get("story_progress", {})
        
        # Check if image was generated for this continuation
        image_url = None
        image_generated = False
        if agent_result.get("image_generation") and agent_result["image_generation"].get("status") == "success":
            generated_file = agent_result["image_generation"].get("generated_file")
            if generated_file:
                image_url = f"/api/images/{generated_file}"
                image_generated = True
                logger.info(f"🎨 Continuation image generated and available at: {image_url}")
        
        # Calculate progress
        total_paragraphs = len(updated_story["paragraphs"])
        current_paragraph = updated_story["current_paragraph"]
        progress_percentage = story_progress.get("progress_percentage", 0)
        
        # Check if story is complete
        is_complete = continuation_data.get("story_complete", False)
        
        # Check for video trigger at 10 iterations
        video_trigger_info = story_progress.get("video_trigger")
        if video_trigger_info:
            logger.info(f"🎬 Video generation triggered for story {story_state.story_id}")
            # Trigger background video generation
            trigger_background_video_generation(story_state.story_id)
        
        logger.info(f"✅ Story continued successfully. Progress: {progress_percentage}%")

        # CRITICAL: Ensure story_id is valid before returning - prioritize agent_result
        response_story_id = agent_result.get("story_id") or story_state.story_id
        if not response_story_id or response_story_id.strip() == "":
            logger.error(f"❌ Both agent_result and story_state story_id are empty in continue-story! Using request story_id as fallback")
            response_story_id = request.story_id
        else:
            # Ensure story_state is synchronized
            story_state.story_id = response_story_id

        return StoryResponse(
            story_id=response_story_id,  # Use backend's authoritative story ID (with fallback)
            paragraphs=updated_story["paragraphs"],
            current_paragraph=current_paragraph,
            choices=updated_story["choices"],
            illustration_prompt=continuation_data.get("illustration_prompts", [""])[0],
            mood=continuation_data.get("mood", "happy"),
            is_complete=is_complete,
            progress_percentage=progress_percentage,
            image_url=image_url,
            image_generated=image_generated,
            scene_count=story_progress.get("scene_count", 0),
            video_trigger=video_trigger_info
        )
        
    except Exception as e:
        logger.error(f"❌ Story continuation failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Story continuation failed",
                "message": "Unable to continue story. Please check AI service configuration.",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Generate story video endpoint (with aliases for compatibility)
@app.post("/api/generate-story-video")
@app.post("/api/generate-video")  # Alias for frontend compatibility
async def generate_story_video(request: VideoGenerationRequest):
    """Manually trigger or check status of story video generation"""
    logger.info(f"🎬 Video generation requested for story {request.story_id}")
    logger.info(f"📊 Request details: manual_trigger={request.manual_trigger}")
    
    if not VIDEO_AGENT_AVAILABLE:
        logger.error(f"❌ Video generation system not available for story {request.story_id}")
        raise HTTPException(status_code=503, detail="Video generation system not available")
    
    try:
        # Check if story has enough scenes
        if not AGENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Reading Agent system required for video generation")

        try:
            status = get_story_status()
            logger.info(f"📊 Story status: scenes={status.get('scene_count', 0)}, video_triggered={status.get('video_generation_triggered', False)}")
        except Exception as e:
            logger.error(f"❌ Failed to get story status for video generation: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get story status: {str(e)}")
        
        if status["scene_count"] < 6 and not request.manual_trigger:
            logger.warning(f"⚠️ Story {request.story_id} not ready for video: {status['scene_count']}/6 scenes")
            return {
                "status": "not_ready",
                "message": f"Story needs 6 scenes for video. Current: {status['scene_count']}/6",
                "scenes_needed": 6 - status["scene_count"]
            }
        
        # Check if video generation is already in progress
        if request.story_id in VIDEO_GENERATION_TASKS:
            task_status = VIDEO_GENERATION_TASKS[request.story_id]
            logger.info(f"📊 Existing task status for {request.story_id}: {task_status.get('status', 'unknown')}")
            
            if task_status.get("status") == "processing":
                logger.info(f"⏳ Video generation already in progress for story {request.story_id}")
                return {
                    "status": "processing",
                    "message": "Video generation in progress. Check back in 2-3 minutes."
                }
            elif task_status.get("status") == "success":
                logger.info(f"✅ Video already generated for story {request.story_id}")
                return task_status
            elif task_status.get("status") == "error":
                logger.warning(f"⚠️ Previous video generation failed for story {request.story_id}, retrying...")
        
        # Trigger new video generation
        logger.info(f"🚀 Starting new video generation for story {request.story_id}")
        logger.info(f"📊 Story context: scenes={status['scene_count']}, images={status.get('images_generated', 0)}")
        
        trigger_background_video_generation(request.story_id)
        
        logger.info(f"✅ Video generation triggered successfully for story {request.story_id}")
        
        return {
            "status": "started",
            "message": "🎬 Video generation started! This will take 2-3 minutes.",
            "story_id": request.story_id,
            "scenes_included": status["scene_count"]
        }
        
    except Exception as e:
        logger.error(f"❌ Video generation request failed for story {request.story_id}: {str(e)}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        logger.error(f"📋 Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

# Test endpoint to check GCS videos
@app.get("/api/test/gcs-videos")
async def test_gcs_videos():
    """Test endpoint to list all GCS videos and their status"""
    logger.info(f"🔍 === GCS VIDEO TEST ===")
    
    result = {
        "tasks": {},
        "gcs_status": "unknown",
        "bucket_name": "wonderkid-demo-videos",
        "current_story_id": story_state.story_id if AGENT_AVAILABLE else None,
        "story_state": get_story_status() if AGENT_AVAILABLE else None
    }
    
    # List all video tasks
    for task_id, task_data in VIDEO_GENERATION_TASKS.items():
        result["tasks"][task_id] = {
            "status": task_data.get("status"),
            "file": task_data.get("generated_file"),
            "gcs_url": task_data.get("gcs_url"),
            "timestamp": task_data.get("timestamp", "unknown")
        }
    
    # Check GCS status
    try:
        from gcs_helper import get_gcs_manager
        gcs = get_gcs_manager()
        if gcs.bucket:
            result["gcs_status"] = "connected"
            logger.info(f"✅ GCS bucket connected")
        else:
            result["gcs_status"] = "not_connected"
            logger.error(f"❌ GCS bucket not connected")
    except Exception as e:
        result["gcs_status"] = f"error: {str(e)}"
        logger.error(f"❌ GCS error: {str(e)}")
    
    logger.info(f"📊 Test result: {json.dumps(result, default=str)}")
    return result

# Get video generation status
@app.get("/api/video-status/{story_id}")
async def get_video_status(story_id: str):
    """Check the status of video generation for a story"""
    logger.info(f"📊 === VIDEO STATUS REQUEST ===")
    logger.info(f"📊 Story ID requested: {story_id}")
    try:
        logger.info(f"📊 CHECKPOINT 1: Starting video status check for: {story_id}")
        logger.info(f"📊 CHECKPOINT 2: Available video tasks: {list(VIDEO_GENERATION_TASKS.keys())}")

        # Log VIDEO_GENERATION_TASKS structure for debugging
        logger.info(f"📊 CHECKPOINT 3: VIDEO_GENERATION_TASKS type: {type(VIDEO_GENERATION_TASKS)}")
        logger.info(f"📊 CHECKPOINT 4: VIDEO_GENERATION_TASKS length: {len(VIDEO_GENERATION_TASKS) if VIDEO_GENERATION_TASKS else 'None/Empty'}")

        for task_id, task_data in (VIDEO_GENERATION_TASKS.items() if VIDEO_GENERATION_TASKS else []):
            logger.info(f"📊 CHECKPOINT 5: Task {task_id} status: {task_data.get('status', 'NO_STATUS')}")

        # Handle current_story as special case for empty/unspecified story ID
        if story_id == "current_story" or story_id == "" or story_id == "undefined":
            logger.info(f"🔍 Handling special case story_id: '{story_id}'")

            # Check if reading agent is available before calling get_story_status
            if not AGENT_AVAILABLE:
                logger.error(f"❌ Reading agent not available, cannot get story status")
                return {
                    "status": "error",
                    "generation_in_progress": False,
                    "video_url": None,
                    "scenes_included": 0,
                    "message": "❌ Reading agent system not available"
                }

            try:
                story_status = get_story_status()
                logger.info(f"📊 Retrieved story status: {story_status}")
                actual_story_id = story_status.get('story_id', '')

                if actual_story_id:
                    logger.info(f"🔄 Redirecting from '{story_id}' to actual story ID: {actual_story_id}")
                    story_id = actual_story_id
                else:
                    # If no story ID in status, check for most recent task
                    logger.info(f"🔍 No story ID in status, checking for recent tasks...")
                    if VIDEO_GENERATION_TASKS:
                        # Get the most recent task
                        recent_tasks = sorted(
                            [(k, v) for k, v in VIDEO_GENERATION_TASKS.items()],
                            key=lambda x: x[1].get('timestamp', ''),
                            reverse=True
                        )
                        if recent_tasks:
                            story_id = recent_tasks[0][0]
                            logger.info(f"🔄 Using most recent task ID: {story_id}")
            except Exception as story_status_error:
                logger.error(f"❌ Failed to get story status: {str(story_status_error)}")
                logger.error(f"🔍 Story status error type: {type(story_status_error).__name__}")
                logger.error(f"📋 Story status error details: {str(story_status_error)}")

                # Continue with the original story_id if status retrieval fails
                logger.info(f"⏭️ Continuing with original story_id: {story_id}")

        logger.info(f"📊 CHECKPOINT 6: Final story_id for processing: {story_id}")
        # Clean up any empty string keys in VIDEO_GENERATION_TASKS
        if '' in VIDEO_GENERATION_TASKS:
            logger.warning("⚠️ Removing empty string key from VIDEO_GENERATION_TASKS")
            del VIDEO_GENERATION_TASKS['']

        # Enhanced logging for debugging
        logger.info(f"📊 Total active tasks: {len(VIDEO_GENERATION_TASKS)}")
        logger.info(f"📊 Active task IDs: {list(VIDEO_GENERATION_TASKS.keys())}")

        # Log all tasks for debugging
        for task_id, task_data in VIDEO_GENERATION_TASKS.items():
            logger.info(f"  Task {task_id}: status={task_data.get('status')}, file={task_data.get('generated_file', 'none')}")
        
        # Check if video generation task exists
        logger.info(f"📊 CHECKPOINT 7: Checking if story_id '{story_id}' exists in VIDEO_GENERATION_TASKS")
        logger.info(f"📊 CHECKPOINT 8: story_id in VIDEO_GENERATION_TASKS: {story_id in VIDEO_GENERATION_TASKS}")

        if story_id in VIDEO_GENERATION_TASKS:
            logger.info(f"📊 CHECKPOINT 9: Found task for {story_id}")
            task_status = VIDEO_GENERATION_TASKS[story_id]
            logger.info(f"✅ Found task for {story_id}")
            # Log without large video data
            task_summary = {k: v for k, v in task_status.items() if k != 'video_data'}
            logger.info(f"📊 Task details: {json.dumps(task_summary, default=str)}")
            
            if task_status.get("status") == "processing":
                # Safely get scene count without direct story_state access
                scene_count = 0
                if AGENT_AVAILABLE:
                    try:
                        current_status = get_story_status()
                        scene_count = current_status.get('scene_count', 0)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get scene count from story status: {e}")
                        scene_count = 0

                return {
                    "status": "processing",
                    "generation_in_progress": True,
                    "video_url": None,
                    "scenes_included": scene_count,
                    "message": "⏳ Video is being generated. Please wait 2-3 minutes."
                }
            elif task_status.get("status") == "success":
                logger.info(f"📊 CHECKPOINT 10: Task status is success, processing success case")
                video_file = task_status.get("generated_file")
                gcs_url = task_status.get("gcs_url")
                logger.info(f"📊 CHECKPOINT 11: Video file found in task: {video_file}")
                logger.info(f"📊 CHECKPOINT 12: GCS URL found in task: {gcs_url}")
                if gcs_url:
                    logger.info(f"☁️ GCS URL available: {gcs_url}")

                logger.info(f"📊 CHECKPOINT 13: About to return success response")
                response = {
                    "status": "completed",
                    "generation_in_progress": False,
                    "video_url": f"/api/videos/{video_file}" if video_file else None,
                    "scenes_included": task_status.get("scenes_included", 6),
                    "message": "✅ Video generation completed!",
                    "gcs_url": gcs_url  # Include GCS URL if available
                }
                logger.info(f"📊 CHECKPOINT 14: Response prepared: {response}")
                return response
            else:
                logger.warning(f"⚠️ Task status not success: {task_status}")
                return {
                    "status": "error",
                    "generation_in_progress": False,
                    "video_url": None,
                    "scenes_included": 0,
                    "message": f"❌ Video generation failed: {task_status.get('error', 'Unknown error')}"
                }
        
        logger.info(f"📊 No task found for {story_id}, checking alternative IDs and filesystem...")
        
        # Try alternative story ID formats including timestamp-based IDs
        alt_story_ids = []
        if not story_id.startswith('story_'):
            alt_story_ids.append(f"story_{story_id}")
        if story_id.startswith('story_'):
            alt_story_ids.append(story_id.replace('story_', ''))

        # Also check for any timestamp-based story IDs from today
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')

        # Get all existing task IDs and check for any that might be related
        all_task_ids = list(VIDEO_GENERATION_TASKS.keys())
        for task_id in all_task_ids:
            if task_id and ('story_' in task_id and today in task_id):
                alt_story_ids.append(task_id)

        # Try current_story and empty string as fallbacks
        alt_story_ids.append('current_story')
        if '' in VIDEO_GENERATION_TASKS:
            alt_story_ids.append('')  # Check for empty string key only if it exists
        
        for alt_id in alt_story_ids:
            if alt_id in VIDEO_GENERATION_TASKS:
                logger.info(f"✅ Found task with alternative ID: {alt_id}")
                task_status = VIDEO_GENERATION_TASKS[alt_id]
                if task_status.get("status") == "success":
                    video_file = task_status.get("generated_file")
                    gcs_url = task_status.get("gcs_url")
                    logger.info(f"✅ Video file found in task: {video_file}")
                    if gcs_url:
                        logger.info(f"☁️ GCS URL available: {gcs_url}")
                    
                    # Prefer local API endpoint but include GCS URL as backup
                    video_url = f"/api/videos/{video_file}" if video_file else None
                    
                    return {
                        "status": "completed",
                        "generation_in_progress": False,
                        "video_url": video_url,
                        "scenes_included": task_status.get("scenes_included", 6),
                        "message": "✅ Video generation completed!",
                        "gcs_url": gcs_url  # Include GCS URL if available
                    }
        
        # Fallback: Check filesystem for video files matching story pattern
        import glob
        # Also check for the actual story ID from story state
        actual_story_id = ''
        if AGENT_AVAILABLE:
            try:
                actual_story_id = get_story_status().get('story_id', '')
            except Exception as e:
                logger.warning(f"⚠️ Could not get actual story ID from status: {e}")
                actual_story_id = ''

        video_patterns = [
            f"wonderkid*{story_id}*.mp4",
            f"wonderkid*{actual_story_id}*.mp4" if actual_story_id else None,
            f"wonderkid*video*.mp4",  # Broader pattern
            "wonderkid*.mp4"  # Even broader for recent files
        ]
        video_patterns = [p for p in video_patterns if p]  # Remove None values
        
        found_videos = []
        for pattern in video_patterns:
            matching_files = glob.glob(pattern)
            found_videos.extend(matching_files)
            logger.info(f"🔍 Pattern '{pattern}' found: {matching_files}")
        
        if found_videos:
            # Use the most recent video file
            latest_video = max(found_videos, key=os.path.getmtime)
            video_filename = os.path.basename(latest_video)
            logger.info(f"✅ Found video file on filesystem: {video_filename}")
            
            # Get GCS URL for the video
            gcs_url = None
            try:
                from gcs_helper import get_gcs_manager
                gcs = get_gcs_manager()
                
                # Check if video exists in GCS, if not upload it
                if not gcs.video_exists(video_filename):
                    logger.info(f"☁️ Uploading found video to GCS...")
                    gcs_url = gcs.upload_video(latest_video)
                else:
                    gcs_url = gcs.get_video_url(video_filename)
                    
                if gcs_url:
                    logger.info(f"☁️ GCS URL for found video: {gcs_url}")
                    return {
                        "status": "completed",
                        "generation_in_progress": False,
                        "video_url": f"/api/videos/{video_filename}",  # Provide local URL for Expo compatibility
                        "scenes_included": 6,
                        "message": "✅ Video found and ready to play!",
                        "gcs_url": gcs_url
                    }
            except Exception as e:
                logger.error(f"❌ Failed to get GCS URL for found video: {str(e)}")
            
            # Fallback if GCS fails
            return {
                "status": "completed",
                "generation_in_progress": False,
                "video_url": f"/api/videos/{video_filename}",
                "scenes_included": 6,
                "message": "✅ Video found locally!"
            }
        
        # Check if story has a generated video
        if AGENT_AVAILABLE:
            try:
                status = get_story_status()
                logger.info(f"📊 Story status: {status}")
                if status.get("generated_video"):
                    return {
                        "status": "completed",
                        "generation_in_progress": False,
                        "video_url": f"/api/videos/{status['generated_video']}",
                        "scenes_included": status.get("scene_count", 0),
                        "message": "✅ Video available!"
                    }
            except Exception as e:
                logger.error(f"❌ Failed to get story status for video check: {str(e)}")
                # Continue to next fallback
        
        # Final fallback: Check if ANY video task is completed (most recent first)
        logger.info(f"📊 No video found for story {story_id}, checking for ANY completed video...")
        
        # Sort tasks by timestamp to get most recent first
        sorted_tasks = sorted(
            [(k, v) for k, v in VIDEO_GENERATION_TASKS.items() if v.get("status") == "success"],
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )
        
        if sorted_tasks:
            task_id, task_data = sorted_tasks[0]
            logger.info(f"✅ Found most recent completed video with task_id: {task_id}")
            video_file = task_data.get("generated_file")
            gcs_url = task_data.get("gcs_url")
            
            # Prioritize GCS URL over local file
            if gcs_url:
                logger.info(f"☁️ Returning GCS URL for most recent video: {gcs_url}")
                return {
                    "status": "completed",
                    "generation_in_progress": False,
                    "video_url": None,  # Don't use local URL if GCS is available
                    "scenes_included": task_data.get("scenes_included", 6),
                    "message": "✅ Video ready from cloud storage!",
                    "gcs_url": gcs_url
                }
            elif video_file:
                return {
                    "status": "completed",
                    "generation_in_progress": False,
                    "video_url": f"/api/videos/{video_file}",
                    "scenes_included": task_data.get("scenes_included", 6),
                    "message": "✅ Video found from recent generation!",
                    "gcs_url": None
                }
        
        logger.info(f"📊 No video found anywhere for story {story_id}")

        # Get scene count safely for the final response
        scene_count = 0
        if AGENT_AVAILABLE:
            try:
                current_status = get_story_status()
                scene_count = current_status.get("scene_count", 0)
            except Exception as e:
                logger.warning(f"⚠️ Could not get scene count for final response: {e}")
                scene_count = 0

        return {
            "status": "not_started",
            "generation_in_progress": False,
            "video_url": None,
            "scenes_included": scene_count,
            "message": "Video generation not started"
        }
        
    except Exception as e:
        logger.error(f"❌ Video status check failed: {str(e)}")
        logger.error(f"🔍 Exception type: {type(e).__name__}")
        logger.error(f"📋 Exception details: {str(e)}")

        # Return proper JSON error response instead of raising HTTPException
        return {
            "status": "error",
            "generation_in_progress": False,
            "video_url": None,
            "scenes_included": 0,
            "message": f"❌ Video status check failed: {str(e)}"
        }

# Serve generated videos as base64 data (hackathon demo approach)
@app.get("/api/videos/{filename}")
async def get_generated_video(filename: str):
    logger.info(f"🎬 === VIDEO FILE REQUEST ===")
    logger.info(f"🎬 Filename requested: {filename}")
    logger.info(f"📁 Current directory: {os.getcwd()}")

    try:
        from fastapi.responses import StreamingResponse
        import io

        # List all MP4 files in current directory
        mp4_files = glob.glob("*.mp4")
        logger.info(f"📁 Available MP4 files: {mp4_files}")

        # Check if file exists in current directory
        file_path = Path(filename)
        logger.info(f"📁 Looking for file at: {file_path.absolute()}")
        logger.info(f"📁 File exists: {file_path.exists()}")

        # If file doesn't exist locally, try to fetch from GCS
        if not file_path.exists():
            logger.info(f"🔍 File not found locally, checking GCS...")
            try:
                from gcs_helper import get_gcs_manager
                gcs = get_gcs_manager()

                # Check if file exists in GCS
                if gcs.video_exists(filename):
                    logger.info(f"☁️ Video found in GCS, downloading...")
                    local_path = gcs.download_video(filename)

                    if local_path and os.path.exists(local_path):
                        logger.info(f"✅ Video downloaded from GCS successfully")
                        file_path = Path(local_path)
                    else:
                        logger.error(f"❌ Failed to download video from GCS")
                else:
                    logger.info(f"❌ Video not found in GCS either")
            except Exception as gcs_error:
                logger.error(f"❌ GCS retrieval error: {str(gcs_error)}")
                logger.info(f"📍 Falling back to local file serving if available")

        if file_path.exists() and file_path.is_file():
            logger.info(f"✅ Serving video file: {filename}")

            def video_stream():
                with open(file_path, 'rb') as video_file:
                    while True:
                        chunk = video_file.read(8192)  # Read in 8KB chunks
                        if not chunk:
                            break
                        yield chunk

            return StreamingResponse(
                video_stream(),
                media_type="video/mp4",
                headers={
                    "Accept-Ranges": "bytes",
                    "Content-Disposition": f"inline; filename={filename}",
                    "Cache-Control": "public, max-age=3600"
                }
            )
        else:
            logger.error(f"❌ Video file not found: {filename}")

            # For streaming endpoints, we need to redirect to GCS or return 404
            for task_id, task_data in VIDEO_GENERATION_TASKS.items():
                if task_data.get("generated_file") == filename and task_data.get("gcs_url"):
                    logger.info(f"☁️ Redirecting to GCS URL: {task_data['gcs_url']}")
                    from fastapi.responses import RedirectResponse
                    return RedirectResponse(url=task_data["gcs_url"], status_code=302)

            raise HTTPException(status_code=404, detail=f"Video not found: {filename}")
            
    except Exception as e:
        logger.error(f"❌ Video serving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video serving failed: {str(e)}")

# Alternative: Direct video file serving (for testing)
@app.get("/api/video-file/{filename}")
async def get_video_file(filename: str):
    """Direct file serving for testing purposes"""
    logger.info(f"🎬 Direct file serving: {filename}")
    
    try:
        file_path = Path(filename)
        if file_path.exists() and file_path.is_file():
            return FileResponse(
                str(file_path),
                media_type="video/mp4",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Cache-Control": "public, max-age=3600",
                    "Accept-Ranges": "bytes"
                }
            )
        else:
            raise HTTPException(status_code=404, detail=f"Video not found: {filename}")
            
    except Exception as e:
        logger.error(f"❌ Video file serving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video file serving failed: {str(e)}")

# Debug endpoint to list all video files
@app.get("/api/debug/videos")
async def debug_list_videos():
    """Debug endpoint to list all available video files"""
    logger.info("🔍 Debug: Listing all video files")
    
    try:
        # Find all video files
        video_files = glob.glob("*.mp4")
        video_info = []
        
        for video_file in video_files:
            file_path = Path(video_file)
            if file_path.exists():
                file_stats = file_path.stat()
                video_info.append({
                    "filename": video_file,
                    "size_bytes": file_stats.st_size,
                    "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    "url": f"/api/videos/{video_file}"
                })
        
        return {
            "total_videos": len(video_files),
            "videos": video_info,
            "current_directory": str(Path.cwd()),
            "video_tasks": {k: v for k, v in VIDEO_GENERATION_TASKS.items()},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Debug video listing failed: {str(e)}")
        return {"error": str(e), "videos": []}

# Get overall video system status
@app.get("/api/video-system-status")
async def get_video_system_status():
    """Get overall video generation system status"""
    logger.info("📊 Getting video system status")
    
    try:
        video_status = {}
        if VIDEO_AGENT_AVAILABLE:
            from agents.video_agent import get_video_generation_status
            video_status = get_video_generation_status()
        
        story_status = get_story_status() if AGENT_AVAILABLE else {}
        
        return {
            "video_system_available": VIDEO_AGENT_AVAILABLE,
            "video_generation_available": VIDEO_GENERATION_AVAILABLE,
            "current_story_progress": {
                "scene_count": story_status.get("scene_count", 0),
                "ready_for_video": story_status.get("video_progress", {}).get("ready_for_video", False),
                "video_triggered": story_status.get("video_generation_triggered", False),
                "generated_video": story_status.get("generated_video")
            },
            "video_generation_stats": video_status,
            "active_tasks": len(VIDEO_GENERATION_TASKS),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Video system status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video system status check failed: {str(e)}")

# Generate illustration for story scene
@app.post("/api/generate-illustration")
async def generate_illustration(prompt: str, story_id: str, scene_number: int):
    logger.info(f"🎨 Generating illustration for story {story_id}, scene {scene_number}")
    
    try:
        # Simulate AI image generation delay
        await asyncio.sleep(3)
        
        # Mock illustration generation (will be replaced with Google Imagen)
        illustration_data = {
            "illustration_id": f"ill_{story_id}_{scene_number}",
            "prompt": prompt,
            "image_url": f"/api/media/illustrations/{story_id}_{scene_number}.png",
            "generated_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        logger.info(f"✅ Illustration generated: {illustration_data['illustration_id']}")
        
        return illustration_data
        
    except Exception as e:
        logger.error(f"❌ Illustration generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Illustration generation failed: {str(e)}")

# Save user progress
@app.post("/api/save-progress", response_model=UserProgressResponse)
async def save_progress(request: UserProgressRequest):
    logger.info(f"💾 Saving progress for user {request.user_id}")
    
    try:
        # Initialize user progress if not exists
        if request.user_id not in USER_PROGRESS:
            USER_PROGRESS[request.user_id] = {
                "stories_read": 0,
                "total_reading_time": 0,
                "current_streak": 0,
                "achievements": [],
                "level": 1,
                "stories": {}
            }
        
        user_data = USER_PROGRESS[request.user_id]
        
        # Update story progress
        user_data["stories"][request.story_id] = {
            "completed_paragraphs": request.completed_paragraphs,
            "total_paragraphs": request.total_paragraphs,
            "reading_time": request.reading_time,
            "completed_at": datetime.now().isoformat()
        }
        
        # Update overall progress
        user_data["total_reading_time"] += request.reading_time
        
        # Check if story is complete
        if request.completed_paragraphs >= request.total_paragraphs:
            user_data["stories_read"] += 1
            user_data["current_streak"] += 1
            
            # Level up logic (mock: every 3 stories)
            new_level = (user_data["stories_read"] // 3) + 1
            if new_level > user_data["level"]:
                user_data["level"] = new_level
                logger.info(f"🎉 User {request.user_id} leveled up to level {new_level}!")
        
        # Mock achievements
        achievements = []
        if user_data["stories_read"] >= 1:
            achievements.append({
                "id": "first_story",
                "title": "First Story",
                "description": "Read your first story!",
                "icon": "📖",
                "unlocked": True
            })
        
        if user_data["stories_read"] >= 5:
            achievements.append({
                "id": "speed_reader",
                "title": "Speed Reader",
                "description": "Read 5 stories",
                "icon": "⚡",
                "unlocked": True
            })
        
        if user_data["current_streak"] >= 5:
            achievements.append({
                "id": "story_lover",
                "title": "Story Lover",
                "description": "Read for 5 days in a row",
                "icon": "❤️",
                "unlocked": True
            })
        
        user_data["achievements"] = achievements
        
        logger.info(f"✅ Progress saved for user {request.user_id}")
        
        return UserProgressResponse(
            user_id=request.user_id,
            stories_read=user_data["stories_read"],
            total_reading_time=user_data["total_reading_time"],
            current_streak=user_data["current_streak"],
            achievements=achievements,
            level=user_data["level"]
        )
        
    except Exception as e:
        logger.error(f"❌ Progress saving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Progress saving failed: {str(e)}")

# Get user progress
@app.get("/api/user-progress/{user_id}", response_model=UserProgressResponse)
async def get_user_progress(user_id: str):
    logger.info(f"📊 Getting progress for user {user_id}")
    
    try:
        if user_id not in USER_PROGRESS:
            # Return default progress for new user
            return UserProgressResponse(
                user_id=user_id,
                stories_read=0,
                total_reading_time=0,
                current_streak=0,
                achievements=[],
                level=1
            )
        
        user_data = USER_PROGRESS[user_id]
        
        return UserProgressResponse(
            user_id=user_id,
            stories_read=user_data["stories_read"],
            total_reading_time=user_data["total_reading_time"],
            current_streak=user_data["current_streak"],
            achievements=user_data["achievements"],
            level=user_data["level"]
        )
        
    except Exception as e:
        logger.error(f"❌ Progress retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Progress retrieval failed: {str(e)}")

# Get user's story history
@app.get("/api/user-stories/{user_id}")
async def get_user_stories(user_id: str):
    logger.info(f"📚 Getting story history for user {user_id}")
    
    try:
        if user_id not in USER_PROGRESS:
            return {"stories": []}
        
        user_data = USER_PROGRESS[user_id]
        stories = []
        
        for story_id, story_data in user_data.get("stories", {}).items():
            stories.append({
                "story_id": story_id,
                "title": f"Story {story_id.split('_')[-1]}",
                "completed_paragraphs": story_data["completed_paragraphs"],
                "total_paragraphs": story_data["total_paragraphs"],
                "reading_time": story_data["reading_time"],
                "completed_at": story_data["completed_at"],
                "progress_percentage": (story_data["completed_paragraphs"] / story_data["total_paragraphs"]) * 100
            })
        
        return {"stories": stories}
        
    except Exception as e:
        logger.error(f"❌ Story history retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story history retrieval failed: {str(e)}")

# Serve generated images with proper CORS headers for Expo Go
@app.get("/api/images/{filename}")
async def get_generated_image(filename: str):
    logger.info(f"🖼️ Serving generated image: {filename}")
    
    try:
        # Check if file exists in current directory (where images are saved)
        file_path = Path(filename)
        if file_path.exists() and file_path.is_file():
            # Return FileResponse with proper headers for mobile apps
            return FileResponse(
                str(file_path),
                media_type="image/png",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Cache-Control": "public, max-age=3600"
                }
            )
        else:
            logger.error(f"❌ Image file not found: {filename}")
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
            
    except Exception as e:
        logger.error(f"❌ Image serving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image serving failed: {str(e)}")

# Generate image for existing story text
@app.post("/api/generate-scene-image")
async def generate_scene_image(story_text: str, scene_context: str = "", age_group: str = "5-8"):
    logger.info(f"🎨 Generating scene image for story text")
    
    if not IMAGE_AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Image generation system not available")
    
    try:
        # Generate image using image agent
        image_result = generate_kid_friendly_image(
            story_text=story_text,
            scene_context=scene_context,
            age_group=age_group
        )
        
        if image_result.get("status") == "success":
            generated_file = image_result.get("generated_file")
            image_url = f"/api/images/{generated_file}" if generated_file else None
            
            logger.info(f"✅ Scene image generated: {generated_file}")
            
            return {
                "status": "success",
                "message": "🎨 Scene image generated successfully!",
                "image_url": image_url,
                "generated_file": generated_file,
                "story_text": story_text,
                "scene_context": scene_context,
                "age_group": age_group,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ Image generation failed: {image_result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Image generation failed",
                    "message": image_result.get("error", "Unknown error"),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Scene image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scene image generation failed: {str(e)}")

# Get image generation status
@app.get("/api/image-status")
async def get_image_status():
    logger.info("📊 Getting image generation status")
    
    try:
        if IMAGE_AGENT_AVAILABLE:
            status = get_image_generation_status()
            return {
                "image_system": "available",
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "image_system": "unavailable",
                "message": "Image generation system not loaded",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Image status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image status retrieval failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    logger.info("🚀 Starting WonderKid Reading Game API with Video Generation...")
    logger.info(f"🎬 Video generation system: {'READY' if VIDEO_AGENT_AVAILABLE else 'NOT AVAILABLE'}")
    logger.info(f"🌐 Server will start on port: {port}")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
