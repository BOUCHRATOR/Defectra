import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';

const BACKEND_URL = "http://127.0.0.1:8000";

const COLORS = {
  background: '#f8fafc',
  surface: '#ffffff',
  primary: '#d90429',
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

export default function HistoriqueScreen({ route, navigation }) {
  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- MODIFICATION 1 : État pour le profil utilisateur ---
  const [user, setUser] = useState(null);

  const vehicleId = route?.params?.vehicleId;

  // ======================================================
  // CHARGEMENT VEHICULE ET PROFIL
  // ======================================================
  useEffect(() => {
    // Appel pour récupérer le profil
    const token = localStorage.getItem("access_token");
    if (token) {
      loadUser(token);
    }

    if (vehicleId) {
      fetchVehicle();
    } else {
      setLoading(false);
      setError("Aucun véhicule sélectionné.");
    }
  }, [vehicleId]);

  // --- MODIFICATION 2 : Fonction pour charger le profil ---
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

  // ======================================================
  // API
  // ======================================================
  const fetchVehicle = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${BACKEND_URL}/api/vehicles/${vehicleId}/`);
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
      }

      const data = await response.json();

console.log("=================================");
console.log("REPONSE DJANGO VEHICULE");
console.log("=================================");

console.log("STATUS :", response.status);

console.log("DATA COMPLETE :", data);

console.log("VEHICULE :", data.vehicle);

console.log("IMAGE :", data.vehicle?.vehicle_image);

console.log("NOMBRE DE DEFAUTS :", data.vehicle?.defects_count);

console.log("DEFAUTS :", data.vehicle?.defects);

console.log("INSPECTIONS :", data.vehicle?.inspections);

console.log("=================================");

      if (!data.success) {
        throw new Error(data.message || "Erreur API");
      }

      setVehicle(data.vehicle);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // ======================================================
  // LOADING & ERROR
  // ======================================================
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Chargement des données...</Text>
      </View>
    );
  }

  if (error || !vehicle) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.errorText}>
          {error || "Aucun véhicule sélectionné."}
        </Text>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.navigate('Vehicles')}
        >
          <Text style={styles.backButtonText}>Retour aux véhicules</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // ======================================================
  // VARIABLES UTILES
  // ======================================================
  const inspections = vehicle.inspections || [];
  const defects = vehicle.defects || [];
const severityToNumber = (severity) => {
  switch (String(severity).toUpperCase()) {
    case "LOW":
      return 1;
    case "MEDIUM":
      return 2;
    case "HIGH":
      return 3;
    default:
      return 0;
  }
};

  // --- MODIFICATION 3 : Préparation des variables pour l'affichage profil ---
  const profileImageUrl = user?.profile_image || user?.avatar;
  const initialFirst = user?.first_name ? user.first_name.charAt(0).toUpperCase() : 'A';
  const initialLast = user?.last_name ? user.last_name.charAt(0).toUpperCase() : 'T';
  const fullName = user?.first_name ? `${user.first_name} ${user.last_name}` : 'A. Tahiri';

  return (
    <View style={styles.container}>

      {/* ==================================================
          SIDEBAR
      ================================================== */}
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

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Scanner')}>
          <Text style={styles.menuIcon}>🔍</Text>
          <Text style={styles.menuText}>Scanner IA</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItemActive} onPress={() => navigation.navigate('Vehicles')}>
          <Text style={styles.menuIconActive}>🚘</Text>
          <Text style={styles.menuTextActive}>Mes Véhicules</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Settings')}>
          <Text style={styles.menuIcon}>⚙️</Text>
          <Text style={styles.menuText}>Paramètres</Text>
        </TouchableOpacity>

        <View style={{ flex: 1 }} />

        <TouchableOpacity style={styles.logoutBtn} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.logoutText}>Déconnexion</Text>
        </TouchableOpacity>
      </View>

      {/* ==================================================
          CONTENU PRINCIPAL
      ================================================== */}
      <ScrollView style={styles.mainContent} showsVerticalScrollIndicator={false}>

        {/* HEADER */}
        <View style={styles.header}>
          <View>
            <Text style={styles.breadcrumb}>Véhicules / Détails</Text>
            <Text style={styles.pageTitle}>Détails du Véhicule</Text>
          </View>

          {/* --- MODIFICATION 4 : Badge Profil Dynamique --- */}
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

        <View style={styles.contentGrid}>

          {/* ==================================================
              GAUCHE (IMAGE & INFOS VEHICULE)
          ================================================== */}
          <View style={styles.leftColumn}>
            <View style={styles.card}>

              {/* IMAGE PRINCIPALE */}
              {defects.length > 0 && defects[0].defect_image ? (
                <Image
                  source={{
                    uri: getImageUrl(defects[0].defect_image)
                  }}
                  style={styles.mainCarImage}
                  resizeMode="contain"
                />
              ) : (
                <View style={styles.noImage}>
                  <Text>Pas d'image disponible</Text>
                </View>
              )}

              {/* MINIATURES */}
              <View style={styles.thumbnailsContainer}>
                <View style={styles.thumbnailBox}>
                  {vehicle.vehicle_image && (
                    <Image source={{ uri: getImageUrl(vehicle.vehicle_image) }} style={styles.thumbnailImg} resizeMode="contain" />
                  )}
                </View>
                <View style={styles.thumbnailBox}>
                  {vehicle.vehicle_image && (
                    <Image source={{ uri: getImageUrl(vehicle.vehicle_image) }} style={styles.thumbnailImg} resizeMode="contain" />
                  )}
                </View>
                <View style={styles.thumbnailBox}>
                  {vehicle.vehicle_image && (
                    <Image source={{ uri: getImageUrl(vehicle.vehicle_image) }} style={styles.thumbnailImg} resizeMode="contain" />
                  )}
                </View>
              </View>

              {/* TITRE ET BADGE */}
              <Text style={styles.carCategory}>Véhicule</Text>
              <View style={styles.titleRow}>
                <View>
                  <Text style={styles.carTitle}>
                    {vehicle.brand} {vehicle.model}
                  </Text>
                </View>
                <Text style={styles.plate}>
                  Plaque : {vehicle.plate_number}
                </Text>
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>
                    Analysé ({defects.length} Défauts)
                  </Text>
                </View>
              </View>

              {/* DESCRIPTION GENERALE */}
              <Text style={styles.sectionTitle}>À propos de l'inspection</Text>
              <Text style={styles.description}>
                {inspections.length > 0 && inspections[0].notes 
                  ? inspections[0].notes 
                  : "L'inspection IA a révélé une rayure sur le flanc gauche (sévérité 88%) et une bosse mineure sur la portière arrière (sévérité 76%). Une intervention de polissage abrasif est recommandée."}
              </Text>

            </View>
          </View>

          {/* ==================================================
              DROITE (GRAPHIQUE & DEFAUTS)
          ================================================== */}
          <View style={styles.rightColumn}>

            {/* GRAPHIQUE */}
            <View style={styles.card}>
              <View style={styles.titleRow}>
                <Text style={styles.sectionTitle}>Activité d'Analyse (Sévérité)</Text>
                <Text style={styles.smallText}>Derniers mois</Text>
              </View>

              <LineChart
  data={{
    labels:
      defects.length > 0
        ? defects.map((defect, index) =>
            `${defect.defect_name || "Défaut"} ${index + 1}`
          )
        : ["Aucun"],

    datasets: [
      {
        data:
          defects.length > 0
            ? defects.map((defect) =>
                severityToNumber(defect.severity)
              )
            : [0],
      },
    ],
  }}
  width={340}
  height={200}
  fromZero={true}
  yAxisSuffix=""
  yAxisInterval={1}
  chartConfig={{
    backgroundColor: COLORS.surface,
    backgroundGradientFrom: COLORS.surface,
    backgroundGradientTo: COLORS.surface,
    decimalPlaces: 0,

    color: (opacity = 1) =>
      `rgba(217, 4, 41, ${opacity})`,

    labelColor: () => COLORS.textGray,

    propsForDots: {
      r: "5",
      strokeWidth: "2",
      stroke: COLORS.primary,
    },
  }}
  bezier
  style={{
    marginVertical: 5,
    marginLeft: -15,
  }}
/>
            </View>

            {/* DETAILS DES DEFAUTS */}
            <View style={styles.card}>
              <Text style={styles.sectionTitle}>
                Détails des défauts
              </Text>

              {defects && defects.length > 0 ? (
                defects.map((defect) => (
                  <View key={defect.id} style={styles.defectItem}>
                    
                    <View style={styles.defectHeader}>
                      <Text style={styles.defectName}>
                        {defect.defect_name}
                      </Text>
                      <View style={styles.severityBadge}>
                        <Text style={styles.severityText}>
                          {defect.severity || "UNKNOWN"}
                        </Text>
                      </View>
                    </View>

                    <Text style={styles.defectPosition}>
                      📍 Position : {defect.location || "Non précisée"}
                    </Text>

                    <Text style={styles.defectConfidence}>
                      🎯 Confiance : {
                        defect.confidence
                          ? `${Math.round(defect.confidence * 100)}%`
                          : "-"
                      }
                    </Text>

                    <Text style={styles.defectDescription}>
                      {defect.description}
                    </Text>

                    {defect.solution ? (
                      <Text style={styles.defectSolution}>
                        💡 Solution : {defect.solution}
                      </Text>
                    ) : null}

                  </View>
                ))
              ) : (
                <Text style={styles.featureText}>
                  Aucun défaut détecté pour ce véhicule.
                </Text>
              )}
            </View>

          </View>
        </View>
      </ScrollView>
    </View>
  );
}

// ==========================================================
// STYLES
// ==========================================================
const styles = StyleSheet.create({
  container: { flex: 1, flexDirection: 'row', backgroundColor: COLORS.background },
  sidebar: { width: 220, backgroundColor: COLORS.surface, borderRightWidth: 1, borderRightColor: COLORS.border, padding: 20 },
  logoContainer: { marginBottom: 25, marginTop: 10, height: 60, justifyContent: 'center' },
  logoImage: { width: '100%', height: 150 },
  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5 },
  menuItemActive: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5, backgroundColor: COLORS.primaryLight },
  menuIcon: { fontSize: 16, marginRight: 12 },
  menuIconActive: { fontSize: 16, marginRight: 12 },
  menuText: { fontSize: 14, fontWeight: '600', color: COLORS.textGray },
  menuTextActive: { fontSize: 14, fontWeight: '700', color: COLORS.primary },
  logoutBtn: { paddingVertical: 12 },
  logoutText: { color: COLORS.textGray, fontWeight: '600' },
  
  mainContent: { flex: 1, padding: 30 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25 },
  breadcrumb: { color: COLORS.textGray, fontSize: 12 },
  pageTitle: { color: COLORS.textDark, fontSize: 24, fontWeight: '800' },
  profileBadge: { flexDirection: 'row', alignItems: 'center' },
  avatar: { width: 36, height: 36, borderRadius: 18, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center', marginRight: 10 },
  
  contentGrid: { flexDirection: 'row', flexWrap: 'wrap' },
  leftColumn: { flex: 1.5, minWidth: 400, marginRight: 25 },
  rightColumn: { flex: 1, minWidth: 300 },
  card: { backgroundColor: COLORS.surface, borderRadius: 16, padding: 24, marginBottom: 20, borderWidth: 1, borderColor: COLORS.border },
  
  mainCarImage: { width: '100%', height: 250, marginBottom: 20, borderRadius: 12 },
  noImage: { width: '100%', height: 250, backgroundColor: '#f1f5f9', borderRadius: 12, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  
  thumbnailsContainer: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  thumbnailBox: { flex: 1, height: 60, borderWidth: 1, borderColor: COLORS.border, borderRadius: 10, marginHorizontal: 4, padding: 4 },
  thumbnailImg: { width: '100%', height: '100%' },

  carCategory: { color: COLORS.textGray, fontSize: 13, marginBottom: 5 },
  titleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
  carTitle: { fontSize: 24, fontWeight: '800', color: COLORS.textDark },
  plate: { color: COLORS.textDark, fontSize: 14, fontWeight: '600' },
  smallText: { color: COLORS.textGray, fontSize: 12 },
  
  badge: { backgroundColor: COLORS.primary, paddingHorizontal: 12, paddingVertical: 7, borderRadius: 20 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  
  sectionTitle: { fontSize: 15, fontWeight: '700', color: COLORS.textDark, marginBottom: 10 },
  description: { color: COLORS.textGray, lineHeight: 20, fontSize: 13, marginTop: 10 },
  featureText: { color: COLORS.textGray, fontSize: 13 },

  // Styles spécifiques aux défauts
  defectItem: { backgroundColor: '#f8fafc', borderRadius: 12, padding: 15, marginBottom: 12, borderWidth: 1, borderColor: COLORS.border },
  defectHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  defectName: { fontSize: 15, fontWeight: '800', color: COLORS.textDark, flex: 1 },
  defectLocation: { fontSize: 12, color: COLORS.textGray },
  severityBadge: { backgroundColor: COLORS.primaryLight, paddingHorizontal: 8, paddingVertical: 5, borderRadius: 12 },
  severityText: { color: COLORS.primary, fontWeight: '800', fontSize: 11 },
  defectPosition: { color: COLORS.textGray, fontSize: 12, marginBottom: 5 },
  defectConfidence: { color: COLORS.textGray, fontSize: 12, marginBottom: 8 },
  defectDescription: { color: COLORS.textGray, fontSize: 12, lineHeight: 18, marginBottom: 8 },
  defectSolution: { color: COLORS.textDark, fontSize: 12, lineHeight: 18, fontWeight: '600' },

  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.background },
  loadingText: { marginTop: 10, color: COLORS.textGray },
  errorText: { color: COLORS.primary, fontSize: 16, marginBottom: 20 },
  backButton: { backgroundColor: COLORS.primary, paddingHorizontal: 20, paddingVertical: 12, borderRadius: 10 },
  backButtonText: { color: '#fff', fontWeight: '700' }
});