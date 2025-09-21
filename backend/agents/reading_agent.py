"""
📚 WonderKid Reading Game AI Agent
A kid-friendly story generation system using Google GenAI

This system creates interactive children's stories with:
- Age-appropriate content generation
- Kid-friendly language and themes
- Interactive story choices
- Illustration prompts for scenes
- Video generation after 10 story iterations
"""

import json
import asyncio
import time
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Google AI imports
try:
    from google import genai
    from google.genai import types
    AI_AVAILABLE = True
    print("✅ Google GenAI SDK available")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ Google GenAI SDK not available. Install with: pip install google-genai")

# Import image generation agent
try:
    from image_agent import (
        generate_kid_friendly_image,
        generate_character_portrait,
        get_image_generation_status,
        clear_image_generation_state
    )
    IMAGE_AGENT_AVAILABLE = True
    print("✅ Image generation agent loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not import image agent: {e}")
    IMAGE_AGENT_AVAILABLE = False

# Import video generation agent
try:
    from video_agent import (
        generate_comprehensive_story_video,
        get_video_generation_status,
        clear_video_generation_state,
        VIDEO_GENERATION_AVAILABLE
    )
    VIDEO_AGENT_AVAILABLE = True
    print("✅ Video generation agent loaded successfully")
    logger.info("🎬 Video generation system ready for story compilation")
except ImportError as e:
    print(f"⚠️ Could not import video agent: {e}")
    logger.warning(f"⚠️ Video generation not available: {e}")
    VIDEO_AGENT_AVAILABLE = False
    VIDEO_GENERATION_AVAILABLE = False

# ============================================================================
# ENHANCED READING GAME STATE WITH VIDEO TRACKING
# ============================================================================

@dataclass
class StoryState:
    """Maintains story state across interactions with video generation tracking"""
    story_id: str = ""
    theme: str = ""
    age_group: str = "5-8"
    current_paragraph: int = 0
    paragraphs: List[str] = field(default_factory=list)
    choices: List[str] = field(default_factory=list)
    story_complete: bool = False
    illustration_prompts: List[str] = field(default_factory=list)
    user_choices_made: List[str] = field(default_factory=list)
    
    # Enhanced tracking for video generation
    scene_count: int = 0  # Track total scenes/iterations
    story_scenes: List[Dict] = field(default_factory=list)  # Store complete scene data
    generated_images: List[str] = field(default_factory=list)  # Track all generated images
    video_generation_triggered: bool = False
    generated_video: Optional[str] = None
    
    def add_scene(self, text: str, choices: List[str], image_file: Optional[str] = None):
        """Add a new scene to the story tracking"""
        self.scene_count += 1
        scene_data = {
            "scene_number": self.scene_count,
            "text": text,
            "choices": choices,
            "image_file": image_file,
            "timestamp": datetime.now().isoformat()
        }
        self.story_scenes.append(scene_data)
        
        if image_file:
            self.generated_images.append(image_file)
        
        logger.info(f"📖 Scene {self.scene_count} added to story")
        
        # Check if we've reached 10 iterations for video generation
        if self.scene_count == 10 and not self.video_generation_triggered:
            logger.info("🎬 Story reached 10 iterations - triggering video generation!")
            self.trigger_video_generation()
    
    def trigger_video_generation(self):
        """Trigger comprehensive video generation after 10 iterations"""
        if VIDEO_AGENT_AVAILABLE and not self.video_generation_triggered:
            self.video_generation_triggered = True
            logger.info(f"🎬 Initiating comprehensive video generation for story {self.story_id}")
            
            # Prepare to generate video with all context
            # This will be called asynchronously from the API
            return {
                "video_trigger": True,
                "scenes_ready": len(self.story_scenes),
                "images_available": len(self.generated_images),
                "message": "🎬 Your story video will be generated with all 10 scenes!"
            }
        return None

# Global story state
story_state = StoryState()

