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

# Add the agents directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

# Import reading agent
try:
    from agents.reading_agent import (
        generate_kid_story,
        continue_story_with_choice,
        get_story_status,
        story_state
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

# Configure logging with emojis
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WonderKid Reading Game API",
    description="📚 AI-Powered Interactive Reading Experience for Kids",
    version="1.0.0"
)

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

# API Health Check
@app.get("/api/health")
async def health_check():
    logger.info("🏥 Health check requested")
    return {
        "status": "healthy",
        "service": "WonderKid Reading Game API",
        "agent_available": AGENT_AVAILABLE,
        "image_agent_available": IMAGE_AGENT_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
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
        # Use AI agent to generate story
        logger.info(f"🤖 Generating AI story for: {request.theme}")
        agent_result = generate_kid_story(request.theme, request.age_group)
        
        story_data = agent_result["story_data"]
        story_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
        
        return StoryResponse(
            story_id=story_id,
            paragraphs=story_data.get("paragraphs", []),
            current_paragraph=0,
            choices=story_data.get("choices", []),
            illustration_prompt=story_data.get("illustration_prompts", [""])[0],
            mood=story_data.get("mood", "adventure"),
            is_complete=False,
            progress_percentage=0,
            image_url=image_url,
            image_generated=image_generated
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
        # Use AI agent to generate story
        logger.info(f"🤖 Generating AI story for: {request.theme}")
        agent_result = generate_kid_story(request.theme, request.age_group)
        
        story_data = agent_result["story_data"]
        
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
        progress_percentage = min((current_paragraph / max(total_paragraphs, 1)) * 100, 100)
        
        # Check if story is complete
        is_complete = continuation_data.get("story_complete", False)
        
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
            image_generated=image_generated
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
    
    logger.info("🚀 Starting WonderKid Reading Game API...")
    logger.info(f"🌐 Server will start on port: {port}")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
