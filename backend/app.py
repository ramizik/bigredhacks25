from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import logging
import os
import sys
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
    progress_percentage: int = 0
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
            logger.info(f"🎬 Background video generation started for story {story_id}")
            logger.info(f"📊 Current story state: {get_story_status()}")
            
            # Get story context for logging
            story_status = get_story_status()
            logger.info(f"📚 Story context: scenes={story_status.get('scene_count', 0)}, images={story_status.get('images_generated', 0)}")
            
            result = generate_story_video_async()
            VIDEO_GENERATION_TASKS[story_id] = result
            
            if result.get("status") == "success":
                logger.info(f"✅ Background video generation completed successfully for {story_id}")
                logger.info(f"📁 Generated file: {result.get('generated_file', 'unknown')}")
            else:
                logger.error(f"❌ Background video generation failed for {story_id}: {result.get('error', 'unknown error')}")
                
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
    logger.info(f"🚀 Starting background thread for video generation of story {story_id}")
    thread = threading.Thread(target=generate_video, daemon=True)
    thread.start()
    VIDEO_GENERATION_TASKS[story_id] = {"status": "processing", "message": "Video generation started"}
    logger.info(f"📊 Active video generation tasks: {len(VIDEO_GENERATION_TASKS)}")

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
        reset_story_state()
        
        # Use AI agent to generate story
        logger.info(f"🤖 Generating AI story for: {request.theme}")
        agent_result = generate_kid_story(request.theme, request.age_group)
        
        story_data = agent_result["story_data"]
        story_id = story_state.story_id  # Use the story ID from story_state
        
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
        
        return StoryResponse(
            story_id=story_id,
            paragraphs=story_data.get("paragraphs", []),
            current_paragraph=0,
            choices=story_data.get("choices", []),
            illustration_prompt=story_data.get("illustration_prompts", [""])[0],
            mood=story_data.get("mood", "adventure"),
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
            "mood": story_data.get("mood", "magical"),
            "educational_theme": story_data.get("educational_theme", ""),
            "ai_powered": agent_result.get("ai_powered", True),
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "story_progress": story_progress,
            "story_id": story_state.story_id,
            **image_info  # Include image information
        }
        
        logger.info(f"✅ AI story generated: {story_data.get('story_title', 'Untitled')}")
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
        
        return StoryResponse(
            story_id=request.story_id,
            paragraphs=updated_story["paragraphs"],
            current_paragraph=current_paragraph,
            choices=updated_story["choices"],
            illustration_prompt=continuation_data.get("illustration_prompts", [""])[0],
            mood="adventure",
            is_complete=is_complete,
            progress_percentage=int(progress_percentage),
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

# Generate story video endpoint
@app.post("/api/generate-story-video")
async def generate_story_video(request: VideoGenerationRequest):
    """Manually trigger or check status of story video generation"""
    logger.info(f"🎬 Video generation requested for story {request.story_id}")
    logger.info(f"📊 Request details: manual_trigger={request.manual_trigger}")
    
    if not VIDEO_AGENT_AVAILABLE:
        logger.error(f"❌ Video generation system not available for story {request.story_id}")
        raise HTTPException(status_code=503, detail="Video generation system not available")
    
    try:
        # Check if story has enough scenes
        status = get_story_status()
        logger.info(f"📊 Story status: scenes={status.get('scene_count', 0)}, video_triggered={status.get('video_generation_triggered', False)}")
        
        if status["scene_count"] < 10 and not request.manual_trigger:
            logger.warning(f"⚠️ Story {request.story_id} not ready for video: {status['scene_count']}/10 scenes")
            return {
                "status": "not_ready",
                "message": f"Story needs 10 scenes for video. Current: {status['scene_count']}/10",
                "scenes_needed": 10 - status["scene_count"]
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

# Get video generation status
@app.get("/api/video-status/{story_id}", response_model=VideoStatusResponse)
async def get_video_status(story_id: str):
    """Check the status of video generation for a story"""
    logger.info(f"📊 Checking video status for story {story_id}")
    
    try:
        # Check if video generation task exists
        if story_id in VIDEO_GENERATION_TASKS:
            task_status = VIDEO_GENERATION_TASKS[story_id]
            
            if task_status.get("status") == "processing":
                return VideoStatusResponse(
                    status="processing",
                    generation_in_progress=True,
                    video_url=None,
                    scenes_included=story_state.scene_count,
                    message="⏳ Video is being generated. Please wait 2-3 minutes."
                )
            elif task_status.get("status") == "success":
                video_file = task_status.get("generated_file")
                return VideoStatusResponse(
                    status="completed",
                    generation_in_progress=False,
                    video_url=f"/api/videos/{video_file}" if video_file else None,
                    scenes_included=task_status.get("scenes_included", 10),
                    message="✅ Video generation completed!"
                )
            else:
                return VideoStatusResponse(
                    status="error",
                    generation_in_progress=False,
                    video_url=None,
                    scenes_included=0,
                    message=f"❌ Video generation failed: {task_status.get('error', 'Unknown error')}"
                )
        
        # Check if story has a generated video
        status = get_story_status()
        if status.get("generated_video"):
            return VideoStatusResponse(
                status="completed",
                generation_in_progress=False,
                video_url=f"/api/videos/{status['generated_video']}",
                scenes_included=status.get("scene_count", 0),
                message="✅ Video available!"
            )
        
        return VideoStatusResponse(
            status="not_started",
            generation_in_progress=False,
            video_url=None,
            scenes_included=status.get("scene_count", 0),
            message="Video generation not started"
        )
        
    except Exception as e:
        logger.error(f"❌ Video status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video status check failed: {str(e)}")

# Serve generated videos
@app.get("/api/videos/{filename}")
async def get_generated_video(filename: str):
    logger.info(f"🎬 Serving generated video: {filename}")
    
    try:
        # Check if file exists in current directory
        file_path = Path(filename)
        if file_path.exists() and file_path.is_file():
            # Return FileResponse with proper headers for mobile apps
            return FileResponse(
                str(file_path),
                media_type="video/mp4",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Cache-Control": "public, max-age=3600",
                    "Accept-Ranges": "bytes"  # Enable video seeking
                }
            )
        else:
            logger.error(f"❌ Video file not found: {filename}")
            raise HTTPException(status_code=404, detail=f"Video not found: {filename}")
            
    except Exception as e:
        logger.error(f"❌ Video serving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video serving failed: {str(e)}")

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
                "progress_percentage": int((story_data["completed_paragraphs"] / story_data["total_paragraphs"]) * 100)
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
