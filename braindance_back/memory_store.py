import json
import os
from datetime import date, datetime
from typing import List

import traceback

from weaviate.collections import Collection
from weaviate.collections.classes.types import GeoCoordinate

from .config import get_collection_name
from .config import weaviate_client

def export_data(collection_src: Collection) -> List:
    objects = list()

    for item in collection_src.iterator(include_vector=True):

        print(f"property: {item.properties}, vector: {item.vector}")
        object = item.properties
        for k, v in object.items():
            if isinstance(v, (datetime, date)):
                object[k] = v.isoformat()
            if isinstance(v, GeoCoordinate):
                object[k] = v._to_dict()

        for k, v in item.vector.items():
            object[f"vector_{k}"]=v
        object["uuid"] = str(item.uuid)
        objects.append(object)

    return objects

def export_weaviate_snapshot(user_id="default_user", collection_name=None, snapshot_path=None):
    """
    Export Qdrant collection to a snapshot file
    
    Args:
        user_id: User ID to specify which collection to export
        collection_name: Name of the collection to export, default is based on user_id
        snapshot_path: Path to save the snapshot file, default is a timestamp-named file in the your_memory directory
        
    Returns:
        str: Path where the snapshot file is saved
    """
    if collection_name is None:
        collection_name = get_collection_name(user_id)
    
    # 创建保存快照的目录
    memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "your_memory", user_id)
    if not os.path.exists(memory_dir):
        print(f"Creating directory: {memory_dir}")
        os.makedirs(memory_dir)
    
    if snapshot_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"{collection_name}_snapshot_{timestamp}"
        snapshot_path = os.path.join(memory_dir, snapshot_filename)

    try:
        # Check if the collection exists
        collections = weaviate_client.collections.get(collection_name)
        coll_objects = export_data(collections)
        print(f"Creating snapshot for collection '{collection_name}'...")

        output_file = f"{snapshot_path}.snapshot"
        with open(output_file, 'w') as f:
            json.dump(coll_objects, f, indent=2, default=str)
        
        full_path = os.path.abspath(f"{snapshot_path}.snapshot")
        print(f"Snapshot successfully exported to: {full_path}")
        return full_path
        
    except Exception as e:
        print(f"Error exporting snapshot: {str(e)}")
        traceback.print_exc()  # Print full error stack
        return None


# def import_qdrant_snapshot(snapshot_path, user_id="default_user", collection_name=None):
#     """
#     Import Qdrant collection from a snapshot file
    
#     Args:
#         snapshot_path: Path to the snapshot file
#         user_id: User ID to specify which collection to import to
#         collection_name: Name of the collection to import to, default is based on user_id
        
#     Returns:
#         bool: Whether the import was successful
#     """
#     if collection_name is None:
#         collection_name = get_collection_name(user_id)
    
#     try:
#         # Check if the snapshot file exists
#         if not os.path.exists(snapshot_path):
#             print(f"Snapshot file does not exist: {snapshot_path}")
#             return False
        
#         # Configure Qdrant API parameters
#         qdrant_host = config["vector_store"]["config"]["host"]
#         qdrant_port = config["vector_store"]["config"]["port"]
        
#         # Delete existing collection (if exists)
#         try:
#             print(f"Deleting existing collection '{collection_name}' (if exists)...")
#             qdrant_client.delete_collection(collection_name=collection_name)
#             print("Collection deleted successfully")
#         except Exception as e:
#             print(f"Exception occurred while deleting collection (possibly collection does not exist): {str(e)}")
        
#         # Check file size and format
#         file_size = os.path.getsize(snapshot_path)
#         print(f"Snapshot file size: {file_size} bytes")
        
#         # Restore collection from snapshot file - use upload endpoint
#         print(f"Restoring collection from snapshot file...")
#         upload_url = f"http://{qdrant_host}:{qdrant_port}/collections/{collection_name}/snapshots/upload"
                
#         # api_key = config["vector_store"]["config"]["api_key"]
#         # headers = {
#         #     "api-key": api_key
#         # }
#         # Open file in binary mode and set up request correctly
#         with open(snapshot_path, 'rb') as f:
#             files = {'snapshot': (os.path.basename(snapshot_path), f)}
#             response = requests.post(upload_url, files=files)
        
#         # Print detailed response information for debugging
#         print(f"Response status code: {response.status_code}")
#         print(f"Response content: {response.text}")
        
#         if response.status_code != 200:
#             print(f"Failed to restore from snapshot: {response.text}")
#             return False
        
#         print(f"Snapshot successfully imported to collection '{collection_name}'")
        
#         print(f"开始替换用户ID为 {user_id}...")
#         update_success = update_user_id_in_collection(collection_name, user_id)
#         if not update_success:
#             print("用户ID替换失败")
#             qdrant_client.delete_collection(collection_name)  # 清理失败数据
#             return False
        
#         return True
        
#     except Exception as e:
#         print(f"Error importing snapshot: {str(e)}")
#         traceback.print_exc()  # Print full stack for debugging
#         return False
    
# 使用
# def update_user_id_in_collection(collection_name, target_user_id):
#     try:
#         # 构建过滤条件
#         old_user_filter = models.Filter(
#             must_not=[
#                 models.FieldCondition(
#                     key="user_id",
#                     match=models.MatchValue(value=target_user_id)
#                 )
#             ]
#         )
#
#         # 分页获取数据
#         all_points = []
#         current_offset = None
#
#         while True:
#             # 获取数据（适配版本）
#             scroll_response = qdrant_client.scroll(
#                 collection_name=collection_name,
#                 scroll_filter=old_user_filter,
#                 limit=100,
#                 offset=current_offset,
#                 with_payload=True,
#                 with_vectors=True  # 明确要求返回向量
#             )
#
#             # 解析响应
#             if isinstance(scroll_response, tuple):
#                 points, next_offset = scroll_response
#             else:
#                 points = scroll_response.points
#                 next_offset = scroll_response.next_page_offset
#
#             if not points:
#                 break
#
#             all_points.extend(points)
#             current_offset = next_offset
#             if not current_offset:
#                 break
#
#         # 构建更新数据
#         update_points = []
#         skipped_points = 0
#
#         for point in all_points:
#             # 向量校验
#             if not hasattr(point, 'vector') or point.vector is None:
#                 skipped_points += 1
#                 continue
#
#             # 类型校验
#             if not isinstance(point.vector, (list, dict)):
#                 print(f"非法向量类型 ({type(point.vector)}) 在点 {point.id}")
#                 skipped_points += 1
#                 continue
#
#             # 构造合法数据
#             update_points.append(
#                 models.PointStruct(
#                     id=point.id,
#                     vector=point.vector,
#                     payload={**point.payload, "user_id": target_user_id}
#                 )
#             )
#
#         # 执行更新
#         if update_points:
#             qdrant_client.upsert(
#                 collection_name=collection_name,
#                 points=update_points,
#                 wait=True
#             )
#             print(f"成功更新 {len(update_points)} 个点，跳过 {skipped_points} 个无效点")
#             return True
#         else:
#             print("没有有效点需要更新")
#             return False
#
#     except Exception as e:
#         print(f"用户ID替换失败: {str(e)}")
#         traceback.print_exc()
#         return False