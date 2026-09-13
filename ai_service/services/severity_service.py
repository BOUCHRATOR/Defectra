# ==========================================================
# services/severity_service.py
# ==========================================================

import json
import re

from rag.retriever import get_retriever
from models.llm import get_llm


# ==========================================================
# CHARGEMENT UNIQUE
# ==========================================================

print("========================================")
print("===== CHARGEMENT SEVERITY SERVICE =====")
print("========================================")

retriever = get_retriever()
llm = get_llm()

print("===== SEVERITY SERVICE CHARGE =====")
print("========================================")


# ==========================================================
# EVALUATE SEVERITY
# ==========================================================

def evaluate_severity(
    defect_name,
    location=None,
    confidence=None,
    bbox=None
):
    """
    Analyse la sévérité d'un défaut avec RAG + LLM.

    Paramètres :
        defect_name : nom du défaut
        location   : position sur le véhicule
        confidence : confiance RT-DETR
        bbox       : coordonnées [x1, y1, x2, y2]
    """

    print("\n========================================")
    print("===== ANALYSE SEVERITE =====")
    print("========================================")

    print("Défaut :", defect_name)
    print("Confiance :", confidence)
    print("Position :", location)
    print("BBox :", bbox)

    try:

        # ==================================================
        # 1. RECHERCHE RAG
        # ==================================================

        query = f"""
        Défaut automobile : {defect_name}

        Position du défaut : {location}

        Confiance de détection : {confidence}

        Bounding box : {bbox}

        Déterminer :
        - niveau de sévérité
        - justification
        - recommandation de réparation
        - informations manquantes
        """

        print("\n===== RECHERCHE RAG =====")

        documents = retriever.invoke(query)

        context = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        print("Documents récupérés :", len(documents))

        # ==================================================
        # 2. PROMPT LLM
        # ==================================================

        prompt = f"""
Tu es un expert en inspection automobile.

Tu dois analyser le défaut détecté par un modèle RT-DETR.

DEFaut :
{defect_name}

POSITION :
{location}

CONFIANCE :
{confidence}

BOUNDING BOX :
{bbox}

DOCUMENTATION TECHNIQUE :
{context}

Donne une réponse UNIQUEMENT sous forme JSON valide.

Format obligatoire :

{{
    "severity": "LOW | MEDIUM | HIGH",
    "description": "explication du défaut et de sa gravité",
    "solution": "recommandation de réparation",
    "missing_information": []
}}

Si certaines informations sont nécessaires mais absentes,
mets-les dans "missing_information".

Ne mets aucun texte avant ou après le JSON.
"""

        print("\n===== APPEL LLM =====")

        response = llm.invoke(prompt)

        # ==================================================
        # 3. EXTRAIRE LE TEXTE
        # ==================================================

        if hasattr(response, "content"):
            content = response.content
        else:
            content = str(response)

        print("\n===== REPONSE LLM =====")
        print(content)

        # ==================================================
        # 4. NETTOYER JSON
        # ==================================================

        content = content.strip()

        if content.startswith("```"):
            content = re.sub(
                r"```json|```",
                "",
                content
            ).strip()

        # ==================================================
        # 5. PARSER JSON
        # ==================================================

        try:

            result = json.loads(content)

        except json.JSONDecodeError:

            print("JSON invalide retourné par le LLM.")

            # Essayer d'extraire le premier objet JSON
            match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL
            )

            if match:

                result = json.loads(
                    match.group(0)
                )

            else:

                result = {
                    "severity": "UNKNOWN",
                    "description": content,
                    "solution": "Inspection professionnelle recommandée.",
                    "missing_information": []
                }

        # ==================================================
        # 6. NORMALISATION
        # ==================================================

        severity = str(
            result.get("severity", "UNKNOWN")
        ).upper()

        if severity not in [
            "LOW",
            "MEDIUM",
            "HIGH"
        ]:
            severity = "UNKNOWN"

        description = result.get(
            "description",
            "Aucune description disponible."
        )

        solution = result.get(
            "solution",
            "Inspection professionnelle recommandée."
        )

        missing_information = result.get(
            "missing_information",
            []
        )

        if missing_information is None:
            missing_information = []

        # ==================================================
        # 7. RESULTAT FINAL
        # ==================================================

        final_result = {

            "severity": severity,

            "description": description,

            "solution": solution,

            "missing_information": missing_information
        }

        print("\n========================================")
        print("===== RESULTAT SEVERITE =====")
        print(json.dumps(
            final_result,
            indent=4,
            ensure_ascii=False
        ))
        print("========================================")

        return final_result

    except Exception as e:

        print("\n========================================")
        print("ERREUR SEVERITY SERVICE")
        print("========================================")
        print(str(e))
        print("========================================")

        return {

            "severity": "UNKNOWN",

            "description":
                "Impossible de déterminer automatiquement la sévérité.",

            "solution":
                "Inspection professionnelle recommandée.",

            "missing_information": [
                "Analyse détaillée nécessaire."
            ]
        }