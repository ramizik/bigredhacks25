import { Video } from 'expo-av';
import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Dimensions,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
const API_URL = 'https://bigredhacks25-331813490179.us-east4.run.app';

const VideoPlayerScreen = ({ storyId, onClose, sceneCount }) => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoData, setVideoData] = useState(null); // For base64 video data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [videoStatus, setVideoStatus] = useState('checking');
  const [progress, setProgress] = useState(0);
  const [paused, setPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [generationProgress, setGenerationProgress] = useState(0);
  const videoRef = useRef(null);
  const checkInterval = useRef(null);

  useEffect(() => {
    checkVideoStatus();
    
    // Set up polling for video generation progress
    checkInterval.current = setInterval(() => {
      if (videoStatus === 'processing') {
        checkVideoStatus();
        // Update progress animation
        setGenerationProgress((prev) => (prev + 5) % 100);
      }
    }, 5000); // Check every 5 seconds

    return () => {
      if (checkInterval.current) {
        clearInterval(checkInterval.current);
      }
    };
  }, [storyId]);

  const loadVideoData = async (videoUrl) => {
    try {
      console.log('🎬 === LOADING VIDEO DATA ===');
      console.log('🎬 Video URL from status:', videoUrl);
      console.log('🎬 Full URL to fetch:', `${API_URL}${videoUrl}`);
      
      // Try to fetch video data from the API
      const response = await fetch(`${API_URL}${videoUrl}`);
      console.log('📡 Video fetch response status:', response.status, response.ok);
      console.log('📡 Response headers:', response.headers);
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        console.log('📡 Content-Type:', contentType);
        
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          console.log('📊 JSON response received:', {
            status: data.status,
            has_video_data: !!data.video_data,
            size_mb: data.size_mb,
            filename: data.filename
          });
          
          if (data.status === 'success' && data.video_data) {
            // Video is served as base64 data
            console.log('✅ Video data received as base64:', data.size_mb, 'MB');
            console.log('🎬 Base64 data length:', data.video_data.length);
            setVideoData(data.video_data);
            const videoDataUrl = `data:${data.mime_type};base64,${data.video_data}`;
            console.log('🎬 Setting video URL as data URL, first 100 chars:', videoDataUrl.substring(0, 100));
            setVideoUrl(videoDataUrl);
          } else {
            console.log('❌ JSON response missing video data');
            // Fallback to direct URL
            console.log('🔄 Using direct video URL');
            setVideoUrl(`${API_URL}${videoUrl}`);
          }
        } else {
          // Not JSON, assume it's the video file directly
          console.log('🔄 Response is not JSON, using direct URL');
          setVideoUrl(`${API_URL}${videoUrl}`);
        }
      } else {
        console.error('❌ Video fetch failed with status:', response.status);
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (err) {
      console.error('❌ Error loading video data:', err);
      console.error('Stack:', err.stack);
      // Fallback to direct URL
      console.log('🔄 Fallback: Using direct video URL');
      setVideoUrl(`${API_URL}${videoUrl}`);
    }
  };

  const checkVideoStatus = async () => {
    console.log(`🔍 Checking video status for story: ${storyId}`);
    try {
      const response = await fetch(`${API_URL}/api/video-status/${storyId}`);
      console.log('📡 Status response:', response.status, response.ok);
      const data = await response.json();
      
      console.log('🎬 Video status data:', JSON.stringify(data, null, 2));
      
      setVideoStatus(data.status);
      
      if (data.status === 'completed' && data.video_url) {
        console.log('✅ Video completed, URL:', data.video_url);
        // Try to load video data (base64 or URL)
        await loadVideoData(data.video_url);
        setLoading(false);
        if (checkInterval.current) {
          clearInterval(checkInterval.current);
        }
      } else if (data.status === 'processing') {
        // Keep loading, video is being generated
        console.log('⏳ Video still generating...');
      } else if (data.status === 'not_started') {
        console.log('🚀 Video not started, triggering generation...');
        // Trigger video generation
        triggerVideoGeneration();
      } else if (data.status === 'error') {
        console.log('❌ Video error:', data.message);
        setError(data.message || 'Video generation failed');
        setLoading(false);
      } else {
        console.log('❓ Unknown status:', data.status);
      }
    } catch (err) {
      console.error('❌ Error checking video status:', err);
      console.error('Stack trace:', err.stack);
      setError('Failed to check video status');
      setLoading(false);
    }
  };

  const triggerVideoGeneration = async () => {
    try {
      console.log('🎬 Triggering video generation for story:', storyId);
      
      const response = await fetch(`${API_URL}/api/generate-story-video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          story_id: storyId,
          manual_trigger: sceneCount < 10 
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'started' || data.status === 'processing') {
        setVideoStatus('processing');
        Alert.alert(
          '🎬 Video Generation Started!',
          'Your story video is being created. This will take 2-3 minutes. You can continue reading while we prepare your magical video!',
          [{ text: 'OK' }]
        );
      } else if (data.status === 'not_ready') {
        setError(`Need ${10 - sceneCount} more scenes for video generation`);
        setLoading(false);
      }
    } catch (err) {
      console.error('❌ Error triggering video generation:', err);
      setError('Failed to start video generation');
      setLoading(false);
    }
  };

      const onVideoLoad = (status) => {
        if (status.isLoaded) {
            setDuration(status.durationMillis / 1000);
            console.log('✅ Video loaded, duration:', status.durationMillis / 1000);
        }
    };

  const onVideoError = (error) => {
    console.error('❌ Video playback error:', error);
    console.error('🔍 Video URL that failed:', videoUrl);
    console.error('🔍 Video data available:', !!videoData);
    setError('Failed to play video. Try refreshing or check your connection.');
    setLoading(false);
  };

  const togglePlayPause = () => {
    setPaused(!paused);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderGeneratingView = () => (
    <View style={styles.generatingContainer}>
      <Text style={styles.generatingTitle}>🎬 Creating Your Story Video!</Text>
      
      <View style={styles.progressContainer}>
        <ActivityIndicator size="large" color="#FFD700" />
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill,
              { width: `${generationProgress}%` }
            ]} 
          />
        </View>
        <Text style={styles.progressText}>
          {Math.min(generationProgress, 95)}% Complete
        </Text>
      </View>
      
      <Text style={styles.generatingMessage}>
        Your magical video is being generated with all {sceneCount || 10} scenes!
      </Text>
      <Text style={styles.generatingSubMessage}>
        This usually takes 2-3 minutes. Feel free to continue reading while we work our magic! ✨
      </Text>
      
      <TouchableOpacity style={styles.continueButton} onPress={onClose}>
        <Text style={styles.continueButtonText}>Continue Reading 📖</Text>
      </TouchableOpacity>
    </View>
  );

          const renderVideoPlayer = () => (
            <View style={styles.videoContainer}>
                <Text style={styles.title}>🎬 Your Story Video</Text>
                
                {videoData && (
                  <Text style={styles.videoInfo}>
                    📊 Video loaded: {videoData.length > 1000000 ? `${Math.round(videoData.length / 1000000)}MB` : `${Math.round(videoData.length / 1000)}KB`} base64 data
                  </Text>
                )}
                
                <View style={styles.videoWrapper}>
                    <Video
                        ref={videoRef}
                        source={{ uri: videoUrl }}
                        style={styles.video}
                        shouldPlay={!paused}
                        isLooping={false}
                        onLoad={onVideoLoad}
                        onPlaybackStatusUpdate={(status) => {
                            if (status.isLoaded) {
                                setDuration(status.durationMillis / 1000);
                                setCurrentTime(status.positionMillis / 1000);
                                if (status.durationMillis > 0) {
                                    setProgress((status.positionMillis / status.durationMillis) * 100);
                                }
                            }
                        }}
                        onError={onVideoError}
                        resizeMode="contain"
                        useNativeControls={false}
                    />
                    
                    {/* Custom Controls Overlay */}
                    <TouchableOpacity 
                        style={styles.videoOverlay}
                        onPress={togglePlayPause}
                        activeOpacity={0.9}
                    >
                        {paused && (
                            <View style={styles.playButton}>
                                <Text style={styles.playButtonText}>▶</Text>
                            </View>
                        )}
                    </TouchableOpacity>
                </View>
      
      {/* Video Controls */}
      <View style={styles.controls}>
        <TouchableOpacity style={styles.controlButton} onPress={togglePlayPause}>
          <Text style={styles.controlButtonText}>{paused ? '▶️' : '⏸️'}</Text>
        </TouchableOpacity>
        
        <View style={styles.timeContainer}>
          <Text style={styles.timeText}>
            {formatTime(currentTime)} / {formatTime(duration)}
          </Text>
        </View>
        
        <View style={styles.progressBarContainer}>
          <View style={styles.videoProgressBar}>
            <View 
              style={[
                styles.videoProgressFill,
                { width: `${progress}%` }
              ]} 
            />
          </View>
        </View>
      </View>
      
      <Text style={styles.videoInfo}>
        This video combines all {sceneCount || 10} scenes from your story journey! 🌟
      </Text>
      
      <TouchableOpacity style={styles.closeButton} onPress={onClose}>
        <Text style={styles.closeButtonText}>Back to Story</Text>
      </TouchableOpacity>
    </View>
  );

  const renderError = () => (
    <View style={styles.errorContainer}>
      <Text style={styles.errorTitle}>😔 Video Not Available</Text>
      <Text style={styles.errorMessage}>{error}</Text>
      
      {videoStatus === 'not_started' && sceneCount >= 10 && (
        <TouchableOpacity style={styles.retryButton} onPress={triggerVideoGeneration}>
          <Text style={styles.retryButtonText}>Generate Video 🎬</Text>
        </TouchableOpacity>
      )}
      
      <TouchableOpacity style={styles.closeButton} onPress={onClose}>
        <Text style={styles.closeButtonText}>Back to Story</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {loading && videoStatus === 'processing' && renderGeneratingView()}
        {!loading && videoUrl && renderVideoPlayer()}
        {!loading && error && renderError()}
        {loading && videoStatus === 'checking' && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FFD700" />
            <Text style={styles.loadingText}>Checking video status...</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
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
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFD700',
    marginBottom: 20,
    textAlign: 'center',
    fontFamily: 'Comic Sans MS',
  },
  videoContainer: {
    width: '100%',
    alignItems: 'center',
  },
  videoWrapper: {
    width: screenWidth - 40,
    height: (screenWidth - 40) * 9 / 16,
    backgroundColor: '#000',
    borderRadius: 15,
    overflow: 'hidden',
    position: 'relative',
  },
  video: {
    width: '100%',
    height: '100%',
  },
  videoOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  playButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 215, 0, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  playButtonText: {
    fontSize: 36,
    color: '#1a1a2e',
  },
  controls: {
    width: '100%',
    marginTop: 20,
    paddingHorizontal: 20,
  },
  controlButton: {
    padding: 15,
    backgroundColor: '#FFD700',
    borderRadius: 10,
    marginBottom: 15,
    alignSelf: 'center',
  },
  controlButtonText: {
    fontSize: 24,
    color: '#1a1a2e',
  },
  timeContainer: {
    alignItems: 'center',
    marginBottom: 10,
  },
  timeText: {
    color: '#FFD700',
    fontSize: 16,
    fontFamily: 'Comic Sans MS',
  },
  progressBarContainer: {
    width: '100%',
    paddingHorizontal: 10,
  },
  videoProgressBar: {
    height: 8,
    backgroundColor: 'rgba(255, 215, 0, 0.3)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  videoProgressFill: {
    height: '100%',
    backgroundColor: '#FFD700',
    borderRadius: 4,
  },
  videoInfo: {
    color: '#9CA3AF',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 20,
    marginHorizontal: 20,
    fontFamily: 'Comic Sans MS',
  },
  generatingContainer: {
    alignItems: 'center',
    padding: 20,
  },
  generatingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFD700',
    marginBottom: 30,
    textAlign: 'center',
    fontFamily: 'Comic Sans MS',
  },
  progressContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  progressBar: {
    width: screenWidth - 80,
    height: 20,
    backgroundColor: 'rgba(255, 215, 0, 0.3)',
    borderRadius: 10,
    overflow: 'hidden',
    marginTop: 20,
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FFD700',
    borderRadius: 10,
  },
  progressText: {
    color: '#FFD700',
    fontSize: 16,
    marginTop: 10,
    fontFamily: 'Comic Sans MS',
  },
  generatingMessage: {
    color: '#FFFFFF',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 10,
    fontFamily: 'Comic Sans MS',
  },
  generatingSubMessage: {
    color: '#9CA3AF',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 30,
    paddingHorizontal: 20,
    fontFamily: 'Comic Sans MS',
  },
  continueButton: {
    backgroundColor: '#10B981',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginTop: 10,
  },
  continueButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
  errorContainer: {
    alignItems: 'center',
    padding: 20,
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#EF4444',
    marginBottom: 20,
    fontFamily: 'Comic Sans MS',
  },
  errorMessage: {
    color: '#9CA3AF',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    fontFamily: 'Comic Sans MS',
  },
  retryButton: {
    backgroundColor: '#FFD700',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginBottom: 20,
  },
  retryButtonText: {
    color: '#1a1a2e',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
  closeButton: {
    backgroundColor: '#4B5563',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginTop: 20,
  },
  closeButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
});

export default VideoPlayerScreen;
