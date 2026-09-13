import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, TextInput, Image, Dimensions } from 'react-native';

const screenWidth = Dimensions.get('window').width;

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

// --- AJOUT : Fonction utilitaire pour l'image de profil ---
const getImageUrl = (image) => {
  if (!image) return null;
  if (image.startsWith("http://") || image.startsWith("https://")) return image;
  return `${BACKEND_URL}${image.startsWith("/") ? "" : "/"}${image}`;
};

export default function VehiclesScreen({ navigation }) {
  const [vehiclesList, setVehiclesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  
  const [selectedBrand, setSelectedBrand] = useState('All');

  // --- MODIFICATION 1 : État pour le profil utilisateur ---
  const [user, setUser] = useState(null);

  const brands = [
    'All',
    ...new Set(
      vehiclesList
        .map(vehicle => vehicle.brand)
        .filter(Boolean)
    )
  ];

  // --- MODIFICATION 2 : Charger le profil au démarrage ---
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      loadUser(token);
    }
    loadVehicles();
  }, []);

  // --- MODIFICATION 3 : Fonction pour charger le profil ---
  const loadUser = async (token) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/profile/`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (response.ok) {
        setUser(data);
      }
    } catch (error) {
      console.log("ERREUR CHARGEMENT PROFIL :", error);
    }
  };

  const loadVehicles = async () => {
    try {
      setLoading(true);

      const response = await fetch(
        'http://127.0.0.1:8000/api/vehicles/'
      );

      const data = await response.json();

      console.log('VEHICULES DEPUIS DJANGO :', data);

      if (data.success) {
        setVehiclesList(data.vehicles);
      } else {
        console.log('Erreur API véhicules');
      }

    } catch (error) {
      console.error('ERREUR CHARGEMENT VEHICULES :', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredVehicles = vehiclesList.filter((vehicle) => {
    const matchesBrand =
      selectedBrand === 'All' ||
      vehicle.brand === selectedBrand;

    const search = searchText.toLowerCase();

    const matchesSearch =
      vehicle.plate_number?.toLowerCase().includes(search) ||
      vehicle.brand?.toLowerCase().includes(search) ||
      vehicle.model?.toLowerCase().includes(search);

    return matchesBrand && matchesSearch;
  });

  // --- MODIFICATION 4 : Variables pour affichage profil ---
  const profileImageUrl = user?.profile_image || user?.avatar;
  const initialFirst = user?.first_name ? user.first_name.charAt(0).toUpperCase() : 'A';
  const initialLast = user?.last_name ? user.last_name.charAt(0).toUpperCase() : 'T';
  const fullName = user?.first_name ? `${user.first_name} ${user.last_name}` : 'A. Tahiri';

  return (
    <View style={styles.container}>
      
      {/* ==========================================
          1. BARRE LATÉRALE (NAVIGATION AVEC LOGO IMAGE)
      ========================================== */}
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
        
        <TouchableOpacity style={styles.menuItemActive}>
          <Text style={styles.menuIconActive}>🚘</Text>
          <Text style={styles.menuTextActive}>Mes Véhicules</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Scanner')}>
          <Text style={styles.menuIcon}>🔍</Text>
          <Text style={styles.menuText}>Scanner IA</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Settings')}>
          <Text style={styles.menuIcon}>⚙️</Text>
          <Text style={styles.menuText}>Paramètres</Text>
        </TouchableOpacity>

        <View style={{flex: 1}} />
        <TouchableOpacity style={styles.logoutBtn} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.logoutText}> Déconnexion</Text>
        </TouchableOpacity>
      </View>

      {/* ==========================================
          2. CONTENU PRINCIPAL (LISTE DES VÉHICULES)
      ========================================== */}
      <ScrollView style={styles.mainContent} showsVerticalScrollIndicator={false}>
        
        {/* En-tête de bienvenue */}
        <View style={styles.header}>
          <View>
            <Text style={styles.breadcrumb}>Parc Automobile</Text>
            <Text style={styles.pageTitle}>Véhicules Consultés</Text>
          </View>
          
          {/* --- MODIFICATION 5 : Badge Profil Dynamique --- */}
          <View style={styles.profileBadge}>
            <View style={styles.avatar}>
              {profileImageUrl ? (
                <Image 
                  source={{ uri: getImageUrl(profileImageUrl) }}
                  style={{ width: 36, height: 36, borderRadius: 18 }}
                  resizeMode="cover"
                />
              ) : (
                <Text style={{color: '#fff', fontWeight: 'bold'}}>
                  {initialFirst}{initialLast}
                </Text>
              )}
            </View>
            <View>
              <Text style={{fontWeight: 'bold', color: COLORS.textDark, fontSize: 13}}>
                {fullName}
              </Text>
              <Text style={{color: COLORS.textGray, fontSize: 11}}>Ingénieur Admin</Text>
            </View>
          </View>
        </View>

        {/* Barre de recherche et filtres de marques */}
        <View style={styles.searchFilterRow}>
          <View style={styles.searchBox}>
            <Text style={{marginRight: 10}}>🔍</Text>
            <TextInput
              placeholder="Rechercher un véhicule..."
              placeholderTextColor="#94a3b8"
              style={styles.searchInput}
              value={searchText}
              onChangeText={setSearchText}
            />          
            </View>
        </View>

        {/* Boutons de sélection par marque */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.brandsScroll}>
          {brands.map((brand) => (
            <TouchableOpacity 
              key={brand} 
              style={[styles.brandChip, selectedBrand === brand && styles.brandChipActive]}
              onPress={() => setSelectedBrand(brand)}
            >
              <Text style={[styles.brandChipText, selectedBrand === brand && styles.brandChipTextActive]}>
                {brand}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Grille / Liste des cartes de véhicules */}
        <View style={styles.vehiclesGrid}>
          {filteredVehicles.map((vehicle) => (
            <TouchableOpacity 
              key={vehicle.id} 
              style={styles.vehicleCard}
              onPress={() =>
              navigation.navigate('Historique', {
                vehicleId: vehicle.id,
              })
              }
            >
              <View style={styles.cardHeaderInfo}>
                <View>
                  <Text style={styles.vehicleName}>
                    {vehicle.brand} {vehicle.model}
                  </Text>

                  <Text style={styles.vehicleDetails}>
                    🚘 {vehicle.plate_number}
                  </Text>
                </View>
                <TouchableOpacity style={styles.arrowButton} onPress={() => navigation.navigate('History')}>
                  <Text style={{color: '#fff', fontWeight: 'bold'}}>↗</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.cardBodyImage}>
                {vehicle.vehicle_image ? (
                  <Image
                    source={{ uri: vehicle.vehicle_image }}
                    style={styles.carImageStyle}
                    resizeMode="contain"
                  />
                ) : (
                  <View style={styles.noImage}>
                    <Text style={{ color: COLORS.textGray }}>
                      Pas d'image
                    </Text>
                  </View>
                )}              
                </View>

              <View style={styles.cardFooterOverlay}>
                <View style={styles.footerInfoItem}>
                  <Text style={styles.footerLabel}>PLAQUE</Text>
                  <Text style={styles.footerValue}>{vehicle.plate_number}</Text>
                </View>

                <View style={styles.footerDivider} />

                <View style={styles.footerInfoItem}>
                  <Text style={styles.footerLabel}>ANNÉE</Text>
                  <Text style={styles.footerValue}>{vehicle.year || '-'}</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>

      </ScrollView>
    </View>
  );
}

// ==========================================
// STYLES DE LA PAGE VÉHICULES
// ==========================================
const styles = StyleSheet.create({
  container: { flex: 1, flexDirection: 'row', backgroundColor: COLORS.background },
  
  // Sidebar & Logo Image Agrandie
  sidebar: { width: 220, backgroundColor: COLORS.surface, borderRightWidth: 1, borderRightColor: COLORS.border, padding: 20, flexDirection: 'column' },
  logoContainer: { marginBottom: 25, marginTop: 10, height: 60, justifyContent: 'center' },
  logoImage: { width: '100%', height: 150 },

  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5 },
  menuItemActive: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5, backgroundColor: COLORS.primaryLight },
  menuIcon: { fontSize: 16, marginRight: 12, color: COLORS.textGray },
  menuIconActive: { fontSize: 16, marginRight: 12, color: COLORS.primary },
  menuText: { fontSize: 14, fontWeight: '600', color: COLORS.textGray },
  menuTextActive: { fontSize: 14, fontWeight: '700', color: COLORS.primary },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, marginTop: 'auto' },
  logoutText: { color: COLORS.textGray, fontWeight: '600' },

  // Contenu principal
  mainContent: { flex: 1, padding: 30 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  breadcrumb: { color: COLORS.textGray, fontSize: 12, marginBottom: 4 },
  pageTitle: { color: COLORS.textDark, fontSize: 24, fontWeight: '800' },
  profileBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.surface, padding: 6, paddingRight: 16, borderRadius: 30, borderWidth: 1, borderColor: COLORS.border },
  avatar: { width: 36, height: 36, borderRadius: 18, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center', marginRight: 10 },

  // Recherche & Filtres marques
  searchFilterRow: { marginBottom: 15 },
  searchBox: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.surface, borderWidth: 1, borderColor: COLORS.border, borderRadius: 12, paddingHorizontal: 15, height: 45 },
  searchInput: { flex: 1, fontSize: 13, color: COLORS.textDark },
  brandsScroll: { marginBottom: 25 },
  brandChip: { paddingVertical: 8, paddingHorizontal: 22, backgroundColor: COLORS.surface, borderWidth: 1, borderColor: COLORS.border, borderRadius: 20, marginRight: 10 },
  brandChipActive: { backgroundColor: COLORS.primary, borderColor: COLORS.primary },
  brandChipText: { fontWeight: '700', fontSize: 13, color: COLORS.textDark },
  brandChipTextActive: { color: '#fff' },

  // Cartes Véhicules
  vehiclesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 20 },
  vehicleCard: { width: '48%', backgroundColor: COLORS.surface, borderRadius: 20, padding: 20, borderWidth: 1, borderColor: COLORS.border, position: 'relative', overflow: 'hidden' },
  cardHeaderInfo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 15 },
  vehicleName: { fontSize: 18, fontWeight: '900', color: COLORS.textDark, marginBottom: 4 },
  vehicleDetails: { fontSize: 12, color: COLORS.textGray },
  arrowButton: { width: 32, height: 32, borderRadius: 16, backgroundColor: COLORS.textDark, justifyContent: 'center', alignItems: 'center' },
  cardBodyImage: { width: '100%', height: 160, justifyContent: 'center', alignItems: 'center', marginBottom: 15 },
  carImageStyle: { width: '100%', height: '100%' },
  cardFooterOverlay: { flexDirection: 'row', backgroundColor: '#f1f5f9', borderRadius: 12, padding: 12, alignItems: 'center', justifyContent: 'space-between' },
  footerInfoItem: { flex: 1, alignItems: 'center' },
  footerLabel: { fontSize: 10, color: COLORS.textGray, fontWeight: '600', marginBottom: 2 },
  footerValue: { fontSize: 13, fontWeight: '800', color: COLORS.textDark },
  footerDivider: { width: 1, height: 25, backgroundColor: COLORS.border },
  noImage: { width: '100%', height: '100%', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f1f5f9', borderRadius: 12 }
});