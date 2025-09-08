#!/usr/bin/env python3
"""
USDZ内容详细诊断工具
用于深入分析USDZ文件的内容和结构，帮助诊断显示问题
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

def diagnose_usdz_content(usdz_path):
    """
    详细诊断USDZ文件内容
    """
    print(f"🔍 详细诊断USDZ文件: {usdz_path}")
    print("=" * 60)
    
    if not os.path.exists(usdz_path):
        print(f"❌ 文件不存在: {usdz_path}")
        return False
    
    # 检查USDZ包结构
    print("📦 检查USDZ包结构...")
    try:
        with zipfile.ZipFile(usdz_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"  📁 包含 {len(file_list)} 个文件:")
            for file_name in file_list:
                file_info = zip_file.getinfo(file_name)
                print(f"    📄 {file_name} ({file_info.file_size} 字节)")
    except Exception as e:
        print(f"❌ 无法读取USDZ包: {e}")
        return False
    
    # 提取并分析USD文件
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(usdz_path, 'r') as zip_file:
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
            
            # 分析主USD文件
            main_usd = usd_files[0]
            print(f"\n🎬 分析USD文件: {os.path.basename(main_usd)}")
            
            stage = Usd.Stage.Open(main_usd)
            if not stage:
                print("❌ 无法打开USD文件")
                return False
            
            # 检查Stage信息
            print("\n📋 Stage信息:")
            print(f"  🔼 上轴: {UsdGeom.GetStageUpAxis(stage)}")
            print(f"  📏 单位: {UsdGeom.GetStageMetersPerUnit(stage)} 米/单位")
            
            default_prim = stage.GetDefaultPrim()
            if default_prim:
                print(f"  🎯 默认Prim: {default_prim.GetPath()}")
            else:
                print("  ⚠️ 未设置默认Prim")
            
            # 检查所有Prim
            print("\n🔷 Prim层次结构:")
            _print_prim_hierarchy(stage.GetPseudoRoot(), 0)
            
            # 检查几何体详情
            print("\n🔷 几何体详细信息:")
            mesh_count = 0
            total_vertices = 0
            total_faces = 0
            
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh_count += 1
                    mesh = UsdGeom.Mesh(prim)
                    
                    # 获取顶点数据
                    points_attr = mesh.GetPointsAttr()
                    if points_attr:
                        points = points_attr.Get()
                        if points:
                            vertex_count = len(points)
                            total_vertices += vertex_count
                            print(f"  🔷 网格 {prim.GetPath()}: {vertex_count} 个顶点")
                            
                            # 检查边界框
                            if vertex_count > 0:
                                bbox = Gf.Range3d()
                                for point in points:
                                    # 转换为Vec3d类型
                                    point_3d = Gf.Vec3d(float(point[0]), float(point[1]), float(point[2]))
                                    bbox.UnionWith(point_3d)
                                min_pt = bbox.GetMin()
                                max_pt = bbox.GetMax()
                                size = max_pt - min_pt
                                print(f"    📏 边界框: {size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f}")
                                print(f"    📍 中心: ({(min_pt[0]+max_pt[0])/2:.3f}, {(min_pt[1]+max_pt[1])/2:.3f}, {(min_pt[2]+max_pt[2])/2:.3f})")
                    
                    # 获取面数据
                    face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()
                    if face_vertex_counts:
                        face_count = len(face_vertex_counts)
                        total_faces += face_count
                        print(f"    🔺 {face_count} 个面")
                    
                    # 检查法线
                    normals_attr = mesh.GetNormalsAttr()
                    if normals_attr and normals_attr.Get():
                        print(f"    ↗️ 有法线数据")
                    else:
                        print(f"    ⚠️ 缺少法线数据")
                    
                    # 检查UV坐标
                    has_uvs = False
                    try:
                        # 检查常见的UV属性
                        st_attr = mesh.GetPrimvar('st')
                        if st_attr and st_attr.Get():
                            has_uvs = True
                        else:
                            # 检查其他可能的UV属性名
                            uv_attr = mesh.GetPrimvar('uv')
                            if uv_attr and uv_attr.Get():
                                has_uvs = True
                    except:
                        pass
                    
                    if has_uvs:
                        print(f"    🗺️ 有UV坐标")
                    else:
                        print(f"    ⚠️ 缺少UV坐标")
            
            print(f"\n📊 几何体统计:")
            print(f"  🔷 总计 {mesh_count} 个网格")
            print(f"  📍 总计 {total_vertices} 个顶点")
            print(f"  🔺 总计 {total_faces} 个面")
            
            # 检查材质详情
            print("\n🎨 材质详细信息:")
            material_count = 0
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    material_count += 1
                    material = UsdShade.Material(prim)
                    print(f"  🎨 材质 {prim.GetPath()}:")
                    
                    # 检查表面着色器
                    surface_output = material.GetSurfaceOutput()
                    if surface_output:
                        shader_prim = surface_output.GetConnectedSource()[0]
                        if shader_prim:
                            shader = UsdShade.Shader(shader_prim)
                            shader_id = shader.GetIdAttr().Get()
                            print(f"    🔧 着色器: {shader_id}")
                            
                            # 检查材质属性
                            try:
                                inputs = shader.GetInputs()
                                for input_attr in inputs:
                                    input_name = input_attr.GetBaseName()
                                    value = input_attr.Get()
                                    if value is not None:
                                        print(f"    🎯 {input_name}: {value}")
                            except:
                                # 如果无法获取输入，跳过
                                pass
            
            print(f"\n📊 材质统计: 总计 {material_count} 个材质")
            
            # 检查可见性
            print("\n👁️ 可见性检查:")
            invisible_prims = []
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Imageable):
                    imageable = UsdGeom.Imageable(prim)
                    visibility = imageable.GetVisibilityAttr().Get()
                    if visibility == UsdGeom.Tokens.invisible:
                        invisible_prims.append(prim.GetPath())
            
            if invisible_prims:
                print(f"  ⚠️ 发现 {len(invisible_prims)} 个不可见的Prim:")
                for path in invisible_prims:
                    print(f"    👻 {path}")
            else:
                print(f"  ✅ 所有几何体都是可见的")
            
            print("\n" + "=" * 60)
            print("🎯 诊断完成！")
            
            # 给出建议
            print("\n💡 建议:")
            if mesh_count == 0:
                print("  ❌ 没有找到网格几何体 - 这是主要问题！")
            elif total_vertices == 0:
                print("  ❌ 网格没有顶点数据 - 这是主要问题！")
            elif invisible_prims:
                print("  ⚠️ 有不可见的几何体，检查可见性设置")
            elif not default_prim:
                print("  ⚠️ 未设置默认Prim，某些查看器可能无法正确显示")
            else:
                print("  ✅ 几何体数据看起来正常")
                print("  💭 如果仍然看不到内容，可能是查看器或设备的问题")
                print("  🔄 建议尝试不同的USDZ查看器或设备")
            
            return True
            
        except Exception as e:
            print(f"❌ 分析USD文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

def _print_prim_hierarchy(prim, indent_level):
    """
    递归打印Prim层次结构
    """
    indent = "  " * indent_level
    prim_type = prim.GetTypeName() if prim.GetTypeName() else "Prim"
    
    # 检查是否有几何体
    geometry_info = ""
    if prim.IsA(UsdGeom.Mesh):
        mesh = UsdGeom.Mesh(prim)
        points = mesh.GetPointsAttr().Get()
        if points:
            geometry_info = f" ({len(points)} 顶点)"
    
    # 检查可见性
    visibility_info = ""
    if prim.IsA(UsdGeom.Imageable):
        imageable = UsdGeom.Imageable(prim)
        visibility = imageable.GetVisibilityAttr().Get()
        if visibility == UsdGeom.Tokens.invisible:
            visibility_info = " [不可见]"
    
    print(f"{indent}📁 {prim.GetPath()} ({prim_type}){geometry_info}{visibility_info}")
    
    # 递归打印子Prim
    for child in prim.GetChildren():
        _print_prim_hierarchy(child, indent_level + 1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python diagnose_usdz_content.py <usdz_file>")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    success = diagnose_usdz_content(usdz_file)
    
    if not success:
        sys.exit(1)