
import streamlit as st
import pandas as pd
import cv2
import tempfile
import os

from PIL import Image
from ultralytics import RTDETR


# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="DEFECTRA | AI Vision",
    page_icon="🚗",
    layout="wide"
)

MODEL_PATH = "best.pt"


# ==========================================================
# CHARGEMENT DU MODÈLE
# ==========================================================

if not os.path.exists(MODEL_PATH):
    st.error(f"Le modèle '{MODEL_PATH}' est introuvable.")
    st.info(
        "Place le fichier best.pt dans le même dossier que app.py."
    )
    st.stop()


@st.cache_resource
def load_model():
    return RTDETR(MODEL_PATH)


try:
    model = load_model()
except Exception as e:
    st.error("Impossible de charger le modèle.")
    st.exception(e)
    st.stop()


# ==========================================================
# FONCTION : DÉTERMINER LA POSITION
# ==========================================================

def get_position(x1, y1, x2, y2, image_width, image_height):
    """
    Détermine la position du défaut dans l'image
    à partir du centre de la bounding box.
    """

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Division de l'image en 3 colonnes
    third_width = image_width / 3

    # Division de l'image en 3 lignes
    third_height = image_height / 3

    # Position horizontale
    if center_x < third_width:
        horizontal = "Gauche"
    elif center_x < 2 * third_width:
        horizontal = "Centre"
    else:
        horizontal = "Droite"

    # Position verticale
    if center_y < third_height:
        vertical = "Haut"
    elif center_y < 2 * third_height:
        vertical = "Centre"
    else:
        vertical = "Bas"

    # Si le défaut est au centre
    if horizontal == "Centre" and vertical == "Centre":
        return "Centre"

    return f"{vertical} {horizontal}"


# ==========================================================
# INTERFACE
# ==========================================================

st.title("DEFECTRA")
st.subheader("AI Vehicle Damage Detection")

st.write(
    "Analysez une image ou une vidéo pour détecter automatiquement "
    "les défauts présents sur le véhicule."
)


# ==========================================================
# SEUIL DE CONFIANCE
# ==========================================================

confidence = st.slider(
    "Seuil de confiance",
    min_value=0.10,
    max_value=0.95,
    value=0.50,
    step=0.05
)


# ==========================================================
# INFORMATIONS DU MODÈLE
# ==========================================================

with st.expander("Informations sur le modèle"):
    st.write("Modèle utilisé : RT-DETR")
    st.write(f"Fichier : {MODEL_PATH}")

    try:
        st.write("Classes détectées :")
        st.write(model.names)
    except Exception:
        st.write("Impossible de récupérer les noms des classes.")


# ==========================================================
# TABS
# ==========================================================

tab_image, tab_video = st.tabs(
    ["Analyse d'une image", "Analyse d'une vidéo"]
)


# ==========================================================
# IMAGE
# ==========================================================

