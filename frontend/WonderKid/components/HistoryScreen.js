import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useState } from 'react';
import {
    Alert,
    Dimensions,
    Image,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';

const { width } = Dimensions.get('window');
const imageSize = (width - 60) / 2; // Two columns with margins

export default function HistoryScreen() {
  const [sessionImages, setSessionImages] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load images from AsyncStorage on component mount
  useEffect(() => {
    loadSessionImages();
  }, []);

  // Refresh images when user navigates to this tab
  useFocusEffect(
    React.useCallback(() => {
      loadSessionImages();
    }, [])
  );

  const loadSessionImages = async () => {
    try {
      const storedImages = await AsyncStorage.getItem('sessionImages');
      if (storedImages) {
        setSessionImages(JSON.parse(storedImages));
      }
    } catch (error) {
      console.log('Error loading session images:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearAllImages = () => {
    Alert.alert(
      '🗑️ Clear Gallery',
      'Are you sure you want to clear all images from this session?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear All',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('sessionImages');
              setSessionImages([]);
              Alert.alert('✅ Cleared!', 'All images have been cleared from the gallery.');
            } catch (error) {
              Alert.alert('❌ Error', 'Failed to clear images. Please try again.');
            }
          }
        }
      ]
    );
  };

  const viewImageFullScreen = (imageUrl, index) => {
    Alert.alert(
      `🖼️ Image ${index + 1}`,
      'Generated from your story adventure!',
      [
        { text: 'Close', style: 'cancel' },
        { 
          text: 'View Details', 
          onPress: () => {
            Alert.alert('Image Details', `Story Scene ${index + 1}\nGenerated: ${new Date().toLocaleDateString()}`);
          }
        }
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient colors={['#7fdeff', '#a5e6ba', '#9683ec']} style={styles.gradientContainer}>
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading your gallery...</Text>
          </View>
        </LinearGradient>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#7fdeff', '#a5e6ba', '#9683ec']} style={styles.gradientContainer}>
        <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerContent}>
              <Text style={styles.headerTitle}>Your Story Gallery</Text>
              <Text style={styles.headerSubtitle}>
                Images generated from your adventures
              </Text>
            </View>
            <View style={styles.headerBadge}>
              <Ionicons name="images" size={20} color="#f35b04" />
              <Text style={styles.headerBadgeText}>
                {sessionImages.length} Images
              </Text>
            </View>
          </View>

          {sessionImages.length === 0 ? (
            // Empty State
            <View style={styles.emptyContainer}>
              <View style={styles.emptyContent}>
                <Text style={styles.emptyEmoji}>📸</Text>
                <Text style={styles.emptyTitle}>No Images Yet!</Text>
                <Text style={styles.emptyMessage}>
                  Start creating stories to see your generated images appear here. 
                  Each story adventure will create beautiful illustrations!
                </Text>
                <TouchableOpacity 
                  style={styles.createStoryButton}
                  onPress={() => {
                    // Navigate to Story tab (this would need navigation context in a real app)
                    Alert.alert('💡 Tip', 'Go to the Story tab to start creating your first adventure!');
                  }}
                >
                  <LinearGradient colors={['#9683ec', '#5d16a6']} style={styles.createStoryGradient}>
                    <Ionicons name="add-circle" size={24} color="white" />
                    <Text style={styles.createStoryText}>Create First Story</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            </View>
          ) : (
            // Image Gallery
            <>
              <View style={styles.galleryContainer}>
                <View style={styles.galleryGrid}>
                  {sessionImages.map((imageUrl, index) => (
                    <TouchableOpacity
                      key={index}
                      style={styles.imageCard}
                      onPress={() => viewImageFullScreen(imageUrl, index)}
                      activeOpacity={0.8}
                    >
                      <Image
                        source={{ uri: imageUrl }}
                        style={styles.image}
                        resizeMode="cover"
                        onError={() => {
                          console.log('Failed to load image:', imageUrl);
                        }}
                      />
                      <View style={styles.imageOverlay}>
                        <Text style={styles.imageNumber}>{index + 1}</Text>
                        <Ionicons name="eye" size={20} color="white" />
                      </View>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              {/* Clear All Button */}
              <View style={styles.actionsContainer}>
                <TouchableOpacity
                  onPress={clearAllImages}
                  style={styles.clearButton}
                  activeOpacity={0.8}
                >
                  <LinearGradient colors={['#ef233c', '#f35b04']} style={styles.clearButtonGradient}>
                    <Ionicons name="trash" size={24} color="white" />
                    <Text style={styles.clearButtonText}>Clear All Images</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            </>
          )}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 10,
  },
  gradientContainer: {
    flex: 1,
  },
  scrollContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#5d16a6',
    fontWeight: '600',
  },
  header: {
    paddingTop: 20,
    paddingBottom: 30,
  },
  headerContent: {
    marginBottom: 15,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#5d16a6',
    textAlign: 'center',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#9683ec',
    textAlign: 'center',
    fontWeight: '500',
  },
  headerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'center',
  },
  headerBadgeText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '600',
    color: '#5d16a6',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyContent: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyEmoji: {
    fontSize: 80,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#5d16a6',
    textAlign: 'center',
    marginBottom: 16,
  },
  emptyMessage: {
    fontSize: 16,
    color: '#9683ec',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  createStoryButton: {
    borderRadius: 25,
    overflow: 'hidden',
  },
  createStoryGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 16,
  },
  createStoryText: {
    marginLeft: 12,
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
  galleryContainer: {
    paddingBottom: 20,
  },
  galleryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  imageCard: {
    width: imageSize,
    height: imageSize,
    marginBottom: 20,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    shadowColor: '#9683ec',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imageOverlay: {
    position: 'absolute',
    top: 10,
    right: 10,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  imageNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: 'white',
    marginRight: 6,
  },
  actionsContainer: {
    paddingBottom: 40,
    alignItems: 'center',
  },
  clearButton: {
    borderRadius: 25,
    overflow: 'hidden',
  },
  clearButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 16,
  },
  clearButtonText: {
    marginLeft: 12,
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
});
