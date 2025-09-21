import { Ionicons } from '@expo/vector-icons';
import { VideoView, useVideoPlayer } from 'expo-video';
import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Dimensions,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Linking,
  Alert
} from 'react-native';
import Constants from 'expo-constants';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
const API_URL = 'https://bigredhacks25-331813490179.us-east4.run.app';

// Check if running in Expo Go (known compatibility issues with expo-video v3)
const isExpoGo = Constants.appOwnership === 'expo';

const VideoPlayerScreen = ({ storyId, onClose, sceneCount }) => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [gcsUrl, setGcsUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [videoStatus, setVideoStatus] = useState('checking');
  const [generationProgress, setGenerationProgress] = useState(0);
  const checkInterval = useRef(null);

  // Initialize video player with expo-video v3 (only for standalone builds)
  const player = !isExpoGo ? useVideoPlayer(videoUrl ? videoUrl : null, (player) => {
    if (player) {
      player.loop = false;
      player.muted = false;
    }
  }) : null;

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
        console.log('🔧 Running in Expo Go:', isExpoGo);
        console.log('📋 Full response:', JSON.stringify(data));

        // Store both URLs
        if (data.gcs_url) {
          setGcsUrl(data.gcs_url);
        }

        if (isExpoGo) {
          // For Expo Go, prefer GCS URL for better compatibility
          console.log('🎯 Expo Go detected - using GCS URL for better compatibility');
          if (data.gcs_url) {
            setVideoUrl(data.gcs_url);
            setLoading(false);
            setError(null);
          } else {
            console.error('❌ No GCS URL available for Expo Go');
            setError('Video playback not available in Expo Go - GCS URL required');
            setLoading(false);
          }
        } else {
          // For standalone builds, try local URL first, then GCS
          if (data.video_url) {
            console.log('🎯 Using local URL for standalone build');
            const fullUrl = data.video_url.startsWith('http')
              ? data.video_url
              : `${API_URL}${data.video_url}`;
            console.log('🌐 Full Local URL:', fullUrl);
            setVideoUrl(fullUrl);
            setLoading(false);
            setError(null);
          } else if (data.gcs_url) {
            console.log('🎯 Falling back to GCS URL');
            setVideoUrl(data.gcs_url);
            setLoading(false);
            setError(null);
          } else {
            console.error('❌ No video URL available');
            setError('Video URL not available');
            setLoading(false);
          }
        }

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
    if (player.playing) {
      player.pause();
    } else {
      player.play();
    }
  };

  const handleVideoError = (error) => {
    console.error('🎬 Video playback error:', error);
    console.error('🎬 Video URL that failed:', videoUrl);
    console.error('🎬 Error details:', JSON.stringify(error, null, 2));
    setError(`Failed to play video: ${error?.message || 'Unknown error'}. Please try again.`);
  };

  const openVideoExternally = async () => {
    if (gcsUrl || videoUrl) {
      const urlToOpen = gcsUrl || videoUrl;
      console.log('🌐 Opening video externally:', urlToOpen);
      try {
        const canOpen = await Linking.canOpenURL(urlToOpen);
        if (canOpen) {
          await Linking.openURL(urlToOpen);
        } else {
          Alert.alert(
            "Can't Open Video",
            "Your device cannot open this video URL. Please try again later.",
            [{ text: 'OK' }]
          );
        }
      } catch (error) {
        console.error('❌ Error opening video externally:', error);
        Alert.alert(
          "Error",
          "Failed to open video. Please try again later.",
          [{ text: 'OK' }]
        );
      }
    }
  };

  // Add error handling for the player (v3 API) - only for standalone builds
  useEffect(() => {
    if (player && !isExpoGo) {
      const handleError = (error) => {
        console.error('🎬 Video player error:', error);
        handleVideoError(error);
      };

      // In v3, error handling might be different
      player.addListener?.('error', handleError);

      return () => {
        player.removeListener?.('error', handleError);
      };
    }
  }, [player]);

  // Update player source when videoUrl changes (v3 API) - only for standalone builds
  useEffect(() => {
    if (player && videoUrl && !isExpoGo) {
      console.log('🎬 Setting video source:', videoUrl);
      try {
        // In v3, might need to use different method
        if (player.replace) {
          player.replace(videoUrl);
        } else if (player.loadAsync) {
          player.loadAsync({ uri: videoUrl });
        } else {
          console.warn('🎬 Player replace method not found, player might auto-load');
        }
      } catch (error) {
        console.error('🎬 Error setting video source:', error);
        handleVideoError(error);
      }
    }
  }, [player, videoUrl]);

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

                {isExpoGo ? (
                  // Expo Go Fallback UI
                  <View style={styles.expoGoFallback}>
                    <View style={styles.videoPlaceholder}>
                      <Ionicons name="videocam" size={80} color="#FFD700" />
                      <Text style={styles.expoGoTitle}>Video Ready!</Text>
                      <Text style={styles.expoGoMessage}>
                        Due to Expo Go limitations, videos need to be opened in your browser for the best experience.
                      </Text>
                    </View>

                    <TouchableOpacity
                      style={styles.openExternalButton}
                      onPress={openVideoExternally}
                    >
                      <Ionicons name="open-outline" size={24} color="#1a1a2e" />
                      <Text style={styles.openExternalButtonText}>Open Video in Browser</Text>
                    </TouchableOpacity>

                    <Text style={styles.videoDescription}>
                      ✨ Your personalized story video with {sceneCount || 10} scenes
                    </Text>
                  </View>
                ) : (
                  // Standalone App UI (expo-video v3)
                  <View style={styles.videoWrapper}>
                      <VideoView
                          style={styles.video}
                          player={player}
                          allowsFullscreen
                          allowsPictureInPicture
                          contentFit="contain"
                          nativeControls={Platform.OS === 'ios'}
                      />

                      {Platform.OS === 'android' && (
                        <View style={styles.controls}>
                          <TouchableOpacity
                            onPress={handlePlayPause}
                            style={styles.playPauseButton}
                          >
                            <Ionicons
                              name={player?.playing ? "pause" : "play"}
                              size={32}
                              color="white"
                            />
                          </TouchableOpacity>
                        </View>
                      )}
                  </View>
                )}

                {!isExpoGo && (
                  <View style={styles.progressContainer}>
                    <Text style={styles.timeText}>
                      🎬 Video Player Ready
                    </Text>
                  </View>
                )}

                {!isExpoGo && (
                  <Text style={styles.videoDescription}>
                    ✨ Your personalized story video with {sceneCount || 10} scenes
                  </Text>
                )}
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
  // Expo Go Fallback Styles
  expoGoFallback: {
    alignItems: 'center',
    padding: 20,
  },
  videoPlaceholder: {
    alignItems: 'center',
    padding: 40,
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#FFD700',
    borderStyle: 'dashed',
    marginBottom: 30,
    width: '100%',
  },
  expoGoTitle: {
    color: '#FFD700',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    fontFamily: 'Comic Sans MS',
  },
  expoGoMessage: {
    color: '#9CA3AF',
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
    fontFamily: 'Comic Sans MS',
  },
  openExternalButton: {
    backgroundColor: '#FFD700',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  openExternalButtonText: {
    color: '#1a1a2e',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
    fontFamily: 'Comic Sans MS',
  },
});

export default VideoPlayerScreen;
