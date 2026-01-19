import os
import subprocess
import json
from pathlib import Path

class ToolDetector:
    def __init__(self):
        self.tools = {
            'obabel': {
                'name': 'OpenBabel',
                'executable': 'obabel.exe',
                'description': '用于分子格式转换',
                'required': True
            },
            'vina': {
                'name': 'AutoDock Vina',
                'executable': 'vina.exe',
                'description': '用于分子对接',
                'required': True
            }
        }
        self.config_file = 'tool_config.json'
        self.config = {}
        self.load_config()
        
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def find_in_path(self, executable):
        try:
            result = subprocess.run(
                ['where', executable],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0 and result.stdout.strip():
                paths = result.stdout.strip().split('\n')
                return paths[0]
        except:
            pass
        return None
    
    def find_in_program_files(self, executable):
        program_files = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'),
            os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local')),
            os.path.dirname(os.path.abspath(__file__))
        ]
        
        for base_dir in program_files:
            if not base_dir or not os.path.exists(base_dir):
                continue
            
            for root, dirs, files in os.walk(base_dir):
                if executable in files:
                    return os.path.join(root, executable)
                
                depth = root.replace(base_dir, '').count(os.sep)
                if depth > 5:
                    break
        
        return None
    
    def detect_tool(self, tool_key):
        tool = self.tools[tool_key]
        executable = tool['executable']
        
        if tool_key in self.config:
            path = self.config[tool_key]
            if os.path.exists(path):
                return path
        
        path = self.find_in_path(executable)
        if path:
            self.config[tool_key] = path
            self.save_config()
            return path
        
        path = self.find_in_program_files(executable)
        if path:
            self.config[tool_key] = path
            self.save_config()
            return path
        
        return None
    
    def detect_all_tools(self):
        results = {}
        for tool_key in self.tools:
            path = self.detect_tool(tool_key)
            results[tool_key] = {
                'found': path is not None,
                'path': path,
                'name': self.tools[tool_key]['name'],
                'description': self.tools[tool_key]['description'],
                'required': self.tools[tool_key]['required']
            }
        return results
    
    def set_tool_path(self, tool_key, path):
        if os.path.exists(path):
            self.config[tool_key] = path
            self.save_config()
            return True
        return False
    
    def get_tool_path(self, tool_key):
        return self.config.get(tool_key)
    
    def verify_tool(self, tool_key):
        path = self.get_tool_path(tool_key)
        if path and os.path.exists(path):
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return True, result.stdout[:100]
            except:
                return False, "无法执行"
        return False, "文件不存在"

if __name__ == "__main__":
    detector = ToolDetector()
    
    print("检测分子对接工具...")
    print("=" * 50)
    
    results = detector.detect_all_tools()
    
    all_found = True
    for tool_key, info in results.items():
        status = "✓" if info['found'] else "✗"
        required = " [必需]" if info['required'] else " [可选]"
        print(f"{status} {info['name']}{required}")
        print(f"  描述: {info['description']}")
        if info['found']:
            print(f"  路径: {info['path']}")
        else:
            print(f"  状态: 未找到")
            all_found = False
        print()
    
    print("=" * 50)
    if all_found:
        print("所有必需工具已找到!")
    else:
        print("警告: 部分必需工具未找到，请手动配置路径")
    
    print(f"\n配置已保存到: {detector.config_file}")
