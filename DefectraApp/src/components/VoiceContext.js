// ==========================================================
// src/components/VoiceContext.js
// ==========================================================

import React, {
  createContext,
  useContext,
  useState,
  useRef,
} from "react";

import {
  ExpoSpeechRecognitionModule,
  useSpeechRecognitionEvent,
} from "expo-speech-recognition";

import * as Speech from "expo-speech";


// ==========================================================
// CONTEXT
// ==========================================================

const VoiceContext = createContext(null);


// ==========================================================
// CONFIGURATION
// ==========================================================

const SERVER_IP = "127.0.0.1";

const FASTAPI_PORT = "8001";

const API_URL =
  `http://${SERVER_IP}:${FASTAPI_PORT}`;

console.log("🌐 API URL :", API_URL);


// ==========================================================
// PROVIDER
// ==========================================================

export const VoiceProvider = ({ children }) => {

  // ========================================================
  // ETATS
  // ========================================================

  const [isVoiceEnabled, setIsVoiceEnabled] =
    useState(false);

  const [isListening, setIsListening] =
    useState(false);

  const [transcript, setTranscript] =
    useState("");

  const [voiceAnswer, setVoiceAnswer] =
    useState("");

  const [isProcessing, setIsProcessing] =
    useState(false);

  const [isSpeaking, setIsSpeaking] =
    useState(false);


  // ========================================================
  // REFS
  // ========================================================

  const isVoiceEnabledRef =
    useRef(false);

  const isSpeakingRef =
    useRef(false);

  const isProcessingRef =
    useRef(false);


  // ========================================================
  // SYNCHRONISER ETAT MICRO
  // ========================================================

  const setVoiceEnabledState = (value) => {

    isVoiceEnabledRef.current = value;

    setIsVoiceEnabled(value);
  };


  // ========================================================
  // SYNCHRONISER SPEAKING
  // ========================================================

  const setSpeakingState = (value) => {

    isSpeakingRef.current = value;

    setIsSpeaking(value);
  };


  // ========================================================
  // COMMANDES POUR ARRÊTER LA VOIX
  // ========================================================

  const isStopCommand = (text) => {

    if (!text) {
      return false;
    }


    const command =
      text
        .toLowerCase()
        .trim()
        .replace(/[.,!?;:]/g, "");


    const stopCommands = [

      // Français
      "arrête",
      "arrete",

      "arrête le vocal",
      "arrete le vocal",

      "arrête la voix",
      "arrete la voix",

      "arrête de parler",
      "arrete de parler",

      "tais toi",
      "tais-toi",

      "silence",

      // Anglais
      "stop",
      "stop vocal",

      "stop talking",
      "stop speaking",

    ];


    if (
      stopCommands.includes(command)
    ) {

      return true;
    }


    if (
      command.includes("arrête le vocal") ||
      command.includes("arrete le vocal") ||
      command.includes("arrête la voix") ||
      command.includes("arrete la voix") ||
      command.includes("arrête de parler") ||
      command.includes("arrete de parler") ||
      command.includes("tais toi") ||
      command.includes("tais-toi") ||
      command.includes("stop vocal") ||
      command.includes("stop talking") ||
      command.includes("stop speaking")
    ) {

      return true;
    }


    return false;
  };


  // ========================================================
  // STOP SPEECH
  // ========================================================

  const stopSpeaking = async () => {

    try {

      console.log(
        "🛑 Arrêt de la réponse vocale..."
      );


      await Speech.stop();


      setSpeakingState(false);


      console.log(
        "🔇 Réponse vocale arrêtée"
      );


    } catch (error) {

      console.log(
        "❌ Erreur arrêt Speech :",
        error
      );

      setSpeakingState(false);
    }
  };


  // ========================================================
  // TEXT → SPEECH
  // ========================================================

  const speakAnswer = async (text) => {

    try {

      if (
        !text ||
        !text.trim()
      ) {

        return;
      }


      console.log(
        "🔊 Lecture réponse LLM :",
        text
      );


      // ----------------------------------------------------
      // Arrêter ancienne lecture
      // ----------------------------------------------------

      await Speech.stop();


      // ----------------------------------------------------
      // Etat speaking
      // ----------------------------------------------------

      setSpeakingState(true);


      // ----------------------------------------------------
      // Lire
      // ----------------------------------------------------

      Speech.speak(
        text,
        {

          language: "fr-FR",

          rate: 0.9,

          pitch: 1.0,

          volume: 1.0,


          // ----------------------------------------------
          // START
          // ----------------------------------------------

          onStart: () => {

            console.log(
              "🔊 SPEECH START"
            );

            setSpeakingState(true);
          },


          // ----------------------------------------------
          // DONE
          // ----------------------------------------------

          onDone: () => {

            console.log(
              "✅ SPEECH DONE"
            );

            setSpeakingState(false);

          },


          // ----------------------------------------------
          // STOPPED
          // ----------------------------------------------

          onStopped: () => {

            console.log(
              "🛑 SPEECH STOPPED"
            );

            setSpeakingState(false);

          },


          // ----------------------------------------------
          // ERROR
          // ----------------------------------------------

          onError: (error) => {

            console.log(
              "❌ SPEECH ERROR :",
              error
            );

            setSpeakingState(false);
          },

        }
      );


    } catch (error) {

      console.log(
        "❌ Erreur Text-to-Speech :",
        error
      );

      setSpeakingState(false);
    }
  };


  // ========================================================
  // QUESTION → FASTAPI → LLM
  // ========================================================

  const askVoiceQuestion = async (question) => {

    try {

      if (
        !question ||
        !question.trim()
      ) {

        return null;
      }


      console.log(
        "📤 Question envoyée au LLM :",
        question
      );


      isProcessingRef.current = true;

      setIsProcessing(true);

      setVoiceAnswer("");


      // ====================================================
      // APPEL FASTAPI
      // ====================================================

      const response =
        await fetch(
          `${API_URL}/voice/ask-text`,
          {

            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              question: question,
            }),

          }
        );


      // ====================================================
      // HTTP ERROR
      // ====================================================

      if (!response.ok) {

        const errorText =
          await response.text();

        console.log(
          "❌ Erreur serveur :",
          errorText
        );

        throw new Error(
          `Erreur serveur ${response.status}`
        );
      }


      // ====================================================
      // JSON
      // ====================================================

      const data =
        await response.json();


      console.log(
        "📥 Réponse FastAPI :",
        data
      );


      // ====================================================
      // SUCCESS
      // ====================================================

      if (!data.success) {

        throw new Error(
          data.message ||
          "Erreur LLM"
        );
      }


      // ====================================================
      // RÉPONSE LLM
      // ====================================================

      const answer =
        data.answer || "";


      console.log(
        "🤖 Réponse LLM :",
        answer
      );


      if (!answer.trim()) {

        return null;
      }


      // ====================================================
      // AFFICHER
      // ====================================================

      setVoiceAnswer(answer);


      // ====================================================
      // LIRE
      // ====================================================

      await speakAnswer(answer);


      return answer;


    } catch (error) {

      console.log(
        "❌ Erreur question vocale :",
        error
      );

      return null;


    } finally {

      isProcessingRef.current = false;

      setIsProcessing(false);
    }
  };


  // ========================================================
  // RESULT SPEECH RECOGNITION
  // ========================================================

  useSpeechRecognitionEvent(
    "result",
    async (event) => {

      const text =
        event.results?.[0]?.transcript || "";


      if (!text) {
        return;
      }


      console.log(
        "🎤 Commande vocale :",
        text
      );


      setTranscript(text);


      // ====================================================
      // IMPORTANT
      // ====================================================

      // Avec continuous:true, certains résultats peuvent
      // être intermédiaires.

      const isFinal =
        event.isFinal === true;


      if (!isFinal) {
        return;
      }


      console.log(
        "✅ Commande finale :",
        text
      );


      // ====================================================
      // STOP ?
      // ====================================================

      if (
        isStopCommand(text)
      ) {

        console.log(
          "🛑 COMMANDE STOP DÉTECTÉE"
        );


        await stopSpeaking();


        setTranscript("");


        // IMPORTANT :
        // On NE désactive PAS le microphone.
        //
        // Le micro reste actif pour permettre une
        // nouvelle question.

        return;
      }


      // ====================================================
      // QUESTION NORMALE
      // ====================================================

      // Si une réponse est actuellement en train de parler,
      // on l'arrête avant de traiter la nouvelle question.

      if (
        isSpeakingRef.current
      ) {

        console.log(
          "🛑 Nouvelle question détectée."
        );

        await stopSpeaking();
      }


      // ====================================================
      // ÉVITER DE LANCER PLUSIEURS QUESTIONS EN MÊME TEMPS
      // ====================================================

      if (
        isProcessingRef.current
      ) {

        console.log(
          "⏳ Une question est déjà en traitement."
        );

        return;
      }


      // ====================================================
      // ENVOYER QUESTION
      // ====================================================

      await askVoiceQuestion(text);

    }
  );


  // ========================================================
  // START
  // ========================================================

  useSpeechRecognitionEvent(
    "start",
    () => {

      console.log(
        "🎤 Microphone démarré"
      );

      setIsListening(true);
    }
  );


  // ========================================================
  // END
  // ========================================================

  useSpeechRecognitionEvent(
    "end",
    () => {

      console.log(
        "🔇 Événement microphone END"
      );

      setIsListening(false);


      // ====================================================
      // IMPORTANT
      // ====================================================

      // Si le mode vocal est toujours activé,
      // on redémarre automatiquement le microphone.

      if (
        isVoiceEnabledRef.current
      ) {

        setTimeout(
          () => {

            try {

              console.log(
                "🔄 Redémarrage automatique du microphone..."
              );


              ExpoSpeechRecognitionModule.start({

                lang: "fr-FR",

                interimResults: true,

                continuous: true,

              });

            } catch (error) {

              console.log(
                "❌ Erreur redémarrage micro :",
                error
              );
            }

          },
          300
        );
      }

    }
  );


  // ========================================================
  // ERROR
  // ========================================================

  useSpeechRecognitionEvent(
    "error",
    (event) => {

      console.log(
        "❌ Erreur microphone :",
        event.error
      );


      setIsListening(false);


      // ----------------------------------------------------
      // Si le mode vocal est toujours activé,
      // essayer de redémarrer
      // ----------------------------------------------------

      if (
        isVoiceEnabledRef.current
      ) {

        setTimeout(
          () => {

            try {

              ExpoSpeechRecognitionModule.start({

                lang: "fr-FR",

                interimResults: true,

                continuous: true,

              });

            } catch (error) {

              console.log(
                "❌ Impossible de redémarrer le micro :",
                error
              );
            }

          },
          500
        );
      }
    }
  );


  // ========================================================
  // ACTIVER MICRO
  // ========================================================

  const enableVoice = async () => {

    try {

      console.log(
        "🎤 Activation du microphone..."
      );


      // ----------------------------------------------------
      // Permission
      // ----------------------------------------------------

      const permission =
        await ExpoSpeechRecognitionModule
          .requestPermissionsAsync();


      console.log(
        "🎤 Permission :",
        permission
      );


      if (!permission.granted) {

        console.log(
          "❌ Permission microphone refusée"
        );

        setVoiceEnabledState(false);

        return false;
      }


      console.log(
        "✅ Permission microphone accordée"
      );


      // ----------------------------------------------------
      // Etat global
      // ----------------------------------------------------

      setVoiceEnabledState(true);


      // ----------------------------------------------------
      // Démarrer reconnaissance
      // ----------------------------------------------------

      console.log(
        "🎤 Démarrage reconnaissance continue..."
      );


      ExpoSpeechRecognitionModule.start({

        lang: "fr-FR",

        interimResults: true,

        // IMPORTANT :
        // Le micro reste actif.
        continuous: true,

      });


      return true;


    } catch (error) {

      console.log(
        "❌ Erreur activation microphone :",
        error
      );

      setVoiceEnabledState(false);

      return false;
    }
  };


  // ========================================================
  // DÉSACTIVER MICRO
  // ========================================================

  const disableVoice = async () => {

    try {

      console.log(
        "🔇 Désactivation du microphone..."
      );


      // ----------------------------------------------------
      // D'abord empêcher le redémarrage automatique
      // ----------------------------------------------------

      setVoiceEnabledState(false);


      // ----------------------------------------------------
      // Arrêter reconnaissance
      // ----------------------------------------------------

      try {

        ExpoSpeechRecognitionModule.stop();

      } catch (error) {

        console.log(
          "⚠️ Erreur arrêt reconnaissance :",
          error
        );
      }


      // ----------------------------------------------------
      // Etats
      // ----------------------------------------------------

      setIsListening(false);

      setTranscript("");


      // ----------------------------------------------------
      // IMPORTANT :
      //
      // On arrête aussi la voix si l'utilisateur désactive
      // complètement le mode vocal.
      // ----------------------------------------------------

      await stopSpeaking();


      console.log(
        "✅ Microphone désactivé"
      );


    } catch (error) {

      console.log(
        "❌ Erreur désactivation :",
        error
      );

      setVoiceEnabledState(false);
    }
  };


  // ========================================================
  // TOGGLE
  // ========================================================

  const toggleVoice = async () => {

    if (
      isVoiceEnabledRef.current
    ) {

      await disableVoice();

    } else {

      await enableVoice();
    }
  };


  // ========================================================
  // CONTEXT
  // ========================================================

  return (

    <VoiceContext.Provider
      value={{

        // --------------------------------------------------
        // MICRO
        // --------------------------------------------------

        isVoiceEnabled,

        isListening,


        // --------------------------------------------------
        // TEXTE
        // --------------------------------------------------

        transcript,


        // --------------------------------------------------
        // RÉPONSE
        // --------------------------------------------------

        voiceAnswer,


        // --------------------------------------------------
        // ETATS
        // --------------------------------------------------

        isProcessing,

        isSpeaking,


        // --------------------------------------------------
        // FONCTIONS MICRO
        // --------------------------------------------------

        enableVoice,

        disableVoice,

        toggleVoice,


        // --------------------------------------------------
        // LLM
        // --------------------------------------------------

        askVoiceQuestion,


        // --------------------------------------------------
        // SPEECH
        // --------------------------------------------------

        speakAnswer,

        stopSpeaking,

      }}
    >

      {children}

    </VoiceContext.Provider>
  );
};


// ==========================================================
// HOOK
// ==========================================================

export const useVoice = () => {

  const context =
    useContext(VoiceContext);


  if (!context) {

    throw new Error(
      "useVoice doit être utilisé à l'intérieur de VoiceProvider"
    );
  }


  return context;
};


// ==========================================================
// EXPORT
// ==========================================================

export default VoiceContext;