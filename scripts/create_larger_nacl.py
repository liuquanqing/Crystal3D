#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
import os

def create_larger_nacl_structures():
    """创建不同大小的NaCl超胞结构"""
    
    # 读取原始NaCl结构
    original_structure = Structure.from_file('examples/NaCl.cif')
    print(f"原始结构: {original_structure.formula} - {len(original_structure)} 原子")
    
    # 创建2x2x2超胞
    supercell_2x2x2 = original_structure.make_supercell([2, 2, 2])
    print(f"2x2x2超胞: {supercell_2x2x2.formula} - {len(supercell_2x2x2)} 原子")
    
    # 创建3x3x3超胞
    supercell_3x3x3 = original_structure.make_supercell([3, 3, 3])
    print(f"3x3x3超胞: {supercell_3x3x3.formula} - {len(supercell_3x3x3)} 原子")
    
    # 保存不同大小的CIF文件
    structures = {
        'NaCl_2x2x2.cif': supercell_2x2x2,
        'NaCl_3x3x3.cif': supercell_3x3x3
    }
    
    for filename, structure in structures.items():
        writer = CifWriter(structure)
        writer.write_file(filename)
        print(f"已保存: {filename}")
    
    return structures

if __name__ == "__main__":
    create_larger_nacl_structures()