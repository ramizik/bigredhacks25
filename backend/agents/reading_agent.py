"""
📚 WonderKid Reading Game AI Agent
A kid-friendly story generation system using Google GenAI

This system creates interactive children's stories with:
- Age-appropriate content generation
- Kid-friendly language and themes
- Interactive story choices
- Illustration prompts for scenes
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

# Load environment variables
load_dotenv()

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

# ============================================================================
# READING GAME STATE
# ============================================================================

@dataclass
class StoryState:
    """Maintains story state across interactions"""
    story_id: str = ""
    theme: str = ""
    age_group: str = "5-8"
    current_paragraph: int = 0
    paragraphs: List[str] = field(default_factory=list)
    choices: List[str] = field(default_factory=list)
    story_complete: bool = False
    illustration_prompts: List[str] = field(default_factory=list)
    user_choices_made: List[str] = field(default_factory=list)

# Global story state
story_state = StoryState()

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
        
        # Fix single quotes to double quotes
        fixed_text = re.sub(r"'([^']*)':", r'"\1":', fixed_text)
        fixed_text = re.sub(r":\s*'([^']*)'", r': "\1"', fixed_text)
        
        # Remove trailing commas
        fixed_text = re.sub(r',\s*}', '}', fixed_text)
        fixed_text = re.sub(r',\s*]', ']', fixed_text)
        
        return json.loads(fixed_text)
    except json.JSONDecodeError:
        pass
    
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
        fallback_story = {
            "story_title": f"Your {theme.title()} Adventure",
            "paragraphs": [
                f"Once upon a time, there was a wonderful {theme} adventure waiting to unfold.",
                "The story continues with magical moments and exciting discoveries.",
                "Every choice you make shapes this amazing journey."
            ],
            "choices": [
                "Explore the magical path",
                "Meet new friends along the way", 
                "Discover hidden treasures"
            ],
            "illustration_prompts": [
                f"A magical {theme} adventure scene with bright colors",
                "Friendly characters in a whimsical setting",
                "An exciting discovery moment"
            ],
            "mood": "adventure",
            "educational_theme": "courage and friendship"
        }
        
        story_data = clean_and_parse_json(response.text, fallback_story)
        
        # Update story state
        story_state.theme = theme
        story_state.age_group = age_group
        story_state.paragraphs = story_data.get("paragraphs", [])
        story_state.choices = story_data.get("choices", [])
        story_state.illustration_prompts = story_data.get("illustration_prompts", [])
        story_state.current_paragraph = 0
        story_state.story_complete = False
        
        print(f"✅ Story generated successfully: {story_data.get('story_title', 'Untitled')}")
        
        # Generate immersive scene image based on the first paragraph
        image_result = None
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
                print(f"✅ Scene image generated: {image_result.get('generated_file')}")
            else:
                print(f"⚠️ Scene image generation failed: {image_result.get('error')}")
        
        return {
            "status": "success",
            "story_data": story_data,
            "message": "AI story generated successfully!",
            "ai_powered": True,
            "image_generation": image_result
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
        
        print(f"✅ Story continued successfully")
        
        # Generate immersive scene image for the new story continuation
        image_result = None
        if IMAGE_AGENT_AVAILABLE and new_paragraphs:
            latest_paragraph = new_paragraphs[-1]  # Get the most recent paragraph
            
            # Create comprehensive story context for better image generation
            story_context = f"""
            Story Theme: {story_state.theme}
            Previous Story: {' '.join(story_state.paragraphs[:-len(new_paragraphs)])}
            Current Choice Made: {choice}
            New Story Development: {latest_paragraph}
            Story Progress: Paragraph {len(story_state.paragraphs)} of ongoing adventure
            """
            
            print(f"🎨 Generating scene image for story continuation with full context...")
            image_result = generate_kid_friendly_image(
                story_text=latest_paragraph,
                scene_context=story_context,
                age_group=story_state.age_group
            )
            
            if image_result.get("status") == "success":
                print(f"✅ Continuation scene image generated: {image_result.get('generated_file')}")
            else:
                print(f"⚠️ Continuation scene image generation failed: {image_result.get('error')}")
        
        return {
            "status": "success",
            "continuation_data": continuation_data,
            "updated_story": {
                "paragraphs": story_state.paragraphs,
                "choices": story_state.choices,
                "current_paragraph": story_state.current_paragraph
            },
            "ai_powered": True,
            "image_generation": image_result
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse AI response as JSON: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Story continuation failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

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
    """Get current story status"""
    return {
        "story_id": story_state.story_id,
        "theme": story_state.theme,
        "current_paragraph": story_state.current_paragraph,
        "total_paragraphs": len(story_state.paragraphs),
        "story_complete": story_state.story_complete,
        "choices_made": len(story_state.user_choices_made),
        "ai_available": AI_AVAILABLE
    }
