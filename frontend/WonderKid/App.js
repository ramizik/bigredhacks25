import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView, StyleSheet } from 'react-native';

import StoryScreen from './components/StoryScreen';
import HistoryScreen from './components/HistoryScreen';
import ProfileScreen from './components/ProfileScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" backgroundColor="#f0f9ff" />
      <LinearGradient
        colors={['#fef3c7', '#fdf2f8', '#dbeafe']}
        style={styles.gradient}
      >
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={({ route }) => ({
              headerShown: false,
              tabBarIcon: ({ focused, color, size }) => {
                let iconName;

                if (route.name === 'Story') {
                  iconName = focused ? 'book' : 'book-outline';
                } else if (route.name === 'History') {
                  iconName = focused ? 'time' : 'time-outline';
                } else if (route.name === 'Profile') {
                  iconName = focused ? 'person' : 'person-outline';
                }

                return <Ionicons name={iconName} size={28} color={color} />;
              },
              tabBarActiveTintColor: '#ffffff',
              tabBarInactiveTintColor: '#8b5cf6',
              tabBarStyle: {
                backgroundColor: '#ffffff',
                borderTopLeftRadius: 24,
                borderTopRightRadius: 24,
                height: 90,
                paddingTop: 10,
                paddingBottom: 30,
                shadowColor: '#000',
                shadowOffset: {
                  width: 0,
                  height: -4,
                },
                shadowOpacity: 0.1,
                shadowRadius: 12,
                elevation: 8,
                borderTopWidth: 0,
              },
              tabBarItemStyle: {
                borderRadius: 16,
                marginHorizontal: 8,
                marginVertical: 4,
              },
              tabBarLabelStyle: {
                fontSize: 12,
                fontWeight: '600',
                marginTop: 4,
              },
              tabBarActiveBackgroundColor: '#8b5cf6',
            })}
          >
            <Tab.Screen 
              name="Story" 
              component={StoryScreen}
              options={{
                tabBarLabel: 'Story',
              }}
            />
            <Tab.Screen 
              name="History" 
              component={HistoryScreen}
              options={{
                tabBarLabel: 'History',
              }}
            />
            <Tab.Screen 
              name="Profile" 
              component={ProfileScreen}
              options={{
                tabBarLabel: 'Profile',
              }}
            />
          </Tab.Navigator>
        </NavigationContainer>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f9ff',
  },
  gradient: {
    flex: 1,
  },
});
