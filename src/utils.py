import json
import os

def load_metadata(region_name):

    path = os.path.join("..", "data", region_name.lower(), "metadata.json")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Metadata in {path} not found")
        
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def save_metadata(region_name, metadata_dict):

    folder_path = os.path.join("..", "data", region_name.lower())
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Made new folder: {folder_path}")
    
    file_path = os.path.join(folder_path, "metadata.json")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_dict, f, indent=4, ensure_ascii=False)
    
    print(f"Metadata saved in: {file_path}")
    
    
