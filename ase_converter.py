#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于ASE (Atomic Simulation Environment) 的CIF到OBJ转换器
这是科学计算领域的标准库，提供最可靠的转换方案
"""

import os
import sys
import numpy as np
from pathlib import Path
from loguru import logger
from typing import Optional, Tuple, Dict, List

try:
    from ase import Atoms
    from ase.io import read, write
    from ase.visualize import view
    from ase.data import atomic_numbers, chemical_symbols, covalent_radii
    from ase.neighborlist import NeighborList
    ASE_AVAILABLE = True
except ImportError:
    ASE_AVAILABLE = False
    logger.warning("ASE库未安装，请运行: pip install ase")

class ASEConverter:
    """基于ASE的CIF到OBJ转换器"""
    
    def __init__(self):
        """初始化ASE转换器"""
        if not ASE_AVAILABLE:
            raise ImportError("ASE库未安装，请运行: pip install ase")
        
        # 元素颜色映射（CPK颜色方案）
        self.cpk_colors = {
            'H': (1.0, 1.0, 1.0),      # 白色
            'C': (0.2, 0.2, 0.2),      # 黑色
            'N': (0.0, 0.0, 1.0),      # 蓝色
            'O': (1.0, 0.0, 0.0),      # 红色
            'F': (0.0, 1.0, 0.0),      # 绿色
            'Na': (0.67, 0.36, 0.95),  # 紫色
            'Mg': (0.54, 1.0, 0.0),    # 绿色
            'Al': (0.75, 0.65, 0.65),  # 灰色
            'Si': (0.94, 0.78, 0.63),  # 黄褐色
            'P': (1.0, 0.5, 0.0),      # 橙色
            'S': (1.0, 1.0, 0.19),     # 黄色
            'Cl': (0.12, 0.94, 0.12),  # 绿色
            'K': (0.56, 0.25, 0.83),   # 紫色
            'Ca': (0.24, 1.0, 0.0),    # 绿色
            'Fe': (0.88, 0.4, 0.2),    # 橙红色
            'Cu': (0.78, 0.5, 0.2),    # 铜色
            'Zn': (0.49, 0.5, 0.69),   # 蓝灰色
        }
        
        # 默认颜色（灰色）
        self.default_color = (0.5, 0.5, 0.5)
    
    def read_cif(self, cif_path: str) -> Optional[Atoms]:
        """读取CIF文件"""
        try:
            atoms = read(cif_path)
            logger.info(f"成功读取CIF文件: {cif_path}")
            logger.info(f"原子数量: {len(atoms)}")
            logger.info(f"元素类型: {set(atoms.get_chemical_symbols())}")
            logger.info(f"晶胞参数: {atoms.get_cell()}")
            return atoms
        except Exception as e:
            logger.error(f"读取CIF文件失败: {e}")
            return None
    
    def get_bonds(self, atoms: Atoms, cutoff_factor: float = 1.2) -> List[Tuple[int, int]]:
        """计算化学键"""
        try:
            # 使用ASE的NeighborList计算邻居
            cutoffs = [covalent_radii[atomic_numbers[symbol]] * cutoff_factor 
                      for symbol in atoms.get_chemical_symbols()]
            
            nl = NeighborList(cutoffs, self_interaction=False, bothways=False)
            nl.update(atoms)
            
            bonds = []
            for i in range(len(atoms)):
                indices, offsets = nl.get_neighbors(i)
                for j in indices:
                    if i < j:  # 避免重复
                        bonds.append((i, j))
            
            logger.info(f"计算得到{len(bonds)}个化学键")
            return bonds
        except Exception as e:
            logger.error(f"计算化学键失败: {e}")
            return []
    
    def create_sphere_obj(self, center: Tuple[float, float, float], 
                         radius: float, resolution: int = 20) -> Tuple[List, List]:
        """创建球体的顶点和面"""
        vertices = []
        faces = []
        
        # 生成球体顶点
        for i in range(resolution + 1):
            lat = np.pi * (-0.5 + float(i) / resolution)
            for j in range(resolution * 2):
                lon = 2 * np.pi * float(j) / (resolution * 2)
                
                x = center[0] + radius * np.cos(lat) * np.cos(lon)
                y = center[1] + radius * np.cos(lat) * np.sin(lon)
                z = center[2] + radius * np.sin(lat)
                
                vertices.append((x, y, z))
        
        # 生成球体面
        for i in range(resolution):
            for j in range(resolution * 2):
                # 当前四边形的四个顶点索引
                v1 = i * (resolution * 2) + j
                v2 = i * (resolution * 2) + (j + 1) % (resolution * 2)
                v3 = (i + 1) * (resolution * 2) + (j + 1) % (resolution * 2)
                v4 = (i + 1) * (resolution * 2) + j
                
                # 分成两个三角形
                if i > 0:  # 避免极点处的退化三角形
                    faces.append([v1 + 1, v2 + 1, v4 + 1])  # OBJ索引从1开始
                if i < resolution - 1:
                    faces.append([v2 + 1, v3 + 1, v4 + 1])
        
        return vertices, faces
    
    def create_cylinder_obj(self, start: Tuple[float, float, float], 
                           end: Tuple[float, float, float], 
                           radius: float, resolution: int = 8) -> Tuple[List, List]:
        """创建圆柱体的顶点和面（用于化学键）"""
        vertices = []
        faces = []
        
        # 计算圆柱体方向向量
        direction = np.array(end) - np.array(start)
        length = np.linalg.norm(direction)
        if length == 0:
            return vertices, faces
        
        direction = direction / length
        
        # 找到垂直于方向向量的两个正交向量
        if abs(direction[2]) < 0.9:
            perpendicular1 = np.cross(direction, [0, 0, 1])
        else:
            perpendicular1 = np.cross(direction, [1, 0, 0])
        
        perpendicular1 = perpendicular1 / np.linalg.norm(perpendicular1)
        perpendicular2 = np.cross(direction, perpendicular1)
        
        # 生成圆柱体顶点
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            offset = radius * (np.cos(angle) * perpendicular1 + np.sin(angle) * perpendicular2)
            
            # 起点圆周
            vertices.append(tuple(np.array(start) + offset))
            # 终点圆周
            vertices.append(tuple(np.array(end) + offset))
        
        # 生成圆柱体侧面
        for i in range(resolution):
            next_i = (i + 1) % resolution
            
            # 每个侧面是一个四边形，分成两个三角形
            v1 = i * 2 + 1      # 起点圆周当前点
            v2 = i * 2 + 2      # 终点圆周当前点
            v3 = next_i * 2 + 2 # 终点圆周下一点
            v4 = next_i * 2 + 1 # 起点圆周下一点
            
            faces.append([v1, v2, v4])
            faces.append([v2, v3, v4])
        
        return vertices, faces
    
    def convert_to_obj(self, atoms: Atoms, obj_path: str, 
                      include_bonds: bool = True, 
                      sphere_resolution: int = 20,
                      bond_resolution: int = 8,
                      scale_factor: float = 1.0) -> bool:
        """将Atoms对象转换为OBJ文件"""
        try:
            obj_content = []
            mtl_content = []
            
            # 添加MTL文件引用
            mtl_filename = obj_path.replace('.obj', '.mtl')
            obj_content.append(f"mtllib {os.path.basename(mtl_filename)}")
            obj_content.append("")
            
            # 获取原子位置和元素
            positions = atoms.get_positions() * scale_factor
            symbols = atoms.get_chemical_symbols()
            
            # 创建材质
            unique_elements = set(symbols)
            for element in unique_elements:
                color = self.cpk_colors.get(element, self.default_color)
                mtl_content.extend([
                    f"newmtl atom_{element}",
                    f"Ka {color[0]:.3f} {color[1]:.3f} {color[2]:.3f}",
                    f"Kd {color[0]:.3f} {color[1]:.3f} {color[2]:.3f}",
                    f"Ks 0.5 0.5 0.5",
                    f"Ns 32.0",
                    f"d 1.0",
                    ""
                ])
            
            # 添加化学键材质
            if include_bonds:
                mtl_content.extend([
                    "newmtl bond",
                    "Ka 0.3 0.3 0.3",
                    "Kd 0.5 0.5 0.5",
                    "Ks 0.7 0.7 0.7",
                    "Ns 64.0",
                    "d 1.0",
                    ""
                ])
            
            vertex_offset = 0
            
            # 添加原子球体
            for i, (pos, symbol) in enumerate(zip(positions, symbols)):
                # 获取原子半径
                radius = covalent_radii[atomic_numbers[symbol]] * 0.5 * scale_factor
                
                # 创建球体
                vertices, faces = self.create_sphere_obj(pos, radius, sphere_resolution)
                
                # 添加材质声明
                obj_content.append(f"usemtl atom_{symbol}")
                obj_content.append(f"g atom_{i}_{symbol}")
                
                # 添加顶点
                for vertex in vertices:
                    obj_content.append(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}")
                
                # 添加面
                for face in faces:
                    face_str = "f " + " ".join(str(v + vertex_offset) for v in face)
                    obj_content.append(face_str)
                
                vertex_offset += len(vertices)
                obj_content.append("")
            
            # 添加化学键
            if include_bonds:
                bonds = self.get_bonds(atoms)
                
                obj_content.append("usemtl bond")
                obj_content.append("g bonds")
                
                for bond_i, (i, j) in enumerate(bonds):
                    start_pos = positions[i]
                    end_pos = positions[j]
                    bond_radius = 0.1 * scale_factor
                    
                    # 创建圆柱体
                    vertices, faces = self.create_cylinder_obj(
                        start_pos, end_pos, bond_radius, bond_resolution)
                    
                    # 添加顶点
                    for vertex in vertices:
                        obj_content.append(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}")
                    
                    # 添加面
                    for face in faces:
                        face_str = "f " + " ".join(str(v + vertex_offset) for v in face)
                        obj_content.append(face_str)
                    
                    vertex_offset += len(vertices)
                
                obj_content.append("")
            
            # 写入OBJ文件
            with open(obj_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(obj_content))
            
            # 写入MTL文件
            with open(mtl_filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(mtl_content))
            
            logger.success(f"ASE转换成功: {obj_path}")
            logger.info(f"原子数量: {len(atoms)}")
            logger.info(f"化学键数量: {len(bonds) if include_bonds else 0}")
            logger.info(f"顶点数量: {vertex_offset}")
            
            return True
            
        except Exception as e:
            logger.error(f"ASE转换失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_cif_to_obj(self, cif_path: str, obj_path: str, **kwargs) -> Dict:
        """CIF到OBJ的完整转换流程"""
        try:
            # 读取CIF文件
            atoms = self.read_cif(cif_path)
            if atoms is None:
                return {
                    'success': False,
                    'error': 'cif_read_failed',
                    'message': 'CIF文件读取失败'
                }
            
            # 转换为OBJ
            success = self.convert_to_obj(atoms, obj_path, **kwargs)
            
            if success:
                return {
                    'success': True,
                    'message': 'ASE转换成功',
                    'atom_count': len(atoms),
                    'elements': list(set(atoms.get_chemical_symbols()))
                }
            else:
                return {
                    'success': False,
                    'error': 'obj_conversion_failed',
                    'message': 'OBJ转换失败'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'conversion_error',
                'message': f'转换过程出错: {str(e)}'
            }

def test_ase_converter():
    """测试ASE转换器"""
    if not ASE_AVAILABLE:
        logger.error("ASE库未安装，无法进行测试")
        return False
    
    logger.info("=== 测试ASE转换器 ===")
    
    # 测试文件
    cif_file = "examples/NaCl.cif"
    if not os.path.exists(cif_file):
        logger.error(f"测试CIF文件不存在: {cif_file}")
        return False
    
    # 创建转换器
    converter = ASEConverter()
    
    # 测试转换
    output_obj = "test_ase_nacl.obj"
    result = converter.convert_cif_to_obj(
        cif_path=cif_file,
        obj_path=output_obj,
        include_bonds=True,
        sphere_resolution=20,
        bond_resolution=8,
        scale_factor=1.0
    )
    
    if result['success']:
        logger.success("ASE转换测试成功！")
        logger.info(f"原子数量: {result['atom_count']}")
        logger.info(f"元素类型: {result['elements']}")
        
        # 分析生成的文件
        if os.path.exists(output_obj):
            file_size = os.path.getsize(output_obj)
            logger.info(f"OBJ文件大小: {file_size} 字节")
            
            with open(output_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vertex_count = content.count('\nv ')
            face_count = content.count('\nf ')
            logger.info(f"顶点数: {vertex_count}")
            logger.info(f"面数: {face_count}")
        
        return True
    else:
        logger.error(f"ASE转换测试失败: {result['message']}")
        return False

def install_ase():
    """安装ASE库"""
    logger.info("正在安装ASE库...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "ase"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.success("ASE库安装成功！")
            return True
        else:
            logger.error(f"ASE库安装失败: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"安装过程出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("ASE转换器 - 科学计算标准库方案")
    
    if not ASE_AVAILABLE:
        logger.warning("ASE库未安装")
        install_choice = input("是否现在安装ASE库？(y/n): ")
        if install_choice.lower() == 'y':
            if install_ase():
                logger.info("请重新运行脚本")
            return
        else:
            logger.info("跳过ASE测试")
            return
    
    # 运行测试
    test_ase_converter()
    
    logger.info("\n=== ASE转换器优势 ===")
    logger.info("1. 科学计算领域标准库，可靠性最高")
    logger.info("2. 正确处理晶体结构和周期性边界条件")
    logger.info("3. 精确计算化学键")
    logger.info("4. 支持多种文件格式")
    logger.info("5. 活跃的开发社区和文档支持")
    logger.info("6. 被全球科研机构广泛使用")

if __name__ == "__main__":
    main()