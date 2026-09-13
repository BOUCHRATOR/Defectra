import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, TextInput, Switch, Image, ActivityIndicator } from 'react-native';
import { useVoice } from "../../components/VoiceContext";

const BACKEND_URL = "http://127.0.0.1:8000";

const COLORS = {
  background: '#f8fafc',
  surface: '#ffffff',
  primary: '#d90429',       // Rouge DEFECTRA
  primaryLight: '#fdf2f2',
  textDark: '#1e293b',
  textGray: '#64748b',
  border: '#e2e8f0',
};

// ======================================================
// FONCTION UTILITAIRE POUR LES IMAGES
// ======================================================
const getImageUrl = (image) => {
  if (!image) return null;
  if (image.startsWith("http://") || image.startsWith("https://")) return image;
  return `${BACKEND_URL}${image.startsWith("/") ? "" : "/"}${image}`;
};

export default function SettingsScreen({ navigation }) {
  const [activeTab, setActiveTab] = useState('General');
  
  const [role, setRole] = useState('Ingénieur Admin');
  const [phone, setPhone] = useState('+212 6 00 00 00 00');
  const [company, setCompany] = useState('DEFECTRA SA');
  const [country, setCountry] = useState('Maroc');
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [city, setCity] = useState('');
  
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const {
    isVoiceEnabled,
    enableVoice,
    disableVoice,
    toggleVoice,
  } = useVoice();

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");

      if (!token) {
        navigation.replace("Login");
        return;
      }

      const response = await fetch(
        `${BACKEND_URL}/api/profile/`,
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      console.log("================================");
      console.log("UTILISATEUR CONNECTÉ");
      console.log("STATUS :", response.status);
      console.log("DATA :", data);
      console.log("================================");

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          navigation.replace("Login");
          return;
        }
        throw new Error("Impossible de récupérer le profil");
      }

      setUser(data);
      setName(`${data.first_name || ''} ${data.last_name || ''}`.trim());
      setEmail(data.email || '');
      setCity(data.city || '');

    } catch (error) {
      console.log("ERREUR PROFIL :", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={{ marginTop: 10, color: COLORS.textGray }}>Chargement des paramètres...</Text>
      </View>
    );
  }

  // Déterminer l'image du profil (prend en compte "profile_image" ou "avatar" selon votre modèle Django)
  const profileImageUrl = user?.profile_image || user?.avatar;

  // Calcul des initiales dynamiques
  const initialFirst = user?.first_name ? user.first_name.charAt(0).toUpperCase() : 'A';
  const initialLast = user?.last_name ? user.last_name.charAt(0).toUpperCase() : 'T';

  return (
    <View style={styles.container}>
      
      {/* BARRE LATÉRALE */}
      <View style={styles.sidebar}>
        <View style={styles.logoContainer}>
          <Image 
            source={require('../../../assets/logo.png')} 
            style={styles.logoImage} 
            resizeMode="contain" 
          />
        </View>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Dashboard')}>
          <Text style={styles.menuIcon}>📊</Text>
          <Text style={styles.menuText}>Tableau de bord</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Vehicles')}>
          <Text style={styles.menuIcon}>🚘</Text>
          <Text style={styles.menuText}>Mes Véhicules</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Scanner')}>
          <Text style={styles.menuIcon}>🔍</Text>
          <Text style={styles.menuText}>Scanner IA</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItemActive}>
          <Text style={styles.menuIconActive}>⚙️</Text>
          <Text style={styles.menuTextActive}>Paramètres</Text>
        </TouchableOpacity>

        <View style={styles.spacer} />
        <TouchableOpacity style={styles.logoutBtn} onPress={() => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            navigation.replace('Login');
        }}>
          <Text style={styles.logoutText}> Déconnexion</Text>
        </TouchableOpacity>
      </View>

      {/* CONTENU PRINCIPAL */}
      <ScrollView style={styles.mainContent} showsVerticalScrollIndicator={false}>
        
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.pageTitle}>Paramètres</Text>
            <Text style={styles.pageSubtitle}>Gérez vos informations et préférences d'interaction vocale.</Text>
          </View>
          <View style={styles.actionButtons}>
            <TouchableOpacity style={styles.cancelBtn} onPress={() => alert('Modifications annulées')}>
              <Text style={styles.cancelBtnText}>Annuler</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.saveBtn} onPress={() => alert('Paramètres enregistrés avec succès !')}>
              <Text style={styles.saveBtnText}>Enregistrer</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.settingsLayout}>
          
          <View style={styles.settingsMenu}>
            <TouchableOpacity 
              style={[styles.settingsMenuItem, activeTab === 'General' && styles.settingsMenuItemActive]}
              onPress={() => setActiveTab('General')}
            >
              <Text style={[styles.settingsMenuText, activeTab === 'General' && styles.settingsMenuTextActive]}>ℹ️ Informations Générales</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.settingsMenuItem, activeTab === 'Voice' && styles.settingsMenuItemActive]}
              onPress={() => setActiveTab('Voice')}
            >
              <Text style={[styles.settingsMenuText, activeTab === 'Voice' && styles.settingsMenuTextActive]}>🎙️ Assistant Vocal & IA</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingsMenuItem} onPress={() => alert('Sécurité')}>
              <Text style={styles.settingsMenuText}>🛡️ Sécurité</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingsMenuItem} onPress={() => alert('Notifications')}>
              <Text style={styles.settingsMenuText}>🔔 Notifications</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingsMenuItem} onPress={() => alert('Compte')}>
              <Text style={styles.settingsMenuText}>👤 Compte</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.settingsCard}>
            
            {activeTab === 'General' ? (
              <>
                <Text style={styles.cardTitle}>Informations Générales</Text>
                <Text style={styles.cardSubtitle}>Mettez à jour vos informations personnelles et professionnelles.</Text>
                
                <View style={styles.profileSection}>
                  {/* AFFICHAGE DYNAMIQUE DE L'IMAGE OU DES INITIALES */}
                  <View style={styles.avatarLarge}>
                    {profileImageUrl ? (
                      <Image 
                        source={{ uri: getImageUrl(profileImageUrl) }}
                        style={{ width: 64, height: 64, borderRadius: 32 }}
                        resizeMode="cover"
                      />
                    ) : (
                      <Text style={{color: '#fff', fontSize: 20, fontWeight: 'bold'}}>
                        {initialFirst}{initialLast}
                      </Text>
                    )}
                  </View>
                  <View style={{marginLeft: 20}}>
                    <Text style={{fontWeight: 'bold', color: COLORS.textDark, fontSize: 16}}>{name || "Utilisateur"}</Text>
                    <Text style={{color: COLORS.textGray, fontSize: 13}}>{role} • {city || "Location non définie"}</Text>
                    <View style={{flexDirection: 'row', marginTop: 10}}>
                      <TouchableOpacity style={styles.uploadPhotoBtn}><Text style={styles.uploadPhotoText}>Changer la photo</Text></TouchableOpacity>
                      <TouchableOpacity style={styles.deletePhotoBtn}><Text style={styles.deletePhotoText}>Supprimer</Text></TouchableOpacity>
                    </View>
                  </View>
                </View>

                <View style={styles.formGrid}>
                  <View style={styles.inputGroup}>
                    <Text style={styles.label}>Nom complet</Text>
                    <TextInput style={styles.input} value={name} onChangeText={setName} />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.label}>Adresse Email</Text>
                    <TextInput style={styles.input} value={email} onChangeText={setEmail} keyboardType="email-address" />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.label}>Numéro de Téléphone</Text>
                    <TextInput style={styles.input} value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.label}>Entreprise / Organisation</Text>
                    <TextInput style={styles.input} value={company} onChangeText={setCompany} />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.label}>Pays</Text>
                    <TextInput style={styles.input} value={country} onChangeText={setCountry} />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.label}>Ville / Région</Text>
                    <TextInput style={styles.input} value={city} onChangeText={setCity} />
                  </View>
                </View>
              </>
            ) : (
              <>
                <Text style={styles.cardTitle}>🎙️ Configuration de l'Assistant Vocal</Text>
                <Text style={styles.cardSubtitle}>Activez ou désactivez les interactions vocales pour piloter DEFECTRA par la voix.</Text>

                <View style={styles.voiceToggleBox}>
                  <View style={{flex: 1, marginRight: 20}}>
                    <Text style={{fontSize: 16, fontWeight: 'bold', color: COLORS.textDark, marginBottom: 5}}>
                      Activation de l'interaction vocale
                    </Text>
                    <Text style={{fontSize: 13, color: COLORS.textGray, lineHeight: 18}}>
                      Permet à l'application de recevoir vos commandes vocales ("Scanner", "Historique", "Rapport PDF") et de vous dicter les synthèses LLM.
                    </Text>
                  </View>
                  <Switch
                      trackColor={{
                        false: '#cbd5e1',
                        true: '#fca5a5',
                      }}
                      thumbColor={
                        isVoiceEnabled
                          ? COLORS.primary
                          : '#f4f3f4'
                      }
                      ios_backgroundColor="#3e3e3e"
                      onValueChange={toggleVoice}
                      value={isVoiceEnabled}
                    />
                </View>

                {isVoiceEnabled ? (
                  <View style={styles.voiceActiveStatus}>
                    <Text
                      style={{
                        color: '#059669',
                        fontWeight: 'bold',
                        fontSize: 13,
                      }}
                    >
                      🟢 Le module de reconnaissance vocale est actif et prêt à écouter.
                    </Text>
                  </View>
                ) : (
                  <View style={styles.voiceInactiveStatus}>
                    <Text
                      style={{
                        color: COLORS.primary,
                        fontWeight: 'bold',
                        fontSize: 13,
                      }}
                    >
                      🔴 L'interaction vocale est actuellement désactivée.
                    </Text>
                  </View>
                )}
              </>
            )}

          </View>

        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, flexDirection: 'row', backgroundColor: COLORS.background },
  
  sidebar: { width: 220, backgroundColor: COLORS.surface, borderRightWidth: 1, borderRightColor: COLORS.border, padding: 20, flexDirection: 'column' },
  logoContainer: { marginBottom: 25, marginTop: 10, height: 60, justifyContent: 'center' }, // Agrandit
  logoImage: { width: '100%', height: 150 }, // Agrandit l'image du logo
  
  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5 },
  menuItemActive: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5, backgroundColor: COLORS.primaryLight },
  menuIcon: { fontSize: 16, marginRight: 12, color: COLORS.textGray },
  menuIconActive: { fontSize: 16, marginRight: 12, color: COLORS.primary },
  menuText: { fontSize: 14, fontWeight: '600', color: COLORS.textGray },
  menuTextActive: { fontSize: 14, fontWeight: '700', color: COLORS.primary },
  spacer: { flex: 1 },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12 },
  logoutText: { color: COLORS.textGray, fontWeight: '600' },

  mainContent: { flex: 1, padding: 30 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25 },
  pageTitle: { color: COLORS.textDark, fontSize: 24, fontWeight: '800' },
  pageSubtitle: { color: COLORS.textGray, fontSize: 13, marginTop: 2 },
  actionButtons: { flexDirection: 'row', gap: 12 },
  cancelBtn: { paddingVertical: 10, paddingHorizontal: 20, borderRadius: 10, borderWidth: 1, borderColor: COLORS.border, backgroundColor: '#fff' },
  cancelBtnText: { color: COLORS.textDark, fontWeight: 'bold', fontSize: 13 },
  saveBtn: { paddingVertical: 10, paddingHorizontal: 20, borderRadius: 10, backgroundColor: COLORS.primary },
  saveBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 13 },

  settingsLayout: { flexDirection: 'row', gap: 25 },
  settingsMenu: { width: 240, backgroundColor: COLORS.surface, borderRadius: 16, padding: 12, borderWidth: 1, borderColor: COLORS.border, height: 'fit-content' },
  settingsMenuItem: { paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5 },
  settingsMenuItemActive: { backgroundColor: COLORS.primaryLight },
  settingsMenuText: { fontSize: 13, fontWeight: '600', color: COLORS.textGray },
  settingsMenuTextActive: { color: COLORS.primary, fontWeight: 'bold' },

  settingsCard: { flex: 1, backgroundColor: COLORS.surface, borderRadius: 16, padding: 30, borderWidth: 1, borderColor: COLORS.border },
  cardTitle: { fontSize: 20, fontWeight: '800', color: COLORS.textDark, marginBottom: 5 },
  cardSubtitle: { fontSize: 13, color: COLORS.textGray, marginBottom: 25 },
  
  profileSection: { flexDirection: 'row', alignItems: 'center', marginBottom: 30, borderBottomWidth: 1, borderBottomColor: COLORS.border, paddingBottom: 25 },
  avatarLarge: { width: 64, height: 64, borderRadius: 32, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center' },
  uploadPhotoBtn: { backgroundColor: COLORS.primaryLight, paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8, marginRight: 10 },
  uploadPhotoText: { color: COLORS.primary, fontWeight: 'bold', fontSize: 12 },
  deletePhotoBtn: { borderWidth: 1, borderColor: COLORS.border, paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8 },
  deletePhotoText: { color: COLORS.textGray, fontWeight: 'bold', fontSize: 12 },

  formGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 20 },
  inputGroup: { width: '48%' },
  label: { fontSize: 12, fontWeight: '700', color: COLORS.textDark, marginBottom: 6 },
  input: { borderWidth: 1, borderColor: COLORS.border, borderRadius: 10, paddingHorizontal: 15, paddingVertical: 10, fontSize: 13, color: COLORS.textDark, backgroundColor: '#fff' },

  voiceToggleBox: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', borderWidth: 1, borderColor: COLORS.border, borderRadius: 16, padding: 20, marginTop: 10 },
  voiceActiveStatus: { backgroundColor: '#ecfdf5', borderWidth: 1, borderColor: '#a7f3d0', padding: 15, borderRadius: 12, marginTop: 20, alignItems: 'center' },
  voiceInactiveStatus: { backgroundColor: '#fef2f2', borderWidth: 1, borderColor: '#fecaca', padding: 15, borderRadius: 12, marginTop: 20, alignItems: 'center' }
});