import weaviate  
from weaviate.auth import AuthApiKey  


def test_weaviate():
    client = weaviate.connect_to_local()
    try:
        collection = client.collections.get("Braindance_memory_user_57d57b4dab129529dffc6f6065edeb8a")
        
        # 获取前5条数据（含向量）
        objects = collection.query.fetch_objects(
            limit=5,
            include_vector=True
        )
        
        for obj in objects.objects:
            print(f"ID: {obj.uuid}")
            print(f"Vector: {obj.vector['title_vector'][:5]}...")  # 展示前5维
            print(f"Properties: {obj.properties}\n")   
    finally:
        client.close()


def main():
    test_weaviate()


if __name__ == "__main__":
    main()