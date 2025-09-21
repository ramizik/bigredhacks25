# 📚 WonderKid: AI-Powered Interactive Reading Adventure for Kids

<div align="center">
  <img src="frontend/WonderKid/assets/icon.png" alt="WonderKid Logo" width="120" height="120">
  
  **Transform reading into an interactive adventure with AI-powered storytelling**
  
  [![React Native](https://img.shields.io/badge/React%20Native-0.72-blue.svg)](https://reactnative.dev/)
  [![Expo](https://img.shields.io/badge/Expo-49.0-black.svg)](https://expo.dev/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
  [![Google AI](https://img.shields.io/badge/Google%20AI-Gemini%20%7C%20Imagen%20%7C%20Veo-orange.svg)](https://ai.google.dev/)
  [![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/atlas)
</div>

## 🌟 Overview

WonderKid is a revolutionary AI-powered reading game designed specifically for children aged 5-8. By combining Google's Gemini AI, Imagen, and Veo 2.0, it transforms reading from a passive activity into an interactive adventure that sparks creativity, improves literacy skills, and makes learning fun.

### ✨ Key Features

- 🤖 **AI Story Generation**: Create personalized stories from any theme using Google Gemini
- 🎨 **Dynamic Illustrations**: AI-generated artwork for every story scene with Google Imagen
- 🎭 **Interactive Choices**: Story branching system that lets children shape their adventure
- 🎬 **Video Compilation**: Automatic video creation using Google Veo 2.0 after 6 scenes
- 📱 **Mobile-First Design**: Optimized React Native interface for young users
- 📊 **Progress Tracking**: Comprehensive analytics and achievement system
- 🏆 **Gamified Learning**: Rewards and milestones to motivate continued reading

## 🏗️ Project Structure

```
bigredhacks25/
├── 📱 frontend/
│   └── WonderKid/                    # React Native Expo App
│       ├── App.js                    # Main app component with navigation
│       ├── app.json                  # Expo configuration
│       ├── package.json              # Frontend dependencies
│       ├── assets/                   # App icons and images
│       └── components/               # React Native components
│           ├── StoryScreen.js        # Main story reading interface
│           ├── VideoPlayerScreen.js  # Video playback component
│           ├── HistoryScreen.js      # Reading history and progress
│           └── ProfileScreen.js      # User profile and achievements
├── 🚀 backend/                       # FastAPI Backend
│   ├── app.py                        # Main FastAPI application
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Container configuration
│   ├── cloudbuild.yaml              # Google Cloud Build config
│   ├── gcs_helper.py                 # Google Cloud Storage utilities
│   └── agents/                       # AI Agent Modules
│       ├── reading_agent.py          # Story generation with Gemini
│       ├── image_agent.py            # Illustration generation with Imagen
│       └── video_agent.py            # Video compilation with Veo 2.0
├── 📖 dd/                           # Reference Project (dreamdirector)
│   └── [Reference implementation patterns]
└── 📄 README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.9+
- **Expo CLI**: `npm install -g @expo/cli`
- **Google Cloud Account** with AI APIs enabled
- **MongoDB Atlas** account

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bigredhacks25.git
cd bigredhacks25
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_gemini_api_key
# MONGODB_URI=your_mongodb_connection_string
# GOOGLE_SERVICE_ACCOUNT_JSON=your_service_account_json

# Run the backend server
python app.py
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend/WonderKid

# Install dependencies
npm install

# Start Expo development server
npx expo start
```

### 4. Mobile App

- Install **Expo Go** on your mobile device
- Scan the QR code from the terminal
- The app will load on your device

## 🛠️ Tech Stack

### Frontend
- **React Native Expo** - Cross-platform mobile development
- **Expo Linear Gradient** - Beautiful gradient effects
- **React Navigation** - Screen navigation
- **AsyncStorage** - Local data persistence
- **Expo Video** - Video playback capabilities

### Backend
- **FastAPI** - High-performance Python web framework
- **Google GenAI SDK** - Gemini, Imagen, and Veo integration
- **MongoDB** - NoSQL database for user data
- **Google Cloud Storage** - File storage for images and videos
- **Uvicorn** - ASGI server for production

### AI Services
- **Google Gemini** - Story generation and content creation
- **Google Imagen** - AI-powered illustration generation
- **Google Veo 2.0** - Video compilation and generation

### Deployment
- **Google Cloud Run** - Backend hosting
- **Expo Application Services** - Mobile app distribution
- **MongoDB Atlas** - Managed database
- **Docker** - Containerization

## 📱 How It Works

### 1. Story Creation
Children input their story theme (e.g., "A brave knight in a magical castle"), and our AI generates an age-appropriate interactive story with multiple choice points.

### 2. Interactive Reading
As children read, they make choices that shape the narrative. Each choice triggers AI-generated story continuation and new illustrations.

### 3. Visual Experience
Every story scene gets a custom AI-generated illustration that matches the narrative and maintains visual consistency.

### 4. Video Compilation
After 6 story scenes, the system automatically compiles everything into a complete video that children can watch and share.

### 5. Progress Tracking
The app tracks reading time, story completion, and achievements to motivate continued learning.

## 🔧 API Endpoints

### Story Management
- `POST /api/generate-story` - Create new story from theme
- `POST /api/continue-story` - Continue story with user choice
- `GET /api/story-status` - Get current story progress

### Media Generation
- `POST /api/generate-scene-image` - Generate illustration for scene
- `POST /api/generate-story-video` - Create video compilation
- `GET /api/video-status/{story_id}` - Check video generation status

### User Progress
- `POST /api/save-progress` - Save reading progress
- `GET /api/user-progress/{user_id}` - Get user statistics
- `GET /api/user-stories/{user_id}` - Get reading history

## 🎯 Key Features Explained

### AI Story Generation
Our reading agent uses Google Gemini to create engaging, age-appropriate stories that adapt to children's interests and reading levels.

```python
# Example story generation
def generate_kid_story(theme: str, age_group: str):
    prompt = f"Create an interactive children's story about {theme} for ages {age_group}..."
    story = gemini_client.generate_content(prompt)
    return process_story_content(story)
```

### Interactive Choices
The choice system creates meaningful story branching that responds to children's decisions, making each reading experience unique.

### Visual Content
Google Imagen generates custom illustrations for every story scene, ensuring visual consistency and age-appropriate content.

### Video Compilation
After sufficient story content, Google Veo 2.0 compiles everything into a cinematic video experience.

## 🚀 Deployment

### Backend (Google Cloud Run)
```bash
# Build and deploy to Google Cloud Run
gcloud builds submit --config cloudbuild.yaml
gcloud run deploy wonderkid-api --source .
```

### Frontend (Expo)
```bash
# Build for production
expo build:android
expo build:ios

# Or use EAS Build
eas build --platform all
```

## 📊 Performance & Monitoring

- **Real-time logging** with emoji indicators for easy debugging
- **Health check endpoints** for service monitoring
- **Error handling** with graceful fallbacks
- **Progress tracking** for user engagement analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI** for providing powerful AI services (Gemini, Imagen, Veo)
- **Expo** for the excellent React Native development platform
- **FastAPI** for the high-performance Python web framework
- **MongoDB** for flexible data storage solutions
- **Big Red Hacks 2025** for the hackathon platform and inspiration

## 📞 Support

For support, email support@wonderkid.app or join our Discord community.

---

<div align="center">
  <p>Made with ❤️ for children's education and literacy development</p>
  <p>© 2025 WonderKid Development Team</p>
</div>