with tab_image:

    st.header("Analyse d'une image")

    uploaded_image = st.file_uploader(
        "Choisir une image",
        type=["jpg", "jpeg", "png"],
        key="image_uploader"
    )

    if uploaded_image is not None:

        image = Image.open(uploaded_image).convert("RGB")

        st.subheader("Image originale")

        st.image(
            image,
            width="stretch"
        )

        if st.button(
            "Lancer la détection",
            type="primary",
            key="detect_image"
        ):

            with st.spinner("Analyse de l'image en cours..."):

                try:

                    # ==================================================
                    # PRÉDICTION RT-DETR
                    # ==================================================

                    results = model.predict(
                        source=image,
                        conf=confidence,
                        verbose=False
                    )

                    result = results[0]

                    # ==================================================
                    # IMAGE ANNOTÉE
                    # ==================================================

                    annotated_image = result.plot()

                    annotated_image = cv2.cvtColor(
                        annotated_image,
                        cv2.COLOR_BGR2RGB
                    )

                    # ==================================================
                    # DIMENSIONS IMAGE
                    # ==================================================

                    image_width, image_height = image.size

                    # ==================================================
                    # RÉCUPÉRATION DES DÉTECTIONS
                    # ==================================================

                    detections = []

                    if result.boxes is not None:

                        boxes = result.boxes

                        for i in range(len(boxes)):

                            # Classe
                            class_id = int(
                                boxes.cls[i].item()
                            )

                            # Confiance
                            conf = float(
                                boxes.conf[i].item()
                            )

                            # Coordonnées
                            x1, y1, x2, y2 = boxes.xyxy[i].tolist()

                            # Nom du défaut
                            try:
                                class_name = model.names[class_id]
                            except Exception:
                                class_name = f"Classe {class_id}"

                            # ==================================================
                            # POSITION
                            # ==================================================

                            position = get_position(
                                x1,
                                y1,
                                x2,
                                y2,
                                image_width,
                                image_height
                            )

                            detections.append({
                                "Défaut": class_name,
                                "Confiance": round(conf * 100, 2),
                                "Position": position,
                                "X1": round(x1),
                                "Y1": round(y1),
                                "X2": round(x2),
                                "Y2": round(y2)
                            })

                    # ==================================================
                    # AFFICHAGE
                    # ==================================================

                    st.success(
                        f"Détection terminée : {len(detections)} défaut(s)"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.subheader("Image originale")

                        st.image(
                            image,
                            width="stretch"
                        )

                    with col2:

                        st.subheader("Défauts détectés")

                        st.image(
                            annotated_image,
                            width="stretch"
                        )

                    # ==================================================
                    # STATISTIQUES
                    # ==================================================

                    st.subheader("Résumé de l'analyse")

                    if len(detections) > 0:

                        total_detections = len(detections)

                        average_confidence = sum(
                            d["Confiance"]
                            for d in detections
                        ) / total_detections

                        unique_classes = len(
                            set(
                                d["Défaut"]
                                for d in detections
                            )
                        )

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Défauts détectés",
                                total_detections
                            )

                        with col2:
                            st.metric(
                                "Confiance moyenne",
                                f"{average_confidence:.2f}%"
                            )

                        with col3:
                            st.metric(
                                "Types de défauts",
                                unique_classes
                            )

                        # ==================================================
                        # TABLEAU
                        # ==================================================

                        st.subheader("Détails des défauts")

                        dataframe = pd.DataFrame(
                            detections
                        )

                        st.dataframe(
                            dataframe,
                            width="stretch",
                            hide_index=True
                        )

                    else:

                        st.info(
                            "Aucun défaut détecté avec le seuil "
                            f"de confiance de {confidence:.2f}."
                        )

                except Exception as e:

                    st.error(
                        "Une erreur est survenue pendant la détection."
                    )

                    st.exception(e)


# ==========================================================
# VIDÉO
# ==========================================================

