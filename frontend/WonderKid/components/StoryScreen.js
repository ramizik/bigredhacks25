import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useState } from 'react';
import {
    Alert,
    Dimensions,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';

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
  });

  // Call backend API to create story
  const generateStory = async (theme) => {
    setPhase('loading');
    
    try {
      // Call backend API
      const response = await fetch('https://bigredhacks25-331813490179.us-east4.run.app/api/create-story', {
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
      
      // Show popup with user's input from backend
      Alert.alert(
        '📚 Story Request Received!',
        `Your story idea: "${result.user_input}"\n\nStatus: ${result.status}\nTime: ${new Date(result.timestamp).toLocaleTimeString()}`,
        [
          { text: 'Great!', style: 'default' }
        ]
      );
      
      // For now, continue with mock story after API call
      const mockStory = {
        paragraphs: [
          `Once upon a time, ${theme} began an amazing adventure. The sun was shining brightly as our hero discovered something magical hidden in the forest.`,
          `As they explored deeper into the enchanted woods, mysterious sounds echoed through the trees. What could be making those strange noises?`,
          `Suddenly, a friendly creature appeared! It had sparkling wings and a warm smile. "I can help you," it said gently.`
        ],
        currentParagraph: 0,
        choices: [
          "Follow the creature to its magical home",
          "Ask the creature about the mysterious sounds", 
          "Invite the creature to join your adventure"
        ],
        iteration: 1,
        maxIterations: 10
      };
      
      setStoryData(mockStory);
      setPhase('reading');
      
    } catch (error) {
      console.error('Error calling backend:', error);
      Alert.alert(
        '❌ Connection Error',
        'Could not connect to the story server. Please check your internet connection and try again.',
        [
          { text: 'OK', style: 'default' }
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
    
    // Simulate API call for choice continuation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
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
  };

  const resetStory = () => {
    setPhase('input');
    setUserInput('');
    setStoryData({
      paragraphs: [],
      currentParagraph: 0,
      iteration: 1,
      maxIterations: 10,
      choices: null,
    });
  };

  const generateVideo = () => {
    Alert.alert('🎬 Video Generation', 'Your story video will be ready soon!', [
      { text: 'Great!', style: 'default' }
    ]);
  };

  // Input Phase
  if (phase === 'input') {
    return (
      <KeyboardAvoidingView 
        style={styles.container} 
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
    );
  }

  // Loading Phase
  if (phase === 'loading') {
    return (
      <LinearGradient
        colors={['#dbeafe', '#f3e8ff']}
        style={styles.gradientContainer}
      >
        <View style={styles.loadingContainer}>
          <View style={styles.loadingIconContainer}>
            <LinearGradient
              colors={['#3b82f6', '#8b5cf6']}
              style={styles.loadingIcon}
            >
              <Ionicons name="sparkles" size={48} color="white" />
            </LinearGradient>
          </View>
          <Text style={styles.loadingTitle}>Creating Your Story...</Text>
          <Text style={styles.loadingSubtitle}>The magic is happening! ✨</Text>
        </View>
      </LinearGradient>
    );
  }

  // Reading Phase
  if (phase === 'reading') {
    const currentText = storyData.paragraphs[storyData.currentParagraph];
    const progress = (storyData.iteration / storyData.maxIterations) * 100;

    return (
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
                <Text style={styles.progressNumbers}>{storyData.iteration}/{storyData.maxIterations}</Text>
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

          {/* Illustration Placeholder */}
          <View style={styles.illustrationContainer}>
            <LinearGradient
              colors={['#fef3c7', '#fce7f3', '#e0e7ff']}
              style={styles.illustrationPlaceholder}
            >
              <Text style={styles.illustrationEmoji}>🌟</Text>
              <Text style={styles.illustrationText}>Story Scene {storyData.currentParagraph + 1}</Text>
            </LinearGradient>
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
    );
  }

  // Choice Phase
  if (phase === 'choosing') {
    return (
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
    );
  }

  // Complete Phase
  if (phase === 'complete') {
    return (
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
              onPress={generateVideo}
              style={styles.actionButton}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#dc2626', '#ec4899']}
                style={styles.actionButtonGradient}
              >
                <Ionicons name="play" size={24} color="white" />
                <Text style={styles.actionButtonText}>Create Story Video</Text>
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
    );
  }

  return null;
}

const styles = StyleSheet.create({
  container: {
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
    padding: 24,
  },
  loadingIconContainer: {
    marginBottom: 24,
  },
  loadingIcon: {
    width: 96,
    height: 96,
    borderRadius: 48,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  loadingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#7c3aed',
    marginBottom: 12,
    textAlign: 'center',
  },
  loadingSubtitle: {
    fontSize: 18,
    color: '#8b5cf6',
    textAlign: 'center',
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
  progressNumbers: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
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
