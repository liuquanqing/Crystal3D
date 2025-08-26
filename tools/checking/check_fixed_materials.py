#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pxr import Usd, UsdShade

def check_usdz_materials(usdz_path):
    """检查USDZ文件中的材质属性"""
    try:
        stage = Usd.Stage.Open(usdz_path)
        if not stage:
            print(f"无法打开USDZ文件: {usdz_path}")
            return
        
        print(f"检查USDZ文件: {usdz_path}")
        print("=" * 50)
        
        # 查找所有材质
        materials = [prim for prim in stage.Traverse() if prim.IsA(UsdShade.Material)]
        print(f"找到材质数量: {len(materials)}")
        print()
        
        for mat_prim in materials:
            material = UsdShade.Material(mat_prim)
            print(f"材质名称: {mat_prim.GetName()}")
            print(f"材质路径: {mat_prim.GetPath()}")
            
            # 查找材质下的着色器
            for child in mat_prim.GetChildren():
                if child.IsA(UsdShade.Shader):
                    shader = UsdShade.Shader(child)
                    print(f"着色器名称: {child.GetName()}")
                    print(f"着色器类型: {shader.GetIdAttr().Get()}")
                    
                    # 检查关键属性
                    diffuse_input = shader.GetInput('diffuseColor')
                    if diffuse_input:
                        diffuse_value = diffuse_input.Get()
                        print(f"diffuseColor: {diffuse_value}")
                    else:
                        print("diffuseColor: 未设置")
                    
                    base_color_input = shader.GetInput('baseColor')
                    if base_color_input:
                        base_color_value = base_color_input.Get()
                        print(f"baseColor: {base_color_value}")
                    else:
                        print("baseColor: 未设置")
                    
                    metallic_input = shader.GetInput('metallic')
                    if metallic_input:
                        metallic_value = metallic_input.Get()
                        print(f"metallic: {metallic_value}")
                    else:
                        print("metallic: 未设置")
                    
                    roughness_input = shader.GetInput('roughness')
                    if roughness_input:
                        roughness_value = roughness_input.Get()
                        print(f"roughness: {roughness_value}")
                    else:
                        print("roughness: 未设置")
                        
            print("-" * 30)
            
    except Exception as e:
        print(f"检查材质时出错: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        usdz_file = sys.argv[1]
    else:
        usdz_file = "test_local_shader.usdz"
    
    check_usdz_materials(usdz_file)