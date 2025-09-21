import { Ionicons } from '@expo/vector-icons';
import { Video } from 'expo-av';
import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Dimensions,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
const API_URL = 'https://bigredhacks25-331813490179.us-east4.run.app';

const VideoPlayerScreen = ({ storyId, onClose, sceneCount }) => {
  const [videoUrl, setVideoUrl] = useState(null);
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
    }, 3000); // Check every 3 seconds

    return () => {
      if (checkInterval.current) {
        clearInterval(checkInterval.current);
      }
    };
  }, [storyId]);

  const checkVideoStatus = async () => {
    console.log(`🔍 Checking video status for story: ${storyId}`);
    try {
      const response = await fetch(`${API_URL}/api/video-status/${storyId}`);
      console.log('📡 Status response:', response.status, response.ok);
      const data = await response.json();
      
      console.log('🎬 Video status data:', JSON.stringify(data, null, 2));
      
      setVideoStatus(data.status);
      
      if (data.status === 'completed') {
        console.log('✅ Video completed!');
        console.log('☁️ GCS URL:', data.gcs_url || 'None');
        console.log('📁 Local URL:', data.video_url || 'None');
        console.log('📋 Full response:', JSON.stringify(data));
        
        // Always prefer GCS URL for reliability
        if (data.gcs_url) {
          console.log('🎯 Using GCS URL directly for video playback');
          console.log('🌐 Full GCS URL:', data.gcs_url);
          
          // Set the video URL directly - GCS URLs are public
          setVideoUrl(data.gcs_url);
          setLoading(false);
          setError(null);
          
          if (checkInterval.current) {
            clearInterval(checkInterval.current);
          }
        } else if (data.video_url) {
          // Fallback to local URL only if no GCS URL
          console.log('⚠️ No GCS URL, falling back to local endpoint');
          const fullUrl = data.video_url.startsWith('http') 
            ? data.video_url 
            : `${API_URL}${data.video_url}`;
          setVideoUrl(fullUrl);
          setLoading(false);
          setError(null);
          
          if (checkInterval.current) {
            clearInterval(checkInterval.current);
          }
        } else {
          console.error('❌ No video URL available in response');
          console.error('📋 Response data:', data);
          setError('Video URL not available');
          setLoading(false);
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
      const response = await fetch(`${API_URL}/api/generate-video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          story_id: storyId,
          manual_trigger: true
        })
      });

      const data = await response.json();
      console.log('📹 Video generation response:', data);
      
      if (data.status === 'started') {
        setVideoStatus('processing');
      } else {
        console.error('Failed to trigger video generation:', data.message);
        setError(data.message || 'Failed to start video generation');
      }
    } catch (err) {
      console.error('Error triggering video generation:', err);
      setError('Failed to start video generation');
    }
  };

  const handlePlayPause = () => {
    setPaused(!paused);
  };

  const handlePlaybackStatusUpdate = (status) => {
    if (status.isLoaded) {
      setDuration(status.durationMillis / 1000);
      setCurrentTime(status.positionMillis / 1000);
      setProgress((status.positionMillis / status.durationMillis) * 100);
      
      if (status.didJustFinish) {
        setPaused(true);
      }
    }
  };

  const handleVideoError = (error) => {
    console.error('🎬 Video playback error:', error);
    setError('Failed to play video. Please try again.');
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const retryVideoGeneration = () => {
    setError(null);
    setLoading(true);
    setVideoStatus('checking');
    checkVideoStatus();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          onPress={onClose}
          style={styles.closeButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="close" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Your Story Video</Text>
        <View style={styles.placeholder} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6B46C1" />
          <Text style={styles.loadingText}>
            {videoStatus === 'processing' 
              ? `Creating your magical video... ${Math.round(generationProgress)}%`
              : 'Loading your video...'}
          </Text>
          {videoStatus === 'processing' && (
            <>
              <Text style={styles.subText}>
                This usually takes 2-3 minutes
              </Text>
              <Text style={styles.sceneCount}>
                Including {sceneCount || 10} amazing scenes!
              </Text>
              <View style={styles.progressBar}>
                <View 
                  style={[
                    styles.progressFill, 
                    { width: `${generationProgress}%` }
                  ]} 
                />
              </View>
            </>
          )}
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={48} color="#EF4444" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity 
            style={styles.retryButton}
            onPress={retryVideoGeneration}
          >
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
          <View style={styles.videoSection}>
            {videoUrl && (
              <>
                <Text style={styles.videoInfo}>
                  🎬 Playing from: {videoUrl.includes('storage.googleapis.com') ? 'Google Cloud' : 'Server'}
                </Text>
                
                <View style={styles.videoWrapper}>
                    <Video
                        ref={videoRef}
                        source={{ uri: videoUrl }}
                        style={styles.video}
                        shouldPlay={!paused}
                        isLooping={false}
                        onPlaybackStatusUpdate={handlePlaybackStatusUpdate}
                        onError={handleVideoError}
                        useNativeControls={Platform.OS === 'ios'}
                        resizeMode="contain"
                    />
                    
                    {Platform.OS === 'android' && (
                      <View style={styles.controls}>
                        <TouchableOpacity 
                          onPress={handlePlayPause}
                          style={styles.playPauseButton}
                        >
                          <Ionicons 
                            name={paused ? "play" : "pause"} 
                            size={32} 
                            color="white" 
                          />
                        </TouchableOpacity>
                      </View>
                    )}
                </View>

                <View style={styles.progressContainer}>
                  <Text style={styles.timeText}>{formatTime(currentTime)}</Text>
                  <View style={styles.progressBarVideo}>
                    <View 
                      style={[
                        styles.progressFillVideo, 
                        { width: `${progress}%` }
                      ]} 
                    />
                  </View>
                  <Text style={styles.timeText}>{formatTime(duration)}</Text>
                </View>

                <Text style={styles.videoDescription}>
                  ✨ Your personalized story video with {sceneCount || 10} scenes
                </Text>
              </>
            )}
          </View>
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    paddingBottom: 10,
    backgroundColor: '#1a1a2e',
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  closeButton: {
    padding: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFD700',
    textAlign: 'center',
    flex: 1,
    fontFamily: 'Comic Sans MS',
  },
  placeholder: {
    width: 50,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    color: '#FFD700',
    fontSize: 18,
    marginTop: 20,
    fontFamily: 'Comic Sans MS',
  },
  subText: {
    color: '#9CA3AF',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
    fontFamily: 'Comic Sans MS',
  },
  sceneCount: {
    color: '#FFD700',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 5,
    fontFamily: 'Comic Sans MS',
  },
  progressBar: {
    width: '100%',
    marginTop: 20,
    paddingHorizontal: 20,
  },
  progressFill: {
    height: 10,
    backgroundColor: '#FFD700',
    borderRadius: 5,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: '#9CA3AF',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    fontFamily: 'Comic Sans MS',
  },
  retryButton: {
    backgroundColor: '#FFD700',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
  },
  retryButtonText: {
    color: '#1a1a2e',
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Comic Sans MS',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 20,
    alignItems: 'center',
  },
  videoSection: {
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
  controls: {
    position: 'absolute',
    bottom: 20,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    zIndex: 10,
  },
  playPauseButton: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 25,
    padding: 10,
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    width: '100%',
    marginTop: 20,
  },
  timeText: {
    color: '#FFD700',
    fontSize: 16,
    fontFamily: 'Comic Sans MS',
  },
  progressBarVideo: {
    width: '60%',
    height: 8,
    backgroundColor: 'rgba(255, 215, 0, 0.3)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFillVideo: {
    height: '100%',
    backgroundColor: '#FFD700',
    borderRadius: 4,
  },
  videoInfo: {
    color: '#9CA3AF',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 10,
    fontFamily: 'Comic Sans MS',
  },
  videoDescription: {
    color: '#9CA3AF',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 20,
    fontFamily: 'Comic Sans MS',
  },
});

export default VideoPlayerScreen;
