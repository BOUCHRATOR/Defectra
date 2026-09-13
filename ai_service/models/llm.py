import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Charger les variables d'environnement
load_dotenv()


def get_llm():
    """
    Retourne une instance du modèle Groq.
    """

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    return llm
if __name__ == "__main__":

    llm = get_llm()

    response = llm.invoke("Bonjour")

    print(response.content)