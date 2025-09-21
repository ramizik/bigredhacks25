import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Animated,
  Dimensions,
  Image,
  KeyboardAvoidingView,
  Modal,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import VideoPlayerScreen from './VideoPlayerScreen';

const { width, height } = Dimensions.get('window');

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
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
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
      setLoadingMessage("Creating your magical story...");

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
    setShowVideoPlayer(true);
  };

  const API_URL = 'https://bigredhacks25-331813490179.us-east4.run.app';

  const checkAndShowVideo = async () => {
    if (isCheckingVideoStatus) return;

    setIsCheckingVideoStatus(true);
    try {
      const storyId = sessionStoryIdRef.current || storyData.storyId || 'current_story';
      console.log(`🎬 Checking video status for story: ${storyId}`);
      const response = await fetch(`${API_URL}/api/video-status/${storyId}`);
      const data = await response.json();

      if (data.status === 'completed' && (data.video_url || data.gcs_url)) {
        console.log(`✅ Video ready! GCS URL: ${data.gcs_url}, Local URL: ${data.video_url}`);
        setShowVideoPlayer(true);
      } else if (data.status === 'processing' || data.status === 'started') {
        Alert.alert(
          "⏳ Still Brewing!",
          "Your magical video is still being created. It usually takes 2-3 minutes. Please try again in a moment!",
          [{ text: 'OK' }]
        );
      } else {
        console.log(`🎬 Video status: ${data.status}, letting VideoPlayerScreen handle it`);
        // Not started or error, let the VideoPlayerScreen handle triggering it
        setShowVideoPlayer(true);
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
          colors={['#f3e8ff', '#fce7f3']}
          style={styles.gradientContainer}
        >
          <ScrollView contentContainerStyle={styles.inputScrollContainer}>
            {/* Header */}
            <View style={styles.headerContainer}>
              <View style={styles.headerIconContainer}>
                <LinearGradient
                  colors={['#8b5cf6', '#ec4899']}
                  style={styles.headerIcon}
                >
                  <Ionicons name="sparkles" size={40} color="white" />
                </LinearGradient>
              </View>
              <Text style={styles.headerTitle}>Create Your Story!</Text>
              <Text style={styles.headerSubtitle}>What adventure would you like to experience today?</Text>
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
                colors={['#8b5cf6', '#ec4899']}
                style={styles.startButtonGradient}
              >
                <Text style={styles.startButtonText}>
                  Start My Story
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
          colors={['#dbeafe', '#f3e8ff', '#fce7f3']}
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
                colors={['#3b82f6', '#8b5cf6', '#ec4899']}
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
          colors={['#e0f2fe', '#f0fdf4']}
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
                    colors={['#10b981', '#3b82f6']}
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
                colors={['#fef3c7', '#fce7f3', '#e0e7ff']}
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
                colors={['#10b981', '#3b82f6']}
                style={styles.nextButtonGradient}
              >
                <Text style={styles.nextButtonEmoji}>🐰</Text>
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
          colors={['#fef3c7', '#fee2e2']}
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
                      colors={['#f97316', '#dc2626']}
                      style={styles.choiceNumber}
                    >
                      <Text style={styles.choiceNumberText}>{index + 1}</Text>
                    </LinearGradient>
                  </View>
                  <Text style={styles.choiceText}>{choice}</Text>
                  <Ionicons name="arrow-forward" size={24} color="#f97316" />
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
          colors={['#fef3c7', '#fed7aa']}
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
                colors={['#dc2626', '#ec4899']}
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
                colors={['#8b5cf6', '#3b82f6']}
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

  return (
    <>
      {/* Video Player Modal */}
      <Modal
        visible={showVideoPlayer}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <VideoPlayerScreen
          storyId={sessionStoryIdRef.current || storyData.storyId || 'current_story'}
          onClose={() => {
            console.log(`📹 Closing video player for story: ${sessionStoryIdRef.current || storyData.storyId}`);
            setShowVideoPlayer(false);
          }}
          sceneCount={storyData.iteration}
        />
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
    color: '#7c3aed',
    marginBottom: 12,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 18,
    color: '#8b5cf6',
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
    shadowColor: '#3b82f6',
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
    color: '#1e40af',
    textAlign: 'center',
    marginBottom: 16,
    textShadowColor: 'rgba(59, 130, 246, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  loadingSubtitle: {
    fontSize: 20,
    color: '#6366f1',
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
    backgroundColor: '#8b5cf6',
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
    borderColor: '#8b5cf6',
    borderStyle: 'dashed',
  },
  illustrationEmoji: {
    fontSize: 64,
    marginBottom: 12,
  },
  illustrationText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#8b5cf6',
  },
  storyImage: {
    height: 192,
    borderRadius: 24,
    borderWidth: 3,
    borderColor: '#8b5cf6',
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
    color: '#ea580c',
    marginBottom: 12,
    textAlign: 'center',
  },
  choiceSubtitle: {
    fontSize: 18,
    color: '#fb923c',
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
    color: '#ea580c',
    marginBottom: 12,
    textAlign: 'center',
  },
  completeSubtitle: {
    fontSize: 18,
    color: '#fb923c',
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