with tab_video:

    st.header("Analyse d'une vidéo")

    uploaded_video = st.file_uploader(
        "Choisir une vidéo",
        type=["mp4", "avi", "mov", "mkv"],
        key="video_uploader"
    )

    if uploaded_video is not None:

        # ==================================================
        # SAUVEGARDE DE LA VIDÉO
        # ==================================================

        input_video = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        )

        input_video.write(
            uploaded_video.read()
        )

        input_video.close()

        # ==================================================
        # AFFICHAGE VIDÉO ORIGINALE
        # ==================================================

        st.subheader("Vidéo originale")

        st.video(
            input_video.name
        )

        if st.button(
            "Lancer l'analyse vidéo",
            type="primary",
            key="detect_video"
        ):

            cap = cv2.VideoCapture(
                input_video.name
            )

            if not cap.isOpened():

                st.error(
                    "Impossible d'ouvrir la vidéo."
                )

            else:

                # ==================================================
                # INFORMATIONS VIDÉO
                # ==================================================

                width = int(
                    cap.get(
                        cv2.CAP_PROP_FRAME_WIDTH
                    )
                )

                height = int(
                    cap.get(
                        cv2.CAP_PROP_FRAME_HEIGHT
                    )
                )

                fps = cap.get(
                    cv2.CAP_PROP_FPS
                )

                total_frames = int(
                    cap.get(
                        cv2.CAP_PROP_FRAME_COUNT
                    )
                )

                if fps <= 0:
                    fps = 25

                # ==================================================
                # FICHIER DE SORTIE
                # ==================================================

                output_video = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                )

                output_video.close()

                fourcc = cv2.VideoWriter_fourcc(
                    *"mp4v"
                )

                writer = cv2.VideoWriter(
                    output_video.name,
                    fourcc,
                    fps,
                    (width, height)
                )

                # ==================================================
                # PROGRESS BAR
                # ==================================================

                progress_bar = st.progress(0)

                status_text = st.empty()

                frame_number = 0
                total_detections = 0

                all_classes = set()

                # ==================================================
                # TRAITEMENT DES FRAMES
                # ==================================================

                while True:

                    ret, frame = cap.read()

                    if not ret:
                        break

                    frame_number += 1

                    # ==============================================
                    # RT-DETR
                    # ==============================================

                    results = model.predict(
                        source=frame,
                        conf=confidence,
                        verbose=False
                    )

                    result = results[0]

                    # ==============================================
                    # COMPTER LES DÉTECTIONS
                    # ==============================================

                    if result.boxes is not None:

                        for i in range(
                            len(result.boxes)
                        ):

                            class_id = int(
                                result.boxes.cls[i].item()
                            )

                            total_detections += 1

                            try:
                                class_name = model.names[
                                    class_id
                                ]
                            except Exception:
                                class_name = str(class_id)

                            all_classes.add(
                                class_name
                            )

                    # ==============================================
                    # ANNOTATION
                    # ==============================================

                    annotated_frame = result.plot()

                    writer.write(
                        annotated_frame
                    )

                    # ==============================================
                    # PROGRESSION
                    # ==============================================

                    if total_frames > 0:

                        progress = (
                            frame_number /
                            total_frames
                        )

                        progress_bar.progress(
                            min(progress, 1.0)
                        )

                        status_text.text(
                            f"Traitement : "
                            f"{frame_number}/"
                            f"{total_frames} frames"
                        )

                # ==================================================
                # FERMETURE
                # ==================================================

                cap.release()
                writer.release()

                progress_bar.progress(1.0)

                status_text.success(
                    "Analyse vidéo terminée."
                )

                # ==================================================
                # STATISTIQUES VIDÉO
                # ==================================================

                st.subheader(
                    "Résultats de l'analyse"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Détections totales",
                        total_detections
                    )

                with col2:

                    st.metric(
                        "Types de défauts",
                        len(all_classes)
                    )

                # ==================================================
                # CLASSES
                # ==================================================

                if len(all_classes) > 0:

                    st.write(
                        "Défauts détectés :"
                    )

                    st.write(
                        ", ".join(
                            sorted(all_classes)
                        )
                    )

                else:

                    st.info(
                        "Aucun défaut détecté dans la vidéo."
                    )

                # ==================================================
                # VIDÉO ANNOTÉE
                # ==================================================

                st.subheader(
                    "Vidéo analysée"
                )

                st.video(
                    output_video.name
                )

                # ==================================================
                # TÉLÉCHARGEMENT
                # ==================================================

                with open(
                    output_video.name,
                    "rb"
                ) as video_file:

                    st.download_button(
                        label="Télécharger la vidéo annotée",
                        data=video_file,
                        file_name="defectra_result.mp4",
                        mime="video/mp4"
                    )


# ==========================================================
# FOOTER
# ==========================================================

st.caption(
    "DEFECTRA — AI Vehicle Damage Detection"
)

