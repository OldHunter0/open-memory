# Configuration information
import os
import weaviate
from openai import OpenAI
#from mem0 import Memory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from os import getenv
from weaviate.classes.config import Property, DataType, Configure
from dotenv import load_dotenv

# 全局用户对话记忆（Key: user_id, Value: List[Message]）
global_memory = {}  # Key: user_id, Value: List[message dicts]

# 全局用户有效策略记忆 (Key: user_id, Value: set[string])
global_what_worked = {}  # Key: user_id, Value: List[message dicts]

# 全局用户需避免记忆 (Key: user_id, Value: set[string])
global_what_to_avoid = {}  # Key: user_id, Value: List[message dicts]

load_dotenv(verbose=True)

# API configuration
API_KEY = "sk-095fa234de724e8c8d6b73b51ab8dd51"
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL_NAME,
    temperature=0.7,
    max_tokens=1024
)

# Set environment variables
os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["OPENAI_API_BASE"] = BASE_URL

# 基础集合名称前缀
BASE_COLLECTION_NAME = "braindance_memory"

# 根据用户ID生成集合名称
def get_collection_name(user_id="default_user"):
    return f"{BASE_COLLECTION_NAME}_{user_id}"

# Configuration information
config = {
    "llm": {
        "provider": "deepseek",
        "config": {
            "api_key": API_KEY,
            "model": "deepseek-chat",
            "temperature": 0.2,
            "max_tokens": 2000,
            "top_p": 1.0
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "mxbai-embed-large"
        }
    },
    "vector_store": {
        "provider": "weaviate",
        "config": {
            "collection_name": BASE_COLLECTION_NAME,  # 默认集合名称，将根据用户ID动态替换
            "cluster_url": "http://localhost:8080",
            "auth_client_secret": None,
            "embedding_model_dims": 1024
        }
    },
    "version": "v1.1",
}

# Initialize client
openai_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Create a direct Qdrant client instance for snapshot operations
# qdrant_client = QdrantClient(
#     host=config["vector_store"]["config"]["host"],
#     port=config["vector_store"]["config"]["port"]
# )

embedder_info = OpenAIEmbeddings(
    model="nomic-embed-text",
    openai_api_base=BASE_URL,
    openai_api_key=API_KEY
)

# 获取用户特定的内存配置
def get_user_config(user_id="default_user"):
    user_config = config.copy()
    user_config["vector_store"] = config["vector_store"].copy()
    user_config["vector_store"]["config"] = config["vector_store"]["config"].copy()
    user_config["vector_store"]["config"]["collection_name"] = get_collection_name(user_id)
    return user_config

# 获取用户特定的内存实例
# def get_user_memory(user_id="default_user"):
#     user_config = get_user_config(user_id)
#     return Memory.from_config(user_config)


def get_user_what_worked(user_id="default_user"):
    user_config = get_user_config(user_id)
    return user_config["vector_store"]["config"]["what_worked"]

def get_user_what_to_avoid(user_id="default_user"):
    user_config = get_user_config(user_id)
    return user_config["vector_store"]["config"]["what_to_avoid"]

# 默认内存对象
# memory = Memory.from_config(config)


payload_schema = {
    "conversation": str,             # 对话内容（TEXT）
    "context_tags": list[str],       # 上下文标签（TEXT5_ARRAY）
    "conversation_summary": str,     # 摘要文本（TEXT）
    "what_worked": str,              # 有效策略（TEXT）
    "what_to_avoid": str             # 需避免内容（TEXT）
}

# 定义集合参数
COLLECTION_NAME = "episodic_memory"
VECTOR_SIZE = 1024  # 与mxbai-embed-large模型输出维度一致

weaviate_client = weaviate.connect_to_custom(
    http_host="localhost",
    http_port=8080,
    http_secure=False,
    grpc_host="localhost",
    grpc_port=50051,
    grpc_secure=False,
    auth_credentials=None
)

# def init_user_collection(user_id: str):
#     collection_name = get_collection_name(user_id)
#     qdrant_client.recreate_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(
#             size=config["vector_store"]["config"]["embedding_model_dims"],
#             distance=Distance.COSINE
#         )
#     )

def init_user_collection_v2(user_id: str):
    # get collection name
    collection_name = get_collection_name(user_id)
    # create collection
    vdb_client.collections.create(
    name=collection_name,
    description="Collection containing historical chat interactions and takeaways.",
    vectorizer_config=[
        Configure.NamedVectors.text2vec_ollama(
            name="title_vector",
            source_properties=["title"],
            api_endpoint="http://ollama:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
            model="nomic-embed-text",
        )
    ],
    properties=[
        Property(name="conversation", data_type=DataType.TEXT),
        Property(name="context_tags", data_type=DataType.TEXT_ARRAY),
        Property(name="conversation_summary", data_type=DataType.TEXT),
        Property(name="what_worked", data_type=DataType.TEXT),
        Property(name="what_to_avoid", data_type=DataType.TEXT),
    ]
)

# Connect to Weaviate Cloud
try:
    # 连接到本地Weaviate
    vdb_client = weaviate.connect_to_local()
    print("连接状态:", vdb_client.is_ready())

    # 初始化集合
    collection_name = "test_collection"
    if not vdb_client.collections.exists(collection_name):
        vdb_client.collections.delete(collection_name)
        print(f"集合 {collection_name} 已存在")
    else:

        init_user_collection_v2(collection_name)
        print(f"集合 {collection_name} 创建成功")
except Exception as e:
    print(f"连接失败: {e}")