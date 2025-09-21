import { Ionicons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';

import HistoryScreen from './components/HistoryScreen';
import ProfileScreen from './components/ProfileScreen';
import StoryScreen from './components/StoryScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" backgroundColor="#9683ec" translucent={false} />
      <LinearGradient
        colors={['#9683ec', '#5d16a6', '#7fdeff']}
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
              tabBarInactiveTintColor: '#ef233c',
              tabBarStyle: {
                backgroundColor: '#ffffff',
                borderTopLeftRadius: 25,
                borderTopRightRadius: 25,
                height: 90,
                paddingTop: 15,
                paddingBottom: 30,
                paddingHorizontal: 20,
                shadowColor: '#ef233c',
                shadowOffset: {
                  width: 0,
                  height: -8,
                },
                shadowOpacity: 0.15,
                shadowRadius: 20,
                elevation: 12,
                borderTopWidth: 0,
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
              },
              tabBarItemStyle: {
                borderRadius: 20,
                marginHorizontal: 6,
                marginVertical: 8,
                paddingVertical: 8,
                paddingHorizontal: 12,
              },
              tabBarLabelStyle: {
                display: 'none',
              },
              tabBarActiveBackgroundColor: '#ef233c',
            })}
          >
            <Tab.Screen 
              name="Story" 
              component={StoryScreen}
            />
            <Tab.Screen 
              name="History" 
              component={HistoryScreen}
            />
            <Tab.Screen 
              name="Profile" 
              component={ProfileScreen}
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
    backgroundColor: '#9683ec',
  },
  gradient: {
    flex: 1,
  },
});
