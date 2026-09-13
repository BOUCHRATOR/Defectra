from langchain_chroma import Chroma

from rag.embeddings import get_embeddings


DB_PATH = "documents/vector_db"


def get_vector_store():

    return Chroma(

        persist_directory=DB_PATH,

        embedding_function=get_embeddings()

    )