def generate_theme_specific_fallback(theme: str, age_group: str = "5-8") -> dict:
    """Generate theme-specific fallback story data instead of generic adventure"""

    # Determine theme-specific elements
    theme_lower = theme.lower()

    # Theme-specific vocabulary
    if any(word in theme_lower for word in ["space", "astronaut", "planet", "star", "rocket"]):
        setting = "cosmic space adventure"
        mood = "exciting"
        adjective = "stellar"
        action = "explore the galaxy"
    elif any(word in theme_lower for word in ["princess", "castle", "royal", "kingdom", "crown"]):
        setting = "royal kingdom adventure"
        mood = "elegant"
        adjective = "royal"
        action = "rule the kingdom"
    elif any(word in theme_lower for word in ["dragon", "magic", "wizard", "fantasy", "spell"]):
        setting = "magical fantasy world"
        mood = "mystical"
        adjective = "magical"
        action = "cast powerful spells"
    elif any(word in theme_lower for word in ["ocean", "sea", "underwater", "fish", "mermaid"]):
        setting = "underwater adventure"
        mood = "peaceful"
        adjective = "aquatic"
        action = "explore the deep seas"
    elif any(word in theme_lower for word in ["robot", "cyber", "future", "tech", "ai"]):
        setting = "futuristic tech world"
        mood = "innovative"
        adjective = "high-tech"
        action = "build amazing inventions"
    else:
        setting = f"{theme} adventure"
        mood = "happy"
        adjective = "wonderful"
        action = f"explore the {theme} world"

    return {
        "story_title": f"Your {theme.title()} Adventure",
        "paragraphs": [
            f"Once upon a time, there was a {adjective} {setting} waiting to unfold.",
            f"The story continues with {mood} moments and exciting discoveries.",
            f"Every choice you make shapes this amazing journey to {action}."
        ],
        "choices": [
            f"Explore the {adjective} path",
            "Meet new friends along the way",
            f"Discover hidden treasures in this {setting}"
        ],
        "illustration_prompts": [
            f"A {adjective} {setting} scene with bright colors",
            f"Friendly characters in a {mood} {theme} setting",
            f"An exciting discovery moment in the {theme} world"
        ],
        "mood": mood,
        "educational_theme": f"courage and friendship in {theme} adventures"
    }

