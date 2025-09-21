import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React from 'react';
import {
    Dimensions,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    View
} from 'react-native';

const { width } = Dimensions.get('window');

export default function ProfileScreen() {
  const profileData = {
    name: "Adventure Seeker",
    avatar: "👧",
    level: "Beginner",
    storiesRead: 6,
    totalTime: "2h 15m",
    readingSince: "Sep 21",
    favoriteGenre: "Adventure"
  };


  const readingGoals = [
    { 
      label: "Daily Reading", 
      current: 1, 
      target: 2, 
      unit: "stories",
      color: '#9683ec'
    },
    { 
      label: "Weekly Goal", 
      current: 6, 
      target: 10, 
      unit: "stories",
      color: '#5d16a6'
    }
  ];


  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={['#a5e6ba', '#7fdeff', '#9683ec']}
        style={styles.gradientContainer}
      >
      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {/* Profile Header */}
        <View style={styles.profileHeader}>
          <View style={styles.profileCard}>
            <View style={styles.profileContent}>
              {/* Avatar */}
              <LinearGradient
                colors={['#9683ec', '#5d16a6']}
                style={styles.avatar}
              >
                <Text style={styles.avatarEmoji}>{profileData.avatar}</Text>
              </LinearGradient>
              
              {/* Name and Level */}
              <Text style={styles.profileName}>{profileData.name}</Text>
              <View style={styles.levelContainer}>
                <LinearGradient
                  colors={['#f35b04', '#ef233c']}
                  style={styles.levelBadge}
                >
                  <Ionicons name="trophy" size={20} color="white" />
                  <Text style={styles.levelText}>{profileData.level}</Text>
                </LinearGradient>
              </View>
            </View>
          </View>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <View style={styles.statIconContainer}>
                <View style={styles.statIcon}>
                  <Ionicons name="book" size={24} color="#9683ec" />
                </View>
              </View>
              <Text style={styles.statNumber}>{profileData.storiesRead}</Text>
              <Text style={styles.statLabel}>Stories Read</Text>
            </View>

            <View style={styles.statCard}>
              <View style={styles.statIconContainer}>
                <View style={styles.statIcon}>
                  <Ionicons name="calendar" size={24} color="#a5e6ba" />
                </View>
              </View>
              <Text style={styles.statNumber}>{profileData.readingSince}</Text>
              <Text style={styles.statLabel}>Reading since</Text>
            </View>
          </View>
        </View>

        {/* Reading Goals */}
        <View style={styles.section}>
          <View style={styles.sectionCard}>
            <View style={styles.sectionHeader}>
              <Ionicons name="flag" size={24} color="#5d16a6" />
              <Text style={styles.sectionTitle}>Reading Goals</Text>
            </View>
            
            <View style={styles.goalsContainer}>
              {readingGoals.map((goal, index) => (
                <View key={index} style={styles.goalItem}>
                  <View style={styles.goalHeader}>
                    <Text style={styles.goalLabel}>{goal.label}</Text>
                    <Text style={styles.goalNumbers}>
                      {goal.current}/{goal.target} {goal.unit}
                    </Text>
                  </View>
                  <View style={styles.progressBarContainer}>
                    <View style={styles.progressBarBg}>
                      <View 
                        style={[
                          styles.progressBarFill, 
                          { 
                            width: `${(goal.current / goal.target) * 100}%`,
                            backgroundColor: goal.color 
                          }
                        ]}
                      />
                    </View>
                  </View>
                </View>
              ))}
            </View>
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Built with ❤️ for BRH</Text>
        </View>

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
    paddingHorizontal: 24,
  },
  profileHeader: {
    paddingVertical: 32,
  },
  profileCard: {
    backgroundColor: 'white',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 12,
  },
  profileContent: {
    alignItems: 'center',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  avatarEmoji: {
    fontSize: 40,
  },
  profileName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 8,
  },
  levelContainer: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  levelBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
  },
  levelText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginLeft: 8,
  },
  statsContainer: {
    marginBottom: 24,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    width: (width - 60) / 2,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
  statIconContainer: {
    marginBottom: 12,
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
    textAlign: 'center',
  },
  section: {
    marginBottom: 24,
  },
  sectionCard: {
    backgroundColor: 'white',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#374151',
    marginLeft: 12,
  },
  goalsContainer: {
    gap: 16,
  },
  goalItem: {
    marginBottom: 8,
  },
  goalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  goalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  goalNumbers: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
  },
  progressBarContainer: {
    width: '100%',
  },
  progressBarBg: {
    width: '100%',
    height: 12,
    backgroundColor: '#e5e7eb',
    borderRadius: 6,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 6,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 24,
    paddingBottom: 32,
  },
  footerText: {
    fontSize: 16,
    color: '#6b7280',
    fontStyle: 'italic',
  },
});
