import weaviate  

def test_episodic_recall(query):
    client = weaviate.connect_to_local()
    try:
        collection = client.collections.get("Braindance_memory_user_57d57b4dab129529dffc6f6065edeb8a")

        # Hybrid Semantic/BM25 Retrieval
        memory = collection.query.hybrid(
            query=query,
            alpha=0.5,
            limit=1,
            )
        return memory
    finally:
        client.close()

def main():
    query = "Talking about my name"
    memory = test_episodic_recall(query)
    print(memory.objects[0].properties)


if __name__ == "__main__":
    main()