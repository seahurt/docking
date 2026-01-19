import json
import os

def get_tool_path(tool_key):
    config_file = 'tool_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get(tool_key)
        except:
            pass
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python get_tool_path.py <工具名称>")
        sys.exit(1)
    
    tool_key = sys.argv[1]
    path = get_tool_path(tool_key)
    
    if path:
        print(path)
    else:
        print("")
