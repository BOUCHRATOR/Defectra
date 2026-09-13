import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet,Platform, Text, View, ScrollView, TouchableOpacity, Image, ActivityIndicator, TextInput } from 'react-native';
import { Camera, CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { ResizeMode, Video } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';

const COLORS = {
  background: '#f8fafc',
  surface: '#ffffff',
  cardDark: '#171a21',
  cardDarker: '#0b0e14',
  primary: '#d90429',
  warning: '#ff9f1c',
  textDark: '#1e293b',
  textGray: '#a0aec0',
  border: '#e2e8f0',
};

// =====================================================================
// ADRESSE MISE À JOUR POUR EXPO WEB / NAVIGATEUR BUREAU
// =====================================================================
const SERVER_IP = "127.0.0.1"; 
const BACKEND_URL = `http://${SERVER_IP}:8000`;

// --- AJOUT UNIQUE : Fonction utilitaire pour les images ---
const getImageUrl = (image) => {
  if (!image) return null;
  if (image.startsWith("http://") || image.startsWith("https://")) return image;
  return `${BACKEND_URL}${image.startsWith("/") ? "" : "/"}${image}`;
};

export default function ScannerScreen({ navigation }) {
  // --- ÉTATS VÉHICULE ---
  const [vehicleData, setVehicleData] = useState({ plate: '', brand: '', model: '' });
  const [isVehicleValidated, setIsVehicleValidated] = useState(false);

  // --- ÉTATS MÉDIA & CAMÉRA ---
  const [mode, setMode] = useState(null); 
  const [cameraType, setCameraType] = useState('photo');
  const [isRecording, setIsRecording] = useState(false);
  const [facing, setFacing] = useState('back');
  const [permission, requestPermission] = useCameraPermissions();
  
  const [mediaUri, setMediaUri] = useState(null);
  const [mediaType, setMediaType] = useState(null);
  
  // --- ÉTATS ANALYSE ---
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [detectionResults, setDetectionResults] = useState(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const cameraRef = useRef(null);

  // --- MODIFICATION 1 : État pour le profil utilisateur ---
  const [user, setUser] = useState(null);

  // --- MODIFICATION 2 : Charger le profil au démarrage ---
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      loadUser(token);
    }
  }, []);

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

  // Validation du formulaire véhicule
  const handleValidateVehicle = () => {
    if (!vehicleData.plate.trim()) {
      alert("La plaque d'immatriculation est requise pour commencer l'inspection.");
      return;
    }
    setIsVehicleValidated(true);
  };

  // Réinitialisation complète (Nouvelle inspection)
  const resetFullInspection = () => {
    setVehicleData({ plate: '', brand: '', model: '' });
    setIsVehicleValidated(false);
    setMediaUri(null);
    setMode(null);
    setAnalysisComplete(false);
    setDetectionResults(null);
  };

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({ quality: 1 });
        setMediaUri(photo.uri);
        setMediaType('image');
        setAnalysisComplete(false);
        setMode(null);
      } catch (error) {
        alert("Erreur lors de la capture photo");
      }
    }
  };

  const toggleRecordVideo = async () => {
    if (!cameraRef.current) return;

    if (isRecording) {
      setIsRecording(false);
      try {
        cameraRef.current.stopRecording();
      } catch (e) {}
    } else {
      try {
        setIsRecording(true);
        const video = await cameraRef.current.recordAsync({ maxDuration: 30 });
        if (video) {
          setMediaUri(video.uri);
          setMediaType('video');
          setAnalysisComplete(false);
          setIsRecording(false);
          setMode(null);
        }
      } catch (error) {
        console.error(error);
        setIsRecording(false);
      }
    }
  };

  const importFromFile = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      const uri = result.assets[0].uri;
      const isVid = result.assets[0].type === 'video' || uri.includes('.mp4') || uri.includes('.mov');
      setMediaUri(uri);
      setMediaType(isVid ? 'video' : 'image');
      setAnalysisComplete(false);
    }
  };

  const runYOLOAnalysis = async () => {
    if (!mediaUri) return alert("Aucun fichier sélectionné.");

    setIsAnalyzing(true);
    setAnalysisComplete(false);
    setDetectionResults(null);

    try {
      const fileResponse = await fetch(mediaUri);
      if (!fileResponse.ok) throw new Error("Impossible de lire le fichier sélectionné.");
      const blob = await fileResponse.blob();

      const formData = new FormData();
      const fileName = mediaType === "video" ? "inspection_video.mp4" : "inspection_image.jpg";
      
      // Ajout du fichier
      formData.append("file", blob, fileName);
      
      // ⚠️ Ajout des informations du véhicule avec les clés exactes pour Django
      formData.append("plate_number", vehicleData.plate);
      formData.append("brand", vehicleData.brand);
      formData.append("model", vehicleData.model);

      const response = await fetch(`${BACKEND_URL}/api/detection/`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.message || "Erreur pendant la détection.");

      setDetectionResults(data);
      setAnalysisComplete(true);

    } catch (error) {
      console.error("ERREUR DETECTION :", error);
      alert(error.message || "Erreur serveur.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadReport = async () => {
    const inspectionId = detectionResults?.inspection_id;

    if (!inspectionId) {
      alert("ID de l'inspection introuvable.");
      return;
    }

    try {
      setIsGeneratingReport(true);

      console.log("======================================");
      console.log("GENERATION RAPPORT");
      console.log("Inspection ID :", inspectionId);
      console.log("URL :", `${BACKEND_URL}/api/reports/${inspectionId}/`);
      console.log("======================================");

      // =====================================================
      // 1. GENERER LE RAPPORT
      // =====================================================

      const response = await fetch(
        `${BACKEND_URL}/api/reports/${inspectionId}/`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        }
      );

      const responseText = await response.text();

      console.log("======================================");
      console.log("REPONSE HTTP RAPPORT");
      console.log("Status :", response.status);
      console.log(
        "Content-Type :",
        response.headers.get("content-type")
      );
      console.log("Body :", responseText);
      console.log("======================================");

      if (!response.ok) {
        throw new Error(
          `Erreur HTTP ${response.status} : ${responseText.substring(0, 500)}`
        );
      }

      let data;

      try {
        data = JSON.parse(responseText);
      } catch (error) {
        throw new Error(
          "Le serveur a retourné une réponse non JSON."
        );
      }

      if (!data.success) {
        throw new Error(
          data.message ||
          "Erreur génération rapport."
        );
      }

      // =====================================================
      // 2. URL PDF
      // =====================================================

      let pdfUrl =
        data.pdf_url ||
        data.report?.pdf_url;

      console.log(
        "PDF URL :",
        pdfUrl
      );

      if (!pdfUrl) {
        throw new Error(
          "Le backend n'a pas retourné l'URL du PDF."
        );
      }

      // URL complète si nécessaire
      if (
        !pdfUrl.startsWith("http://") &&
        !pdfUrl.startsWith("https://")
      ) {
        pdfUrl =
          `${BACKEND_URL}` +
          `${pdfUrl.startsWith("/") ? "" : "/"}` +
          pdfUrl;
      }

      console.log(
        "PDF URL COMPLETE :",
        pdfUrl
      );

      // =====================================================
      // 3. EXPO WEB
      // =====================================================

      if (Platform.OS === "web") {

        console.log(
          "Plateforme Web détectée."
        );

        // Téléchargement navigateur
        const link = document.createElement("a");

        link.href = pdfUrl;

        link.download =
          `rapport_inspection_${inspectionId}.pdf`;

        link.target = "_blank";

        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);

        alert(
          "Le rapport PDF a été téléchargé."
        );

        return;
      }

      // =====================================================
      // 4. ANDROID / IOS
      // =====================================================

      const destination =
        new FileSystem.Directory(
          FileSystem.Paths.cache
        );

      const downloadedFile =
        await FileSystem.File.downloadFileAsync(
          pdfUrl,
          destination,
          {
            idempotent: true,
          }
        );

      console.log(
        "PDF téléchargé :",
        downloadedFile.uri
      );

      // =====================================================
      // 5. PARTAGE MOBILE
      // =====================================================

      const sharingAvailable =
        await Sharing.isAvailableAsync();

      if (sharingAvailable) {

        await Sharing.shareAsync(
          downloadedFile.uri,
          {
            mimeType: "application/pdf",
            dialogTitle:
              "Rapport d'inspection",
          }
        );

      } else {

        alert(
          "Rapport téléchargé avec succès."
        );
      }

    } catch (error) {

      console.error(
        "ERREUR RAPPORT :",
        error
      );

      alert(
        error?.message ||
        "Impossible de télécharger le rapport."
      );

    } finally {

      setIsGeneratingReport(false);
    }
  };

  const annotatedImageUri =
    detectionResults?.annotated_image_url
      ? `${BACKEND_URL}${detectionResults.annotated_image_url}`
      : detectionResults?.annotated_image?.url
        ? `${BACKEND_URL}${detectionResults.annotated_image.url}`
        : null;

  // --- MODIFICATION 3 : Variables pour affichage profil ---
  const profileImageUrl = user?.profile_image || user?.avatar;
  const initialFirst = user?.first_name ? user.first_name.charAt(0).toUpperCase() : 'A';
  const initialLast = user?.last_name ? user.last_name.charAt(0).toUpperCase() : 'T';
  const fullName = user?.first_name ? `${user.first_name} ${user.last_name}` : 'A. Tahiri';

  return (
    <View style={styles.container}>
      
      {/* ==========================================
          1. BARRE LATÉRALE
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
          <Text style={styles.menuIconActive}>🔍</Text>
          <Text style={styles.menuTextActive}>Scanner IA</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Vehicles')}>
          <Text style={styles.menuIcon}>🚘</Text>
          <Text style={styles.menuText}>Mes Véhicules</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Settings')}>
          <Text style={styles.menuIcon}>⚙️</Text>
          <Text style={styles.menuText}>Paramètres</Text>
        </TouchableOpacity>

        <View style={styles.spacer} />
        <TouchableOpacity style={styles.logoutBtn} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.logoutText}> Déconnexion</Text>
        </TouchableOpacity>
      </View>

      {/* ==========================================
          2. CONTENU PRINCIPAL
      ========================================== */}
      <View style={styles.mainContentWrapper}>
        <ScrollView style={styles.mainContent} showsVerticalScrollIndicator={false}>
          
          {/* --- EN-TÊTE --- */}
          <View style={styles.header}>
            <View>
              <Text style={styles.breadcrumb}>Module d'inspection</Text>
              <Text style={styles.pageTitle}>🔍 Analyse IA & Détection des Défauts</Text>
            </View>
            
            {/* --- MODIFICATION 4 : Badge Profil Dynamique --- */}
            <View style={styles.profileBadge}>
              <View style={styles.avatar}>
                {profileImageUrl ? (
                  <Image 
                    source={{ uri: getImageUrl(profileImageUrl) }}
                    style={{ width: 32, height: 32, borderRadius: 16 }}
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

          {/* ==========================================
              ÉTAPE 1 : FORMULAIRE VÉHICULE
          ========================================== */}
          {!isVehicleValidated && (
            <View style={styles.cardDark}>
              <Text style={[styles.cardSubtitle, { color: '#fff', fontSize: 18, marginBottom: 20 }]}>
                🚘 Identifier le véhicule
              </Text>
              
              <Text style={styles.inputLabel}>Plaque d'immatriculation *</Text>
              <TextInput 
                style={styles.inputDark}
                placeholder="Ex: 1234-A-56"
                placeholderTextColor="#4a5568"
                value={vehicleData.plate}
                onChangeText={(text) => setVehicleData({...vehicleData, plate: text})}
              />

              <Text style={styles.inputLabel}>Marque (Optionnel)</Text>
              <TextInput 
                style={styles.inputDark}
                placeholder="Ex: Peugeot, Renault..."
                placeholderTextColor="#4a5568"
                value={vehicleData.brand}
                onChangeText={(text) => setVehicleData({...vehicleData, brand: text})}
              />

              <Text style={styles.inputLabel}>Modèle (Optionnel)</Text>
              <TextInput 
                style={styles.inputDark}
                placeholder="Ex: 208, Clio..."
                placeholderTextColor="#4a5568"
                value={vehicleData.model}
                onChangeText={(text) => setVehicleData({...vehicleData, model: text})}
              />

              <TouchableOpacity style={styles.launchButton} onPress={handleValidateVehicle}>
                <Text style={styles.launchButtonText}>Valider et continuer ➡️</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* ==========================================
              ÉTAPE 2 : SÉLECTION DE MÉDIA
          ========================================== */}
          {isVehicleValidated && !mediaUri && mode === null && (
            <View style={styles.uploadCard}>
              <View style={{flexDirection: 'row', justifyContent: 'space-between', width: '100%', paddingHorizontal: 20}}>
                <Text style={styles.vehicleBadge}>🚗 {vehicleData.plate}</Text>
                <TouchableOpacity onPress={() => setIsVehicleValidated(false)}>
                  <Text style={{color: COLORS.primary, fontWeight: 'bold'}}>Modifier le véhicule</Text>
                </TouchableOpacity>
              </View>
              
              <Text style={{fontSize: 45, marginBottom: 10, marginTop: 20}}>📷🎥</Text>
              <Text style={styles.uploadTitle}>Choisissez votre mode d'inspection</Text>
              <Text style={styles.uploadSubtitle}>Capturez une photo/vidéo en direct ou importez vos fichiers</Text>
              
              <View style={styles.uploadButtonsRow}>
                <TouchableOpacity style={styles.primaryButton} onPress={() => {
                  if (!permission || !permission.granted) requestPermission();
                  setCameraType('photo');
                  setMode('camera');
                }}>
                  <Text style={styles.primaryButtonText}>📸 Caméra (Photo)</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.primaryButton} onPress={() => {
                  if (!permission || !permission.granted) requestPermission();
                  setCameraType('video');
                  setMode('camera');
                }}>
                  <Text style={styles.primaryButtonText}>📹 Caméra (Vidéo)</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.secondaryButton} onPress={importFromFile}>
                  <Text style={styles.secondaryButtonText}>📁 Importer Fichier</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {/* ==========================================
              ÉTAPE 3 : CAMÉRA EN DIRECT
          ========================================== */}
          {isVehicleValidated && !mediaUri && mode === 'camera' && (
            <View style={styles.cardDark}>
              <View style={{flexDirection: 'row', justifyContent: 'space-between', marginBottom: 15}}>
                <Text style={styles.cardSubtitle}>
                  {cameraType === 'video' ? '📹 Enregistrement Vidéo en direct' : '📸 Prise de vue Photo'}
                </Text>
                <TouchableOpacity onPress={() => setMode(null)}>
                  <Text style={{color: COLORS.primary, fontWeight: 'bold'}}>✕ Annuler</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.cameraContainer}>
                <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
                  <View style={styles.cameraButtonOverlay}>
                    {cameraType === 'photo' ? (
                      <TouchableOpacity style={styles.captureBtn} onPress={takePicture}>
                        <View style={styles.captureBtnInner} />
                      </TouchableOpacity>
                    ) : (
                      <TouchableOpacity 
                        style={[styles.captureBtn, isRecording && {borderColor: COLORS.primary}]} 
                        onPress={toggleRecordVideo}
                      >
                        <View style={[styles.captureBtnInner, isRecording && {backgroundColor: COLORS.primary, borderRadius: 4, width: 26, height: 26}]} />
                      </TouchableOpacity>
                    )}
                  </View>
                  {isRecording && (
                    <View style={styles.recordingBadge}>
                      <View style={styles.redDot} />
                      <Text style={{color: '#fff', fontWeight: 'bold', fontSize: 12}}>ENREGISTREMENT...</Text>
                    </View>
                  )}
                </CameraView>
              </View>
            </View>
          )}

          {/* ==========================================
              ÉTAPE 4 : AFFICHAGE IMAGE & LANCEMENT
          ========================================== */}
          {isVehicleValidated && mediaUri && (
            <View style={styles.cardDark}>
              <Text style={styles.cardSubtitle}>
                {analysisComplete ? "Résultat de l'inspection IA" : `Média prêt pour l'analyse (${mediaType === 'video' ? 'Vidéo' : 'Image'})`}
              </Text>
              
              <View style={styles.imagePreviewContainer}>
                {mediaType === 'video' && !analysisComplete ? (
                  <Video
                    source={{ uri: mediaUri }}
                    style={styles.previewImage}
                    useNativeControls
                    resizeMode={ResizeMode.CONTAIN}
                    isLooping
                  />
                ) : (
                  <Image
                    source={{ uri: analysisComplete && annotatedImageUri ? annotatedImageUri : mediaUri }}
                    style={styles.previewImage}
                    resizeMode="contain"
                  />
                )}
              </View>

              {!analysisComplete ? (
                <View style={{flexDirection: 'row', gap: 15, marginTop: 20}}>
                  <TouchableOpacity style={[styles.resetButton, {flex: 1, marginTop: 0}]} onPress={() => { setMediaUri(null); setMode(null); }}>
                    <Text style={styles.resetButtonText}>✕ Annuler</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.launchButton, {flex: 2, marginTop: 0}]} onPress={runYOLOAnalysis} disabled={isAnalyzing}>
                    {isAnalyzing ? <ActivityIndicator color="#fff" /> : <Text style={styles.launchButtonText}> Lancer le diagnostic IA </Text>}
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={{flexDirection: 'row', gap: 15, marginTop: 20}}>
                  <TouchableOpacity style={[styles.resetButton, {flex: 1, marginTop: 0}]} onPress={() => { setMediaUri(null); setMode(null); }}>
                    <Text style={styles.resetButtonText}>🔄 Analyser autre média</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.launchButton, {flex: 1, marginTop: 0, backgroundColor: COLORS.textDark}]} onPress={resetFullInspection}>
                    <Text style={styles.launchButtonText}> Nouvelle Inspection</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          )}

          {/* ==========================================
              ÉTAPE 5 : RÉSULTATS (Score, LLM, Détails)
          ========================================== */}
          {analysisComplete && (
            <>
              <View style={styles.resultsGrid}>
                <View style={styles.resultCard}>
                  <Text style={styles.resultCardTitle}> Score de Sévérité</Text>
                  {detectionResults?.defects?.map((defect, index) => {
                    const severity = defect.severity || "MEDIUM";
                    const severityColor = severity === "HIGH" ? COLORS.primary : severity === "MEDIUM" ? COLORS.warning : "#22c55e";
                    const severityScore = severity === "HIGH" ? 100 : severity === "MEDIUM" ? 60 : 30;

                    return (
                      <View key={index} style={styles.severityItem}>
                        <View style={styles.severityHeader}>
                          <Text style={styles.severityName}>{defect.defect_name}</Text>
                          <Text style={[styles.severityPercent, { color: severityColor }]}>{severity}</Text>
                        </View>
                        <View style={styles.progressBarBg}>
                          <View style={[styles.progressBarFill, { width: `${severityScore}%`, backgroundColor: severityColor }]} />
                        </View>
                      </View>
                    );
                  })}
                </View>

                <View style={styles.resultCard}>
                  <Text style={styles.resultCardTitle}> Synthèse LLM</Text>
                  {detectionResults?.defects?.map((defect, index) => (
                    <View key={index} style={styles.llmBox}>
                      <Text style={styles.llmText}>
                        <Text style={{ fontWeight: "bold" }}>{defect.defect_name}</Text>{"\n\n"}
                        {defect.description}{"\n\n"}
                        🔧 {defect.solution}
                      </Text>
                    </View>
                  ))}
                  <TouchableOpacity
                      style={[
                        styles.pdfButton,
                        isGeneratingReport && {
                          opacity: 0.6,
                        }
                      ]}
                      onPress={downloadReport}
                      disabled={isGeneratingReport}
                    >
                      {isGeneratingReport ? (
                        <View
                          style={{
                            flexDirection: "row",
                            alignItems: "center",
                            gap: 10,
                          }}
                        >
                          <ActivityIndicator color="#fff" />

                          <Text style={styles.pdfButtonText}>
                            Génération du rapport...
                          </Text>
                        </View>
                      ) : (
                        <Text style={styles.pdfButtonText}>
                          📥 Télécharger le Rapport (PDF)
                        </Text>
                      )}
                    </TouchableOpacity>
                </View>
              </View>

              <View style={styles.detailsContainer}>
                <Text style={styles.detailsTitle}> Détails des Défauts Détectés</Text>
                {detectionResults?.defects?.map((defect, index) => {
                  const severity = defect.severity || "MEDIUM";
                  const severityColor = severity === "MEDIUM" ? COLORS.warning : COLORS.primary;
                  const displayConfidence = defect.confidence === 0 ? "0.00%" : `${(defect.confidence * 100).toFixed(2)}%`;

                  return (
                    <View key={index} style={styles.defectCard}>
                      <View style={styles.defectHeader}>
                        <Text style={styles.defectTitle}>{defect.defect_name}</Text>
                        <View style={[styles.severityBadge, { backgroundColor: severityColor }]}>
                          <Text style={styles.severityBadgeText}>{severity}</Text>
                        </View>
                      </View>
                      <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Confiance IA</Text>
                        <Text style={styles.infoValue}>{displayConfidence}</Text>
                      </View>
                      <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Localisation</Text>
                        <Text style={styles.infoValue}>{defect.location || "middle-center"}</Text>
                      </View>
                      <View style={styles.analysisSection}>
                        <Text style={styles.analysisLabel}>🤖 Description détaillée</Text>
                        <Text style={styles.analysisText}>{defect.description}</Text>
                      </View>
                      <View style={styles.analysisSection}>
                        <Text style={styles.analysisLabel}>🔧 Recommandation</Text>
                        <Text style={styles.analysisText}>{defect.solution}</Text>
                      </View>
                    </View>
                  );
                })}
              </View>
            </>
          )}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, flexDirection: 'row', backgroundColor: COLORS.background },
  sidebar: { width: 220, backgroundColor: COLORS.surface, borderRightWidth: 1, borderRightColor: COLORS.border, padding: 20, flexDirection: 'column' },
  logoContainer: { marginBottom: 25, marginTop: 10, height: 60, justifyContent: 'center' },
  logoImage: { width: '100%', height: 150 },
  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5 },
  menuItemActive: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 15, borderRadius: 10, marginBottom: 5, backgroundColor: '#fdf2f2' },
  menuIcon: { fontSize: 16, marginRight: 12, color: COLORS.textGray },
  menuIconActive: { fontSize: 16, marginRight: 12, color: COLORS.primary },
  menuText: { fontSize: 14, fontWeight: '600', color: COLORS.textGray },
  menuTextActive: { fontSize: 14, fontWeight: '700', color: COLORS.primary },
  spacer: { flex: 1 },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12 },
  logoutText: { color: COLORS.textGray, fontWeight: '600' },
  mainContentWrapper: { flex: 1 },
  mainContent: { flex: 1, padding: 30 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25 },
  breadcrumb: { color: COLORS.textGray, fontSize: 12, marginBottom: 4 },
  pageTitle: { color: COLORS.textDark, fontSize: 24, fontWeight: '800' },
  profileBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.surface, padding: 6, paddingRight: 16, borderRadius: 30, borderWidth: 1, borderColor: COLORS.border },
  avatar: { width: 32, height: 32, borderRadius: 16, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center', marginRight: 10 },
  uploadCard: { backgroundColor: COLORS.surface, borderRadius: 20, padding: 30, alignItems: 'center', borderWidth: 2, borderColor: COLORS.border, borderStyle: 'dashed', marginBottom: 25 },
  uploadTitle: { fontSize: 18, fontWeight: '800', color: COLORS.textDark, marginBottom: 5, textAlign: 'center' },
  uploadSubtitle: { color: COLORS.textGray, fontSize: 13, marginBottom: 25, textAlign: 'center' },
  uploadButtonsRow: { flexDirection: 'row', gap: 15, flexWrap: 'wrap', justifyContent: 'center' },
  primaryButton: { backgroundColor: COLORS.primary, paddingVertical: 14, paddingHorizontal: 24, borderRadius: 12 },
  primaryButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 13 },
  secondaryButton: { backgroundColor: '#f1f5f9', paddingVertical: 14, paddingHorizontal: 24, borderRadius: 12, borderWidth: 1, borderColor: COLORS.border },
  secondaryButtonText: { color: COLORS.textDark, fontWeight: 'bold', fontSize: 13 },
  cardDark: { backgroundColor: COLORS.cardDark, borderRadius: 20, padding: 24, marginBottom: 25 },
  cardSubtitle: { color: COLORS.textGray, fontSize: 14, fontWeight: '600', marginBottom: 15 },
  inputLabel: { color: '#a0aec0', fontSize: 13, marginBottom: 8, fontWeight: 'bold' },
  inputDark: { backgroundColor: COLORS.cardDarker, borderWidth: 1, borderColor: '#2d3748', borderRadius: 12, padding: 15, color: '#fff', marginBottom: 20, fontSize: 14 },
  vehicleBadge: { backgroundColor: '#f1f5f9', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, fontWeight: 'bold', color: COLORS.textDark, fontSize: 13 },
  imagePreviewContainer: { width: '100%', height: 400, borderRadius: 16, overflow: 'hidden', backgroundColor: COLORS.cardDarker },
  previewImage: { width: '100%', height: '100%' },
  cameraContainer: { width: '100%', height: 400, borderRadius: 16, overflow: 'hidden', backgroundColor: '#000', position: 'relative' },
  camera: { flex: 1, width: '100%', height: '100%' },
  cameraButtonOverlay: { position: 'absolute', bottom: 20, left: 0, right: 0, alignItems: 'center' },
  captureBtn: { width: 70, height: 70, borderRadius: 35, borderWidth: 4, borderColor: '#fff', justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.3)' },
  captureBtnInner: { width: 52, height: 52, borderRadius: 26, backgroundColor: COLORS.primary },
  recordingBadge: { position: 'absolute', top: 20, left: 20, flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.6)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  redDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: COLORS.primary, marginRight: 8 },
  launchButton: { backgroundColor: COLORS.primary, padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 20 },
  launchButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  resetButton: { backgroundColor: COLORS.border, padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 20 },
  resetButtonText: { color: '#fff', fontWeight: 'bold' },
  resultsGrid: { flexDirection: 'row', gap: 20, marginBottom: 30 },
  resultCard: { flex: 1, backgroundColor: COLORS.surface, borderRadius: 20, padding: 24, borderWidth: 1, borderColor: COLORS.border },
  resultCardTitle: { fontSize: 18, fontWeight: '800', color: COLORS.textDark, marginBottom: 20 },
  severityItem: { marginBottom: 20 },
  severityHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  severityName: { fontSize: 13, fontWeight: '700' },
  severityPercent: { fontSize: 13, fontWeight: '900' },
  progressBarBg: { width: '100%', height: 8, backgroundColor: '#f1f5f9', borderRadius: 4 },
  progressBarFill: { height: '100%', borderRadius: 4 },
  llmBox: { backgroundColor: COLORS.cardDarker, padding: 16, borderRadius: 12, marginBottom: 20 },
  llmText: { color: COLORS.textGray, fontSize: 13, lineHeight: 20 },
  pdfButton: { backgroundColor: COLORS.textDark, padding: 14, borderRadius: 12, alignItems: 'center' },
  pdfButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 13 },
  detailsContainer: { marginTop: 10, paddingBottom: 40 },
  detailsTitle: { fontSize: 20, fontWeight: '800', marginBottom: 20 },
  defectCard: { backgroundColor: COLORS.surface, borderRadius: 16, padding: 20, marginBottom: 15, borderWidth: 1, borderColor: COLORS.border },
  defectHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 15 },
  defectTitle: { fontSize: 18, fontWeight: '800' },
  severityBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  severityBadgeText: { color: '#fff', fontSize: 12, fontWeight: '900' },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: COLORS.border },
  infoLabel: { color: COLORS.textGray, fontSize: 13 },
  infoValue: { color: COLORS.textDark, fontSize: 13, fontWeight: '700' },
  analysisSection: { marginTop: 15 },
  analysisLabel: { fontSize: 14, fontWeight: '800', marginBottom: 6 },
  analysisText: { color: COLORS.textGray, fontSize: 13, lineHeight: 20 },
});