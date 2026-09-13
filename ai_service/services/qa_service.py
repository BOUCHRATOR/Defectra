from database.repository import Repository
from rag.retriever import get_retriever
from models.llm import get_llm


# ==========================================================
# Chargement unique au démarrage
# ==========================================================

retriever = get_retriever()
llm = get_llm()


# ==========================================================
# SERVICE QA / RAG HYBRIDE
# ==========================================================

class QAService:

    def __init__(self, db):

        self.repository = Repository(db)

    # ======================================================
    # 1. Récupérer les données PostgreSQL
    # ======================================================

    def get_postgres_context(self, inspection_id):

        data = self.repository.get_inspection_context(
            inspection_id
        )

        if not data:

            return "No inspection information found."

        vehicle = data["vehicle"]
        inspection = data["inspection"]
        defects = data["defects"]
        report = data["report"]

        context = f"""
VEHICLE INFORMATION

Brand: {vehicle.brand}
Model: {vehicle.model}
Plate: {vehicle.plate_number}
Year: {vehicle.year}


INSPECTION INFORMATION

Inspection ID: {inspection.id}
Date: {inspection.inspection_date}
Status: {inspection.status}
Notes: {inspection.notes}


DETECTED DEFECTS
"""

        # ==================================================
        # Défauts
        # ==================================================

        if not defects:

            context += """
No defects were detected.
"""

        else:

            for defect in defects:

                context += f"""
Defect name: {defect.defect_name}
Confidence: {defect.confidence}
Severity: {defect.severity}
Description: {defect.description}
Solution: {defect.solution}

"""

        # ==================================================
        # Rapport existant
        # ==================================================

        if report:

            context += f"""

PREVIOUS INSPECTION REPORT

Summary:
{report.summary}

Overall condition:
{report.overall_condition}

Recommendation:
{report.recommendation}

"""

        return context


    # ======================================================
    # 2. Recherche dans ChromaDB
    # ======================================================

    def get_chroma_context(self, question):

        docs = retriever.invoke(question)

        if not docs:

            return "No relevant technical knowledge found."

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        return context


    # ======================================================
    # 3. RAG hybride
    # ======================================================

    def ask(
        self,
        question,
        inspection_id=None
    ):

        # --------------------------------------------------
        # PostgreSQL
        # --------------------------------------------------

        postgres_context = ""

        if inspection_id:

            postgres_context = (
                self.get_postgres_context(
                    inspection_id
                )
            )


        # --------------------------------------------------
        # ChromaDB
        # --------------------------------------------------

        chroma_context = (
            self.get_chroma_context(
                question
            )
        )


        # --------------------------------------------------
        # Combiner PostgreSQL + ChromaDB
        # --------------------------------------------------

        context = f"""

========================================
POSTGRESQL - VEHICLE DATA
========================================

{postgres_context}


========================================
CHROMADB - TECHNICAL KNOWLEDGE
========================================

{chroma_context}

"""


        # ==================================================
        # Prompt envoyé au LLM
        # ==================================================

        prompt = f"""
You are an intelligent automotive inspection assistant.

You have access to two information sources.

SOURCE 1: PostgreSQL

PostgreSQL contains real information about:
- vehicles
- inspections
- detected defects
- reports
- recommendations


SOURCE 2: ChromaDB

ChromaDB contains general automotive technical knowledge,
maintenance information and repair recommendations.


IMPORTANT RULES:

1. Use PostgreSQL for information about the specific vehicle.

2. Use ChromaDB for general technical explanations.

3. Do not invent information.

4. If the requested information is not available,
say that you do not have enough information.

5. Give a clear and professional answer.

6. When possible, explain the answer using both sources.


CONTEXT:

{context}


USER QUESTION:

{question}


ANSWER:
"""


        # ==================================================
        # LLM
        # ==================================================

        response = llm.invoke(prompt)

        return response.content


# ==========================================================
# Fonction simple compatible avec ton ancien code
# ==========================================================

def ask(
    question: str,
    inspection_id=None,
    db=None
):

    if db is None:

        # Ancien comportement :
        # ChromaDB uniquement

        docs = retriever.invoke(question)

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        prompt = f"""
Use the following technical knowledge to answer the question.

Context:

{context}

Question:

{question}

Answer clearly and professionally.
"""

        response = llm.invoke(prompt)

        return response.content


    # Nouveau comportement :
    # PostgreSQL + ChromaDB

    service = QAService(db)

    return service.ask(
        question,
        inspection_id
    )


# ==========================================================
# Appel direct du LLM
# Utilisé par ReportService
# ==========================================================

def ask_prompt(prompt: str) -> str:

    response = llm.invoke(prompt)

    return response.content