def clean_and_parse_json(response_text: str, fallback_data: dict) -> dict:
    """Clean and parse JSON response with multiple fallback strategies"""
    try:
        # First try direct parsing
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    try:
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Remove any markdown code blocks
        cleaned_text = re.sub(r'```json\s*', '', cleaned_text)
        cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
        
        # Remove any text before the first {
        json_start = cleaned_text.find('{')
        if json_start > 0:
            cleaned_text = cleaned_text[json_start:]
        
        # Remove any text after the last }
        json_end = cleaned_text.rfind('}')
        if json_end >= 0:
            cleaned_text = cleaned_text[:json_end + 1]
        
        # Try parsing the cleaned text
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass
    
    try:
        # Try to fix common JSON issues
        fixed_text = response_text

        # Fix the specific issue with paragraphs field having invalid array structure
        # Look for pattern: ], [" and replace with ", "
        fixed_text = re.sub(r'\],\s*\[', ', ', fixed_text)

        # Also handle patterns like: "paragraphs": ["text1", "text2"], ["text3", "text4"]
        # This should become: "paragraphs": ["text1", "text2", "text3", "text4"]

        # More robust pattern to handle the paragraph array issue
        # Look for: "paragraphs": [...], [...] and merge the arrays
        paragraphs_pattern = r'"paragraphs":\s*\[([^\]]+)\],\s*\[([^\]]+)\]'
        def fix_paragraphs(match):
            first_array = match.group(1).strip()
            second_array = match.group(2).strip()
            return f'"paragraphs": [{first_array}, {second_array}]'

        if re.search(paragraphs_pattern, fixed_text):
            print(f"🔧 Found malformed paragraphs array - fixing...")
            fixed_text = re.sub(paragraphs_pattern, fix_paragraphs, fixed_text)
            print(f"📋 After paragraphs fix: {fixed_text[:300]}...")

        # Fix single quotes to double quotes
        fixed_text = re.sub(r"'([^']*)':", r'"\1":', fixed_text)
        fixed_text = re.sub(r":\s*'([^']*)'", r': "\1"', fixed_text)

        # Remove trailing commas
        fixed_text = re.sub(r',\s*}', '}', fixed_text)
        fixed_text = re.sub(r',\s*]', ']', fixed_text)

        print(f"🔧 Attempting to fix JSON with paragraph array issue...")
        print(f"📋 Fixed text preview: {fixed_text[:200]}...")

        return json.loads(fixed_text)
    except json.JSONDecodeError as e:
        print(f"❌ JSON fix attempt failed: {str(e)}")
        pass
    
    # Final attempt: Try to extract values manually if JSON parsing fails
    try:
        print(f"🔧 Attempting manual extraction as last resort...")

        # Extract story title
        title_match = re.search(r'"story_title":\s*"([^"]*)"', response_text)
        title = title_match.group(1) if title_match else fallback_data["story_title"]

        # Extract paragraphs with flexible pattern - find strings within paragraphs array
        paragraphs = []

        # First try to find the paragraphs array content even if malformed
        paragraphs_section = re.search(r'"paragraphs":\s*\[(.*?)(?:\],\s*\[.*?)?\]', response_text, re.DOTALL)
        if paragraphs_section:
            paragraph_content = paragraphs_section.group(1)
            # Extract all quoted strings from the paragraphs section
            paragraph_matches = re.findall(r'"([^"]{20,})"', paragraph_content)  # 20+ chars for story content
            if paragraph_matches:
                paragraphs = paragraph_matches

        # Fallback: look for any long quoted strings that look like story content
        if not paragraphs:
            all_quotes = re.findall(r'"([^"]{30,})"', response_text)  # 30+ chars likely story content
            paragraphs = all_quotes[:4] if all_quotes else fallback_data["paragraphs"]
        else:
            paragraphs = paragraphs if paragraphs else fallback_data["paragraphs"]

        # Extract choices
        choices = []
        choices_match = re.search(r'"choices":\s*\[(.*?)\]', response_text, re.DOTALL)
        if choices_match:
            choice_text = choices_match.group(1)
            choice_matches = re.findall(r'"([^"]+)"', choice_text)
            choices = choice_matches if len(choice_matches) >= 3 else fallback_data["choices"]
        else:
            choices = fallback_data["choices"]

        # Extract illustration prompts
        illustration_prompts = []
        prompts_match = re.search(r'"illustration_prompts":\s*\[(.*?)\]', response_text, re.DOTALL)
        if prompts_match:
            prompts_text = prompts_match.group(1)
            prompt_matches = re.findall(r'"([^"]+)"', prompts_text)
            illustration_prompts = prompt_matches if len(prompt_matches) >= 2 else fallback_data["illustration_prompts"]
        else:
            illustration_prompts = fallback_data["illustration_prompts"]

        # Extract mood
        mood_match = re.search(r'"mood":\s*"([^"]*)"', response_text)
        mood = mood_match.group(1) if mood_match else "happy"

        # Extract educational theme
        theme_match = re.search(r'"educational_theme":\s*"([^"]*)"', response_text)
        educational_theme = theme_match.group(1) if theme_match else fallback_data["educational_theme"]

        manual_data = {
            "story_title": title,
            "paragraphs": paragraphs,
            "choices": choices,
            "illustration_prompts": illustration_prompts,
            "mood": mood,
            "educational_theme": educational_theme
        }

        print(f"✅ Manual extraction successful! Title: {title}")
        return manual_data

    except Exception as extract_error:
        print(f"❌ Manual extraction also failed: {str(extract_error)}")

    # If all parsing attempts fail, return fallback data
    print(f"⚠️ All JSON parsing attempts failed. Using fallback data.")
    print(f"🔍 FULL Raw response for debugging:")
    print(f"📋 START_OF_RESPONSE")
    print(response_text)
    print(f"📋 END_OF_RESPONSE")
    print(f"📊 Response length: {len(response_text)} characters")
    print(f"🔤 Response type: {type(response_text)}")
    return fallback_data

def initialize_genai_client():
    """Initialize Google GenAI client following dd project pattern"""
    if not AI_AVAILABLE:
        return None
    
    try:
        # Use same pattern as dd project - create client directly
        client = genai.Client(
            api_key=os.getenv('GOOGLE_API_KEY'),
            http_options={'api_version': 'v1alpha'}
        )
        print("✅ GenAI client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ GenAI client initialization failed: {e}")
        return None

