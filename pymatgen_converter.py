#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pymatgen CIF to OBJ Converter
基于pymatgen库的CIF到OBJ转换器

pymatgen是Materials Project开发的材料科学Python库，
被全球材料科学研究机构广泛使用，是最权威的材料结构处理库之一。
"""

import os
import math
import numpy as np
from loguru import logger
from typing import List, Tuple, Dict, Optional

try:
    from pymatgen.core import Structure
    from pymatgen.io.cif import CifParser
    from pymatgen.analysis.local_env import CrystalNN
    PYMATGEN_AVAILABLE = True
except ImportError:
    logger.error("pymatgen库未安装，请运行: pip install pymatgen")
    PYMATGEN_AVAILABLE = False

class PymatgenConverter:
    """基于pymatgen的CIF到OBJ转换器"""
    
    def __init__(self):
        if not PYMATGEN_AVAILABLE:
            raise ImportError("pymatgen库未安装")
        
        # 元素颜色映射（CPK颜色方案）
        self.element_colors = {
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
        
        # 元素半径映射（范德华半径，单位：埃）
        self.element_radii = {
            'H': 1.2, 'C': 1.7, 'N': 1.55, 'O': 1.52, 'F': 1.47,
            'Na': 2.27, 'Mg': 1.73, 'Al': 1.84, 'Si': 2.1, 'P': 1.8,
            'S': 1.8, 'Cl': 1.75, 'K': 2.75, 'Ca': 2.31, 'Fe': 2.0,
            'Cu': 1.4, 'Zn': 1.39
        }
        
        self.bond_radius = 0.1  # 化学键半径
        self.sphere_resolution = 20  # 球体分辨率
        self.cylinder_resolution = 12  # 圆柱体分辨率
    
    def read_cif(self, cif_file: str) -> Structure:
        """读取CIF文件"""
        try:
            parser = CifParser(cif_file)
            # 使用parse_structures并设置primitive=False获取完整晶胞
            structures = parser.parse_structures(primitive=False)
            structure = structures[0]  # 获取第一个结构
            
            logger.info(f"成功读取CIF文件: {cif_file}")
            logger.info(f"原子数量: {len(structure)}")
            logger.info(f"元素类型: {set([site.specie.symbol for site in structure])}")
            logger.info(f"晶胞参数: {structure.lattice}")
            
            return structure
            
        except Exception as e:
            logger.error(f"读取CIF文件失败: {e}")
            raise
    
    def get_bonds(self, structure: Structure) -> List[Tuple[int, int, float]]:
        """使用pymatgen的CrystalNN算法计算化学键"""
        try:
            # 使用CrystalNN算法识别化学键
            nn = CrystalNN()
            bonds = []
            
            for i, site in enumerate(structure):
                try:
                    # 获取近邻原子
                    neighbors = nn.get_nn_info(structure, i)
                    
                    for neighbor in neighbors:
                        j = neighbor['site_index']
                        distance = neighbor['weight']  # 键长
                        
                        # 避免重复添加键（只添加i < j的键）
                        if i < j:
                            bonds.append((i, j, distance))
                            
                except Exception as e:
                    logger.warning(f"计算原子{i}的近邻失败: {e}")
                    continue
            
            logger.info(f"计算得到{len(bonds)}个化学键")
            return bonds
            
        except Exception as e:
            logger.error(f"计算化学键失败: {e}")
            return []
    
    def create_sphere(self, center: Tuple[float, float, float], 
                     radius: float, resolution: int = 20) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """创建球体的顶点和面"""
        vertices = []
        faces = []
        
        # 生成球体顶点
        for i in range(resolution + 1):
            lat = math.pi * (-0.5 + float(i) / resolution)
            for j in range(resolution * 2):
                lon = 2 * math.pi * float(j) / (resolution * 2)
                
                x = center[0] + radius * math.cos(lat) * math.cos(lon)
                y = center[1] + radius * math.cos(lat) * math.sin(lon)
                z = center[2] + radius * math.sin(lat)
                
                vertices.append((x, y, z))
        
        # 生成球体面
        for i in range(resolution):
            for j in range(resolution * 2):
                first = i * (resolution * 2) + j
                second = first + resolution * 2
                
                # 第一个三角形
                faces.append((first, second, first + 1))
                # 第二个三角形
                faces.append((second, second + 1, first + 1))
        
        return vertices, faces
    
    def create_cylinder(self, start: Tuple[float, float, float], 
                       end: Tuple[float, float, float], 
                       radius: float, resolution: int = 12) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """创建圆柱体的顶点和面"""
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
            angle = 2 * math.pi * i / resolution
            offset = radius * (math.cos(angle) * perpendicular1 + math.sin(angle) * perpendicular2)
            
            # 底面顶点
            bottom_vertex = np.array(start) + offset
            vertices.append(tuple(bottom_vertex))
            
            # 顶面顶点
            top_vertex = np.array(end) + offset
            vertices.append(tuple(top_vertex))
        
        # 生成圆柱体侧面
        for i in range(resolution):
            next_i = (i + 1) % resolution
            
            # 当前环的底面和顶面顶点索引
            bottom_current = i * 2
            top_current = i * 2 + 1
            bottom_next = next_i * 2
            top_next = next_i * 2 + 1
            
            # 侧面的两个三角形
            faces.append((bottom_current, top_current, bottom_next))
            faces.append((top_current, top_next, bottom_next))
        
        return vertices, faces
    
    def convert_to_obj(self, structure: Structure, output_file: str) -> bool:
        """将pymatgen Structure转换为OBJ文件"""
        try:
            # 获取化学键
            bonds = self.get_bonds(structure)
            
            vertices = []
            faces = []
            materials = []
            vertex_offset = 0
            
            # 为每个元素创建材质
            elements = set([site.specie.symbol for site in structure])
            for element in elements:
                color = self.element_colors.get(element, (0.5, 0.5, 0.5))
                materials.append(f"newmtl {element}\n")
                materials.append(f"Kd {color[0]:.3f} {color[1]:.3f} {color[2]:.3f}\n")
                materials.append(f"Ka {color[0]*0.3:.3f} {color[1]*0.3:.3f} {color[2]*0.3:.3f}\n")
                materials.append(f"Ks 0.5 0.5 0.5\n")
                materials.append(f"Ns 32\n\n")
            
            # 为化学键创建材质
            materials.append("newmtl bond\n")
            materials.append("Kd 0.7 0.7 0.7\n")
            materials.append("Ka 0.2 0.2 0.2\n")
            materials.append("Ks 0.5 0.5 0.5\n")
            materials.append("Ns 32\n\n")
            
            # 写入MTL文件
            mtl_file = output_file.replace('.obj', '.mtl')
            with open(mtl_file, 'w', encoding='utf-8') as f:
                f.writelines(materials)
            
            # 开始写入OBJ文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Pymatgen CIF to OBJ Converter\n")
                f.write(f"# 原子数量: {len(structure)}\n")
                f.write(f"# 化学键数量: {len(bonds)}\n")
                f.write(f"mtllib {os.path.basename(mtl_file)}\n\n")
                
                # 按元素分组处理原子
                for element in elements:
                    f.write(f"# {element} 原子\n")
                    f.write(f"usemtl {element}\n")
                    
                    element_faces = []
                    
                    for i, site in enumerate(structure):
                        if site.specie.symbol == element:
                            # 获取原子半径
                            radius = self.element_radii.get(element, 1.5) * 0.3  # 缩放因子
                            
                            # 创建球体
                            sphere_vertices, sphere_faces = self.create_sphere(
                                tuple(site.coords), radius, self.sphere_resolution
                            )
                            
                            # 添加顶点
                            for vertex in sphere_vertices:
                                f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
                            
                            # 记录面（需要加上顶点偏移）
                            for face in sphere_faces:
                                adjusted_face = tuple(idx + vertex_offset + 1 for idx in face)
                                element_faces.append(adjusted_face)
                            
                            vertex_offset += len(sphere_vertices)
                    
                    # 写入该元素的所有面
                    for face in element_faces:
                        f.write(f"f {face[0]} {face[1]} {face[2]}\n")
                    
                    f.write("\n")
                
                # 处理化学键
                if bonds:
                    f.write("# 化学键\n")
                    f.write("usemtl bond\n")
                    
                    bond_faces = []
                    
                    for bond in bonds:
                        i, j, distance = bond
                        start_pos = structure[i].coords
                        end_pos = structure[j].coords
                        
                        # 创建圆柱体
                        cylinder_vertices, cylinder_faces = self.create_cylinder(
                            tuple(start_pos), tuple(end_pos), 
                            self.bond_radius, self.cylinder_resolution
                        )
                        
                        # 添加顶点
                        for vertex in cylinder_vertices:
                            f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
                        
                        # 记录面
                        for face in cylinder_faces:
                            adjusted_face = tuple(idx + vertex_offset + 1 for idx in face)
                            bond_faces.append(adjusted_face)
                        
                        vertex_offset += len(cylinder_vertices)
                    
                    # 写入化学键的所有面
                    for face in bond_faces:
                        f.write(f"f {face[0]} {face[1]} {face[2]}\n")
            
            logger.success(f"Pymatgen转换成功: {output_file}")
            logger.info(f"原子数量: {len(structure)}")
            logger.info(f"化学键数量: {len(bonds)}")
            logger.info(f"顶点数量: {vertex_offset}")
            
            return True
            
        except Exception as e:
            logger.error(f"转换失败: {e}")
            return False

def test_pymatgen_converter():
    """测试pymatgen转换器"""
    if not PYMATGEN_AVAILABLE:
        logger.error("pymatgen库未安装，无法测试")
        return False
    
    try:
        converter = PymatgenConverter()
        
        # 测试文件
        test_file = "examples/NaCl.cif"
        if not os.path.exists(test_file):
            logger.error(f"测试文件不存在: {test_file}")
            return False
        
        # 读取CIF文件
        structure = converter.read_cif(test_file)
        
        # 转换为OBJ
        output_file = "test_pymatgen_nacl.obj"
        success = converter.convert_to_obj(structure, output_file)
        
        if success:
            logger.success("Pymatgen转换测试成功！")
            logger.info(f"原子数量: {len(structure)}")
            logger.info(f"元素类型: {[site.specie.symbol for site in structure]}")
            
            # 分析生成的OBJ文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"OBJ文件大小: {file_size} 字节")
                
                # 统计OBJ文件内容
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                    vertex_count = sum(1 for line in lines if line.startswith('v '))
                    face_count = sum(1 for line in lines if line.startswith('f '))
                    
                logger.info(f"顶点数: {vertex_count}")
                logger.info(f"面数: {face_count}")
            
            return True
        else:
            logger.error("Pymatgen转换测试失败")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("=== Pymatgen CIF to OBJ 转换器测试 ===")
    
    if not PYMATGEN_AVAILABLE:
        logger.error("请先安装pymatgen: pip install pymatgen")
        return
    
    # 测试转换器
    success = test_pymatgen_converter()
    
    if success:
        logger.info("\n=== Pymatgen转换器优势 ===")
        logger.info("1. Materials Project官方开发，权威性最高")
        logger.info("2. 被全球材料科学研究机构广泛使用")
        logger.info("3. 先进的CrystalNN算法精确识别化学键")
        logger.info("4. 完整的晶体学功能和数据库支持")
        logger.info("5. 持续更新和维护")
        logger.info("6. 与Materials Project数据库无缝集成")
        logger.info("7. 支持复杂的材料结构分析")
    else:
        logger.error("测试失败，请检查错误信息")

if __name__ == "__main__":
    main()