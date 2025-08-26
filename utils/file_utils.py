"""
文件处理工具函数
"""
import os
import tempfile
import shutil
import uuid
from pathlib import Path
from typing import List


def ensure_dir(path: str) -> str:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
    return path


def get_temp_filename(suffix: str = '') -> str:
    """生成临时文件名"""
    temp_dir = os.getenv('CIF_CONVERTER_TEMP_DIR', tempfile.gettempdir())
    ensure_dir(temp_dir)
    
    filename = f"cif_conv_{uuid.uuid4().hex[:8]}{suffix}"
    return os.path.join(temp_dir, filename)


def cleanup_temp_files(file_paths: List[str]) -> None:
    """清理临时文件"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # 静默忽略清理错误


def is_valid_cif_file(file_path: str) -> bool:
    """检查是否为有效的CIF文件"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # 读取前1000字符
            # 简单检查CIF文件标识
            return any(keyword in content.lower() for keyword in [
                'data_', '_cell_length_a', '_atom_site_', 'loop_'
            ])
    except Exception:
        return False


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    if not os.path.exists(file_path):
        return 0.0
    return os.path.getsize(file_path) / (1024 * 1024)


def analyze_obj_file(obj_path: str) -> dict:
    """分析OBJ文件的基本信息"""
    if not os.path.exists(obj_path):
        return {'error': 'File not found'}
    
    try:
        with open(obj_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 统计基本元素
        vertices = content.count('\nv ')
        faces = content.count('\nf ')
        materials = len(set(line.split()[1] for line in content.split('\n') if line.startswith('usemtl ')))
        
        return {
            'vertices': vertices,
            'faces': faces,
            'materials': materials,
            'file_size': os.path.getsize(obj_path),
            'lines': len(content.split('\n'))
        }
    except Exception as e:
        return {'error': str(e)}