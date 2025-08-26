#!/usr/bin/env python3
"""
调试CIF坐标解析问题
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from converter.cif_parser import CIFParser
import numpy as np

def debug_cif_parsing():
    """调试CIF解析"""
    print("🔍 调试CIF坐标解析")
    print("=" * 40)
    
    # 测试文件
    cif_file = "examples/NaCl.cif"
    
    if not Path(cif_file).exists():
        print(f"❌ CIF文件不存在: {cif_file}")
        return
    
    # 解析CIF
    parser = CIFParser()
    success = parser.parse_file(cif_file)
    
    if not success:
        print("❌ CIF解析失败")
        return
    
    print(f"✅ CIF解析成功")
    print(f"📊 元数据: {parser.metadata}")
    
    # 获取坐标
    coords = parser.get_atomic_coordinates()
    symbols = parser.get_atomic_symbols()
    
    if coords is None:
        print("❌ 无法获取原子坐标")
        return
    
    if symbols is None:
        print("❌ 无法获取原子符号")
        return
    
    print(f"\n📍 原子信息:")
    print(f"   原子数量: {len(coords)}")
    print(f"   坐标形状: {coords.shape}")
    print(f"   符号列表: {symbols}")
    
    print(f"\n🎯 前5个原子坐标:")
    for i in range(min(5, len(coords))):
        print(f"   {i+1}: {symbols[i]} at ({coords[i][0]:.3f}, {coords[i][1]:.3f}, {coords[i][2]:.3f})")
    
    print(f"\n📈 坐标范围:")
    print(f"   X: {coords[:, 0].min():.3f} ~ {coords[:, 0].max():.3f}")
    print(f"   Y: {coords[:, 1].min():.3f} ~ {coords[:, 1].max():.3f}")
    print(f"   Z: {coords[:, 2].min():.3f} ~ {coords[:, 2].max():.3f}")
    
    # 检查是否有重复坐标
    unique_coords = np.unique(coords, axis=0)
    print(f"\n🔍 坐标分析:")
    print(f"   总坐标数: {len(coords)}")
    print(f"   唯一坐标数: {len(unique_coords)}")
    
    if len(unique_coords) < len(coords):
        print("⚠️ 发现重复坐标!")
        # 找出重复的坐标
        for i, coord in enumerate(coords):
            duplicates = []
            for j, other_coord in enumerate(coords):
                if i != j and np.allclose(coord, other_coord, atol=1e-6):
                    duplicates.append(j)
            if duplicates:
                print(f"   坐标 {i} ({symbols[i]}) 与 {duplicates} 重复")
    else:
        print("✅ 所有坐标都是唯一的")
    
    # 测试球体生成
    print(f"\n🔮 测试球体生成:")
    from converter.obj_generator import OBJGenerator
    
    obj_gen = OBJGenerator(sphere_resolution=5)  # 低分辨率测试
    
    # 手动生成一个球体
    test_center = np.array([1.0, 2.0, 3.0])
    test_radius = 0.5
    
    print(f"   测试中心: {test_center}")
    print(f"   测试半径: {test_radius}")
    
    # 重置数据
    obj_gen._reset_data()
    
    # 生成球体
    obj_gen._generate_sphere(test_center, test_radius, "test_material")
    
    print(f"   生成顶点数: {len(obj_gen.vertices)}")
    print(f"   前5个顶点:")
    for i in range(min(5, len(obj_gen.vertices))):
        v = obj_gen.vertices[i]
        print(f"     {i+1}: ({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})")
    
    # 检查顶点是否都相同
    if len(obj_gen.vertices) > 1:
        first_vertex = obj_gen.vertices[0]
        all_same = all(np.allclose(v, first_vertex, atol=1e-6) for v in obj_gen.vertices)
        if all_same:
            print("❌ 所有顶点都相同！球体生成有问题")
        else:
            print("✅ 顶点坐标正常")
            
        # 检查顶点分布
        vertices_array = np.array(obj_gen.vertices)
        print(f"   顶点范围:")
        print(f"     X: {vertices_array[:, 0].min():.3f} ~ {vertices_array[:, 0].max():.3f}")
        print(f"     Y: {vertices_array[:, 1].min():.3f} ~ {vertices_array[:, 1].max():.3f}")
        print(f"     Z: {vertices_array[:, 2].min():.3f} ~ {vertices_array[:, 2].max():.3f}")
        
        # 检查是否有重复顶点
        unique_vertices = np.unique(vertices_array, axis=0)
        print(f"   唯一顶点数: {len(unique_vertices)} / {len(obj_gen.vertices)}")
        
        if len(unique_vertices) < len(obj_gen.vertices):
            print("⚠️ 发现重复顶点！")
        
        # 检查距离中心的距离
        distances = np.linalg.norm(vertices_array - test_center, axis=1)
        print(f"   距离中心范围: {distances.min():.3f} ~ {distances.max():.3f} (期望: {test_radius:.3f})")
        
        if not np.allclose(distances, test_radius, atol=1e-3):
            print("❌ 顶点距离中心不正确！")
        else:
            print("✅ 顶点距离中心正确")

if __name__ == "__main__":
    debug_cif_parsing()