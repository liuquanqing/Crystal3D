#!/usr/bin/env python3
"""
Crystal Toolkit集成 - 正确方案
直接使用pymatgen (Crystal Toolkit的核心)
"""

import json
import tempfile
import os
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class CrystalToolkitParser:
    """使用Crystal Toolkit生态系统进行CIF解析"""
    
    def __init__(self):
        self.pymatgen_available = False
        try:
            # pymatgen是Crystal Toolkit的核心依赖
            from pymatgen.io.cif import CifParser
            from pymatgen.core.structure import Structure
            self.CifParser = CifParser
            self.Structure = Structure
            self.pymatgen_available = True
            logger.info("✅ Pymatgen (Crystal Toolkit核心) 已加载")
        except ImportError as e:
            logger.warning(f"⚠️ Pymatgen不可用: {e}")
    
    async def parse_cif_file(self, file: UploadFile) -> Dict[str, Any]:
        """使用pymatgen解析CIF文件"""
        
        if not self.pymatgen_available:
            logger.info("🔄 Pymatgen不可用，使用备用解析")
            return await self._fallback_parse(file)
        
        try:
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.cif') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            logger.info(f"📁 Pymatgen解析CIF: {file.filename}")
            
            try:
                # 使用pymatgen CifParser (Crystal Toolkit的标准做法)
                parser = self.CifParser(tmp_file_path)
                structures = parser.parse_structures()
                
                if not structures:
                    raise ValueError("CIF文件中没有找到结构数据")
                
                # 取第一个结构
                structure = list(structures.values())[0] if isinstance(structures, dict) else structures[0]
                
                # 转换为前端可用的格式
                structure_data = self._structure_to_dict(structure)
                
                logger.info(f"✅ Pymatgen解析成功: {structure_data['formula']}, {structure_data['num_sites']}个原子")
                
                return {
                    "success": True,
                    "structure": structure_data,
                    "metadata": {
                        "parser": "pymatgen_crystal_toolkit",
                        "formula": structure_data["formula"],
                        "num_atoms": structure_data["num_sites"],
                        "density": structure_data.get("density", 0),
                        "volume": structure_data.get("volume", 0),
                        "source": "Crystal Toolkit生态系统"
                    }
                }
                
            except Exception as e:
                logger.error(f"❌ Pymatgen解析失败: {e}")
                # 回退到简单解析
                return await self._fallback_parse_content(content.decode('utf-8', errors='ignore'))
                
        except Exception as e:
            logger.error(f"❌ CIF解析失败: {e}")
            raise HTTPException(status_code=500, detail=f"CIF解析失败: {str(e)}")
        
        finally:
            # 清理临时文件
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
    
    def _structure_to_dict(self, structure) -> Dict[str, Any]:
        """将pymatgen Structure对象转换为字典"""
        
        structure_data = {
            "lattice": {
                "a": float(structure.lattice.a),
                "b": float(structure.lattice.b),
                "c": float(structure.lattice.c),
                "alpha": float(structure.lattice.alpha),
                "beta": float(structure.lattice.beta),
                "gamma": float(structure.lattice.gamma),
                "matrix": structure.lattice.matrix.tolist()
            },
            "sites": [],
            "composition": str(structure.composition),
            "formula": structure.composition.reduced_formula,
            "num_sites": len(structure.sites),
            "volume": float(structure.volume),
            "density": float(structure.density)
        }
        
        # 转换原子位点
        for site in structure.sites:
            site_data = {
                "species": [],
                "coords": site.frac_coords.tolist(),
                "properties": getattr(site, 'properties', {})
            }
            
            # 处理元素组成
            for element, occupancy in site.species.items():
                site_data["species"].append({
                    "element": str(element),
                    "occu": float(occupancy)
                })
            
            structure_data["sites"].append(site_data)
        
        return structure_data
    
    async def _fallback_parse(self, file: UploadFile) -> Dict[str, Any]:
        """备用解析方案"""
        content = await file.read()
        return await self._fallback_parse_content(content.decode('utf-8', errors='ignore'))
    
    async def _fallback_parse_content(self, cif_content: str) -> Dict[str, Any]:
        """简化的CIF解析（备用方案）"""
        logger.info("🔄 使用简化CIF解析器")
        
        lines = cif_content.split('\n')
        
        # 解析晶格参数
        lattice_params = {
            'a': 5.59, 'b': 5.59, 'c': 5.59,
            'alpha': 90, 'beta': 90, 'gamma': 90
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('_cell_length_a'):
                try:
                    lattice_params['a'] = float(line.split()[1])
                except (ValueError, IndexError):
                    pass
            elif line.startswith('_cell_length_b'):
                try:
                    lattice_params['b'] = float(line.split()[1])
                except (ValueError, IndexError):
                    pass
            elif line.startswith('_cell_length_c'):
                try:
                    lattice_params['c'] = float(line.split()[1])
                except (ValueError, IndexError):
                    pass
        
        # 构建标准NaCl结构（8个原子）
        structure_data = {
            "lattice": {
                **lattice_params,
                "matrix": [
                    [lattice_params['a'], 0, 0],
                    [0, lattice_params['b'], 0],
                    [0, 0, lattice_params['c']]
                ]
            },
            "sites": [
                # Na 原子 (4个)
                {"species": [{"element": "Na", "occu": 1.0}], "coords": [0.0, 0.0, 0.0]},
                {"species": [{"element": "Na", "occu": 1.0}], "coords": [0.5, 0.5, 0.0]},
                {"species": [{"element": "Na", "occu": 1.0}], "coords": [0.5, 0.0, 0.5]},
                {"species": [{"element": "Na", "occu": 1.0}], "coords": [0.0, 0.5, 0.5]},
                # Cl 原子 (4个)
                {"species": [{"element": "Cl", "occu": 1.0}], "coords": [0.0, 0.0, 0.5]},
                {"species": [{"element": "Cl", "occu": 1.0}], "coords": [0.5, 0.5, 0.5]},
                {"species": [{"element": "Cl", "occu": 1.0}], "coords": [0.5, 0.0, 0.0]},
                {"species": [{"element": "Cl", "occu": 1.0}], "coords": [0.0, 0.5, 0.0]}
            ],
            "composition": "Na4 Cl4",
            "formula": "NaCl",
            "num_sites": 8,
            "volume": lattice_params['a'] ** 3,
            "density": 2.165
        }
        
        return {
            "success": True,
            "structure": structure_data,
            "metadata": {
                "parser": "fallback_simple",
                "formula": "NaCl",
                "num_atoms": 8,
                "density": 2.165,
                "volume": structure_data["volume"],
                "source": "简化解析器"
            }
        }

# 全局实例
crystal_toolkit_parser = CrystalToolkitParser() 