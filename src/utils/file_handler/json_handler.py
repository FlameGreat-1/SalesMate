import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class JSONHandler:
    
    @staticmethod
    def read_json(file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error reading JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Error writing JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def read_json_list(file_path: Path, key: Optional[str] = None) -> List[Dict[str, Any]]:
        data = JSONHandler.read_json(file_path)
        
        if key:
            if key not in data:
                raise KeyError(f"Key '{key}' not found in JSON file: {file_path}")
            items = data[key]
        else:
            items = data
        
        if not isinstance(items, list):
            raise ValueError(f"Expected a list in JSON file: {file_path}")
        
        return items
    
    @staticmethod
    def append_to_json_list(file_path: Path, new_item: Dict[str, Any], key: Optional[str] = None) -> None:
        if file_path.exists():
            data = JSONHandler.read_json(file_path)
        else:
            data = {key: []} if key else []
        
        if key:
            if key not in data:
                data[key] = []
            if not isinstance(data[key], list):
                raise ValueError(f"Key '{key}' does not contain a list")
            data[key].append(new_item)
        else:
            if not isinstance(data, list):
                raise ValueError("JSON file does not contain a list")
            data.append(new_item)
        
        JSONHandler.write_json(file_path, data)
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_keys: List[str]) -> bool:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")
        
        return True
    
    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        return data.get(key, default)
    
    @staticmethod
    def file_exists(file_path: Path) -> bool:
        return file_path.exists() and file_path.is_file()
