#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查USDZ文件的可见性和材质绑定
"""

from pxr import Usd, UsdGeom, UsdShade

def check_usdz_visibility(usdz_path):
    """
    检查USDZ文件的可见性和材质绑定
    """
    stage = Usd.Stage.Open(usdz_path)
    if not stage:
        print(f"无法打开文件: {usdz_path}")
        return
    
    print(f"检查文件: {usdz_path}")
    print("=" * 50)
    
    # 检查所有几何体
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Mesh):
            mesh_path = prim.GetPath()
            print(f"\n网格: {mesh_path}")
            
            # 检查可见性
            imageable = UsdGeom.Imageable(prim)
            visibility = imageable.GetVisibilityAttr().Get()
            purpose = imageable.GetPurposeAttr().Get()
            
            print(f"  可见性: {visibility}")
            print(f"  用途: {purpose}")
            
            # 检查材质绑定
            material_binding = UsdShade.MaterialBindingAPI(prim)
            bound_material = material_binding.GetDirectBinding()
            
            if bound_material.GetMaterial():
                material_path = bound_material.GetMaterial().GetPath()
                print(f"  绑定材质: {material_path}")
            else:
                print(f"  绑定材质: 无")
            
            # 检查几何体数据
            mesh = UsdGeom.Mesh(prim)
            points = mesh.GetPointsAttr().Get()
            faces = mesh.GetFaceVertexIndicesAttr().Get()
            
            print(f"  顶点数: {len(points) if points else 0}")
            print(f"  面数: {len(faces) if faces else 0}")
    
    # 检查根节点可见性
    root_prim = stage.GetDefaultPrim()
    if root_prim:
        print(f"\n根节点: {root_prim.GetPath()}")
        if root_prim.IsA(UsdGeom.Imageable):
            imageable = UsdGeom.Imageable(root_prim)
            visibility = imageable.GetVisibilityAttr().Get()
            print(f"  根节点可见性: {visibility}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        usdz_file = sys.argv[1]
    else:
        usdz_file = "test_local_shader.usdz"
    
    check_usdz_visibility(usdz_file)