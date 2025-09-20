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
        system_prompt = f"""
        You are a professional children's book author creating stories for ages {age_group}.
        
        REQUIREMENTS:
        - Create a magical, positive story about: {theme}
        - Use simple, age-appropriate language
        - Include 3-4 short paragraphs (2-3 sentences each)
        - Make it engaging but not scary
        - Include friendly characters
        - End with 3 choices for what happens next
        - Make it educational and fun
        
        FORMAT your response as JSON:
        {{
            "story_title": "title here",
            "paragraphs": ["paragraph 1", "paragraph 2", "paragraph 3"],
            "choices": ["choice 1", "choice 2", "choice 3"],
            "illustration_prompts": ["scene 1 description", "scene 2 description", "scene 3 description"],
            "mood": "adventure/magical/friendship",
            "educational_theme": "what kids learn from this story"
        }}
        """
        
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
        
        # Parse response
        story_data = json.loads(response.text)
        
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

def continue_story_with_choice(choice: str, choice_index: int) -> Dict:
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
        system_prompt = f"""
        You are continuing a children's story for ages {story_state.age_group}.
        
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
        
        FORMAT your response as JSON:
        {{
            "continuation_paragraphs": ["new paragraph 1", "new paragraph 2"],
            "choices": ["new choice 1", "new choice 2", "new choice 3"],
            "illustration_prompts": ["new scene description"],
            "story_complete": false,
            "educational_message": "what kids learn from this part"
        }}
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=800,
                response_mime_type="application/json"
            )
        )
        
        continuation_data = json.loads(response.text)
        
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
            scene_context = f"Story continuation, Current choice: {choice}, Theme: {story_state.theme}"
            
            print(f"🎨 Generating scene image for story continuation...")
            image_result = generate_kid_friendly_image(
                story_text=latest_paragraph,
                scene_context=scene_context,
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
