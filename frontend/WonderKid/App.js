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
      <StatusBar style="dark" backgroundColor="#9683ec" />
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

                return <Ionicons name={iconName} size={32} color={color} />;
              },
              tabBarActiveTintColor: '#ffffff',
              tabBarInactiveTintColor: '#9683ec',
              tabBarStyle: {
                backgroundColor: '#ffffff',
                borderTopLeftRadius: 25,
                borderTopRightRadius: 25,
                height: 90,
                paddingTop: 10,
                paddingBottom: 15,
                paddingHorizontal: 10,
                shadowColor: '#000000',
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
                borderRadius: 18,
                marginHorizontal: 6,
                marginVertical: 6,
                paddingVertical: 12,
                paddingHorizontal: 12,
                minHeight: 60,
                height: 60,
                justifyContent: 'center',
                alignItems: 'center',
                flex: 1,
              },
              tabBarActiveBackgroundColor: '#ef233c',
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
    paddingTop: 10,
  },
  gradient: {
    flex: 1,
  },
});
