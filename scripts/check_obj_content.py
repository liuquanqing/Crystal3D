#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def analyze_obj_file(obj_path):
    """分析OBJ文件内容"""
    if not os.path.exists(obj_path):
        print(f"❌ OBJ文件不存在: {obj_path}")
        return
    
    vertices = []
    faces = []
    materials = []
    
    print(f"📂 分析OBJ文件: {obj_path}")
    print(f"📊 文件大小: {os.path.getsize(obj_path)} bytes")
    
    with open(obj_path, 'r') as f:
        line_count = 0
        for line in f:
            line_count += 1
            line = line.strip()
            
            if line.startswith('v '):
                # 顶点
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append((x, y, z))
                    
            elif line.startswith('f '):
                # 面
                faces.append(line)
                
            elif line.startswith('usemtl '):
                # 材质
                materials.append(line.split()[1])
                
            # 显示前20行
            if line_count <= 20:
                print(f"  {line_count:2d}: {line}")
    
    print(f"\n📈 统计:")
    print(f"  总行数: {line_count}")
    print(f"  顶点数: {len(vertices)}")
    print(f"  面数: {len(faces)}")
    print(f"  材质数: {len(set(materials))}")
    
    if vertices:
        print(f"\n🎯 顶点范围:")
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        
        print(f"  X: {min(xs):.3f} ~ {max(xs):.3f}")
        print(f"  Y: {min(ys):.3f} ~ {max(ys):.3f}")  
        print(f"  Z: {min(zs):.3f} ~ {max(zs):.3f}")
        
        print(f"\n🔍 前5个顶点:")
        for i, v in enumerate(vertices[:5]):
            print(f"  {i+1}: ({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})")
    
    if faces:
        print(f"\n🔍 前5个面:")
        for i, f in enumerate(faces[:5]):
            print(f"  {i+1}: {f}")
    
    return len(vertices), len(faces)

def main():
    # 先运行一次转换生成OBJ文件
    try:
        from converter.main_converter import CIFToUSDZConverter
        
        converter = CIFToUSDZConverter()
        result = converter.convert("examples/simple_crystal.cif", "test_obj.usdz", clean_temp=False)
        
        if result['success']:
            obj_file = result['metadata']['obj_file']
            print(f"✅ 转换成功，分析OBJ文件...")
            analyze_obj_file(obj_file)
        else:
            print(f"❌ 转换失败: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 