#!/usr/bin/env python3
"""
测试多面体数据生成的脚本
"""

import requests
import os
import json

def test_polyhedra_generation():
    """测试多面体数据生成"""
    
    # 检查是否有示例CIF文件
    cif_files = [
        "examples/simple_crystal.cif",
        "examples/LiCoO2.cif",
        "test.cif"
    ]
    
    cif_file = None
    for file_path in cif_files:
        if os.path.exists(file_path):
            cif_file = file_path
            break
    
    if not cif_file:
        print("❌ 没有找到测试CIF文件")
        # 创建一个简单的测试CIF文件
        cif_content = """data_test
_cell_length_a 5.0
_cell_length_b 5.0
_cell_length_c 5.0
_cell_angle_alpha 90.0
_cell_angle_beta 90.0
_cell_angle_gamma 90.0
_space_group_name_H-M_alt 'P 1'
loop_
_atom_site_label
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Na1 0.0 0.0 0.0
Cl1 0.5 0.5 0.5
"""
        with open("test_simple.cif", "w") as f:
            f.write(cif_content)
        cif_file = "test_simple.cif"
        print(f"✅ 创建了测试CIF文件: {cif_file}")
    
    print(f"📤 测试文件: {cif_file}")
    
    try:
        # 上传CIF文件到parse_cif端点
        with open(cif_file, 'rb') as f:
            files = {'file': (os.path.basename(cif_file), f, 'application/octet-stream')}
            
            print("🔬 发送CIF文件到服务器...")
            response = requests.post('http://localhost:8000/parse_cif', files=files, timeout=30)
            
            print(f"📥 服务器响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 解析成功")
                
                # 检查多面体数据
                if 'polyhedra' in result:
                    polyhedra = result['polyhedra']
                    print(f"🔍 多面体数据: {len(polyhedra)} 个多面体")
                    
                    if polyhedra:
                        print("✅ 找到多面体数据:")
                        for i, poly in enumerate(polyhedra):
                            print(f"  多面体 {i+1}: {poly.get('center_element', 'Unknown')} - {poly.get('geometry_type', 'Unknown')}")
                    else:
                        print("❌ 没有找到多面体数据")
                else:
                    print("❌ 响应中没有多面体字段")
                
                # 打印结构信息
                if 'structure' in result:
                    structure = result['structure']
                    print(f"📊 结构信息: {structure.get('formula', 'Unknown')}")
                    print(f"📊 原子数量: {len(structure.get('sites', []))}")
                
            else:
                print(f"❌ 服务器错误: {response.status_code}")
                print(f"错误内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_polyhedra_generation()