def generate_kid_story(theme: str, age_group: str = "5-8") -> Dict:
    """Generate a kid-friendly story based on theme using Google Gemini"""
    
    if not AI_AVAILABLE:
        error_msg = "Google GenAI SDK not available. Please install with: pip install google-genai"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    client = initialize_genai_client()
    if not client:
        error_msg = "Failed to initialize Google GenAI client. Check GOOGLE_API_KEY environment variable."
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    try:
        print(f"📚 Generating kid story for theme: {theme}")
        logger.info(f"📚 Starting new story generation - Theme: {theme}, Age: {age_group}")
        
        # Generate unique story ID
        generated_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        story_state.story_id = generated_id
        story_state.theme = theme
        story_state.age_group = age_group

        logger.info(f"📊 Generated story ID: '{generated_id}'")
        logger.info(f"📊 Story state ID after assignment: '{story_state.story_id}'")
        
        # Create age-appropriate prompt following dd project pattern
        system_prompt = f"""You are a professional children's book author creating stories for ages {age_group}.

REQUIREMENTS:
- Create a magical, positive story about: {theme}
- Use simple, age-appropriate language
- Include 3-4 short paragraphs (2-3 sentences each)
- Make it engaging but not scary
- Include friendly characters
- End with 3 choices for what happens next
- Make it educational and fun

IMPORTANT: Respond with ONLY valid JSON. No additional text before or after.

{{
    "story_title": "title here",
    "paragraphs": ["paragraph 1", "paragraph 2", "paragraph 3"],
    "choices": ["choice 1", "choice 2", "choice 3"],
    "illustration_prompts": ["scene 1 description", "scene 2 description", "scene 3 description"],
    "mood": "adventure",
    "educational_theme": "what kids learn from this story"
}}"""
        
        # Generate story using client - following dd project pattern
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=1000,
                response_mime_type="application/json"
            )
        )
        
        # Parse response with robust JSON cleaning
        fallback_story = generate_theme_specific_fallback(theme, age_group)
        
        story_data = clean_and_parse_json(response.text, fallback_story)
        
        # Update story state
        story_state.paragraphs = story_data.get("paragraphs", [])
        story_state.choices = story_data.get("choices", [])
        story_state.illustration_prompts = story_data.get("illustration_prompts", [])
        story_state.current_paragraph = 0
        story_state.story_complete = False
        
        print(f"✅ Story generated successfully: {story_data.get('story_title', 'Untitled')}")
        
        # Generate immersive scene image based on the first paragraph
        image_result = None
        image_file = None
        if IMAGE_AGENT_AVAILABLE and story_data.get("paragraphs"):
            first_paragraph = story_data["paragraphs"][0]
            scene_context = f"Story theme: {theme}, Setting: {story_data.get('story_title', 'Adventure')}"
            
            print(f"🎨 Generating immersive scene image for first paragraph...")
            image_result = generate_kid_friendly_image(
                story_text=first_paragraph,
                scene_context=scene_context,
                age_group=age_group
            )
            
            if image_result.get("status") == "success":
                image_file = image_result.get('generated_file')
                print(f"✅ Scene image generated: {image_file}")
            else:
                print(f"⚠️ Scene image generation failed: {image_result.get('error')}")
        
        # Add first scene to story tracking
        full_text = " ".join(story_data.get("paragraphs", []))
        story_state.add_scene(
            text=full_text,
            choices=story_data.get("choices", []),
            image_file=image_file
        )
        
        logger.info(f"📚 Story initialized - ID: {story_state.story_id}, Scenes: {story_state.scene_count}/10")
        
        return {
            "status": "success",
            "story_data": story_data,
            "story_id": story_state.story_id,  # Include story_id in response for reliability
            "message": "AI story generated successfully!",
            "ai_powered": True,
            "image_generation": image_result,
            "story_progress": {
                "scene_count": story_state.scene_count,
                "video_at": 10,
                "progress_percentage": (story_state.scene_count / 10) * 100
            }
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse AI response as JSON: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Story generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

def continue_story_with_choice(choice: str) -> Dict:
    """Continue story based on user choice using Google Gemini"""
    
    if not AI_AVAILABLE:
        error_msg = "Google GenAI SDK not available. Please install with: pip install google-genai"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    client = initialize_genai_client()
    if not client:
        error_msg = "Failed to initialize Google GenAI client. Check GOOGLE_API_KEY environment variable."
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    try:
        print(f"📖 Continuing story with choice: {choice}")
        logger.info(f"📖 Story continuation - Scene {story_state.scene_count + 1}/10")
        
        # Add choice to history
        story_state.user_choices_made.append(choice)
        
        # Create continuation prompt
        system_prompt = f"""You are continuing a children's story for ages {story_state.age_group}.

STORY CONTEXT:
- Theme: {story_state.theme}
- Previous paragraphs: {' '.join(story_state.paragraphs)}
- User chose: {choice}

REQUIREMENTS:
- Continue the story based on the user's choice
- Add 2-3 new paragraphs
- Keep it age-appropriate and positive
- Create 3 new choices for what happens next
- Make it engaging and educational

IMPORTANT: Respond with ONLY valid JSON. No additional text before or after.

{{
    "continuation_paragraphs": ["new paragraph 1", "new paragraph 2"],
    "choices": ["new choice 1", "new choice 2", "new choice 3"],
    "illustration_prompts": ["new scene description"],
    "story_complete": false,
    "educational_message": "what kids learn from this part"
}}"""
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=800,
                response_mime_type="application/json"
            )
        )
        
        # Parse response with robust JSON cleaning
        fallback_continuation = {
            "continuation_paragraphs": [
                f"You chose to {choice}. The adventure continues with new discoveries ahead.",
                "Your decision leads to exciting new possibilities and wonderful surprises."
            ],
            "choices": [
                "Continue exploring",
                "Look for new friends", 
                "Discover something magical"
            ],
            "illustration_prompts": ["Adventure continues with new discoveries"],
            "story_complete": False,
            "educational_message": "Every choice leads to new adventures"
        }
        
        continuation_data = clean_and_parse_json(response.text, fallback_continuation)
        
        # Update story state
        new_paragraphs = continuation_data.get("continuation_paragraphs", [])
        story_state.paragraphs.extend(new_paragraphs)
        story_state.choices = continuation_data.get("choices", [])
        story_state.current_paragraph = len(story_state.paragraphs) - 1
        
        # Add new illustration prompts
        new_prompts = continuation_data.get("illustration_prompts", [])
        story_state.illustration_prompts.extend(new_prompts)
        
        
        # Generate immersive scene image for the new story continuation
        image_result = None
        image_file = None
        if IMAGE_AGENT_AVAILABLE and new_paragraphs:
            latest_paragraph = new_paragraphs[-1]  # Get the most recent paragraph
            
            # Create comprehensive story context for better image generation
            story_context = f"""
            Story Theme: {story_state.theme}
            Previous Story: {' '.join(story_state.paragraphs[:-len(new_paragraphs)])}
            Current Choice Made: {choice}
            New Story Development: {latest_paragraph}
            Story Progress: Paragraph {len(story_state.paragraphs)} of ongoing adventure
            Scene Number: {story_state.scene_count + 1}
            """
            
            image_result = generate_kid_friendly_image(
                story_text=latest_paragraph,
                scene_context=story_context,
                age_group=story_state.age_group
            )
            
            if image_result.get("status") == "success":
                image_file = image_result.get('generated_file')
            else:
                print(f"⚠️ Continuation scene image generation failed: {image_result.get('error')}")
        
        # Add new scene to story tracking
        full_continuation_text = " ".join(new_paragraphs)
        story_state.add_scene(
            text=full_continuation_text,
            choices=continuation_data.get("choices", []),
            image_file=image_file
        )
        
        # Check if video generation should be triggered (at 10 scenes)
        video_trigger_info = None
        if story_state.scene_count == 10 and story_state.video_generation_triggered:
            # Video was just triggered in this iteration, provide trigger info
            video_trigger_info = {
                "video_triggered": True,
                "message": "🎬 Congratulations! Your story has reached 10 scenes. A magical video is being created!",
                "scenes_included": story_state.scene_count,
                "images_available": len(story_state.generated_images)
            }
            logger.info(f"🎬 Video trigger info provided for story {story_state.story_id}")
        
        return {
            "status": "success",
            "story_id": story_state.story_id,  # Include story_id in response for reliability
            "continuation_data": continuation_data,
            "updated_story": {
                "paragraphs": story_state.paragraphs,
                "choices": story_state.choices,
                "current_paragraph": story_state.current_paragraph
            },
            "ai_powered": True,
            "image_generation": image_result,
            "story_progress": {
                "scene_count": story_state.scene_count,
                "video_at": 10,
                "progress_percentage": min((story_state.scene_count / 10) * 100, 100),
                "video_trigger": video_trigger_info
            }
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse AI response as JSON: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Story continuation failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

def generate_story_video_async() -> Dict:
    """Generate comprehensive story video with all 10 scenes"""
    if not VIDEO_AGENT_AVAILABLE:
        logger.error("❌ Video generation agent not available")
        return {
            "status": "error",
            "error": "Video generation system not available"
        }
    
    try:
        logger.info(f"🎬 Starting comprehensive video generation for story {story_state.story_id}")
        
        # Generate the video with all story context
        from video_agent import generate_comprehensive_story_video
        
        video_result = generate_comprehensive_story_video(
            story_scenes=story_state.story_scenes,
            story_theme=story_state.theme,
            story_id=story_state.story_id,
            age_group=story_state.age_group
        )
        
        # UNPACK the nested dictionary to fix the bug
        if video_result.get("status") == "success" and isinstance(video_result.get("generated_file"), dict):
            logger.info("📦 Unpacking nested video result...")
            unpacked_result = video_result["generated_file"]
            
            # Carry over top-level metadata
            for key, value in video_result.items():
                if key not in unpacked_result:
                    unpacked_result[key] = value
            
            video_result = unpacked_result
        
        if video_result.get("status") == "success":
            story_state.generated_video = video_result.get("generated_file")
            logger.info(f"✅ Story video generated successfully: {story_state.generated_video}")
        
        return video_result
        
    except Exception as e:
        error_msg = f"Video generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg
        }

