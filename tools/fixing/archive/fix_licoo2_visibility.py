#!/usr/bin/env python3
"""
修复LiCoO2 USDZ文件的显示问题
主要解决坐标偏移和几何体复杂度问题
"""

import zipfile
import tempfile
import os
from pathlib import Path
import sys

try:
    from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf
except ImportError:
    print("❌ 错误: 需要安装USD Python库")
    print("请运行: pip install usd-core")
    sys.exit(1)

def fix_licoo2_visibility(input_usdz, output_usdz):
    """
    修复LiCoO2 USDZ文件的显示问题
    """
    print(f"🔧 修复LiCoO2显示问题: {input_usdz} -> {output_usdz}")
    print("=" * 60)
    
    if not os.path.exists(input_usdz):
        print(f"❌ 输入文件不存在: {input_usdz}")
        return False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 提取USDZ文件
            print("📦 提取USDZ文件...")
            with zipfile.ZipFile(input_usdz, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # 查找USD文件
            usd_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.usd', '.usda', '.usdc')):
                        usd_files.append(os.path.join(root, file))
            
            if not usd_files:
                print("❌ 未找到USD文件")
                return False
            
            main_usd = usd_files[0]
            print(f"🎬 处理USD文件: {os.path.basename(main_usd)}")
            
            # 打开USD Stage
            stage = Usd.Stage.Open(main_usd)
            if not stage:
                print("❌ 无法打开USD文件")
                return False
            
            # 获取网格
            mesh_prim = None
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh_prim = prim
                    break
            
            if not mesh_prim:
                print("❌ 未找到网格")
                return False
            
            mesh = UsdGeom.Mesh(mesh_prim)
            print(f"🔷 找到网格: {mesh_prim.GetPath()}")
            
            # 获取当前顶点
            points_attr = mesh.GetPointsAttr()
            if not points_attr:
                print("❌ 网格没有顶点数据")
                return False
            
            points = points_attr.Get()
            if not points:
                print("❌ 顶点数据为空")
                return False
            
            print(f"📍 原始顶点数: {len(points)}")
            
            # 计算边界框和中心
            bbox = Gf.Range3d()
            for point in points:
                point_3d = Gf.Vec3d(float(point[0]), float(point[1]), float(point[2]))
                bbox.UnionWith(point_3d)
            
            min_pt = bbox.GetMin()
            max_pt = bbox.GetMax()
            center = (min_pt + max_pt) / 2.0
            size = max_pt - min_pt
            
            print(f"📏 原始边界框: {size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f}")
            print(f"📍 原始中心: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
            
            # 修复1: 将模型中心移到原点
            print("\n🎯 修复1: 将模型中心移到原点...")
            centered_points = []
            for point in points:
                new_point = Gf.Vec3f(
                    float(point[0]) - center[0],
                    float(point[1]) - center[1], 
                    float(point[2]) - center[2]
                )
                centered_points.append(new_point)
            
            # 应用居中的顶点
            points_attr.Set(centered_points)
            
            # 验证新的边界框
            new_bbox = Gf.Range3d()
            for point in centered_points:
                point_3d = Gf.Vec3d(float(point[0]), float(point[1]), float(point[2]))
                new_bbox.UnionWith(point_3d)
            
            new_min = new_bbox.GetMin()
            new_max = new_bbox.GetMax()
            new_center = (new_min + new_max) / 2.0
            new_size = new_max - new_min
            
            print(f"✅ 新边界框: {new_size[0]:.3f} x {new_size[1]:.3f} x {new_size[2]:.3f}")
            print(f"✅ 新中心: ({new_center[0]:.3f}, {new_center[1]:.3f}, {new_center[2]:.3f})")
            
            # 修复2: 简化材质结构 - 使用单一材质
            print("\n🎨 修复2: 简化材质结构...")
            
            # 创建简化的材质
            material_path = "/LiCoO2/Materials/SimplifiedMaterial"
            if stage.GetPrimAtPath(material_path):
                stage.RemovePrim(material_path)
            
            material_prim = stage.DefinePrim(material_path, "Material")
            material = UsdShade.Material(material_prim)
            
            # 创建简化的着色器
            shader_path = material_path + "/surfaceShader"
            shader_prim = stage.DefinePrim(shader_path, "Shader")
            shader = UsdShade.Shader(shader_prim)
            shader.CreateIdAttr("UsdPreviewSurface")
            
            # 设置简单的材质属性 (使用醒目的颜色)
            shader.CreateInput("baseColor", Sdf.ValueTypeNames.Color3f).Set((1.0, 0.5, 0.0))  # 橙色
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.1)
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.3)
            shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(1.0)
            
            # 连接着色器到材质
            material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
            
            # 将简化材质绑定到网格
            UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)
            
            # 移除所有GeomSubset (简化几何体结构)
            print("🔧 修复3: 移除GeomSubset分组...")
            subsets_removed = 0
            for child in mesh_prim.GetChildren():
                if child.IsA(UsdGeom.Subset):
                    stage.RemovePrim(child.GetPath())
                    subsets_removed += 1
            
            print(f"✅ 移除了 {subsets_removed} 个GeomSubset")
            
            # 修复4: 确保可见性
            print("\n👁️ 修复4: 确保几何体可见...")
            if mesh_prim.IsA(UsdGeom.Imageable):
                imageable = UsdGeom.Imageable(mesh_prim)
                imageable.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)
            
            # 确保父级也可见
            parent_prim = mesh_prim.GetParent()
            while parent_prim and parent_prim.GetPath() != Sdf.Path.absoluteRootPath:
                if parent_prim.IsA(UsdGeom.Imageable):
                    imageable = UsdGeom.Imageable(parent_prim)
                    imageable.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)
                parent_prim = parent_prim.GetParent()
            
            print("✅ 设置几何体和父级为可见")
            
            # 修复5: 添加简单的边界框信息
            print("\n📏 修复5: 添加边界框信息...")
            extent_attr = mesh.GetExtentAttr()
            if not extent_attr:
                extent_attr = mesh.CreateExtentAttr()
            
            extent_attr.Set([new_min, new_max])
            print("✅ 设置边界框信息")
            
            # 保存修改后的USD文件
            stage.Save()
            print("💾 保存USD文件修改")
            
            # 创建新的USDZ文件
            print("\n📦 创建修复后的USDZ文件...")
            with zipfile.ZipFile(output_usdz, 'w', zipfile.ZIP_STORED) as zip_file:
                zip_file.write(main_usd, os.path.basename(main_usd))
            
            # 验证输出文件
            output_size = os.path.getsize(output_usdz)
            print(f"✅ 修复完成: {output_usdz} ({output_size:,} 字节)")
            
            print("\n🎯 应用的修复:")
            print("  ✅ 将模型中心移到原点 (0,0,0)")
            print("  ✅ 简化材质结构 (单一橙色材质)")
            print("  ✅ 移除GeomSubset分组")
            print("  ✅ 确保几何体可见性")
            print("  ✅ 添加边界框信息")
            
            return True
            
        except Exception as e:
            print(f"❌ 修复过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python fix_licoo2_visibility.py <input_usdz> <output_usdz>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = fix_licoo2_visibility(input_file, output_file)
    
    if success:
        print(f"\n🎉 修复成功! 请测试新文件: {output_file}")
        print("💡 如果仍然看不到，请尝试在查看器中:")
        print("   - 重置视角 (Reset View)")
        print("   - 缩放到适合 (Fit to View)")
        print("   - 手动调整距离和角度")
    else:
        print("❌ 修复失败")
        sys.exit(1)
