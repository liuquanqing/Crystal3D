#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

def analyze_obj_file(obj_path):
    """分析OBJ文件内容"""
    
    with open(obj_path, 'r') as f:
        content = f.read()
    
    # 统计基本信息
    vertices = len(re.findall(r'^v ', content, re.MULTILINE))
    faces = len(re.findall(r'^f ', content, re.MULTILINE))
    groups = re.findall(r'^g (.+)', content, re.MULTILINE)
    materials = re.findall(r'^usemtl (.+)', content, re.MULTILINE)
    
    print(f"=== OBJ文件分析: {obj_path} ===")
    print(f"顶点数: {vertices}")
    print(f"面数: {faces}")
    print(f"组数: {len(groups)}")
    print(f"材质数: {len(materials)}")
    print(f"文件大小: {len(content)} 字符")
    
    print(f"\n=== 前20个组 ===")
    for i, group in enumerate(groups[:20]):
        print(f"{i+1:2d}. {group}")
    if len(groups) > 20:
        print(f"... 还有{len(groups)-20}个组")
    
    print(f"\n=== 前10个材质 ===")
    unique_materials = list(set(materials))
    for i, material in enumerate(unique_materials[:10]):
        print(f"{i+1:2d}. {material}")
    if len(unique_materials) > 10:
        print(f"... 还有{len(unique_materials)-10}个材质")
    
    # 分析原子类型
    atom_groups = [g for g in groups if '_Atom' in g]
    bond_groups = [g for g in groups if '_Bond' in g]
    
    print(f"\n=== 原子和键分析 ===")
    print(f"原子组数: {len(atom_groups)}")
    print(f"键组数: {len(bond_groups)}")
    
    # 统计不同原子类型
    atom_types = {}
    for group in atom_groups:
        atom_type = group.split('_')[0]
        atom_types[atom_type] = atom_types.get(atom_type, 0) + 1
    
    print(f"\n=== 原子类型统计 ===")
    for atom_type, count in atom_types.items():
        print(f"{atom_type}: {count}个")
    
    return {
        'vertices': vertices,
        'faces': faces,
        'groups': len(groups),
        'materials': len(unique_materials),
        'atom_groups': len(atom_groups),
        'bond_groups': len(bond_groups),
        'atom_types': atom_types
    }

if __name__ == "__main__":
    # 查找当前目录下的OBJ文件进行分析
    import glob
    obj_files = glob.glob('*.obj')
    
    if obj_files:
        for obj_file in obj_files:
            print(f"=== 分析OBJ文件: {obj_file} ===")
            analyze_obj_file(obj_file)
            print("\n" + "="*60)
    else:
        print("当前目录下没有找到OBJ文件")