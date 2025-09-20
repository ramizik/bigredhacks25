from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import asyncio

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

# Mock data for development (will be replaced with AI and MongoDB)
MOCK_STORIES = {
    "magic_dragon": {
        "id": "magic_dragon",
        "title": "The Magic Dragon Adventure",
        "paragraphs": [
            "Once upon a time, a brave little dragon named Sparkle lived in a magical forest. Sparkle had shimmering purple scales that sparkled in the sunlight.",
            "One sunny morning, Sparkle discovered a mysterious golden key hidden under a rainbow-colored mushroom. The key seemed to glow with magical energy!",
            "As Sparkle picked up the key, the forest around them began to shimmer and change. Trees started to sing, and flowers began to dance in the gentle breeze.",
            "Suddenly, a wise old owl named Hoot appeared on a nearby branch. 'That key belongs to the Crystal Castle,' Hoot explained. 'But the castle is guarded by friendly forest creatures who need your help.'",
            "Sparkle felt excited and a little nervous. The adventure was just beginning! What should Sparkle do next?"
        ],
        "choices": [
            "Follow the singing trees to find the Crystal Castle",
            "Ask Hoot the owl for more information about the forest creatures",
            "Try to use the golden key to unlock something nearby"
        ],
        "illustration_prompts": [
            "A cute purple dragon with sparkling scales in a magical forest",
            "A golden key glowing under a rainbow mushroom",
            "A singing tree with dancing flowers in a magical forest",
            "A wise owl on a branch talking to a dragon",
            "A crystal castle in the distance with friendly forest creatures"
        ]
    }
}

USER_PROGRESS = {}

# API Health Check
@app.get("/api/health")
async def health_check():
    logger.info("🏥 Health check requested")
    return {
        "status": "healthy",
        "service": "WonderKid Reading Game API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Generate new story based on theme
@app.post("/api/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryThemeRequest):
    logger.info(f"📚 Generating story for theme: {request.theme}")
    
    try:
        # Simulate AI story generation delay
        await asyncio.sleep(2)
        
        # For now, use mock data - will be replaced with Google Gemini
        story_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate story based on theme (mock implementation)
        if "dragon" in request.theme.lower():
            story_data = MOCK_STORIES["magic_dragon"].copy()
        else:
            # Generate custom story based on theme
            story_data = {
                "id": story_id,
                "title": f"The {request.theme.title()} Adventure",
                "paragraphs": [
                    f"Once upon a time, there was a wonderful adventure about {request.theme}. The story begins in a magical place where anything is possible.",
                    f"As our hero explored the world of {request.theme}, they discovered amazing things that filled their heart with wonder and joy.",
                    f"The adventure continued as new friends joined the journey, each bringing their own special magic to the story of {request.theme}.",
                    f"Together, they faced challenges and celebrated victories, learning that the best adventures are shared with friends.",
                    f"The story of {request.theme} was just beginning, and our hero couldn't wait to see what would happen next!"
                ],
                "choices": [
                    f"Explore more about {request.theme} with your new friends",
                    f"Ask the wise characters about the secrets of {request.theme}",
                    f"Use your imagination to create new adventures with {request.theme}"
                ],
                "illustration_prompts": [
                    f"A magical scene featuring {request.theme} with bright, kid-friendly colors",
                    f"Adventure characters discovering {request.theme} in a beautiful landscape",
                    f"Friends celebrating their {request.theme} adventure together",
                    f"A whimsical illustration of {request.theme} with sparkles and magic",
                    f"The final scene of the {request.theme} adventure with happy characters"
                ]
            }
        
        story_data["id"] = story_id
        
        logger.info(f"✅ Story generated successfully: {story_id}")
        
        return StoryResponse(
            story_id=story_id,
            paragraphs=story_data["paragraphs"],
            current_paragraph=0,
            choices=story_data["choices"],
            illustration_prompt=story_data["illustration_prompts"][0],
            mood="adventure",
            is_complete=False,
            progress_percentage=0
        )
        
    except Exception as e:
        logger.error(f"❌ Story generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

# Continue story with user choice
@app.post("/api/continue-story", response_model=StoryResponse)
async def continue_story(request: StoryChoiceRequest):
    logger.info(f"🎭 Processing choice for story {request.story_id}: {request.choice}")
    
    try:
        # Simulate AI processing delay
        await asyncio.sleep(1.5)
        
        # Mock story continuation logic
        story_data = MOCK_STORIES.get("magic_dragon", MOCK_STORIES["magic_dragon"])
        
        # Generate next paragraph based on choice
        next_paragraph = f"You chose to {request.choice.lower()}. The adventure continues as new wonders unfold before your eyes, and you discover even more magical surprises along the way!"
        
        # Add the new paragraph
        updated_paragraphs = story_data["paragraphs"] + [next_paragraph]
        new_current_paragraph = request.current_paragraph + 1
        
        # Check if story is complete (mock: complete after 8 paragraphs)
        is_complete = new_current_paragraph >= 8
        progress_percentage = min((new_current_paragraph / 8) * 100, 100)
        
        # Generate new choices if not complete
        new_choices = None
        if not is_complete:
            new_choices = [
                "Explore the magical path ahead",
                "Talk to the friendly forest creatures",
                "Use your special powers to help others"
            ]
        
        logger.info(f"✅ Story continued successfully. Progress: {progress_percentage}%")
        
        return StoryResponse(
            story_id=request.story_id,
            paragraphs=updated_paragraphs,
            current_paragraph=new_current_paragraph,
            choices=new_choices,
            illustration_prompt=story_data["illustration_prompts"][min(new_current_paragraph, len(story_data["illustration_prompts"]) - 1)],
            mood="adventure",
            is_complete=is_complete,
            progress_percentage=int(progress_percentage)
        )
        
    except Exception as e:
        logger.error(f"❌ Story continuation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story continuation failed: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    logger.info("🚀 Starting WonderKid Reading Game API...")
    logger.info(f"🌐 Server will start on port: {port}")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
