#!/usr/bin/env python3
import sys
from pathlib import Path
import numpy as np

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_coordinates():
    """调试坐标转换过程"""
    try:
        from converter.cif_parser import CIFParser
        from converter.obj_generator import OBJGenerator
        
        print("DEBUG: 调试坐标转换过程...")
        
        # 解析CIF
        parser = CIFParser()
        success = parser.parse_file("examples/simple_crystal.cif")
        
        if not success:
            print("ERROR: CIF解析失败")
            return
        
        print("SUCCESS: CIF解析成功")
        
        # 获取原子信息
        coords = parser.get_atomic_coordinates()
        symbols = parser.get_atomic_symbols()
        
        print(f"\nATOM INFO:")
        print(f"  原子数: {len(coords) if coords is not None else 0}")
        print(f"  符号: {symbols}")
        
        if coords is not None:
            print(f"\nORIGINAL COORDS:")
            for i, (coord, symbol) in enumerate(zip(coords, symbols)):
                print(f"  {i+1}: {symbol} @ ({coord[0]:.3f}, {coord[1]:.3f}, {coord[2]:.3f})")
            
            print(f"\nCOORD RANGES:")
            print(f"  X: {coords[:, 0].min():.3f} ~ {coords[:, 0].max():.3f}")
            print(f"  Y: {coords[:, 1].min():.3f} ~ {coords[:, 1].max():.3f}")
            print(f"  Z: {coords[:, 2].min():.3f} ~ {coords[:, 2].max():.3f}")
            
            # 测试缩放后的坐标
            scale_factor = 1.0
            scaled_coords = coords * scale_factor
            
            print(f"\nSCALED COORDS (scale={scale_factor}):")
            for i, (coord, symbol) in enumerate(zip(scaled_coords, symbols)):
                print(f"  {i+1}: {symbol} @ ({coord[0]:.3f}, {coord[1]:.3f}, {coord[2]:.3f})")
            
            # 检查是否所有坐标都相同
            unique_coords = np.unique(coords, axis=0)
            print(f"\nUNIQUE COORDS: {len(unique_coords)} (should be {len(coords)})")
            
            if len(unique_coords) < len(coords):
                print("WARNING: Found duplicate coordinates!")
                for i, unique_coord in enumerate(unique_coords):
                    print(f"  Unique {i+1}: ({unique_coord[0]:.3f}, {unique_coord[1]:.3f}, {unique_coord[2]:.3f})")
            
            # 检查晶格信息
            lattice_vectors = parser.get_lattice_vectors()
            if lattice_vectors is not None:
                print(f"\nLATTICE VECTORS:")
                for i, vector in enumerate(lattice_vectors):
                    print(f"  a{i+1}: ({vector[0]:.3f}, {vector[1]:.3f}, {vector[2]:.3f})")
            
            # 测试球体生成
            print(f"\nTEST SPHERE GENERATION...")
            obj_gen = OBJGenerator()
            obj_gen._reset_data()
            
            # 只为第一个原子生成球体来检查
            if len(coords) > 0:
                first_coord = scaled_coords[0]
                first_symbol = symbols[0]
                radius = obj_gen.ATOMIC_RADII.get(first_symbol, 1.0)
                
                print(f"  Atom: {first_symbol}")
                print(f"  Center: ({first_coord[0]:.3f}, {first_coord[1]:.3f}, {first_coord[2]:.3f})")
                print(f"  Radius: {radius:.3f}")
                
                obj_gen._generate_sphere(first_coord, radius, f"atom_{first_symbol}")
                
                print(f"  Generated vertices: {len(obj_gen.vertices)}")
                print(f"  First 5 vertices:")
                for i, vertex in enumerate(obj_gen.vertices[:5]):
                    print(f"    {i+1}: ({vertex[0]:.3f}, {vertex[1]:.3f}, {vertex[2]:.3f})")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_coordinates() 