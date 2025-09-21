import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import * as WebBrowser from 'expo-web-browser';
import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Animated,
  Dimensions,
  Image,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

const { width, height } = Dimensions.get('window');

// Helper function to save image to gallery
const saveImageToGallery = async (imageUrl) => {
  if (!imageUrl) {
    console.log('⚠️ No image URL provided to saveImageToGallery');
    return;
  }
  
  try {
    const existingImages = await AsyncStorage.getItem('sessionImages');
    const imageArray = existingImages ? JSON.parse(existingImages) : [];
    
    // Avoid duplicates
    if (!imageArray.includes(imageUrl)) {
      imageArray.push(imageUrl);
      await AsyncStorage.setItem('sessionImages', JSON.stringify(imageArray));
      console.log('📸 Image saved to gallery! Total images:', imageArray.length);
      console.log('🖼️ Image URL:', imageUrl);
    } else {
      console.log('📸 Image already exists in gallery, skipping duplicate');
    }
  } catch (error) {
    console.error('❌ Failed to save image to gallery:', error);
  }
};

export default function StoryScreen() {
  const [phase, setPhase] = useState('input'); // 'input' | 'loading' | 'reading' | 'choosing' | 'complete'
  const [userInput, setUserInput] = useState('');
  const [storyData, setStoryData] = useState({
    paragraphs: [],
    currentParagraph: 0,
    iteration: 1,
    maxIterations: 10,
    choices: null,
    imageUrl: null,
    imageGenerated: false,
  });

  // Video generation states
  const [videoTriggered, setVideoTriggered] = useState(false);
  const [isCheckingVideoStatus, setIsCheckingVideoStatus] = useState(false);

  // Animation refs for loading screen
  const spinValue = useRef(new Animated.Value(0)).current;
  const pulseValue = useRef(new Animated.Value(1)).current;
  const fadeValue = useRef(new Animated.Value(0)).current;

  // Session story ID ref - tracks the authoritative backend story ID for this session
  const sessionStoryIdRef = useRef(null);
  const [loadingMessage, setLoadingMessage] = useState("Preparing your magical adventure...");

  // Animation effects for loading screen
  useEffect(() => {
    if (phase === 'loading') {
      // Start animations
      const spinAnimation = Animated.loop(
        Animated.timing(spinValue, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        })
      );
      
      const pulseAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseValue, {
            toValue: 1.2,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseValue, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      );
      
      const fadeAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(fadeValue, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(fadeValue, {
            toValue: 0.3,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      );

      // Start all animations
      spinAnimation.start();
      pulseAnimation.start();
      fadeAnimation.start();

      // Set a single, static loading message
      setLoadingMessage("Gemini is working on your story. Prepare to read and immerse in story now!");

      return () => {
        spinAnimation.stop();
        pulseAnimation.stop();
        fadeAnimation.stop();
      };
    }
  }, [phase, spinValue, pulseValue, fadeValue]);

  // Call backend API to create story
  const generateStory = async (theme) => {
    setPhase('loading');

    // Reset session state for new story
    sessionStoryIdRef.current = null;
    setVideoTriggered(false);

    try {
      // Call backend API
      const response = await fetch('https://bigredhacks25-331813490179.us-east4.run.app/api/generate-story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: theme,
          age_group: "5-8",
          reading_level: "beginner"
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Debug: Log the full response to see image data
      console.log('📱 Full API Response:', JSON.stringify(result, null, 2));
      console.log('🖼️ Image URL:', result.image_url);
      console.log('🎨 Image Generated:', result.image_generated);
      
      // Use real AI-generated story data - ALWAYS use backend story_id for session consistency
      let storyId = result.story_id;

      // Smart fallback: If backend doesn't provide story_id, generate one for this session
      if (!storyId || storyId.trim() === '') {
        console.warn('⚠️ Backend did not provide story_id! Generating fallback for session consistency.');
        console.warn('📋 Full backend response:', result);
        storyId = `story_${Date.now()}`;
        console.log(`🔧 Generated fallback story ID: ${storyId}`);
      }

      sessionStoryIdRef.current = storyId; // Store in ref for immediate access
      console.log(`📚 Story session created with ID: ${storyId}`);
      
      const aiStory = {
        paragraphs: result.paragraphs || [],
        currentParagraph: 0,
        choices: result.choices || [],
        iteration: 1,
        maxIterations: 10,
        storyTitle: result.story_title,
        mood: result.mood,
        educationalTheme: result.educational_theme,
        illustrationPrompts: result.illustration_prompts || [],
        imageUrl: result.image_url || null,
        imageGenerated: result.image_generated || false,
        storyId: storyId
      };
      
      setStoryData(aiStory);
      
      // Save image to gallery if available
      if (result.image_url) {
        console.log('🖼️ Initial story image detected:', result.image_url);
        saveImageToGallery(result.image_url);
      }
      
      setPhase('reading');
      
    } catch (error) {
      console.error('Error calling backend:', error);
      
      // Parse error response if available
      let errorMessage = 'Could not connect to the story server. Please check your internet connection and try again.';
      
      try {
        if (error.response) {
          const errorData = await error.response.json();
          errorMessage = errorData.detail?.message || errorData.detail || errorMessage;
        }
      } catch (parseError) {
        // Use default error message if parsing fails
      }
      
      Alert.alert(
        '❌ Story Generation Failed',
        errorMessage,
        [
          { text: 'Try Again', style: 'default', onPress: () => setPhase('input') },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
      setPhase('input');
    }
  };

  const handleNext = () => {
    if (storyData.currentParagraph < storyData.paragraphs.length - 1) {
      setStoryData(prev => ({
        ...prev,
        currentParagraph: prev.currentParagraph + 1
      }));
    } else if (storyData.choices && storyData.iteration < storyData.maxIterations) {
      setPhase('choosing');
    } else {
      setPhase('complete');
    }
  };

  const handleChoice = async (choiceIndex) => {
    setPhase('loading');
    
    try {
      // Call backend API to continue story with AI
      const response = await fetch('https://bigredhacks25-331813490179.us-east4.run.app/api/continue-story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          choice: storyData.choices[choiceIndex],
          story_id: sessionStoryIdRef.current || 'current_story', // Use session ref for immediate access
          current_paragraph: storyData.currentParagraph
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Debug: Log the continuation response
      console.log('📱 Story Continuation Response:', JSON.stringify(result, null, 2));
      console.log('🖼️ New Image URL:', result.image_url);
      console.log('🎨 New Image Generated:', result.image_generated);
      
      // Update story data with AI-generated continuation
      // ALWAYS use backend story_id for session consistency - backend is authoritative
      if (!result.story_id) {
        console.error('❌ Backend continue-story did not provide story_id! Using previous ID as fallback.');
        console.error('📋 Full backend response:', result);
      }
      const currentStoryId = result.story_id || storyData.storyId;
      // Update session ref if backend provided a story_id
      if (result.story_id) {
        sessionStoryIdRef.current = result.story_id;
      }
      console.log(`📖 Continuing story with backend ID: ${result.story_id}, using ID: ${currentStoryId}, iteration: ${storyData.iteration + 1}`);
      
      setStoryData(prev => ({
        ...prev,
        paragraphs: result.paragraphs || prev.paragraphs,
        currentParagraph: result.current_paragraph || prev.currentParagraph,
        choices: result.choices || null,
        iteration: prev.iteration + 1,
        imageUrl: result.image_url || prev.imageUrl,
        imageGenerated: result.image_generated || false,
        storyId: currentStoryId
      }));
      
      // Save new image to gallery if available
      if (result.image_url) {
        console.log('🖼️ New image detected during story continuation:', result.image_url);
        saveImageToGallery(result.image_url);
      }
      
      // Check for video generation trigger at 10th iteration
      if (result.video_trigger || storyData.iteration + 1 >= 10) {
        console.log('🎬 Video generation triggered!');
        setVideoTriggered(true);
        Alert.alert(
          '🎬 Amazing!',
          'You\'ve completed 10 scenes! Your story video is being created. This will take 2-3 minutes.',
          [
            {
              text: 'Watch Video',
              onPress: () => checkAndShowVideo()
            },
            {
              text: 'Continue Reading',
              style: 'cancel'
            }
          ]
        );
      }
      
      setPhase('reading');
      
    } catch (error) {
      console.error('Error continuing story:', error);
      
      // Fallback to simple continuation if API fails
      const newParagraph = `You chose to ${storyData.choices[choiceIndex].toLowerCase()}. The adventure continues as new wonders unfold before your eyes...`;
      
      setStoryData(prev => ({
        ...prev,
        paragraphs: [...prev.paragraphs, newParagraph],
        currentParagraph: prev.paragraphs.length,
        iteration: prev.iteration + 1,
        choices: prev.iteration + 1 >= prev.maxIterations ? null : [
          "Explore the glowing cave ahead",
          "Climb the ancient oak tree",
          "Follow the rainbow path"
        ]
      }));
      
      setPhase('reading');
    }
  };

  const resetStory = () => {
    setPhase('input');
    setUserInput('');
    setVideoTriggered(false);
    setStoryData({
      paragraphs: [],
      currentParagraph: 0,
      iteration: 1,
      maxIterations: 10,
      choices: null,
    });
  };

  const generateVideo = () => {
    Alert.alert(
      "🎬 Video Generation Started",
      "Your magical video is now being created! This will take 2-3 minutes. You can continue reading your story and check back later.",
      [{ text: 'OK' }]
    );
  };

  const API_URL = 'https://bigredhacks25-331813490179.us-east4.run.app';

  const checkAndShowVideo = async () => {
    if (isCheckingVideoStatus) return;

    setIsCheckingVideoStatus(true);
    try {
      const storyId = sessionStoryIdRef.current || storyData.storyId || 'current_story';
      console.log(`🎬 Checking video status for story: ${storyId}`);

      // Ensure story ID is properly URL encoded
      const encodedStoryId = encodeURIComponent(storyId);
      const response = await fetch(`${API_URL}/api/video-status/${encodedStoryId}`);

      // Better error handling for non-JSON responses
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Video status API error ${response.status}: ${errorText}`);
        throw new Error(`Video status API error: ${response.status}`);
      }

      const responseText = await response.text();
      console.log(`📋 Raw video status response: ${responseText.substring(0, 200)}...`);

      let data;
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        console.error(`❌ Failed to parse video status response as JSON: ${parseError.message}`);
        console.error(`📋 Raw response: ${responseText}`);
        throw new Error(`Invalid response from video status API: ${parseError.message}`);
      }

      if (data.status === 'completed' && (data.video_url || data.gcs_url)) {
        console.log(`✅ Video ready! GCS URL: ${data.gcs_url}, Local URL: ${data.video_url}`);

        // Prefer GCS URL for better browser compatibility
        const videoUrl = data.gcs_url || (data.video_url?.startsWith('http') ? data.video_url : `${API_URL}${data.video_url}`);

        console.log(`🌐 Opening video in browser: ${videoUrl}`);

        await WebBrowser.openBrowserAsync(videoUrl, {
          presentationStyle: WebBrowser.WebBrowserPresentationStyle.PAGE_SHEET,
          controlsColor: '#f35b04',
        });
      } else if (data.status === 'processing' || data.status === 'started') {
        Alert.alert(
          "⏳ Still Brewing!",
          "Your magical video is still being created. It usually takes 2-3 minutes. Please try again in a moment!",
          [{ text: 'OK' }]
        );
      } else if (data.status === 'error') {
        console.error(`❌ Video status error: ${data.message}`);
        Alert.alert(
          "🚫 Video Error",
          `There was an issue checking your video status: ${data.message}. Please try again.`,
          [{ text: 'OK' }]
        );
      } else {
        console.log(`🎬 Video status: ${data.status}, triggering generation...`);
        Alert.alert(
          "🎬 Video Not Ready",
          "Your video hasn't been generated yet. Let's create it now! This usually takes 2-3 minutes.",
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Generate Video', onPress: generateVideo }
          ]
        );
      }
    } catch (error) {
      console.error("Error checking video status:", error);
      Alert.alert("Error", "Could not check the video status. Please try again later.");
    } finally {
      setIsCheckingVideoStatus(false);
    }
  };

  // Input Phase
  if (phase === 'input') {
    return (
      <SafeAreaView style={styles.container}>
        <KeyboardAvoidingView 
          style={styles.keyboardContainer} 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
        <LinearGradient
          colors={['#7fdeff', '#a5e6ba']}
          style={styles.gradientContainer}
        >
          <ScrollView contentContainerStyle={styles.inputScrollContainer}>
            {/* Header */}
            <View style={styles.headerContainer}>
              <View style={styles.headerIconContainer}>
                <LinearGradient
                  colors={['#9683ec', '#5d16a6']}
                  style={styles.headerIcon}
                >
                  <Ionicons name="sparkles" size={40} color="white" />
                </LinearGradient>
              </View>
              <Text style={styles.headerTitle}>Create Your Story!</Text>
              <Text style={styles.headerSubtitle}>What adventure would you like to experience today?{'\n\n'}💡 Try: "A brave knight in a magical castle", "A space explorer on Mars", "A mermaid under the sea", or "A detective solving mysteries"</Text>
            </View>

            {/* Input Area */}
            <View style={styles.inputContainer}>
              <View style={styles.inputCard}>
                <TextInput
                  value={userInput}
                  onChangeText={setUserInput}
                  placeholder="I want to go on an adventure with a magic dragon..."
                  placeholderTextColor="#9ca3af"
                  style={styles.textInput}
                  multiline
                  maxLength={200}
                  textAlignVertical="top"
                />
                <Text style={styles.characterCount}>
                  {userInput.length}/200
                </Text>
              </View>
            </View>

            {/* Start Button */}
            <TouchableOpacity
              onPress={() => generateStory(userInput)}
              style={styles.startButton}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#9683ec', '#5d16a6']}
                style={styles.startButtonGradient}
              >
                <Text style={styles.startButtonText}>
                  Start Reading Journey
                </Text>
                <Ionicons 
                  name="arrow-forward" 
                  size={24} 
                  color="white" 
                />
              </LinearGradient>
            </TouchableOpacity>
          </ScrollView>
        </LinearGradient>
        </KeyboardAvoidingView>
      </SafeAreaView>
    );
  }

  // Loading Phase
  if (phase === 'loading') {
    const spin = spinValue.interpolate({
      inputRange: [0, 1],
      outputRange: ['0deg', '360deg'],
    });

    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient
          colors={['#7fdeff', '#a5e6ba', '#9683ec']}
          style={styles.gradientContainer}
        >
        <View style={styles.loadingContainer}>
          {/* Animated Magic Circle */}
          <View style={styles.loadingIconContainer}>
            <Animated.View
              style={[
                styles.magicCircle,
                {
                  transform: [{ rotate: spin }, { scale: pulseValue }],
                },
              ]}
            >
              <LinearGradient
                colors={['#9683ec', '#5d16a6', '#f35b04']}
                style={styles.loadingIcon}
              >
                <View style={styles.spinningLogo} />
              </LinearGradient>
            </Animated.View>
            
            {/* Floating Magic Particles */}
            <Animated.View
              style={[
                styles.magicParticle1,
                {
                  opacity: fadeValue,
                  transform: [{ scale: pulseValue }],
                },
              ]}
            >
              <Text style={styles.particleEmoji}>✨</Text>
            </Animated.View>
            <Animated.View
              style={[
                styles.magicParticle2,
                {
                  opacity: fadeValue,
                  transform: [{ scale: pulseValue }],
                },
              ]}
            >
              <Text style={styles.particleEmoji}>🌟</Text>
            </Animated.View>
            <Animated.View
              style={[
                styles.magicParticle3,
                {
                  opacity: fadeValue,
                  transform: [{ scale: pulseValue }],
                },
              ]}
            >
              <Text style={styles.particleEmoji}>💫</Text>
            </Animated.View>
          </View>
          
          {/* Static Loading Messages */}
          <View>
            <Text style={styles.loadingTitle}>Creating Your Story...</Text>
            <Text style={styles.loadingSubtitle}>{loadingMessage}</Text>
          </View>
        </View>
        </LinearGradient>
      </SafeAreaView>
    );
  }

  // Reading Phase
  if (phase === 'reading') {
    const currentText = storyData.paragraphs[storyData.currentParagraph];
    const progress = (storyData.iteration / storyData.maxIterations) * 100;

    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient
          colors={['#7fdeff', '#a5e6ba']}
          style={styles.gradientContainer}
        >
        <ScrollView style={styles.readingContainer}>
          {/* Progress Bar */}
          <View style={styles.progressContainer}>
            <View style={styles.progressCard}>
              <View style={styles.progressHeader}>
                <Text style={styles.progressLabel}>Story Progress</Text>
                <View style={styles.progressRight}>
                  <Text style={styles.progressNumbers}>{storyData.iteration}/{storyData.maxIterations}</Text>
                  {videoTriggered && (
                    <TouchableOpacity 
                      onPress={checkAndShowVideo}
                      disabled={isCheckingVideoStatus}
                      style={styles.watchVideoButton}
                    >
                      {isCheckingVideoStatus 
                        ? <ActivityIndicator size="small" color="#fff" />
                        : <Text style={styles.watchVideoText}>🎬 Watch Video</Text>
                      }
                    </TouchableOpacity>
                  )}
                </View>
              </View>
              <View style={styles.progressBarBg}>
                <View style={[styles.progressBar, { width: `${progress}%` }]}>
                  <LinearGradient
                    colors={['#a5e6ba', '#9683ec']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.progressBarGradient}
                  />
                </View>
              </View>
            </View>
          </View>

          {/* Story Illustration */}
          <View style={styles.illustrationContainer}>
            {storyData.imageGenerated && storyData.imageUrl ? (
              <Image
                source={{ uri: `https://bigredhacks25-331813490179.us-east4.run.app${storyData.imageUrl}` }}
                style={styles.storyImage}
                resizeMode="cover"
                onLoad={() => {
                  console.log('✅ Image loaded successfully:', storyData.imageUrl);
                }}
                onError={(error) => {
                  console.log('❌ Image load error:', error);
                  console.log('🔗 Attempted URL:', `https://bigredhacks25-331813490179.us-east4.run.app${storyData.imageUrl}`);
                  // Fallback to placeholder if image fails to load
                }}
              />
            ) : (
              <LinearGradient
                colors={['#7fdeff', '#a5e6ba', '#9683ec']}
                style={styles.illustrationPlaceholder}
              >
                <Text style={styles.illustrationEmoji}>🌟</Text>
                <Text style={styles.illustrationText}>
                  {storyData.imageGenerated ? 'Loading Image...' : `Story Scene ${storyData.currentParagraph + 1}`}
                </Text>
              </LinearGradient>
            )}
          </View>

          {/* Text Area */}
          <View style={styles.storyTextContainer}>
            <View style={styles.storyTextCard}>
              <Text style={styles.storyText}>{currentText}</Text>
            </View>
          </View>

          {/* Next Button */}
          <View style={styles.nextButtonContainer}>
            <TouchableOpacity
              onPress={handleNext}
              style={styles.nextButton}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#a5e6ba', '#9683ec']}
                style={styles.nextButtonGradient}
              >
                <Ionicons name="arrow-forward" size={20} color="white" />
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </ScrollView>
        </LinearGradient>
      </SafeAreaView>
    );
  }

  // Choice Phase
  if (phase === 'choosing') {
    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient
          colors={['#7fdeff', '#a5e6ba']}
          style={styles.gradientContainer}
        >
        <ScrollView style={styles.choiceContainer}>
          <View style={styles.choiceHeader}>
            <Text style={styles.choiceTitle}>Choose Your Path!</Text>
            <Text style={styles.choiceSubtitle}>What happens next in your adventure?</Text>
          </View>

          <View style={styles.choicesContainer}>
            {storyData.choices?.map((choice, index) => (
              <TouchableOpacity
                key={index}
                onPress={() => handleChoice(index)}
                style={styles.choiceButton}
                activeOpacity={0.8}
              >
                <View style={styles.choiceCard}>
                  <View style={styles.choiceNumberContainer}>
                    <LinearGradient
                      colors={['#f35b04', '#ef233c']}
                      style={styles.choiceNumber}
                    >
                      <Text style={styles.choiceNumberText}>{index + 1}</Text>
                    </LinearGradient>
                  </View>
                  <Text style={styles.choiceText}>{choice}</Text>
                  <Ionicons name="arrow-forward" size={24} color="#f35b04" />
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
        </LinearGradient>
      </SafeAreaView>
    );
  }

  // Complete Phase
  if (phase === 'complete') {
    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient
          colors={['#7fdeff', '#a5e6ba']}
          style={styles.gradientContainer}
        >
        <View style={styles.completeContainer}>
          <View style={styles.completeContent}>
            <Text style={styles.completeEmoji}>🎉</Text>
            <Text style={styles.completeTitle}>Story Complete!</Text>
            <Text style={styles.completeSubtitle}>You've created an amazing adventure!</Text>
          </View>

          <View style={styles.completeButtonsContainer}>
            <TouchableOpacity
              onPress={checkAndShowVideo}
              disabled={isCheckingVideoStatus}
              style={styles.actionButton}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#ef233c', '#f35b04']}
                style={styles.actionButtonGradient}
              >
                {isCheckingVideoStatus ? (
                  <ActivityIndicator size="large" color="#fff" />
                ) : (
                  <>
                    <Ionicons name="play" size={24} color="white" />
                    <Text style={styles.actionButtonText}>Create Story Video</Text>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={resetStory}
              style={styles.actionButton}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#9683ec', '#5d16a6']}
                style={styles.actionButtonGradient}
              >
                <Ionicons name="refresh" size={24} color="white" />
                <Text style={styles.actionButtonText}>Create New Story</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
        </LinearGradient>
      </SafeAreaView>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 10,
  },
  keyboardContainer: {
    flex: 1,
  },
  gradientContainer: {
    flex: 1,
  },
  inputScrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24,
  },
  headerContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  headerIconContainer: {
    marginBottom: 16,
  },
  headerIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#9683ec',
    marginBottom: 12,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 18,
    color: '#5d16a6',
    textAlign: 'center',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 32,
  },
  inputCard: {
    backgroundColor: 'white',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 12,
  },
  textInput: {
    height: 120,
    fontSize: 18,
    color: '#374151',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 16,
    padding: 16,
    textAlignVertical: 'top',
  },
  characterCount: {
    textAlign: 'right',
    marginTop: 8,
    fontSize: 14,
    color: '#6b7280',
  },
  startButton: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  startButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 32,
    minHeight: 70,
  },
  startButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginRight: 12,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  loadingIconContainer: {
    marginBottom: 40,
    position: 'relative',
  },
  magicCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#9683ec',
    shadowOffset: {
      width: 0,
      height: 12,
    },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 12,
  },
  spinningLogo: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    shadowColor: 'rgba(255, 255, 255, 0.5)',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.8,
    shadowRadius: 4,
    elevation: 4,
  },
  magicParticle1: {
    position: 'absolute',
    top: -20,
    right: -10,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  magicParticle2: {
    position: 'absolute',
    bottom: -15,
    left: -15,
    width: 35,
    height: 35,
    justifyContent: 'center',
    alignItems: 'center',
  },
  magicParticle3: {
    position: 'absolute',
    top: 20,
    left: -25,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  particleEmoji: {
    fontSize: 24,
  },
  loadingTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#5d16a6',
    textAlign: 'center',
    marginBottom: 16,
    textShadowColor: 'rgba(59, 130, 246, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  loadingSubtitle: {
    fontSize: 20,
    color: '#9683ec',
    textAlign: 'center',
    fontWeight: '600',
    marginBottom: 32,
    lineHeight: 28,
  },
  readingContainer: {
    flex: 1,
    padding: 24,
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  progressRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  progressNumbers: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  watchVideoButton: {
    backgroundColor: '#9683ec',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  watchVideoText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  progressBarBg: {
    width: '100%',
    height: 12,
    backgroundColor: '#e5e7eb',
    borderRadius: 6,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    borderRadius: 6,
  },
  progressBarGradient: {
    flex: 1,
  },
  illustrationContainer: {
    marginBottom: 16,
  },
  illustrationPlaceholder: {
    height: 192,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#9683ec',
    borderStyle: 'dashed',
  },
  illustrationEmoji: {
    fontSize: 64,
    marginBottom: 12,
  },
  illustrationText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#5d16a6',
  },
  storyImage: {
    height: 192,
    borderRadius: 24,
    borderWidth: 3,
    borderColor: '#9683ec',
  },
  storyTextContainer: {
    flex: 1,
    marginBottom: 16,
  },
  storyTextCard: {
    backgroundColor: '#eff6ff',
    borderRadius: 24,
    padding: 24,
    minHeight: 120,
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#93c5fd',
  },
  storyText: {
    fontSize: 20,
    lineHeight: 30,
    color: '#374151',
    fontWeight: '500',
    textAlign: 'center',
  },
  nextButtonContainer: {
    alignItems: 'center',
    paddingBottom: 20,
  },
  nextButton: {
    borderRadius: 40,
    overflow: 'hidden',
  },
  nextButtonGradient: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  nextButtonEmoji: {
    fontSize: 24,
    marginBottom: 4,
  },
  choiceContainer: {
    flex: 1,
    padding: 24,
  },
  choiceHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  choiceTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#f35b04',
    marginBottom: 12,
    textAlign: 'center',
  },
  choiceSubtitle: {
    fontSize: 18,
    color: '#f35b04',
    textAlign: 'center',
  },
  choicesContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  choiceButton: {
    marginBottom: 16,
    borderRadius: 24,
    overflow: 'hidden',
  },
  choiceCard: {
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 24,
    borderWidth: 4,
    borderColor: '#fed7aa',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 12,
  },
  choiceNumberContainer: {
    marginRight: 16,
  },
  choiceNumber: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  choiceNumberText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  choiceText: {
    flex: 1,
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
  },
  completeContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  completeContent: {
    alignItems: 'center',
    marginBottom: 32,
  },
  completeEmoji: {
    fontSize: 80,
    marginBottom: 16,
  },
  completeTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#f35b04',
    marginBottom: 12,
    textAlign: 'center',
  },
  completeSubtitle: {
    fontSize: 18,
    color: '#f35b04',
    textAlign: 'center',
  },
  completeButtonsContainer: {
    width: '100%',
    maxWidth: 320,
  },
  actionButton: {
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
  },
  actionButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 24,
    minHeight: 70,
  },
  actionButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginLeft: 12,
  },
});