def generate_illustration_prompt(paragraph_text: str, scene_number: int) -> str:
    """Generate kid-friendly illustration prompt for a story scene using Google Gemini"""
    
    if not AI_AVAILABLE:
        error_msg = "Google GenAI SDK not available. Please install with: pip install google-genai"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    client = initialize_genai_client()
    if not client:
        error_msg = "Failed to initialize Google GenAI client. Check GOOGLE_API_KEY environment variable."
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    try:
        system_prompt = f"""
        Create a detailed, kid-friendly illustration prompt for this story scene:
        "{paragraph_text}"
        
        REQUIREMENTS:
        - Make it colorful and magical
        - Include cute, friendly characters
        - Describe a scene that would appeal to children ages {story_state.age_group}
        - Keep it positive and non-scary
        - Make it detailed enough for an AI image generator
        
        Return ONLY the illustration prompt text, no additional formatting.
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=system_prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        error_msg = f"Illustration prompt generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)


def get_story_status() -> Dict:
    """Get current story status with video generation info"""
    return {
        "story_id": story_state.story_id,
        "theme": story_state.theme,
        "current_paragraph": story_state.current_paragraph,
        "total_paragraphs": len(story_state.paragraphs),
        "story_complete": story_state.story_complete,
        "choices_made": len(story_state.user_choices_made),
        "ai_available": AI_AVAILABLE,
        "scene_count": story_state.scene_count,
        "video_generation_triggered": story_state.video_generation_triggered,
        "generated_video": story_state.generated_video,
        "images_generated": len(story_state.generated_images),
        "video_progress": {
            "current_scene": story_state.scene_count,
            "scenes_needed_for_video": 10,
            "ready_for_video": story_state.scene_count >= 10,
            "percentage_to_video": min((story_state.scene_count / 10) * 100, 100)
        }
    }

def reset_story_state():
    """Reset story state for new story"""
    global story_state
    story_state = StoryState()
    
    # Clear image generation state if available
    if IMAGE_AGENT_AVAILABLE:
        clear_image_generation_state()
    
    # Clear video generation state if available  
    if VIDEO_AGENT_AVAILABLE:
        clear_video_generation_state()
    
    logger.info("🧹 Story state reset for new adventure")
    return {"status": "reset", "message": "Ready for new story"}
