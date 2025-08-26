#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复USDZ文件的可见性问题
确保所有几何体都正确可见
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from pxr import Usd, UsdGeom, UsdShade, Sdf, UsdUtils
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("错误: USD Python绑定不可用")
    sys.exit(1)

def fix_usdz_visibility(usdz_path: str) -> bool:
    """
    修复USDZ文件的可见性问题
    
    Args:
        usdz_path: USDZ文件路径
        
    Returns:
        bool: 是否成功修复
    """
    if not os.path.exists(usdz_path):
        print(f"错误: 文件不存在 {usdz_path}")
        return False
    
    try:
        # 打开USDZ文件
        stage = Usd.Stage.Open(usdz_path)
        if not stage:
            print(f"错误: 无法打开USDZ文件 {usdz_path}")
            return False
        
        print(f"检查文件: {usdz_path}")
        print("=" * 50)
        
        fixes_applied = 0
        
        # 检查根节点
        root_prim = stage.GetDefaultPrim()
        if root_prim:
            print(f"根节点: {root_prim.GetPath()}")
            
            # 确保根节点可见
            if root_prim.IsA(UsdGeom.Imageable):
                imageable = UsdGeom.Imageable(root_prim)
                visibility_attr = imageable.GetVisibilityAttr()
                
                if not visibility_attr or visibility_attr.Get() != UsdGeom.Tokens.inherited:
                    print("  修复根节点可见性")
                    imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
                    fixes_applied += 1
        
        # 检查所有几何体
        mesh_count = 0
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh_count += 1
                mesh_path = prim.GetPath()
                print(f"\n网格 {mesh_count}: {mesh_path}")
                
                # 检查可见性
                imageable = UsdGeom.Imageable(prim)
                visibility_attr = imageable.GetVisibilityAttr()
                current_visibility = visibility_attr.Get() if visibility_attr else None
                
                print(f"  当前可见性: {current_visibility}")
                
                # 修复可见性
                if current_visibility != UsdGeom.Tokens.inherited:
                    print("  设置可见性为 inherited")
                    imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
                    fixes_applied += 1
                
                # 检查用途
                purpose_attr = imageable.GetPurposeAttr()
                current_purpose = purpose_attr.Get() if purpose_attr else None
                
                print(f"  当前用途: {current_purpose}")
                
                # 确保用途设置正确 (render是默认用途)
                if current_purpose != UsdGeom.Tokens.render and current_purpose is not None:
                    print("  设置用途为 render")
                    imageable.CreatePurposeAttr(UsdGeom.Tokens.render)
                    fixes_applied += 1
                elif current_purpose is None:
                    print("  设置默认用途")
                    # 不设置purpose属性，让它使用默认值
                    pass
                
                # 检查材质绑定
                material_binding = UsdShade.MaterialBindingAPI(prim)
                bound_material = material_binding.GetDirectBinding()
                
                if bound_material.GetMaterial():
                    material_path = bound_material.GetMaterial().GetPath()
                    print(f"  绑定材质: {material_path}")
                    
                    # 检查材质是否存在
                    material_prim = stage.GetPrimAtPath(material_path)
                    if not material_prim or not material_prim.IsValid():
                        print(f"  警告: 材质不存在或无效 {material_path}")
                else:
                    print("  警告: 未绑定材质")
                
                # 检查几何体数据
                mesh = UsdGeom.Mesh(prim)
                points = mesh.GetPointsAttr().Get()
                faces = mesh.GetFaceVertexIndicesAttr().Get()
                
                print(f"  顶点数: {len(points) if points else 0}")
                print(f"  面数: {len(faces)//3 if faces else 0}")
                
                if not points or len(points) == 0:
                    print("  错误: 没有顶点数据!")
                if not faces or len(faces) == 0:
                    print("  错误: 没有面数据!")
        
        print(f"\n总共找到 {mesh_count} 个网格")
        
        if fixes_applied > 0:
            print(f"应用了 {fixes_applied} 个修复")
            
            # 保存修改到USDZ文件
            try:
                # 创建临时USD文件
                with tempfile.NamedTemporaryFile(suffix='.usd', delete=False) as tmp_file:
                    temp_usd_path = tmp_file.name
                
                # 导出为USD文件
                stage.Export(temp_usd_path)
                
                # 重新打包为USDZ
                success = UsdUtils.CreateNewUsdzPackage(temp_usd_path, usdz_path)
                
                # 清理临时文件
                if os.path.exists(temp_usd_path):
                    os.unlink(temp_usd_path)
                
                if success:
                    print("✅ 可见性修复已保存")
                    return True
                else:
                    print("❌ 重新打包USDZ失败")
                    return False
                    
            except Exception as save_error:
                print(f"❌ 保存修复时出错: {save_error}")
                return False
        else:
            print("✅ 没有发现可见性问题")
            return True
            
    except Exception as e:
        print(f"错误: 修复可见性时出错 {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python fix_visibility.py <usdz_file>")
        sys.exit(1)
    
    usdz_path = sys.argv[1]
    success = fix_usdz_visibility(usdz_path)
    
    if success:
        print("\n🎉 可见性修复完成")
    else:
        print("\n❌ 可见性修复失败")
        sys.exit(1)

if __name__ == '__main__':
    main()