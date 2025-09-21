import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React from 'react';
import {
    Alert,
    Dimensions,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';

const { width } = Dimensions.get('window');
const cardWidth = (width - 60) / 2; // Two columns with margins

export default function HistoryScreen() {
  const completedStories = [
    {
      id: 1,
      title: "The Magic Garden",
      completedDate: "Today",
      rating: 5,
      thumbnail: "🐰",
      color: ['#a5e6ba', '#7fdeff']
    },
    {
      id: 2,
      title: "Space Adventure",
      completedDate: "Yesterday",
      rating: 4,
      thumbnail: "🚀",
      color: ['#9683ec', '#ef233c']
    },
    {
      id: 3,
      title: "Ocean Friends",
      completedDate: "2 days ago",
      rating: 5,
      thumbnail: "🐠",
      color: ['#7fdeff', '#a5e6ba']
    },
    {
      id: 4,
      title: "Forest Animals",
      completedDate: "3 days ago",
      rating: 4,
      thumbnail: "🦝",
      color: ['#a5e6ba', '#f35b04']
    },
    {
      id: 5,
      title: "Princess Castle",
      completedDate: "1 week ago",
      rating: 5,
      thumbnail: "👸",
      color: ['#ef233c', '#9683ec']
    },
    {
      id: 6,
      title: "Dinosaur Land",
      completedDate: "1 week ago",
      rating: 4,
      thumbnail: "🦕",
      color: ['#f35b04', '#ef233c']
    }
  ];

  const handleStoryPress = (story) => {
    Alert.alert(
      `📖 ${story.title}`,
      'Would you like to read this story again?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Read Again', style: 'default', onPress: () => console.log('Reread story:', story.title) }
      ]
    );
  };

  const startNewStory = () => {
    // Navigate to story creation - in real app this would use navigation
    Alert.alert('✨ New Story', 'Starting a new adventure!');
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Ionicons
        key={i}
        name={i < rating ? "star" : "star-outline"}
        size={16}
        color={i < rating ? "#f35b04" : "#d1d5db"}
        style={styles.star}
      />
    ));
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={['#7fdeff', '#a5e6ba', '#9683ec']}
        style={styles.gradientContainer}
      >
      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Your Story Collection</Text>
          <View style={styles.headerBadge}>
            <Ionicons name="library" size={20} color="#f35b04" />
            <Text style={styles.headerBadgeText}>
              {completedStories.length} Stories Read
            </Text>
          </View>
        </View>

        {/* Stories Grid */}
        <View style={styles.storiesGrid}>
          {completedStories.map((story) => (
            <TouchableOpacity
              key={story.id}
              onPress={() => handleStoryPress(story)}
              style={[styles.storyCard, { width: cardWidth }]}
              activeOpacity={0.8}
            >
              <View style={styles.storyCardInner}>
                {/* Thumbnail */}
                <LinearGradient
                  colors={story.color}
                  style={styles.thumbnailContainer}
                >
                  <Text style={styles.thumbnailEmoji}>{story.thumbnail}</Text>
                </LinearGradient>

                {/* Story Info */}
                <View style={styles.storyInfo}>
                  <Text style={styles.storyTitle} numberOfLines={2}>
                    {story.title}
                  </Text>
                  
                  {/* Rating */}
                  <View style={styles.ratingContainer}>
                    {renderStars(story.rating)}
                  </View>

                  {/* Date */}
                  <View style={styles.dateContainer}>
                    <Ionicons name="time" size={14} color="#5d16a6" />
                    <Text style={styles.dateText}>{story.completedDate}</Text>
                  </View>
                </View>

                {/* Read Again Button */}
                <TouchableOpacity 
                  style={styles.readAgainButton}
                  onPress={() => handleStoryPress(story)}
                  activeOpacity={0.8}
                >
                  <LinearGradient
                    colors={['#f35b04', '#ef233c']}
                    style={styles.readAgainButtonGradient}
                  >
                    <Text style={styles.readAgainButtonText}>Read Again</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Bottom Action */}
        <View style={styles.bottomAction}>
          <TouchableOpacity
            onPress={startNewStory}
            style={styles.newStoryButton}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={['#9683ec', '#5d16a6']}
              style={styles.newStoryButtonGradient}
            >
              <Ionicons name="book" size={24} color="white" />
              <Text style={styles.newStoryButtonText}>Start New Story</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradientContainer: {
    flex: 1,
  },
  scrollContainer: {
    flex: 1,
    paddingHorizontal: 24,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ea580c',
    textAlign: 'center',
    marginBottom: 16,
  },
  headerBadge: {
    backgroundColor: 'white',
    borderRadius: 20,
    paddingVertical: 12,
    paddingHorizontal: 24,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  headerBadgeText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginLeft: 8,
  },
  storiesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingBottom: 24,
  },
  storyCard: {
    marginBottom: 20,
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 12,
  },
  storyCardInner: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 24,
  },
  thumbnailContainer: {
    height: 96,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 3,
    borderColor: 'rgba(255, 255, 255, 0.6)',
  },
  thumbnailEmoji: {
    fontSize: 40,
  },
  storyInfo: {
    alignItems: 'center',
    marginBottom: 12,
  },
  storyTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#374151',
    textAlign: 'center',
    marginBottom: 8,
    lineHeight: 22,
    minHeight: 44, // Ensure consistent height for two lines
  },
  ratingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 8,
  },
  star: {
    marginHorizontal: 1,
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dateText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6b7280',
    marginLeft: 4,
  },
  readAgainButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  readAgainButtonGradient: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  readAgainButtonText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: 'white',
  },
  bottomAction: {
    paddingBottom: 32,
    paddingTop: 8,
  },
  newStoryButton: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 12,
  },
  newStoryButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 24,
    minHeight: 70,
  },
  newStoryButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginLeft: 12,
  },
});
