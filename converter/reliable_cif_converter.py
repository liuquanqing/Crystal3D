#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可靠的CIF转换器
集成官方推荐的转换方案，替代Jmol和自制转换器

优先级顺序:
1. Pymatgen (Materials Project官方，最权威)
2. ASE (科学计算标准库)
3. 内置生成器 (仅作为最后备用)
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 尝试导入所有可用的转换器
try:
    from pymatgen_converter import PymatgenConverter
    PYMATGEN_AVAILABLE = True
except ImportError:
    PYMATGEN_AVAILABLE = False
    logger.warning("Pymatgen转换器不可用，请安装: pip install pymatgen")

try:
    from ase_converter import ASEConverter
    ASE_AVAILABLE = True
except ImportError:
    ASE_AVAILABLE = False
    logger.warning("ASE转换器不可用，请安装: pip install ase")

try:
    from .obj_generator import OBJGenerator
    from .cif_parser import CIFParser
    BUILTIN_AVAILABLE = True
except ImportError:
    BUILTIN_AVAILABLE = False
    logger.warning("内置转换器不可用")


class ReliableCIFConverter:
    """可靠的CIF转换器"""
    
    def __init__(self, sphere_resolution: int = 20, bond_cylinder_resolution: int = 8):
        self.sphere_resolution = sphere_resolution
        self.bond_cylinder_resolution = bond_cylinder_resolution
        self.converters = self._initialize_converters()
        
        if not self.converters:
            raise RuntimeError("没有可用的转换器，请安装pymatgen或ASE库")
        
        logger.info(f"可用转换器: {list(self.converters.keys())}")
    
    def _initialize_converters(self) -> Dict[str, Any]:
        """初始化可用的转换器"""
        converters = {}
        
        # 按优先级顺序初始化转换器
        if PYMATGEN_AVAILABLE:
            try:
                converters['pymatgen'] = PymatgenConverter()
                logger.info("✓ Pymatgen转换器已加载 (最高优先级)")
            except Exception as e:
                logger.error(f"Pymatgen转换器初始化失败: {e}")
        
        if ASE_AVAILABLE:
            try:
                converters['ase'] = ASEConverter()
                logger.info("✓ ASE转换器已加载")
            except Exception as e:
                logger.error(f"ASE转换器初始化失败: {e}")
        
        if BUILTIN_AVAILABLE:
            try:
                converters['builtin'] = {
                    'parser': CIFParser(),
                    'generator': OBJGenerator(self.sphere_resolution, self.bond_cylinder_resolution)
                }
                logger.info("✓ 内置转换器已加载 (备用)")
            except Exception as e:
                logger.error(f"内置转换器初始化失败: {e}")
        
        return converters
    
    def convert_cif_to_obj(self, cif_file: str, obj_file: str, 
                          preferred_converter: Optional[str] = None,
                          include_bonds: bool = True,
                          scale_factor: float = 1.0) -> Dict[str, Any]:
        """转换CIF文件到OBJ文件
        
        Args:
            cif_file: 输入的CIF文件路径
            obj_file: 输出的OBJ文件路径
            preferred_converter: 首选转换器 ('pymatgen', 'ase', 'builtin')
            include_bonds: 是否包含化学键
            scale_factor: 缩放因子
        
        Returns:
            转换结果字典
        """
        result = {
            'success': False,
            'converter_used': None,
            'error': None,
            'atoms': 0,
            'bonds': 0,
            'vertices': 0,
            'faces': 0,
            'file_size': 0,
            'warnings': []
        }
        
        # 检查输入文件
        if not os.path.exists(cif_file):
            result['error'] = f"CIF文件不存在: {cif_file}"
            return result
        
        # 确定转换器尝试顺序
        converter_order = self._get_converter_order(preferred_converter)
        
        # 依次尝试转换器
        for converter_name in converter_order:
            if converter_name not in self.converters:
                continue
            
            logger.info(f"尝试使用 {converter_name} 转换器...")
            
            try:
                success = self._try_converter(
                    converter_name, cif_file, obj_file, 
                    include_bonds, scale_factor, result
                )
                
                if success:
                    result['success'] = True
                    result['converter_used'] = converter_name
                    
                    # 获取文件大小
                    if os.path.exists(obj_file):
                        result['file_size'] = os.path.getsize(obj_file)
                    
                    logger.success(f"转换成功！使用了 {converter_name} 转换器")
                    logger.info(f"输出文件: {obj_file} ({result['file_size']} 字节)")
                    
                    # 添加Blender导入建议
                    if converter_name in ['pymatgen', 'ase']:
                        result['warnings'].append("建议在Blender中导入时选择'Keep Vert Order'选项")
                        result['warnings'].append("如果原子显示不完整，请检查材质设置")
                    
                    return result
                
            except Exception as e:
                error_msg = f"{converter_name} 转换器失败: {str(e)}"
                logger.warning(error_msg)
                result['warnings'].append(error_msg)
                continue
        
        # 所有转换器都失败了
        result['error'] = "所有可用的转换器都失败了"
        logger.error(result['error'])
        
        return result
    
    def _get_converter_order(self, preferred: Optional[str]) -> list:
        """获取转换器尝试顺序"""
        # 默认优先级顺序
        default_order = ['pymatgen', 'ase', 'builtin']
        
        if preferred and preferred in self.converters:
            # 将首选转换器放在第一位
            order = [preferred]
            order.extend([c for c in default_order if c != preferred and c in self.converters])
            return order
        else:
            # 使用默认顺序
            return [c for c in default_order if c in self.converters]
    
    def _try_converter(self, converter_name: str, cif_file: str, obj_file: str,
                      include_bonds: bool, scale_factor: float, result: Dict) -> bool:
        """尝试使用指定的转换器"""
        converter = self.converters[converter_name]
        
        if converter_name == 'pymatgen':
            return self._try_pymatgen(converter, cif_file, obj_file, result)
        elif converter_name == 'ase':
            return self._try_ase(converter, cif_file, obj_file, result)
        elif converter_name == 'builtin':
            return self._try_builtin(converter, cif_file, obj_file, include_bonds, scale_factor, result)
        else:
            return False
    
    def _try_pymatgen(self, converter, cif_file: str, obj_file: str, result: Dict) -> bool:
        """尝试Pymatgen转换器"""
        structure = converter.read_cif(cif_file)
        success = converter.convert_to_obj(structure, obj_file)
        
        if success:
            result['atoms'] = len(structure)
            bonds = converter.get_bonds(structure)
            result['bonds'] = len(bonds)
            
            # 分析OBJ文件获取顶点和面数
            self._analyze_obj_file(obj_file, result)
        
        return success
    
    def _try_ase(self, converter, cif_file: str, obj_file: str, result: Dict) -> bool:
        """尝试ASE转换器"""
        atoms = converter.read_cif(cif_file)
        success = converter.convert_to_obj(atoms, obj_file)
        
        if success:
            result['atoms'] = len(atoms)
            bonds = converter.get_bonds(atoms)
            result['bonds'] = len(bonds)
            
            # 分析OBJ文件获取顶点和面数
            self._analyze_obj_file(obj_file, result)
        
        return success
    
    def _try_builtin(self, converter, cif_file: str, obj_file: str,
                    include_bonds: bool, scale_factor: float, result: Dict) -> bool:
        """尝试内置转换器"""
        parser = converter['parser']
        generator = converter['generator']
        
        # 解析CIF文件
        if not parser.parse_file(cif_file):
            return False
        
        # 生成OBJ文件
        success = generator.generate_obj_from_cif(
            parser, obj_file, include_bonds=include_bonds, scale_factor=scale_factor
        )
        
        if success:
            result['atoms'] = parser.metadata.get('num_atoms', 0)
            result['vertices'] = len(generator.vertices)
            result['faces'] = len(generator.faces)
            # 内置转换器的化学键数量需要从生成器获取
            result['bonds'] = len(getattr(generator, 'bonds', []))
        
        return success
    
    def _analyze_obj_file(self, obj_file: str, result: Dict):
        """分析OBJ文件获取统计信息"""
        try:
            vertices = 0
            faces = 0
            
            with open(obj_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('v '):
                        vertices += 1
                    elif line.startswith('f '):
                        faces += 1
            
            result['vertices'] = vertices
            result['faces'] = faces
            
        except Exception as e:
            logger.warning(f"分析OBJ文件失败: {e}")
    
    def get_converter_info(self) -> Dict[str, Dict]:
        """获取转换器信息"""
        info = {}
        
        for name in self.converters.keys():
            if name == 'pymatgen':
                info[name] = {
                    'name': 'Pymatgen (Materials Project)',
                    'description': 'Materials Project官方开发，权威性最高',
                    'advantages': ['全球科研机构广泛使用', 'CrystalNN算法精确识别化学键', '与Materials Project数据库集成'],
                    'recommended': True
                }
            elif name == 'ase':
                info[name] = {
                    'name': 'ASE (Atomic Simulation Environment)',
                    'description': '科学计算领域标准库，可靠性高',
                    'advantages': ['正确处理晶体结构', '精确计算化学键', '活跃的开发社区'],
                    'recommended': True
                }
            elif name == 'builtin':
                info[name] = {
                    'name': '内置生成器',
                    'description': '自开发的备用转换器',
                    'advantages': ['无需额外依赖', '快速转换'],
                    'recommended': False
                }
        
        return info
    
    def is_available(self) -> bool:
        """检查转换器是否可用"""
        return len(self.converters) > 0
    
    def get_conversion_info(self) -> Dict[str, Any]:
        """获取转换信息"""
        return {
            'available_converters': list(self.converters.keys()),
            'recommended_converter': 'pymatgen' if 'pymatgen' in self.converters else 'ase' if 'ase' in self.converters else 'builtin',
            'converter_info': self.get_converter_info(),
            'blender_tips': [
                "在Blender中导入时选择'Keep Vert Order'选项",
                "检查材质设置确保所有原子正确显示",
                "如果原子数量不对，检查OBJ文件的顶点和面的索引"
            ],
            'professional_software': ['VESTA', 'PyMOL', 'Mercury', 'ChemCraft']
        }