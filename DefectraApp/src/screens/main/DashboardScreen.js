import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Image, Dimensions } from 'react-native';
import { BarChart } from 'react-native-chart-kit';

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
  tagNew: '#0ea5e9',
  tagProgress: '#f59e0b',
  tagSubmitted: '#6366f1'
};

export default function DashboardScreen({ navigation }) {
  const [activeTab, setActiveTab] = useState('Pending Queries');
  const [timeFilter, setTimeFilter] = useState('Mois');

  const [consultations, setConsultations] = useState([]);
  const [loadingConsultations, setLoadingConsultations] = useState(true);

  const [statistics, setStatistics] = useState({
    vehicles_consulted: 0,
    inspections: 0,
    defects: 0,
    severe_defects: 0,
    chart: []
  });
  const [loadingStatistics, setLoadingStatistics] = useState(true);

  // --- MODIFICATION 1 : État pour le profil utilisateur ---
  const [user, setUser] = useState(null);

  const clearTokens = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    console.log("✅ ANCIENS TOKENS SUPPRIMÉS");
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigation.replace("Login");
      return;
    }

    loadUser(token); // --- MODIFICATION 2 : Appel de la fonction ---
    loadRecentConsultations(token);
    loadStatistics(token, "month");

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

  const refreshAccessToken = async () => {
    try {
        const refreshToken = localStorage.getItem("refresh_token");

        if (!refreshToken) {
            console.log("Aucun refresh token disponible");
            return null;
        }

        console.log("RENOUVELLEMENT DU TOKEN...");

        const response = await fetch(
            `${BACKEND_URL}/api/token/refresh/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    refresh: refreshToken,
                }),
            }
        );

        const data = await response.json();

        console.log("REFRESH STATUS :", response.status);
        console.log("REFRESH RESPONSE :", data);

        if (!response.ok) {
            console.log("REFRESH TOKEN INVALIDE");
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            return null;
        }

        localStorage.setItem("access_token", data.access);
        console.log("NOUVEAU ACCESS TOKEN ENREGISTRÉ");
        return data.access;

    } catch (error) {
        console.log("ERREUR REFRESH TOKEN :", error);
        return null;
    }
  };

  const loadRecentConsultations = async (token) => {
    try {
        setLoadingConsultations(true);

        console.log("====================================");
        console.log("APPEL CONSULTATIONS");
        console.log("URL :", `${BACKEND_URL}/api/inspections/recent/`);
        console.log("====================================");

        let response = await fetch(
            `${BACKEND_URL}/api/inspections/recent/`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            }
        );

        console.log("STATUS CONSULTATIONS :", response.status);

        // ==========================================
        // TOKEN EXPIRÉ
        // ==========================================
        if (response.status === 401) {
            const errorData = await response.json();
            console.log("TOKEN EXPIRÉ :", errorData);

            // Demander un nouveau token
            const newToken = await refreshAccessToken();

            if (!newToken) {
                console.log("Impossible de renouveler le token");
                navigation.replace("Login");
                return;
            }

            console.log("NOUVEAU TOKEN OBTENU");

            // ==========================================
            // REFAIRE LA REQUÊTE
            // ==========================================
            response = await fetch(
                `${BACKEND_URL}/api/inspections/recent/`,
                {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${newToken}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            console.log("NOUVEAU STATUS CONSULTATIONS :", response.status);
        }

        // ==========================================
        // SI ERREUR
        // ==========================================
        if (!response.ok) {
            const errorText = await response.text();
            console.log("ERREUR API CONSULTATIONS :", errorText);
            return;
        }

        // ==========================================
        // RÉCUPÉRER LES DONNÉES
        // ==========================================
        const data = await response.json();
        console.log("DERNIÈRES CONSULTATIONS :", data);
        setConsultations(data.results || data);

    } catch (error) {
        console.log("ERREUR CHARGEMENT CONSULTATIONS :", error);
    } finally {
        setLoadingConsultations(false);
    }
  };

  const loadStatistics = async (token, period) => {
    try {
      setLoadingStatistics(true);

      console.log("====================================");
      console.log("APPEL STATISTICS");
      console.log("PERIOD :", period);
      console.log("====================================");

      const response = await fetch(
        `${BACKEND_URL}/api/inspections/statistics/?period=${period}`,
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log("STATUS STATISTICS :", response.status);

      const data = await response.json();
      console.log("STATISTICS :", data);

      if (!response.ok) {
        console.log("ERREUR STATISTICS :", data);
        return;
      }

      setStatistics(data);

    } catch (error) {
      console.log("ERREUR CHARGEMENT STATISTICS :", error);
    } finally {
      setLoadingStatistics(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigation.replace("Login");
  };

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

        <TouchableOpacity style={styles.menuItemActive}>
          <Text style={styles.menuIconActive}>📊</Text>
          <Text style={styles.menuTextActive}>Tableau de bord</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Scanner')}>
          <Text style={styles.menuIcon}>🔍</Text>
          <Text style={styles.menuText}>Scanner IA</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Vehicles')}>
          <Text style={styles.menuIcon}>🚘</Text>
          <Text style={styles.menuText}>Mes Véhicules</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Settings')}>
          <Text style={styles.menuIcon}>⚙️</Text>
          <Text style={styles.menuText}>Paramètres</Text>
        </TouchableOpacity>

        <View style={{flex: 1}} />
        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <Text style={styles.logoutText}> Déconnexion</Text>
        </TouchableOpacity>
      </View>

      {/* ==========================================
          2. CONTENU PRINCIPAL
      ========================================== */}
      <ScrollView style={styles.mainContent} showsVerticalScrollIndicator={false}>
        
        {/* Barre de Filtres Temporels et Profil */}
        <View style={styles.topBar}>
          <View style={styles.timeTabs}>
            {['Aujourd\'hui', 'Semaine', 'Mois', 'Trimestre', 'Année'].map((tab) => (
              <TouchableOpacity 
                key={tab} 
                style={[styles.timeTab, timeFilter === tab && styles.timeTabActive]}
                onPress={() => {
                  setTimeFilter(tab);
                  const token = localStorage.getItem("access_token");

                  if (!token) {
                    navigation.replace("Login");
                    return;
                  }

                  let period = "month";
                  if (tab === "Aujourd'hui") period = "today";
                  if (tab === "Semaine") period = "week";
                  if (tab === "Mois") period = "month";
                  if (tab === "Trimestre") period = "quarter";
                  if (tab === "Année") period = "year";

                  loadStatistics(token, period);
                }}
              >
                <Text style={[styles.timeTabText, timeFilter === tab && styles.timeTabTextActive]}>{tab}</Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={styles.timeTabCustom}><Text style={styles.timeTabText}>Personnalisé</Text></TouchableOpacity>
          </View>

          <View style={styles.headerRightControls}>
            {/* --- MODIFICATION 4 : Badge Profil Dynamique --- */}
            <View style={styles.profileBadge}>
              <View style={styles.avatar}>
                {user?.profile_image ? (
                  <Image 
                    source={{ uri: user.profile_image }}
                    style={{ width: 32, height: 32, borderRadius: 16 }}
                    resizeMode="cover"
                  />
                ) : (
                  <Text style={{color: '#fff', fontWeight: 'bold'}}>
                    {user?.first_name ? user.first_name.charAt(0).toUpperCase() : 'A'}
                    {user?.last_name ? user.last_name.charAt(0).toUpperCase() : 'T'}
                  </Text>
                )}
              </View>
              <View>
                <Text style={{fontWeight: 'bold', color: COLORS.textDark, fontSize: 13}}>
                  {user?.first_name ? `${user.first_name} ${user.last_name}` : 'A. Tahiri'}
                </Text>
                <Text style={{color: COLORS.textGray, fontSize: 11}}>Ingénieur Admin</Text>
              </View>
            </View>
          </View>
        </View>

        {/* --- SECTION DES KPI EN ENTONNOIR --- */}
        <View style={styles.funnelCard}>
          <View style={styles.funnelStep}>
            <Text style={styles.funnelNumber}>{statistics.vehicles_consulted}</Text>
            <Text style={styles.funnelLabel}>VÉHICULES CONSULTÉS</Text>
          </View>
          <Text style={styles.funnelArrow}>➔</Text>
          <View style={styles.funnelStep}>
            <Text style={styles.funnelNumber}>{statistics.inspections}</Text>
            <Text style={styles.funnelLabel}>INSPECTIONS</Text>
          </View>
          <Text style={styles.funnelArrow}>➔</Text>
          <View style={styles.funnelStep}>
            <Text style={[styles.funnelNumber, { color: COLORS.primary }]}>{statistics.defects}</Text>
            <Text style={styles.funnelLabel}>DÉFAUTS DÉTECTÉS</Text>
          </View>
          <Text style={styles.funnelArrow}>➔</Text>
          <View style={styles.funnelStep}>
            <Text style={styles.funnelNumber}>{statistics.severe_defects}</Text>
            <Text style={styles.funnelLabel}>DÉFAUTS GRAVES</Text>
          </View>
        </View>

        {/* --- GRAPHIQUE À BARRES --- */}
        <View style={styles.card}>
          <View style={styles.chartLegendRow}>
            <Text style={styles.cardTitle}>Évolution des Inspections & Sévérité</Text>
            <View style={styles.legendContainer}>
              <View style={styles.legendItem}><View style={[styles.legendDot, {backgroundColor: COLORS.primary}]} /><Text style={styles.legendText}>Commandé</Text></View>
              <View style={styles.legendItem}><View style={[styles.legendDot, {backgroundColor: '#3b82f6'}]} /><Text style={styles.legendText}>Accepté</Text></View>
              <View style={styles.legendItem}><View style={[styles.legendDot, {backgroundColor: '#f43f5e'}]} /><Text style={styles.legendText}>Décliné</Text></View>
            </View>
          </View>

          {(() => {
            // 1. Extraire les données pour calculer le maximum
            const chartData = statistics.chart?.length > 0 
              ? statistics.chart.map(item => item.count) 
              : [0];
            
            // 2. Calculer une valeur max propre (minimum 4 pour avoir de beaux segments)
            const maxValue = Math.max(...chartData, 4);
            const segments = Math.min(maxValue, 4); // Limiter à 4 lignes horizontales max

            return (
              <BarChart
                data={{
                  labels: statistics.chart?.length > 0 
                    ? statistics.chart.map(item => item.date) 
                    : ["Aucune"],
                  datasets: [{ data: chartData }]
                }}
                width={screenWidth * 0.52}
                height={230}
                fromZero={true} // <-- FORCE LE GRAPHIQUE À COMMENCER À 0
                segments={segments} // <-- ÉVITE LES LIGNES EN DOUBLE
                showValuesOnTopOfBars={true} // <-- AFFICHE LE NOMBRE AU-DESSUS DE LA BARRE
                chartConfig={{
                  backgroundColor: COLORS.surface,
                  backgroundGradientFrom: COLORS.surface,
                  backgroundGradientTo: COLORS.surface,
                  decimalPlaces: 0,
                  color: (opacity = 1) => `rgba(217, 4, 41, ${opacity})`,
                  labelColor: () => COLORS.textGray,
                  propsForBars: { borderRadius: 4 },
                  // Sécurité supplémentaire pour forcer l'affichage entier sur l'axe Y
                  formatYLabel: (yLabel) => Math.round(Number(yLabel)).toString()
                }}
                style={{ marginVertical: 8, borderRadius: 16 }}
              />
            );
          })()}
        </View>

        {/* --- TABLEAU DE DONNÉES EN BAS --- */}
        <View style={styles.card}>
          <View style={styles.tableHeaderTabs}>
            <TouchableOpacity onPress={() => setActiveTab('Pending Queries')}><Text style={[styles.tableTab, activeTab === 'Pending Queries' && styles.tableTabActive]}>Requêtes en attente</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setActiveTab('Top 10')}><Text style={[styles.tableTab, activeTab === 'Top 10' && styles.tableTabActive]}>Top 10 Véhicules</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => setActiveTab('Proposals')}><Text style={[styles.tableTab, activeTab === 'Proposals' && styles.tableTabActive]}>Propositions à suivre</Text></TouchableOpacity>
          </View>

          <View style={styles.table}>
            <View style={styles.tableRowHeader}>
                <Text style={[styles.tableHead, { flex: 2 }]}>VÉHICULE</Text>
                <Text style={[styles.tableHead, { flex: 1.5 }]}>PLAQUE</Text>
                <Text style={[styles.tableHead, { flex: 1.5 }]}>DÉFAUTS</Text>
                <Text style={[styles.tableHead, { flex: 1.5 }]}>DATE</Text>
                <Text style={[styles.tableHead, { flex: 1, textAlign: 'right' }]}>STATUT</Text>
            </View>

            {loadingConsultations ? (
                <View style={{ padding: 20 }}>
                    <Text style={{ color: COLORS.textGray }}>Chargement des consultations...</Text>
                </View>
            ) : consultations.length === 0 ? (
                <View style={{ padding: 20 }}>
                    <Text style={{ color: COLORS.textGray }}>Aucune consultation trouvée.</Text>
                </View>
            ) : (
                consultations.map((row) => (
                    <View key={row.id} style={styles.tableRow}>
                        {/* VÉHICULE */}
                        <View style={{ flex: 2 }}>
                            <Text style={styles.tableCellBold}>
                                {row.vehicle?.brand || "Inconnu"} {row.vehicle?.model || ""}
                            </Text>
                            <Text style={{ fontSize: 11, color: COLORS.textGray, marginTop: 3 }}>
                                Inspection #{row.id}
                            </Text>
                        </View>

                        {/* PLAQUE */}
                        <Text style={[styles.tableCell, { flex: 1.5 }]}>
                            {row.vehicle?.plate_number || "N/A"}
                        </Text>

                        {/* DÉFAUTS */}
                        <Text style={[styles.tableCell, { flex: 1.5 }]}>
                            {row.defects_count} défauts
                        </Text>

                        {/* DATE */}
                        <Text style={[styles.tableCell, { flex: 1.5 }]}>
                            {row.inspection_date}
                        </Text>

                        {/* STATUT */}
                        <View style={{ flex: 1, alignItems: 'flex-end' }}>
                            <View
                                style={[
                                    styles.statusBadge,
                                    {
                                        backgroundColor:
                                            row.status === "Completed"
                                                ? COLORS.tagSubmitted
                                                : COLORS.tagProgress
                                    }
                                ]}
                            >
                                <Text style={styles.statusText}>{row.status}</Text>
                            </View>
                        </View>
                    </View>
                ))
            )}
          </View>
        </View>

      </ScrollView>
    </View>
  );
}

// ==========================================
// STYLES DU TABLEAU DE BORD
// ==========================================
const styles = StyleSheet.create({
  container: { flex: 1, flexDirection: 'row', backgroundColor: COLORS.background },
  
  // Sidebar & Logo Image Agrandie
  sidebar: { width: 220, backgroundColor: COLORS.surface, borderRightWidth: 1, borderRightColor: COLORS.border, padding: 20, flexDirection: 'column' },
  logoContainer: { marginBottom: 25, marginTop: 10, height: 60, justifyContent: 'center' },
  logoImage: { width: '100%', height: 150 },

  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5 },
  menuItemActive: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5, backgroundColor: COLORS.primaryLight },
  menuIcon: { fontSize: 16, marginRight: 12 },
  menuIconActive: { fontSize: 16, marginRight: 12, color: COLORS.primary },
  menuText: { fontSize: 14, fontWeight: '600', color: COLORS.textGray },
  menuTextActive: { fontSize: 14, fontWeight: '700', color: COLORS.primary },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, marginTop: 'auto' },
  logoutText: { color: COLORS.textGray, fontWeight: '600' },

  // Main Content
  mainContent: { flex: 1, padding: 30 },
  topBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25, flexWrap: 'wrap' },
  timeTabs: { flexDirection: 'row', backgroundColor: COLORS.surface, padding: 4, borderRadius: 12, borderWidth: 1, borderColor: COLORS.border },
  timeTab: { paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8 },
  timeTabActive: { backgroundColor: COLORS.primary },
  timeTabCustom: { paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8, backgroundColor: '#e2e8f0' },
  timeTabText: { fontSize: 12, fontWeight: '600', color: COLORS.textGray },
  timeTabTextActive: { color: '#fff', fontWeight: '700' },
  headerRightControls: { flexDirection: 'row', alignItems: 'center' },
  profileBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.surface, padding: 6, paddingRight: 16, borderRadius: 30, borderWidth: 1, borderColor: COLORS.border },
  avatar: { width: 32, height: 32, borderRadius: 16, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center', marginRight: 10 },

  // Funnel KPI Section
  funnelCard: { flexDirection: 'row', backgroundColor: COLORS.surface, borderRadius: 16, padding: 20, marginBottom: 25, borderWidth: 1, borderColor: COLORS.border, alignItems: 'center', justifyContent: 'space-around' },
  funnelStep: { alignItems: 'center' },
  funnelNumber: { fontSize: 22, fontWeight: '900', color: COLORS.textDark, marginBottom: 2 },
  funnelLabel: { fontSize: 10, fontWeight: '700', color: COLORS.textGray },
  funnelArrow: { color: COLORS.border, fontSize: 18, fontWeight: 'bold' },

  // Cards & Graphs
  card: { backgroundColor: COLORS.surface, borderRadius: 16, padding: 24, marginBottom: 25, borderWidth: 1, borderColor: COLORS.border },
  chartLegendRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  cardTitle: { fontSize: 15, fontWeight: '800', color: COLORS.textDark },
  legendContainer: { flexDirection: 'row', alignItems: 'center' },
  legendItem: { flexDirection: 'row', alignItems: 'center', marginLeft: 15 },
  legendDot: { width: 8, height: 8, borderRadius: 4, marginRight: 5 },
  legendText: { fontSize: 11, color: COLORS.textGray },

  // Table
  tableHeaderTabs: { flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: COLORS.border, paddingBottom: 12, marginBottom: 15 },
  tableTab: { fontSize: 13, fontWeight: '700', color: COLORS.textGray, marginRight: 25 },
  tableTabActive: { color: COLORS.primary, borderBottomWidth: 2, borderBottomColor: COLORS.primary, paddingBottom: 12, marginBottom: -13 },
  table: { width: '100%' },
  tableRowHeader: { flexDirection: 'row', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: COLORS.border },
  tableHead: { fontSize: 11, fontWeight: '700', color: COLORS.textGray },
  tableRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#f1f5f9' },
  tableCellBold: { fontSize: 13, fontWeight: '700', color: COLORS.textDark },
  tableCell: { fontSize: 12, color: COLORS.textGray },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 },
  statusText: { color: '#fff', fontSize: 10, fontWeight: 'bold' }
});