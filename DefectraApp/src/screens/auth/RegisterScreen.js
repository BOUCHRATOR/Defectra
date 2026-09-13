import React, { useState } from 'react';
import { StyleSheet, Text, View, ImageBackground, TextInput, TouchableOpacity, ScrollView, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const COLORS = {
  background: '#f8fafc',
  surface: '#ffffff',
  primary: '#d90429',       // Rouge DEFECTRA
  primaryLight: '#fdf2f2',
  textDark: '#1e293b',
  textGray: '#64748b',
  border: '#e2e8f0',
};

export default function RegisterScreen({ navigation }) {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [city, setCity] = useState('');
  const [birthDate, setBirthDate] = useState('');
  
  // État pour stocker l'URI de l'image de profil uploadée
  const [profileImage, setProfileImage] = useState(null);

  // Fonction pour sélectionner une image depuis la galerie
  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 1,
    });

    if (!result.canceled) {
      setProfileImage(result.assets[0].uri);
    }
  };

  const handleRegister = async () => {

  const formData = new FormData();

  formData.append("first_name", firstName);
  formData.append("last_name", lastName);
  formData.append("email", email);
  formData.append("password", password);
  formData.append("city", city);
  formData.append("birth_date", birthDate);

  if (profileImage) {
  const imageResponse = await fetch(profileImage);
  const blob = await imageResponse.blob();

  formData.append("profile_image", blob, "profile.jpg");
}

  try {

    const response = await fetch(
      "http://127.0.0.1:8000/api/register/",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (response.ok) {

      alert("Compte créé avec succès");

      navigation.navigate("Login");

    } else {

      console.log(data);

      alert("Erreur");

    }

  } catch (error) {

    console.log(error);

  }

};

  return (
    <ImageBackground
      source={{ uri: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=1920&auto=format&fit=crop' }} 
      style={styles.background}
    >
      <View style={styles.overlay}>
        <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
          
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardIcon}>🚘</Text>
              <Text style={styles.cardTitle}>Créer un Compte DEFECTRA</Text>
            </View>

            {/* SECTION UPLOAD D'IMAGE DE PROFIL */}
            <View style={styles.uploadContainer}>
              <TouchableOpacity style={styles.avatarPreview} onPress={pickImage}>
                {profileImage ? (
                  <Image source={{ uri: profileImage }} style={styles.avatarImage} />
                ) : (
                  <Text style={styles.avatarPlaceholderText}>📷</Text>
                )}
              </TouchableOpacity>
              <View>
                <Text style={styles.label}>Image de profil (profile_image)</Text>
                <TouchableOpacity style={styles.uploadButton} onPress={pickImage}>
                  <Text style={styles.uploadButtonText}>📁 Choisir une photo</Text>
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.formGrid}>
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Prénom (first_name)</Text>
                <TextInput 
                  style={styles.input} 
                  placeholder="Ex: Adam" 
                  placeholderTextColor="#999"
                  value={firstName} 
                  onChangeText={setFirstName} 
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Nom (last_name)</Text>
                <TextInput 
                  style={styles.input} 
                  placeholder="Ex: Smith" 
                  placeholderTextColor="#999"
                  value={lastName} 
                  onChangeText={setLastName} 
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Adresse Email (email)</Text>
                <TextInput 
                  style={styles.input} 
                  placeholder="adam.smith@email.com" 
                  placeholderTextColor="#999"
                  value={email} 
                  onChangeText={setEmail} 
                  keyboardType="email-address"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Mot de passe (password)</Text>
                <TextInput 
                  style={styles.input} 
                  placeholder="********" 
                  placeholderTextColor="#999"
                  secureTextEntry 
                  value={password} 
                  onChangeText={setPassword} 
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Ville (city)</Text>
                <TextInput 
                  style={styles.input} 
                  placeholder="Ex: Berkane / Oujda" 
                  placeholderTextColor="#999"
                  value={city} 
                  onChangeText={setCity} 
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Date de naissance (birth_date)</Text>
                <TextInput 
                  style={styles.input} 
                  placeholder="JJ/MM/AAAA" 
                  placeholderTextColor="#999"
                  value={birthDate} 
                  onChangeText={setBirthDate} 
                />
              </View>
            </View>

            <View style={styles.actionContainer}>
              <TouchableOpacity 
                style={styles.linkContainer}
                onPress={() => navigation.navigate('Login')}
              >
                <Text style={styles.linkText}>Déjà un compte ? Se connecter</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.submitButton} onPress={handleRegister}>
                <Text style={styles.submitButtonText}>S'inscrire</Text>
              </TouchableOpacity>
            </View>

          </View>

        </ScrollView>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: { flex: 1, width: '100%', height: '100%' },
  overlay: { flex: 1, backgroundColor: 'rgba(20, 25, 30, 0.75)' },
  scrollContainer: { flexGrow: 1, justifyContent: 'center', alignItems: 'center', paddingVertical: 40 },
  card: { backgroundColor: '#ffffff', width: '90%', maxWidth: 600, padding: 40, borderRadius: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 10 }, shadowOpacity: 0.3, shadowRadius: 20, elevation: 10 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 25 },
  cardIcon: { fontSize: 24, marginRight: 10 },
  cardTitle: { fontSize: 22, fontWeight: '800', color: '#1a1a1a' },
  
  // Style pour l'upload d'image
  uploadContainer: { flexDirection: 'row', alignItems: 'center', marginBottom: 25, backgroundColor: '#f8fafc', padding: 15, borderRadius: 12, borderWidth: 1, borderColor: COLORS.border },
  avatarPreview: { width: 60, height: 60, borderRadius: 30, backgroundColor: '#e2e8f0', justifyContent: 'center', alignItems: 'center', overflow: 'hidden', marginRight: 20 },
  avatarImage: { width: '100%', height: '100%' },
  avatarPlaceholderText: { fontSize: 24 },
  uploadButton: { backgroundColor: COLORS.primaryLight, paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8, marginTop: 5, alignSelf: 'flex-start' },
  uploadButtonText: { color: COLORS.primary, fontWeight: 'bold', fontSize: 12 },

  formGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  inputGroup: { width: '48%', marginBottom: 20 },
  label: { fontSize: 12, fontWeight: '700', color: COLORS.textDark, marginBottom: 6 },
  input: { borderWidth: 1, borderColor: COLORS.border, borderRadius: 10, paddingHorizontal: 15, paddingVertical: 12, fontSize: 13, color: COLORS.textDark, backgroundColor: '#f8fafc' },
  actionContainer: { marginTop: 20, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  linkContainer: { paddingVertical: 10 },
  linkText: { color: COLORS.textGray, fontSize: 13, textDecorationLine: 'underline' },
  submitButton: { backgroundColor: COLORS.primary, paddingVertical: 14, paddingHorizontal: 30, borderRadius: 25, shadowColor: COLORS.primary, shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.4, shadowRadius: 8, elevation: 5 },
  submitButtonText: { color: '#ffffff', fontWeight: 'bold', fontSize: 14 },
});