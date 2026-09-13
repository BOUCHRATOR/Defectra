import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import LoginScreen from './src/screens/auth/LoginScreen';
import DashboardScreen from './src/screens/main/DashboardScreen';
import HistoriqueScreen from './src/screens/main/HistoriqueScreen';
import ScannerScreen from './src/screens/main/ScannerScreen';
import VehiclesScreen from './src/screens/main/VehiclesScreen';
import SettingsScreen from './src/screens/main/SettingsScreen';
import RegisterScreen from './src/screens/auth/RegisterScreen';

import { VoiceProvider } from './src/components/VoiceContext';

const Stack = createNativeStackNavigator();

export default function App() {

  const [initialRoute, setInitialRoute] = useState(null);

  useEffect(() => {

    const token = localStorage.getItem(
      "access_token"
    );

    if (token) {
      setInitialRoute("Dashboard");
    } else {
      setInitialRoute("Login");
    }

  }, []);

  if (initialRoute === null) {
    return null;
  }

  return (
    <VoiceProvider>
    <NavigationContainer>

      <Stack.Navigator
        initialRouteName={initialRoute}
        screenOptions={{
          headerShown: false
        }}
      >

        <Stack.Screen
          name="Login"
          component={LoginScreen}
        />

        <Stack.Screen
          name="Register"
          component={RegisterScreen}
        />

        <Stack.Screen
          name="Dashboard"
          component={DashboardScreen}
        />

        <Stack.Screen
          name="Historique"
          component={HistoriqueScreen}
        />

        <Stack.Screen
          name="Scanner"
          component={ScannerScreen}
        />

        <Stack.Screen
          name="Vehicles"
          component={VehiclesScreen}
        />

        <Stack.Screen
          name="Settings"
          component={SettingsScreen}
        />

      </Stack.Navigator>

    </NavigationContainer>
    </VoiceProvider>
  );
}