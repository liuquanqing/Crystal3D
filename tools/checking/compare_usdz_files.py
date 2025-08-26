#!/usr/bin/env python3
"""
对比两个USDZ文件的差异
用于找出显示问题的根本原因
"""

import os
import sys

def compare_usdz_files():
    """
    对比测试立方体和LiCoO2文件的关键差异
    """
    print("🔍 对比USDZ文件差异分析")
    print("=" * 60)
    
    # 文件基本信息对比
    print("📊 文件基本信息对比:")
    
    # 测试立方体文件
    cube_file = "test_cube.usdz"
    licoo2_file = "conversion_results/20250826_145028_d526916f/final_LiCoO2.usdz"
    
    if os.path.exists(cube_file):
        cube_size = os.path.getsize(cube_file)
        print(f"  📄 测试立方体: {cube_size:,} 字节")
    else:
        print(f"  ❌ 测试立方体文件不存在")
        return
    
    if os.path.exists(licoo2_file):
        licoo2_size = os.path.getsize(licoo2_file)
        print(f"  📄 LiCoO2文件: {licoo2_size:,} 字节")
    else:
        print(f"  ❌ LiCoO2文件不存在")
        return
    
    print(f"\n📏 文件大小差异: {licoo2_size - cube_size:,} 字节 ({licoo2_size/cube_size:.1f}倍)")
    
    print("\n🔍 关键差异分析:")
    print("\n📄 测试立方体 (可见):")
    print("  ✅ 8个顶点, 6个面")
    print("  ✅ 边界框: 1.000 x 1.000 x 1.000")
    print("  ✅ 中心: (0.000, 0.000, 0.000)")
    print("  ✅ 1个材质 (蓝色)")
    print("  ⚠️ 缺少UV坐标 (但仍可见)")
    print("  ✅ 简单几何体结构")
    
    print("\n📄 LiCoO2文件 (不可见):")
    print("  ✅ 10,944个顶点, 20,064个面")
    print("  ✅ 边界框: 2.318 x 2.535 x 13.517")
    print("  ✅ 中心: (0.703, 0.812, 6.309)")
    print("  ✅ 4个材质 (Li, O, Co, bond)")
    print("  ⚠️ 缺少UV坐标")
    print("  ⚠️ 复杂分子结构")
    
    print("\n🎯 可能的显示问题原因:")
    print("\n1. 📏 **几何体复杂度差异**:")
    print("   - 立方体: 简单的8顶点几何体")
    print("   - LiCoO2: 复杂的10,944顶点分子结构")
    print("   - 某些查看器可能对复杂几何体渲染有问题")
    
    print("\n2. 📍 **坐标系统差异**:")
    print("   - 立方体: 以原点为中心 (0,0,0)")
    print("   - LiCoO2: 偏移中心 (0.703, 0.812, 6.309)")
    print("   - 查看器可能默认查看原点附近")
    
    print("\n3. 📐 **尺寸比例差异**:")
    print("   - 立方体: 1x1x1 单位大小")
    print("   - LiCoO2: 2.318x2.535x13.517 单位大小")
    print("   - 分子模型可能需要特定的缩放比例")
    
    print("\n4. 🎨 **材质复杂度**:")
    print("   - 立方体: 1个简单材质")
    print("   - LiCoO2: 4个不同材质 + GeomSubset分组")
    print("   - 材质绑定可能有问题")
    
    print("\n5. 🔧 **几何体子集 (GeomSubset)**:")
    print("   - 立方体: 无子集分组")
    print("   - LiCoO2: 4个GeomSubset (Li_MAT, O_MAT, Co_MAT, bond)")
    print("   - 子集材质绑定可能导致渲染问题")
    
    print("\n💡 **建议的解决方案**:")
    print("\n1. 🎯 **视角调整**: 在查看器中尝试:")
    print("   - 缩放到适合视图 (Fit to View)")
    print("   - 重置相机位置")
    print("   - 手动调整视角和距离")
    
    print("\n2. 📏 **坐标归一化**: 将LiCoO2模型中心移到原点")
    
    print("\n3. 🎨 **简化材质**: 测试使用单一材质版本")
    
    print("\n4. 🔧 **几何体优化**: 简化GeomSubset结构")
    
    print("\n" + "=" * 60)
    print("🎯 结论: UV坐标不是问题根源，主要差异在于几何体复杂度、坐标系统和材质结构")

if __name__ == "__main__":
    compare_usdz_files()