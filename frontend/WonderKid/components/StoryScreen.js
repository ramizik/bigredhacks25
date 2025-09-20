import React, { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Dimensions,
    Image,
    Modal,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import VideoPlayerScreen from './VideoPlayerScreen';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
const API_URL = 'https://bigredhacks25-331813490179.us-east4.run.app';

const StoryScreen = ({ route, navigation }) => {
  const { theme } = route.params || { theme: 'adventure' };
  const [story, setStory] = useState(null);
  const [currentParagraph, setCurrentParagraph] = useState(0);
  const [loading, setLoading] = useState(true);
  const [imageLoading, setImageLoading] = useState(false);
  const [selectedChoice, setSelectedChoice] = useState(null);
  const [storyImages, setStoryImages] = useState({});
  const [sceneCount, setSceneCount] = useState(0);
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
  const [videoTriggered, setVideoTriggered] = useState(false);

  useEffect(() => {
    generateStory();
  }, [theme]);

  const generateStory = async () => {
    setLoading(true);
    try {
      console.log('📚 Generating story for theme:', theme);
      
      const response = await fetch(`${API_URL}/api/generate-story`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          theme: theme,
          age_group: '5-8',
          reading_level: 'beginner'
        }),
      });
      
      const data = await response.json();
      console.log('📖 Story generated:', data);
      
      setStory(data);
      setCurrentParagraph(0);
      setSceneCount(data.scene_count || 1);
      
      // Store image if generated
      if (data.image_url) {
        setStoryImages(prev => ({
          ...prev,
          0: data.image_url
        }));
      }
      
    } catch (error) {
      console.error('❌ Error generating story:', error);
      Alert.alert('Error', 'Failed to generate story. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChoice = async (choice) => {
    setSelectedChoice(choice);
    setImageLoading(true);
    
    try {
      console.log('🎯 Selected choice:', choice);
      
      const response = await fetch(`${API_URL}/api/continue-story`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          choice: choice,
          story_id: story.story_id,
          current_paragraph: currentParagraph,
        }),
      });
      
      const data = await response.json();
      console.log('📖 Story continued:', data);
      
      // Update story with new content
      setStory(prev => ({
        ...prev,
        paragraphs: data.paragraphs,
        choices: data.choices,
        current_paragraph: data.current_paragraph,
        is_complete: data.is_complete,
        progress_percentage: data.progress_percentage,
      }));
      
      // Update scene count
      setSceneCount(data.scene_count || sceneCount + 1);
      
      // Store new image if generated
      if (data.image_url) {
        const paragraphIndex = data.current_paragraph;
        setStoryImages(prev => ({
          ...prev,
          [paragraphIndex]: data.image_url
        }));
      }
      
      // Check for video trigger
      if (data.video_trigger && !videoTriggered) {
        setVideoTriggered(true);
        Alert.alert(
          '🎬 Video Generation Triggered!',
          'Congratulations! Your story has reached 10 scenes. A magical video is being created with all your story scenes!',
          [
            { 
              text: 'Watch Video', 
              onPress: () => setShowVideoPlayer(true)
            },
            { 
              text: 'Continue Reading', 
              style: 'cancel'
            }
          ]
        );
      }
      
      setCurrentParagraph(data.current_paragraph);
      setSelectedChoice(null);
      
    } catch (error) {
      console.error('❌ Error continuing story:', error);
      Alert.alert('Error', 'Failed to continue story. Please try again.');
    } finally {
      setImageLoading(false);
    }
  };

  const renderSceneProgress = () => (
    <View style={styles.progressContainer}>
      <View style={styles.sceneCounter}>
        <Text style={styles.sceneCounterText}>
          Scene {sceneCount} of 10
        </Text>
        {sceneCount >= 10 && (
          <TouchableOpacity 
            style={styles.videoButton}
            onPress={() => setShowVideoPlayer(true)}
          >
            <Text style={styles.videoButtonText}>🎬 Watch Video</Text>
          </TouchableOpacity>
        )}
      </View>
      <View style={styles.progressBar}>
        <View 
          style={[
            styles.progressFill,
            { width: `${Math.min((sceneCount / 10) * 100, 100)}%` }
          ]}
        />
        {[...Array(10)].map((_, i) => (
          <View
            key={i}
            style={[
              styles.progressMilestone,
              { left: `${(i + 1) * 10}%` },
              i < sceneCount && styles.progressMilestoneActive
            ]}
          />
        ))}
      </View>
      {sceneCount < 10 && (
        <Text style={styles.progressText}>
          {10 - sceneCount} more scenes until video generation! 🎬
        </Text>
      )}
      {sceneCount >= 10 && videoTriggered && (
        <Text style={styles.progressCompleteText}>
          ✨ Video generation in progress! Continue reading while we create your magical video!
        </Text>
      )}
    </View>
  );

  const renderStoryContent = () => {
    if (!story) return null;
    
    const currentImage = storyImages[currentParagraph] || storyImages[0];
    
    return (
      <ScrollView style={styles.storyContainer}>
        {/* Scene Progress */}
        {renderSceneProgress()}
        
        {/* Story Title */}
        <Text style={styles.storyTitle}>
          {theme.charAt(0).toUpperCase() + theme.slice(1)} Adventure
        </Text>
        
        {/* Illustration */}
        {currentImage && (
          <View style={styles.imageContainer}>
            {imageLoading && (
              <ActivityIndicator 
                size="large" 
                color="#FFD700" 
                style={styles.imageLoader}
              />
            )}
            <Image
              source={{ uri: `${API_URL}${currentImage}` }}
              style={styles.illustration}
              resizeMode="cover"
              onLoadStart={() => setImageLoading(true)}
              onLoadEnd={() => setImageLoading(false)}
            />
          </View>
        )}
        
        {/* Story Text */}
        <View style={styles.textContainer}>
          {story.paragraphs.slice(0, currentParagraph + 1).map((paragraph, index) => (
            <Text key={index} style={styles.storyText}>
              {paragraph}
            </Text>
          ))}
        </View>
        
        {/* Choices */}
        {!story.is_complete && story.choices && story.choices.length > 0 && (
          <View style={styles.choicesContainer}>
            <Text style={styles.choicesTitle}>What happens next?</Text>
            {story.choices.map((choice, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.choiceButton,
                  selectedChoice === choice && styles.choiceButtonSelected
                ]}
                onPress={() => handleChoice(choice)}
                disabled={imageLoading || selectedChoice !== null}
              >
                <Text style={styles.choiceText}>
                  {['🌟', '🚀', '🌈'][index % 3]} {choice}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
        
        {/* Story Complete */}
        {story.is_complete && (
          <View style={styles.completeContainer}>
            <Text style={styles.completeText}>
              🎉 The End! What a wonderful adventure!
            </Text>
            <TouchableOpacity
              style={styles.newStoryButton}
              onPress={() => navigation.goBack()}
            >
              <Text style={styles.newStoryButtonText}>Start New Story</Text>
            </TouchableOpacity>
            {sceneCount >= 10 && (
              <TouchableOpacity
                style={styles.watchVideoButton}
                onPress={() => setShowVideoPlayer(true)}
              >
                <Text style={styles.watchVideoButtonText}>
                  🎬 Watch Your Story Video
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </ScrollView>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FFD700" />
          <Text style={styles.loadingText}>Creating your magical story...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {renderStoryContent()}
      
      {/* Video Player Modal */}
      <Modal
        visible={showVideoPlayer}
        animationType="slide"
        onRequestClose={() => setShowVideoPlayer(false)}
      >
        <VideoPlayerScreen
          storyId={story?.story_id}
          sceneCount={sceneCount}
          onClose={() => setShowVideoPlayer(false)}
        />
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#FFD700',
    fontSize: 18,
    marginTop: 20,
    fontFamily: 'Comic Sans MS',
  },
  storyContainer: {
    flex: 1,
    padding: 20,
  },
  progressContainer: {
    marginBottom: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 15,
    padding: 15,
  },
  sceneCounter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sceneCounterText: {
    color: '#FFD700',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
  videoButton: {
    backgroundColor: '#FFD700',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 20,
  },
  videoButtonText: {
    color: '#1a1a2e',
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
  progressBar: {
    height: 20,
    backgroundColor: 'rgba(255, 215, 0, 0.2)',
    borderRadius: 10,
    overflow: 'hidden',
    position: 'relative',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FFD700',
    borderRadius: 10,
  },
  progressMilestone: {
    position: 'absolute',
    top: 5,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    transform: [{ translateX: -5 }],
  },
  progressMilestoneActive: {
    backgroundColor: '#FFFFFF',
  },
  progressText: {
    color: '#9CA3AF',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
    fontFamily: 'Comic Sans MS',
  },
  progressCompleteText: {
    color: '#10B981',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
    fontFamily: 'Comic Sans MS',
    fontWeight: 'bold',
  },
  storyTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFD700',
    textAlign: 'center',
    marginBottom: 20,
    fontFamily: 'Comic Sans MS',
  },
  imageContainer: {
    width: '100%',
    height: 250,
    borderRadius: 15,
    overflow: 'hidden',
    marginBottom: 20,
    backgroundColor: '#2a2a3e',
    position: 'relative',
  },
  illustration: {
    width: '100%',
    height: '100%',
  },
  imageLoader: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -25 }, { translateY: -25 }],
    zIndex: 1,
  },
  textContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
  },
  storyText: {
    color: '#FFFFFF',
    fontSize: 18,
    lineHeight: 28,
    marginBottom: 15,
    fontFamily: 'Comic Sans MS',
  },
  choicesContainer: {
    marginBottom: 30,
  },
  choicesTitle: {
    color: '#FFD700',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
    fontFamily: 'Comic Sans MS',
  },
  choiceButton: {
    backgroundColor: 'rgba(255, 215, 0, 0.2)',
    borderWidth: 2,
    borderColor: '#FFD700',
    borderRadius: 15,
    padding: 15,
    marginBottom: 10,
  },
  choiceButtonSelected: {
    backgroundColor: 'rgba(255, 215, 0, 0.4)',
  },
  choiceText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontFamily: 'Comic Sans MS',
  },
  completeContainer: {
    alignItems: 'center',
    marginTop: 30,
  },
  completeText: {
    color: '#10B981',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    fontFamily: 'Comic Sans MS',
  },
  newStoryButton: {
    backgroundColor: '#10B981',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginBottom: 15,
  },
  newStoryButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
  watchVideoButton: {
    backgroundColor: '#FFD700',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
  },
  watchVideoButtonText: {
    color: '#1a1a2e',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
});

export default StoryScreen;
