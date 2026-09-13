from pathlib import Path

from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.vector_store import get_vector_store


DOCUMENTS_PATH = Path("documents")


def ingest_documents():

    print("===== Début de l'ingestion =====")

    pdfs = list(DOCUMENTS_PATH.glob("*.pdf"))

    print(f"Nombre de PDF trouvés : {len(pdfs)}")

    if len(pdfs) == 0:
        print("Aucun PDF trouvé.")
        return

    print("\n===== Chargement ChromaDB =====")

    vector_store = get_vector_store()

    print("===== ChromaDB chargée =====")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    documents = []

    for pdf in pdfs:

        print(f"\nLecture : {pdf.name}")

        reader = PdfReader(str(pdf))

        print(f"Nombre de pages : {len(reader.pages)}")

        text = ""

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        print(
            f"Caractères extraits : {len(text)}"
        )

        document = Document(
            page_content=text,
            metadata={
                "source": pdf.name
            }
        )

        chunks = splitter.split_documents(
            [document]
        )

        print(
            f"Chunks créés : {len(chunks)}"
        )

        documents.extend(chunks)

    print(
        f"\nNombre total de chunks : "
        f"{len(documents)}"
    )

    print("\n===== Création des embeddings =====")

    vector_store.add_documents(
        documents
    )

    print(
        "\n✅ Base vectorielle mise à jour."
    )


if __name__ == "__main__":

    ingest_documents()