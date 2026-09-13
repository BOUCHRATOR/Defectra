if __name__ == "__main__":

    llm = get_llm()

    response = llm.invoke("Bonjour")

    print(response.content)