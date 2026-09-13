from typing import TypedDict, Optional


class DefectraState(TypedDict):

    # Question utilisateur
    question: str

    # Plaque détectée ou saisie
    plate: str

    # Données récupérées
    vehicle: Optional[dict]

    inspection: Optional[dict]

    defects: list

    report: Optional[dict]

    # Documents RAG
    retrieved_docs: list

    # Réponse finale du LLM
    answer: str