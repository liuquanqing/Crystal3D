#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试材质颜色是否正确应用到USDZ文件中
"""

import os
import tempfile
import subprocess
from pathlib import Path
from converter.material_standardizer import MaterialStandardizer
from config.arkit_config import ARKitMaterialConfig

def create_test_obj_with_colors():
    """创建一个包含多种颜色的测试OBJ文件"""
    
    # 创建临时文件
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    obj_file = temp_dir / "test_multicolor.obj"
    mtl_file = temp_dir / "test_multicolor.mtl"
    
    # 创建OBJ文件 - 三个不同颜色的立方体
    obj_content = """
# Multi-color test object
mtllib test_multicolor.mtl

# 红色立方体 (O元素)
g oxygen_cube
usemtl O_MAT
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0

f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 5 1 4 8

# 紫色立方体 (Li元素)
g lithium_cube
usemtl Li_MAT
v  3.0 -1.0 -1.0
v  5.0 -1.0 -1.0
v  5.0  1.0 -1.0
v  3.0  1.0 -1.0
v  3.0 -1.0  1.0
v  5.0 -1.0  1.0
v  5.0  1.0  1.0
v  3.0  1.0  1.0

f 9 10 11 12
f 13 16 15 14
f 9 13 14 10
f 10 14 15 11
f 11 15 16 12
f 13 9 12 16

# 粉红色立方体 (Co元素)
g cobalt_cube
usemtl Co_MAT
v  7.0 -1.0 -1.0
v  9.0 -1.0 -1.0
v  9.0  1.0 -1.0
v  7.0  1.0 -1.0
v  7.0 -1.0  1.0
v  9.0 -1.0  1.0
v  9.0  1.0  1.0
v  7.0  1.0  1.0

f 17 18 19 20
f 21 24 23 22
f 17 21 22 18
f 18 22 23 19
f 19 23 24 20
f 21 17 20 24
"""
    
    # 创建MTL文件 - 使用正确的CPK颜色
    standardizer = MaterialStandardizer()
    
    # 获取标准颜色
    o_color = standardizer.get_standard_color('O')   # 红色
    li_color = standardizer.get_standard_color('Li') # 紫色
    co_color = standardizer.get_standard_color('Co') # 粉红色
    
    mtl_content = f"""
# Multi-color test materials
# 使用标准CPK颜色

newmtl O_MAT
# Element: O (氧) - 红色
Ka {o_color[0]:.3f} {o_color[1]:.3f} {o_color[2]:.3f}
Kd {o_color[0]:.3f} {o_color[1]:.3f} {o_color[2]:.3f}
Ks 0.1 0.1 0.1
Ns 10.0
Ni 1.0
d 1.0
illum 2

newmtl Li_MAT
# Element: Li (锂) - 紫色
Ka {li_color[0]:.3f} {li_color[1]:.3f} {li_color[2]:.3f}
Kd {li_color[0]:.3f} {li_color[1]:.3f} {li_color[2]:.3f}
Ks 0.1 0.1 0.1
Ns 10.0
Ni 1.0
d 1.0
illum 2

newmtl Co_MAT
# Element: Co (钴) - 粉红色
Ka {co_color[0]:.3f} {co_color[1]:.3f} {co_color[2]:.3f}
Kd {co_color[0]:.3f} {co_color[1]:.3f} {co_color[2]:.3f}
Ks 0.1 0.1 0.1
Ns 10.0
Ni 1.0
d 1.0
illum 2
"""
    
    # 写入文件
    with open(obj_file, 'w') as f:
        f.write(obj_content)
    
    with open(mtl_file, 'w') as f:
        f.write(mtl_content)
    
    print(f"✅ 创建测试文件:")
    print(f"   OBJ: {obj_file}")
    print(f"   MTL: {mtl_file}")
    print(f"   O颜色:  {o_color} (红色)")
    print(f"   Li颜色: {li_color} (紫色)")
    print(f"   Co颜色: {co_color} (粉红色)")
    
    return str(obj_file), str(mtl_file)

def convert_to_usdz(obj_file, output_file):
    """转换OBJ到USDZ"""
    try:
        cmd = ['usdzconvert', obj_file, output_file, '-v']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ USDZ转换成功: {output_file}")
            print(f"   文件大小: {os.path.getsize(output_file)/1024:.1f} KB")
            return True
        else:
            print(f"❌ USDZ转换失败:")
            print(f"   错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 转换异常: {e}")
        return False

def main():
    print("🎨 测试材质颜色应用")
    print("=" * 50)
    
    # 1. 创建测试文件
    print("\n1️⃣ 创建多色测试模型...")
    obj_file, mtl_file = create_test_obj_with_colors()
    
    # 2. 转换为USDZ
    print("\n2️⃣ 转换为USDZ...")
    usdz_file = "temp/test_multicolor.usdz"
    success = convert_to_usdz(obj_file, usdz_file)
    
    if success:
        print(f"\n🎯 测试完成！")
        print(f"   请在AR Quick Look中打开: {usdz_file}")
        print(f"   应该看到三个不同颜色的立方体:")
        print(f"   - 红色立方体 (氧元素)")
        print(f"   - 紫色立方体 (锂元素)")
        print(f"   - 粉红色立方体 (钴元素)")
    else:
        print("\n❌ 测试失败")

if __name__ == '__main__':
    main()