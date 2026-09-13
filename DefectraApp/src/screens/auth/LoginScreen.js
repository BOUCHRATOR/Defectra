import React, { useState } from 'react';
import { StyleSheet, Text, View, ImageBackground, TextInput, TouchableOpacity, Dimensions, Image } from 'react-native';

const { width } = Dimensions.get('window');

export default function LoginScreen({ navigation }) { 
  // États pour stocker l'email et le mot de passe saisis
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  // Fonction pour gérer la connexion avec l'API Django
  const handleLogin = async () => {
    if (!email || !password) {
      alert("Veuillez remplir tous les champs.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Succès : Redirection vers le tableau de bord
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        navigation.replace('Dashboard');
      } else {
        // Erreur renvoyée par le backend
        alert(data.error || "Identifiants incorrects.");
      }
    } catch (error) {
      console.error(error);
      alert("Erreur de connexion au serveur.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ImageBackground
      source={{ uri: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=1920&auto=format&fit=crop' }} 
      style={styles.background}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>

          {/* COLONNE GAUCHE */}
          <View style={styles.leftContent}>
            <Text style={styles.headline}>
              We let you{'\n'}
              <Text style={styles.headlineBold}>Analyze </Text>
              <Text style={styles.headlineRed}>Premium Cars</Text>
            </Text>
            <Text style={styles.subtext}>
              Plateforme d'inspection intelligente assistée par IA.
            </Text>

            <Image
              source={{ uri: 'https://pngimg.com/uploads/audi/audi_PNG1768.png' }} 
              style={styles.carImage}
              resizeMode="contain"
            />
          </View>

          {/* COLONNE DROITE */}
          <View style={styles.rightContent}>
            <View style={styles.redDecoration} />

            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardIcon}>🚘</Text>
                <Text style={styles.cardTitle}>Connexion</Text>
              </View>

              <TextInput
                style={styles.input}
                placeholder="Identifiant ou Email"
                placeholderTextColor="#999"
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
              />
              <TextInput
                style={styles.input}
                placeholder="Mot de passe"
                placeholderTextColor="#999"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
              />

              <View style={styles.actionContainer}>
                {/* Redirection vers l'écran d'inscription Register */}
                <TouchableOpacity 
                  style={styles.linkContainer}
                  onPress={() => navigation.navigate('Register')}
                >
                  <Text style={styles.linkText}>Créer un compte ?</Text>
                </TouchableOpacity>

                <TouchableOpacity 
                  style={styles.loginButton} 
                  onPress={handleLogin}
                  disabled={loading}
                >
                  <Text style={styles.loginButtonText}>
                    {loading ? "Connexion..." : "Se connecter"}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>

        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: { flex: 1, width: '100%', height: '100%' },
  overlay: { flex: 1, backgroundColor: 'rgba(20, 25, 30, 0.75)', justifyContent: 'center' },
  container: { flexDirection: width > 800 ? 'row' : 'column', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: '10%', flex: 1 },
  leftContent: { flex: 1, justifyContent: 'center', paddingRight: 50 },
  headline: { fontSize: 48, color: '#ffffff', fontWeight: '300', lineHeight: 55, marginBottom: 10 },
  headlineBold: { fontWeight: 'bold' },
  headlineRed: { fontWeight: 'bold', color: '#d90429' },
  subtext: { color: '#a0aec0', fontSize: 16, marginBottom: 40, maxWidth: 400 },
  carImage: { width: 600, height: 300, marginLeft: -50 },
  rightContent: { position: 'relative', width: 380, justifyContent: 'center' },
  redDecoration: { position: 'absolute', top: -20, left: -20, width: 100, height: 100, backgroundColor: '#d90429', zIndex: 1 },
  card: { backgroundColor: '#ffffff', padding: 40, shadowColor: '#000', shadowOffset: { width: 0, height: 10 }, shadowOpacity: 0.3, shadowRadius: 20, elevation: 10, zIndex: 2 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 30 },
  cardIcon: { fontSize: 24, marginRight: 10 },
  cardTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a1a' },
  input: { borderBottomWidth: 1, borderBottomColor: '#e2e8f0', color: '#1a1a1a', fontSize: 14, paddingVertical: 12, marginBottom: 20 },
  actionContainer: { marginTop: 10, alignItems: 'flex-end' },
  linkContainer: { marginBottom: 15 },
  linkText: { color: '#64748b', fontSize: 13, textDecorationLine: 'underline' },
  loginButton: { backgroundColor: '#d90429', paddingVertical: 12, paddingHorizontal: 30, borderRadius: 25, shadowColor: '#d90429', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.4, shadowRadius: 8, elevation: 5 },
  loginButtonText: { color: '#ffffff', fontWeight: 'bold', fontSize: 14 },
});