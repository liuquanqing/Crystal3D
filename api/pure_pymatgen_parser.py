#!/usr/bin/env python3
"""
纯Pymatgen CIF解析器 - 最靠谱的唯一方案
删除所有简化/备用解析器
"""

import json
import tempfile
import os
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class PurePymatgenParser:
    """纯pymatgen解析器 - 最靠谱的方案"""
    
    def __init__(self):
        try:
            from pymatgen.io.cif import CifParser
            from pymatgen.core.structure import Structure
            self.CifParser = CifParser
            self.Structure = Structure
            logger.info("Pymatgen loaded - reliable solution")
        except ImportError as e:
            logger.error("Pymatgen not available: {}".format(str(e)))
            raise ImportError("Must install pymatgen: pip install pymatgen")
    
    async def parse_cif_file(self, file: UploadFile) -> Dict[str, Any]:
        """使用pymatgen解析CIF文件 - 唯一方案"""
        
        # 保存临时文件 (二进制模式)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.cif', mode='wb') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        logger.info("Pymatgen parsing CIF: {}".format(file.filename))
        
        try:
            # 使用pymatgen CifParser
            parser = self.CifParser(tmp_file_path)
            structures = parser.parse_structures()
            
            if not structures:
                raise ValueError("CIF文件中没有找到结构数据")
            
            # 取第一个结构
            structure = list(structures.values())[0] if isinstance(structures, dict) else structures[0]
            
            # 转换为前端可用的格式
            structure_data = self._structure_to_dict(structure)
            
            logger.info("Pymatgen parsing success: {}, {} atoms".format(structure_data['formula'], structure_data['num_sites']))
            
            return {
                "success": True,
                "structure": structure_data,
                "metadata": {
                    "parser": "pymatgen",
                    "formula": structure_data["formula"],
                    "num_atoms": structure_data["num_sites"],
                    "density": structure_data.get("density", 0),
                    "volume": structure_data.get("volume", 0),
                    "space_group": getattr(structure, 'get_space_group_info', lambda: ['-', '-'])()[1] if hasattr(structure, 'get_space_group_info') else '-',
                    "source": "Crystal Toolkit ecosystem"
                }
            }
            
        except Exception as e:
            logger.error("Pymatgen parsing failed: {}".format(str(e)))
            raise HTTPException(status_code=500, detail="Pymatgen parsing failed: {}".format(str(e)))
            
        finally:
            # 清理临时文件
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

# 全局实例
pure_pymatgen_parser = PurePymatgenParser() 