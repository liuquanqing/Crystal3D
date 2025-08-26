#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试材质绑定的正确性
"""

import os
import sys
from pathlib import Path

try:
    from pxr import Usd, UsdGeom, UsdShade
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("⚠️ USD Python绑定不可用")

def test_material_binding(usdz_path: str):
    """
    测试USDZ文件的材质绑定
    """
    if not USD_AVAILABLE:
        print("❌ 无法测试，USD Python绑定不可用")
        return False
    
    if not os.path.exists(usdz_path):
        print(f"❌ 文件不存在: {usdz_path}")
        return False
    
    try:
        stage = Usd.Stage.Open(usdz_path)
        if not stage:
            print(f"❌ 无法打开USDZ文件: {usdz_path}")
            return False
        
        print(f"🔍 测试文件: {usdz_path}")
        print("=" * 60)
        
        # 统计信息
        mesh_count = 0
        material_count = 0
        bound_meshes = 0
        unbound_meshes = 0
        
        # 收集所有材质
        materials = {}
        for prim in stage.Traverse():
            if prim.IsA(UsdShade.Material):
                material_count += 1
                materials[prim.GetPath()] = prim
                print(f"📦 找到材质: {prim.GetPath()}")
        
        print(f"\n📊 总共找到 {material_count} 个材质")
        
        # 检查每个网格的材质绑定
        print("\n🔍 检查网格材质绑定:")
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh_count += 1
                mesh_path = prim.GetPath()
                print(f"\n🔷 网格: {mesh_path}")
                
                # 检查材质绑定
                material_binding = UsdShade.MaterialBindingAPI(prim)
                bound_material = material_binding.GetDirectBinding()
                
                if bound_material.GetMaterial():
                    bound_meshes += 1
                    material_path = bound_material.GetMaterial().GetPath()
                    print(f"  ✅ 绑定材质: {material_path}")
                    
                    # 验证材质是否存在
                    if material_path in materials:
                        print(f"  ✅ 材质存在且有效")
                        
                        # 检查材质属性
                        material = UsdShade.Material(materials[material_path])
                        surface_output = material.GetSurfaceOutput()
                        
                        if surface_output.HasConnectedSource():
                            source_info = surface_output.GetConnectedSource()
                            shader_prim = source_info[0].GetPrim()
                            shader = UsdShade.Shader(shader_prim)
                            
                            # 检查关键属性
                            base_color = shader.GetInput("baseColor")
                            diffuse_color = shader.GetInput("diffuseColor")
                            metallic = shader.GetInput("metallic")
                            roughness = shader.GetInput("roughness")
                            opacity = shader.GetInput("opacity")
                            
                            print(f"  🎨 材质属性:")
                            if base_color and base_color.Get():
                                print(f"    - baseColor: {base_color.Get()}")
                            if diffuse_color and diffuse_color.Get():
                                print(f"    - diffuseColor: {diffuse_color.Get()} (⚠️ 应使用baseColor)")
                            if metallic and metallic.Get() is not None:
                                print(f"    - metallic: {metallic.Get()}")
                            if roughness and roughness.Get() is not None:
                                print(f"    - roughness: {roughness.Get()}")
                            if opacity and opacity.Get() is not None:
                                print(f"    - opacity: {opacity.Get()}")
                        else:
                            print(f"  ⚠️ 材质没有连接的着色器")
                    else:
                        print(f"  ❌ 材质不存在: {material_path}")
                else:
                    unbound_meshes += 1
                    print(f"  ❌ 未绑定材质")
                
                # 检查几何体数据
                mesh = UsdGeom.Mesh(prim)
                points = mesh.GetPointsAttr().Get()
                faces = mesh.GetFaceVertexIndicesAttr().Get()
                
                print(f"  📐 几何数据:")
                print(f"    - 顶点数: {len(points) if points else 0}")
                print(f"    - 面索引数: {len(faces) if faces else 0}")
                
                if not points or len(points) == 0:
                    print(f"    ❌ 没有顶点数据!")
                if not faces or len(faces) == 0:
                    print(f"    ❌ 没有面数据!")
        
        # 总结报告
        print("\n" + "=" * 60)
        print(f"📊 材质绑定测试报告:")
        print(f"  🔷 总网格数: {mesh_count}")
        print(f"  📦 总材质数: {material_count}")
        print(f"  ✅ 已绑定网格: {bound_meshes}")
        print(f"  ❌ 未绑定网格: {unbound_meshes}")
        
        # 评估结果
        if mesh_count == 0:
            print(f"\n❌ 测试失败: 没有找到网格")
            return False
        elif material_count == 0:
            print(f"\n❌ 测试失败: 没有找到材质")
            return False
        elif unbound_meshes > 0:
            print(f"\n⚠️ 测试警告: 有 {unbound_meshes} 个网格未绑定材质")
            return False
        else:
            print(f"\n✅ 测试通过: 所有网格都正确绑定了材质")
            return True
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python test_material_binding.py <usdz_file>")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    success = test_material_binding(usdz_file)
    
    if success:
        print("\n🎯 材质绑定测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 材质绑定测试失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
