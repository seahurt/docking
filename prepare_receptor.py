import os
import subprocess
import json
from Bio.PDB import PDBParser
import numpy as np

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

def pdb_to_pdbqt(pdb_file, output_pdbqt):
    """
    使用OpenBabel将PDB文件转换为PDBQT格式
    """
    try:
        obabel_path = get_tool_path('obabel')
        if not obabel_path:
            raise Exception("未找到OpenBabel路径，请在工具配置中设置")
        
        cmd = f'"{obabel_path}" "{pdb_file}" -O "{output_pdbqt}" -xr'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"OpenBabel转换失败: {result.stderr}")
        
        print(f"[OK] PDB转PDBQT成功: {output_pdbqt}")
        return True
    except Exception as e:
        print(f"[FAIL] PDB转PDBQT失败: {str(e)}")
        return False

def extract_ligand_from_pdb(pdb_file):
    """
    从PDB文件中提取配体信息
    返回配体的原子坐标
    """
    parser = PDBParser()
    structure = parser.get_structure("receptor", pdb_file)
    
    ligand_atoms = []
    
    for model in structure:
        for chain in model:
            for residue in chain:
                hetfield = residue.get_id()[0]
                if hetfield != ' ':
                    for atom in residue:
                        ligand_atoms.append(atom.get_coord())
    
    return np.array(ligand_atoms) if len(ligand_atoms) > 0 else None

def calculate_binding_site_center(ligand_atoms, padding=5.0):
    """
    计算活性位点中心坐标
    """
    if ligand_atoms is None or len(ligand_atoms) == 0:
        return None
    
    center = np.mean(ligand_atoms, axis=0)
    return center

def calculate_box_size(ligand_atoms, padding=10.0):
    """
    计算对接盒子大小
    """
    if ligand_atoms is None or len(ligand_atoms) == 0:
        return [20.0, 20.0, 20.0]
    
    min_coords = np.min(ligand_atoms, axis=0)
    max_coords = np.max(ligand_atoms, axis=0)
    
    size = (max_coords - min_coords) + padding * 2
    return size.tolist()

def generate_vina_conf(output_file, receptor_pdbqt, center, size, 
                       exhaustiveness=8, num_modes=9, energy_range=3):
    """
    生成vina.conf配置文件
    """
    config_content = f"""receptor = {receptor_pdbqt}

center_x = {center[0]:.3f}
center_y = {center[1]:.3f}
center_z = {center[2]:.3f}

size_x = {size[0]:.3f}
size_y = {size[1]:.3f}
size_z = {size[2]:.3f}

exhaustiveness = {exhaustiveness}
num_modes = {num_modes}
energy_range = {energy_range}
"""
    
    with open(output_file, 'w') as f:
        f.write(config_content)
    
    print(f"[OK] 配置文件生成成功: {output_file}")
    return True

def prepare_receptor(pdb_file, output_dir="."):
    """
    准备受体文件：
    1. 将PDB转换为PDBQT
    2. 提取活性位点
    3. 生成vina.conf配置文件
    """
    os.makedirs(output_dir, exist_ok=True)
    
    pdb_name = os.path.splitext(os.path.basename(pdb_file))[0]
    pdbqt_file = os.path.join(output_dir, f"{pdb_name}.pdbqt")
    conf_file = os.path.join(output_dir, "vina.conf")
    
    print(f"开始处理受体文件: {pdb_file}")
    
    if not os.path.exists(pdb_file):
        raise Exception(f"PDB文件不存在: {pdb_file}")
    
    print("步骤1: 转换PDB为PDBQT...")
    if not pdb_to_pdbqt(pdb_file, pdbqt_file):
        raise Exception("PDB转PDBQT失败")
    
    print("步骤2: 提取活性位点...")
    ligand_atoms = extract_ligand_from_pdb(pdb_file)
    
    if ligand_atoms is not None:
        print(f"找到 {len(ligand_atoms)} 个配体原子")
        center = calculate_binding_site_center(ligand_atoms)
        size = calculate_box_size(ligand_atoms)
        print(f"活性位点中心: {center}")
        print(f"对接盒子大小: {size}")
    else:
        print("警告: 未找到配体，使用默认参数")
        center = [0.0, 0.0, 0.0]
        size = [20.0, 20.0, 20.0]
    
    print("步骤3: 生成vina.conf...")
    if not generate_vina_conf(conf_file, pdbqt_file, center, size):
        raise Exception("生成配置文件失败")
    
    print("\n受体准备完成!")
    print(f"  - PDBQT文件: {pdbqt_file}")
    print(f"  - 配置文件: {conf_file}")
    
    return {
        'pdbqt_file': pdbqt_file,
        'conf_file': conf_file,
        'center': center,
        'size': size
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python prepare_receptor.py <pdb文件> [输出目录]")
        sys.exit(1)
    
    pdb_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    try:
        result = prepare_receptor(pdb_file, output_dir)
        print("\n成功!")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        sys.exit(1)
