#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查USDZ文件是否符合Apple ARKit要求
"""

import os
import sys
import zipfile
from pathlib import Path

try:
    from pxr import Usd, UsdGeom, UsdShade, Sdf
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("⚠️ USD Python绑定不可用")

def check_arkit_compatibility(usdz_path: str):
    """
    检查USDZ文件是否符合Apple ARKit要求
    """
    if not USD_AVAILABLE:
        print("❌ 无法检查，USD Python绑定不可用")
        return False
    
    if not os.path.exists(usdz_path):
        print(f"❌ 文件不存在: {usdz_path}")
        return False
    
    print(f"🍎 ARKit兼容性检查: {usdz_path}")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    try:
        # 1. 检查文件格式和结构
        print("📦 检查USDZ包结构...")
        package_issues = check_package_structure(usdz_path)
        issues.extend(package_issues)
        
        # 2. 打开USD Stage
        stage = Usd.Stage.Open(usdz_path)
        if not stage:
            issues.append("无法打开USDZ文件")
            return False
        
        # 3. 检查Stage元数据
        print("🎬 检查Stage元数据...")
        metadata_issues = check_stage_metadata(stage)
        issues.extend(metadata_issues)
        
        # 4. 检查几何体
        print("🔷 检查几何体...")
        geometry_issues = check_geometry(stage)
        issues.extend(geometry_issues)
        
        # 5. 检查材质
        print("🎨 检查材质...")
        material_issues, material_warnings = check_materials(stage)
        issues.extend(material_issues)
        warnings.extend(material_warnings)
        
        # 6. 检查可见性和用途
        print("👁️ 检查可见性和用途...")
        visibility_issues = check_visibility_and_purpose(stage)
        issues.extend(visibility_issues)
        
        # 7. 检查文件大小
        print("📏 检查文件大小...")
        size_warnings = check_file_size(usdz_path)
        warnings.extend(size_warnings)
        
    except Exception as e:
        issues.append(f"检查过程中出错: {e}")
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📊 ARKit兼容性报告:")
    
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    if warnings:
        print(f"\n⚠️ 发现 {len(warnings)} 个警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not issues and not warnings:
        print("\n✅ 完全符合ARKit要求！")
        return True
    elif not issues:
        print("\n✅ 符合ARKit基本要求（有一些优化建议）")
        return True
    else:
        print("\n❌ 不符合ARKit要求，需要修复")
        return False

def check_package_structure(usdz_path: str) -> list:
    """检查USDZ包结构"""
    issues = []
    
    try:
        with zipfile.ZipFile(usdz_path, 'r') as zf:
            files = zf.namelist()
            
            # 检查是否有USD文件
            usd_files = [f for f in files if f.endswith(('.usd', '.usda', '.usdc'))]
            if not usd_files:
                issues.append("USDZ包中没有找到USD文件")
            
            # 检查主USD文件是否在根目录
            root_usd_files = [f for f in usd_files if '/' not in f]
            if not root_usd_files:
                issues.append("没有在根目录找到USD文件")
            
            print(f"  📄 找到 {len(usd_files)} 个USD文件")
            print(f"  📁 包含 {len(files)} 个文件")
            
    except Exception as e:
        issues.append(f"无法读取USDZ包: {e}")
    
    return issues

def check_stage_metadata(stage) -> list:
    """检查Stage元数据"""
    issues = []
    
    # 检查upAxis
    up_axis = UsdGeom.GetStageUpAxis(stage)
    print(f"  🔼 上轴: {up_axis}")
    if up_axis != UsdGeom.Tokens.y:
        issues.append(f"上轴应该是Y，当前是{up_axis}")
    
    # 检查metersPerUnit
    meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    print(f"  📏 单位: {meters_per_unit} 米/单位")
    # 对于分子结构，0.01米/单位是合适的；对于一般3D模型，1.0米/单位是标准
    if meters_per_unit not in [0.01, 1.0]:
        issues.append(f"建议使用1.0米/单位（一般模型）或0.01米/单位（分子结构），当前是{meters_per_unit}")
    
    # 检查defaultPrim
    default_prim = stage.GetDefaultPrim()
    if not default_prim:
        issues.append("没有设置defaultPrim")
    else:
        print(f"  🎯 默认Prim: {default_prim.GetPath()}")
    
    return issues

def check_geometry(stage) -> list:
    """检查几何体"""
    issues = []
    mesh_count = 0
    
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Mesh):
            mesh_count += 1
            mesh = UsdGeom.Mesh(prim)
            
            # 检查顶点数据
            points = mesh.GetPointsAttr().Get()
            if not points or len(points) == 0:
                issues.append(f"网格 {prim.GetPath()} 没有顶点数据")
            
            # 检查面数据
            faces = mesh.GetFaceVertexIndicesAttr().Get()
            if not faces or len(faces) == 0:
                issues.append(f"网格 {prim.GetPath()} 没有面数据")
            
            # 检查法线
            normals = mesh.GetNormalsAttr().Get()
            if not normals:
                print(f"  ⚠️ 网格 {prim.GetPath()} 没有法线数据（可能会自动计算）")
    
    print(f"  🔷 找到 {mesh_count} 个网格")
    
    if mesh_count == 0:
        issues.append("没有找到任何网格")
    
    return issues

def check_materials(stage) -> tuple:
    """检查材质"""
    issues = []
    warnings = []
    material_count = 0
    
    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Material):
            material_count += 1
            material = UsdShade.Material(prim)
            
            # 检查surface输出
            surface_output = material.GetSurfaceOutput()
            if not surface_output.HasConnectedSource():
                issues.append(f"材质 {prim.GetPath()} 没有连接surface输出")
                continue
            
            # 检查着色器
            source_info = surface_output.GetConnectedSource()
            shader_prim = source_info[0].GetPrim()
            shader = UsdShade.Shader(shader_prim)
            
            # 检查着色器ID
            shader_id = shader.GetIdAttr().Get()
            if shader_id != "UsdPreviewSurface":
                issues.append(f"材质 {prim.GetPath()} 使用了非标准着色器: {shader_id}")
            
            # 检查关键属性
            base_color = shader.GetInput("baseColor")
            diffuse_color = shader.GetInput("diffuseColor")
            
            if diffuse_color and diffuse_color.Get():
                warnings.append(f"材质 {prim.GetPath()} 使用了diffuseColor，建议使用baseColor")
            
            if not base_color or not base_color.Get():
                warnings.append(f"材质 {prim.GetPath()} 没有设置baseColor")
            
            # 检查透明度
            opacity = shader.GetInput("opacity")
            if opacity and opacity.Get() is not None:
                opacity_value = opacity.Get()
                if opacity_value < 1.0:
                    warnings.append(f"材质 {prim.GetPath()} 使用了透明度 ({opacity_value})，可能影响性能")
    
    print(f"  🎨 找到 {material_count} 个材质")
    
    return issues, warnings

def check_visibility_and_purpose(stage) -> list:
    """检查可见性和用途"""
    issues = []
    
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Imageable):
            imageable = UsdGeom.Imageable(prim)
            
            # 检查可见性
            visibility = imageable.GetVisibilityAttr().Get()
            if visibility == UsdGeom.Tokens.invisible:
                issues.append(f"Prim {prim.GetPath()} 被设置为不可见")
            
            # 检查用途
            purpose = imageable.GetPurposeAttr().Get()
            if purpose and purpose not in [UsdGeom.Tokens.default_, UsdGeom.Tokens.render, UsdGeom.Tokens.proxy, UsdGeom.Tokens.guide]:
                issues.append(f"Prim {prim.GetPath()} 使用了无效的用途: {purpose}")
    
    return issues

def check_file_size(usdz_path: str) -> list:
    """检查文件大小"""
    warnings = []
    
    file_size = os.path.getsize(usdz_path)
    size_mb = file_size / (1024 * 1024)
    
    print(f"  📏 文件大小: {size_mb:.2f} MB")
    
    # ARKit建议的文件大小限制
    if size_mb > 25:
        warnings.append(f"文件大小 ({size_mb:.2f} MB) 超过ARKit建议的25MB限制")
    elif size_mb > 10:
        warnings.append(f"文件大小 ({size_mb:.2f} MB) 较大，可能影响加载性能")
    
    return warnings

def main():
    if len(sys.argv) < 2:
        print("用法: python check_arkit_compatibility.py <usdz_file>")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    success = check_arkit_compatibility(usdz_file)
    
    if success:
        print("\n🎯 ARKit兼容性检查通过！")
        sys.exit(0)
    else:
        print("\n❌ ARKit兼容性检查失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
