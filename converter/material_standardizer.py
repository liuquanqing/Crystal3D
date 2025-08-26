#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
材质标准化模块
统一内置转换器和Jmol转换器的材质处理逻辑
基于Crystal Toolkit的CPK颜色标准
"""

import os
import re
from typing import Dict, Tuple, Optional, List
from loguru import logger


class MaterialStandardizer:
    """
    材质标准化器
    
    功能：
    1. 统一材质命名规范（语义化名称 + _MAT后缀）
    2. 标准化CPK颜色方案
    3. 提供材质转换和映射功能
    4. 支持向后兼容
    """
    
    # Crystal Toolkit/Materials Project标准CPK颜色 (RGB 0-1范围)
    STANDARD_CPK_COLORS = {
        'H': (1.0, 1.0, 1.0),          # 白色
        'He': (0.85, 1.0, 1.0),        # 淡青色
        'Li': (0.8, 0.5, 1.0),         # 淡紫色
        'Be': (0.76, 1.0, 0.0),        # 黄绿色
        'B': (1.0, 0.71, 0.71),        # 粉红色
        'C': (0.565, 0.565, 0.565),    # 灰色
        'N': (0.19, 0.31, 0.97),       # 蓝色
        'O': (1.0, 0.05, 0.05),        # 红色
        'F': (0.56, 0.88, 0.31),       # 绿色
        'Ne': (0.7, 0.89, 0.96),       # 淡蓝色
        'Na': (0.67, 0.36, 0.95),      # 紫色
        'Mg': (0.54, 1.0, 0.0),        # 亮绿色
        'Al': (0.75, 0.65, 0.65),      # 灰色
        'Si': (0.94, 0.78, 0.63),      # 黄褐色
        'P': (1.0, 0.5, 0.0),          # 橙色
        'S': (1.0, 1.0, 0.19),         # 黄色
        'Cl': (0.0, 1.0, 0.0),        # 绿色
        'Ar': (0.5, 0.82, 0.89),       # 淡蓝色
        'K': (0.56, 0.25, 0.83),       # 深紫色
        'Ca': (0.24, 1.0, 0.0),        # 绿色
        'Sc': (0.9, 0.9, 0.9),         # 浅灰色
        'Ti': (0.75, 0.76, 0.78),      # 银灰色
        'V': (0.65, 0.65, 0.67),       # 灰色
        'Cr': (0.54, 0.6, 0.78),       # 蓝灰色
        'Mn': (0.61, 0.48, 0.78),      # 紫灰色
        'Fe': (0.88, 0.4, 0.2),        # 橙红色
        'Co': (0.94, 0.56, 0.63),      # 粉红色
        'Ni': (0.31, 0.82, 0.31),      # 绿色
        'Cu': (0.78, 0.5, 0.2),        # 铜色
        'Zn': (0.49, 0.5, 0.69),       # 蓝灰色
        'Ga': (0.76, 0.56, 0.56),      # 粉色
        'Ge': (0.4, 0.56, 0.56),       # 青色
        'As': (0.74, 0.5, 0.89),       # 紫色
        'Se': (1.0, 0.63, 0.0),        # 橙色
        'Br': (0.65, 0.16, 0.16),      # 棕红色
        'Kr': (0.36, 0.72, 0.82),      # 蓝色
        'Rb': (0.44, 0.18, 0.69),      # 紫色
        'Sr': (0.0, 1.0, 0.15),        # 绿色
        'Y': (0.58, 1.0, 1.0),         # 青色
        'Zr': (0.58, 0.88, 0.88),      # 青色
        'Nb': (0.45, 0.76, 0.79),      # 蓝绿色
        'Mo': (0.33, 0.71, 0.71),      # 青色
        'Tc': (0.23, 0.62, 0.62),      # 青色
        'Ru': (0.14, 0.56, 0.56),      # 青色
        'Rh': (0.04, 0.49, 0.55),      # 青色
        'Pd': (0.0, 0.41, 0.52),       # 蓝色
        'Ag': (0.75, 0.75, 0.75),      # 银色
        'Cd': (1.0, 0.85, 0.56),       # 黄色
        'In': (0.65, 0.46, 0.45),      # 棕色
        'Sn': (0.4, 0.5, 0.5),         # 灰色
        'Sb': (0.62, 0.39, 0.71),      # 紫色
        'Te': (0.83, 0.48, 0.0),       # 橙色
        'I': (0.58, 0.0, 0.58),        # 紫色
        'Xe': (0.26, 0.62, 0.69),      # 蓝色
        'Cs': (0.34, 0.09, 0.56),      # 深紫色
        'Ba': (0.0, 0.79, 0.0),        # 绿色
        'La': (0.44, 0.83, 1.0),       # 淡蓝色
        'Ce': (1.0, 1.0, 0.78),        # 淡黄色
        'Pr': (0.85, 1.0, 0.78),       # 淡绿色
        'Nd': (0.78, 1.0, 0.78),       # 淡绿色
        'Pm': (0.64, 1.0, 0.78),       # 淡绿色
        'Sm': (0.56, 1.0, 0.78),       # 淡绿色
        'Eu': (0.38, 1.0, 0.78),       # 淡绿色
        'Gd': (0.27, 1.0, 0.78),       # 淡绿色
        'Tb': (0.19, 1.0, 0.78),       # 淡绿色
        'Dy': (0.12, 1.0, 0.78),       # 淡绿色
        'Ho': (0.0, 1.0, 0.61),        # 绿色
        'Er': (0.0, 0.9, 0.46),        # 绿色
        'Tm': (0.0, 0.83, 0.32),       # 绿色
        'Yb': (0.0, 0.75, 0.22),       # 绿色
        'Lu': (0.0, 0.67, 0.14),       # 绿色
        'Hf': (0.3, 0.76, 1.0),        # 淡蓝色
        'Ta': (0.3, 0.65, 1.0),        # 蓝色
        'W': (0.13, 0.58, 0.84),       # 蓝色
        'Re': (0.15, 0.49, 0.67),      # 蓝色
        'Os': (0.15, 0.4, 0.59),       # 蓝色
        'Ir': (0.09, 0.33, 0.53),      # 蓝色
        'Pt': (0.81, 0.82, 0.88),      # 银灰色
        'Au': (1.0, 0.82, 0.14),       # 金色
        'Hg': (0.72, 0.72, 0.82),      # 银色
        'Tl': (0.65, 0.33, 0.3),       # 棕色
        'Pb': (0.34, 0.35, 0.38),      # 深灰色
        'Bi': (0.62, 0.31, 0.71),      # 紫色
        'Po': (0.67, 0.36, 0.0),       # 棕色
        'At': (0.46, 0.31, 0.27),      # 棕色
        'Rn': (0.26, 0.51, 0.59),      # 蓝色
        'Fr': (0.26, 0.0, 0.4),        # 深紫色
        'Ra': (0.0, 0.49, 0.0),        # 绿色
        'Ac': (0.44, 0.67, 0.98),      # 淡蓝色
        'Th': (0.0, 0.73, 1.0),        # 青色
        'Pa': (0.0, 0.63, 1.0),        # 蓝色
        'U': (0.0, 0.56, 1.0),         # 蓝色
        'Np': (0.0, 0.5, 1.0),         # 蓝色
        'Pu': (0.0, 0.42, 1.0),        # 蓝色
        'Am': (0.33, 0.36, 0.95),      # 蓝紫色
        'Cm': (0.47, 0.36, 0.89),      # 紫色
        'Bk': (0.54, 0.31, 0.89),      # 紫色
        'Cf': (0.63, 0.21, 0.83),      # 紫色
        'Es': (0.7, 0.12, 0.83),       # 紫色
        'Fm': (0.7, 0.12, 0.73),       # 紫色
        'Md': (0.7, 0.05, 0.65),       # 紫色
        'No': (0.74, 0.05, 0.53),      # 紫色
        'Lr': (0.78, 0.0, 0.4),        # 紫红色
    }
    
    def __init__(self):
        """初始化材质标准化器"""
        self.color_tolerance = 0.05  # 颜色匹配容差
        self.preserve_original_colors = False  # 是否保留原始颜色
        
    def get_standard_material_name(self, element: str) -> str:
        """
        获取标准化的材质名称
        
        Args:
            element: 元素符号（如 'Na', 'Cl'）
            
        Returns:
            标准化材质名称（如 'Na_MAT', 'Cl_MAT'）
        """
        # 清理元素符号
        clean_element = self._clean_element_symbol(element)
        return f"{clean_element}_MAT"
    
    def get_standard_color(self, element: str) -> Tuple[float, float, float]:
        """
        获取元素的标准CPK颜色
        
        Args:
            element: 元素符号
            
        Returns:
            RGB颜色元组 (0-1范围)
        """
        clean_element = self._clean_element_symbol(element)
        return self.STANDARD_CPK_COLORS.get(clean_element, (0.5, 0.5, 0.5))
    
    def standardize_obj_materials(self, obj_path: str, mtl_path: str, preserve_colors: bool = False) -> bool:
        """
        标准化OBJ和MTL文件中的材质
        
        Args:
            obj_path: OBJ文件路径
            mtl_path: MTL文件路径
            preserve_colors: 是否保留原始颜色（不使用标准CPK颜色）
            
        Returns:
            是否成功标准化
        """
        # 临时设置颜色保留选项
        original_preserve_setting = self.preserve_original_colors
        self.preserve_original_colors = preserve_colors
        try:
            # 分析现有材质
            material_mapping = self._analyze_materials(obj_path, mtl_path)
            
            if not material_mapping:
                logger.warning("未找到需要标准化的材质")
                return True
            
            # 更新OBJ文件
            self._update_obj_file(obj_path, material_mapping)
            
            # 重写MTL文件
            self._rewrite_mtl_file(mtl_path, material_mapping)
            
            logger.info(f"材质标准化完成: {len(material_mapping)} 个材质")
            return True
            
        except Exception as e:
            logger.error(f"材质标准化失败: {e}")
            return False
        finally:
            # 恢复原始设置
            self.preserve_original_colors = original_preserve_setting
    
    def _analyze_materials(self, obj_path: str, mtl_path: str) -> Dict[str, Dict]:
        """
        分析OBJ和MTL文件中的材质，创建标准化映射
        
        Returns:
            材质映射字典: {old_name: {new_name: str, element: str, color: tuple}}
        """
        material_mapping = {}
        
        # 读取MTL文件中的材质和颜色
        mtl_materials = self._parse_mtl_file(mtl_path)
        
        for old_name, color in mtl_materials.items():
            # 尝试从材质名称推断元素
            element = self._infer_element_from_material(old_name, color)
            
            if element:
                new_name = self.get_standard_material_name(element)
                # 根据设置决定使用原始颜色还是标准颜色
                if self.preserve_original_colors:
                    final_color = color  # 保留原始颜色
                    logger.debug(f"保留原始颜色: {old_name} -> {new_name} ({element}) 颜色: {color}")
                else:
                    final_color = self.get_standard_color(element)  # 使用标准CPK颜色
                    logger.debug(f"使用标准颜色: {old_name} -> {new_name} ({element}) 颜色: {final_color}")
                
                material_mapping[old_name] = {
                    'new_name': new_name,
                    'element': element,
                    'color': final_color
                }
                
                logger.debug(f"材质映射: {old_name} -> {new_name} ({element})")
        
        return material_mapping
    
    def _parse_mtl_file(self, mtl_path: str) -> Dict[str, Tuple[float, float, float]]:
        """
        解析MTL文件，提取材质名称和颜色
        
        Returns:
            材质字典: {material_name: (r, g, b)}
        """
        materials = {}
        
        if not os.path.exists(mtl_path):
            return materials
        
        try:
            with open(mtl_path, 'r', encoding='utf-8') as f:
                current_material = None
                
                for line in f:
                    line = line.strip()
                    
                    if line.startswith('newmtl '):
                        current_material = line.split()[1]
                    elif line.startswith('Kd ') and current_material:
                        # 漫反射颜色
                        rgb_values = line.split()[1:4]
                        if len(rgb_values) == 3:
                            color = tuple(float(x) for x in rgb_values)
                            materials[current_material] = color
                            
        except Exception as e:
            logger.warning(f"解析MTL文件失败: {e}")
        
        return materials
    
    def _infer_element_from_material(self, material_name: str, color: Tuple[float, float, float]) -> Optional[str]:
        """
        从材质名称和颜色推断元素符号
        
        Args:
            material_name: 材质名称
            color: RGB颜色
            
        Returns:
            元素符号或None
        """
        # 方法1: 从材质名称直接提取元素
        element = self._extract_element_from_name(material_name)
        if element and element in self.STANDARD_CPK_COLORS:
            return element
        
        # 方法2: 通过颜色匹配推断元素
        element = self._match_element_by_color(color)
        if element:
            return element
        
        # 方法3: 从十六进制颜色名称推断（Jmol风格）
        element = self._infer_from_hex_name(material_name)
        if element:
            return element
        
        logger.warning(f"无法推断材质元素: {material_name} {color}")
        return None
    
    def _extract_element_from_name(self, material_name: str) -> Optional[str]:
        """
        从材质名称中提取元素符号
        
        支持格式:
        - atom_Na, atom_Cl (内置转换器格式)
        - Na, Cl (直接元素名)
        - Na_MAT, Cl_MAT (标准格式)
        """
        # 移除常见前缀和后缀
        name = material_name.replace('atom_', '').replace('_MAT', '')
        
        # 提取可能的元素符号
        match = re.match(r'^([A-Z][a-z]?)\d*[+-]*$', name)
        if match:
            element = match.group(1)
            if element in self.STANDARD_CPK_COLORS:
                return element
        
        return None
    
    def _match_element_by_color(self, color: Tuple[float, float, float]) -> Optional[str]:
        """
        通过颜色匹配找到最接近的元素
        """
        min_distance = float('inf')
        best_match = None
        
        for element, standard_color in self.STANDARD_CPK_COLORS.items():
            # 计算颜色距离
            distance = sum((c1 - c2) ** 2 for c1, c2 in zip(color, standard_color)) ** 0.5
            
            if distance < min_distance and distance < self.color_tolerance:
                min_distance = distance
                best_match = element
        
        return best_match
    
    def _infer_from_hex_name(self, material_name: str) -> Optional[str]:
        """
        从十六进制颜色名称推断元素（Jmol风格）
        
        例如: 'x909090' -> 'C' (碳的颜色)
        """
        # 检查是否是十六进制格式
        hex_match = re.match(r'^x?([0-9A-Fa-f]{6})$', material_name)
        if not hex_match:
            return None
        
        hex_color = hex_match.group(1)
        
        # 转换为RGB
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            
            return self._match_element_by_color((r, g, b))
            
        except ValueError:
            return None
    
    def _update_obj_file(self, obj_path: str, material_mapping: Dict[str, Dict]):
        """
        更新OBJ文件中的材质引用
        """
        if not material_mapping:
            return
        
        try:
            with open(obj_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            updated_lines = []
            for line in lines:
                if line.startswith('usemtl '):
                    old_material = line.split()[1]
                    if old_material in material_mapping:
                        new_material = material_mapping[old_material]['new_name']
                        line = f"usemtl {new_material}\n"
                        logger.debug(f"OBJ材质更新: {old_material} -> {new_material}")
                
                updated_lines.append(line)
            
            with open(obj_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
                
        except Exception as e:
            logger.error(f"更新OBJ文件失败: {e}")
            raise
    
    def _rewrite_mtl_file(self, mtl_path: str, material_mapping: Dict[str, Dict]):
        """
        重写MTL文件，使用标准化的材质名称和颜色
        """
        if not material_mapping:
            return
        
        try:
            with open(mtl_path, 'w', encoding='utf-8') as f:
                f.write("# Crystal Toolkit标准化材质文件\n")
                f.write("# 基于CPK颜色标准\n\n")
                
                for old_name, mapping in material_mapping.items():
                    new_name = mapping['new_name']
                    element = mapping['element']
                    color = mapping['color']
                    
                    f.write(f"newmtl {new_name}\n")
                    f.write(f"# Element: {element}\n")
                    f.write(f"Kd {color[0]:.6f} {color[1]:.6f} {color[2]:.6f}\n")
                    f.write(f"Ka {color[0]*0.2:.6f} {color[1]*0.2:.6f} {color[2]*0.2:.6f}\n")
                    f.write(f"Ks 0.5 0.5 0.5\n")
                    f.write(f"Ns 50\n")
                    f.write(f"d 1.0\n")  # 不透明度
                    f.write(f"\n")
                    
                logger.info(f"MTL文件重写完成: {len(material_mapping)} 个标准化材质")
                
        except Exception as e:
            logger.error(f"重写MTL文件失败: {e}")
            raise
    
    def _clean_element_symbol(self, element: str) -> str:
        """
        清理元素符号，移除数字、电荷等
        
        Args:
            element: 原始元素符号
            
        Returns:
            清理后的元素符号
        """
        # 移除数字、+、-、空格等
        clean = re.sub(r'[0-9+\-\s]', '', element)
        
        # 确保首字母大写，其余小写
        if clean:
            clean = clean[0].upper() + clean[1:].lower()
        
        return clean
    
    def create_material_mapping_report(self, obj_path: str, mtl_path: str) -> str:
        """
        创建材质映射报告
        
        Returns:
            报告文本
        """
        material_mapping = self._analyze_materials(obj_path, mtl_path)
        
        report = ["# 材质标准化报告\n"]
        report.append(f"文件: {obj_path}\n")
        report.append(f"时间: {__import__('datetime').datetime.now()}\n\n")
        
        if not material_mapping:
            report.append("未找到需要标准化的材质\n")
            return ''.join(report)
        
        report.append(f"发现 {len(material_mapping)} 个材质需要标准化:\n\n")
        
        for old_name, mapping in material_mapping.items():
            element = mapping['element']
            new_name = mapping['new_name']
            color = mapping['color']
            
            report.append(f"- {old_name} -> {new_name}\n")
            report.append(f"  元素: {element}\n")
            report.append(f"  颜色: RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f})\n\n")
        
        return ''.join(report)


# 全局实例
material_standardizer = MaterialStandardizer()