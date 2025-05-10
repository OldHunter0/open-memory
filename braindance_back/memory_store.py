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
