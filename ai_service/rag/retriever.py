from rag.vector_store import get_vector_store


print("===== RETRIEVER TEST =====")


def get_retriever():

    print("Chargement de ChromaDB...")

    vector_store = get_vector_store()

    print("ChromaDB chargée.")

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 3
        }
    )

    print("Retriever créé.")

    return retriever


if __name__ == "__main__":

    print("Début du test...")

    retriever = get_retriever()

    question = """
    How can the severity of a vehicle crack,
    dent or scratch be evaluated?
    """

    print("\nQuestion :")
    print(question)

    print("\nRecherche dans ChromaDB...")

    docs = retriever.invoke(question)

    print(
        f"\nNombre de documents récupérés : {len(docs)}"
    )

    for i, doc in enumerate(docs, start=1):

        print("\n================================")
        print(f"DOCUMENT {i}")
        print("================================")

        print("Source :")
        print(
            doc.metadata.get(
                "source",
                "unknown"
            )
        )

        print("\nContenu :")
        print(
            doc.page_content[:1000]
        )

    print("\n===== TEST TERMINÉ =====")