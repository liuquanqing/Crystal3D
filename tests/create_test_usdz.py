#!/usr/bin/env python3
"""
创建一个简单的测试USDZ文件
用于验证查看器是否正常工作
"""

import os
import zipfile
import tempfile
from pathlib import Path

try:
    from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf
except ImportError:
    print("❌ 错误: 需要安装USD Python库")
    print("请运行: pip install usd-core")
    exit(1)

def create_simple_test_usdz(output_path):
    """
    创建一个简单的立方体USDZ文件用于测试
    """
    print(f"🔧 创建测试USDZ文件: {output_path}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        usd_file = os.path.join(temp_dir, "test_cube.usd")
        
        # 创建USD Stage
        stage = Usd.Stage.CreateNew(usd_file)
        
        # 设置Stage元数据
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
        
        # 创建根Prim
        root_prim = stage.DefinePrim("/TestCube", "Xform")
        stage.SetDefaultPrim(root_prim)
        
        # 创建立方体网格
        cube_prim = stage.DefinePrim("/TestCube/Geometry/cube", "Mesh")
        cube_mesh = UsdGeom.Mesh(cube_prim)
        
        # 定义立方体顶点 (简单的1x1x1立方体)
        points = [
            (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),  # 底面
            (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)      # 顶面
        ]
        
        # 定义面（每个面4个顶点）
        face_vertex_counts = [4, 4, 4, 4, 4, 4]  # 6个面，每个面4个顶点
        face_vertex_indices = [
            0, 1, 2, 3,  # 底面
            4, 7, 6, 5,  # 顶面
            0, 4, 5, 1,  # 前面
            2, 6, 7, 3,  # 后面
            0, 3, 7, 4,  # 左面
            1, 5, 6, 2   # 右面
        ]
        
        # 设置网格数据
        cube_mesh.GetPointsAttr().Set(points)
        cube_mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
        cube_mesh.GetFaceVertexIndicesAttr().Set(face_vertex_indices)
        
        # 计算法线（简单的面法线）
        normals = [
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),  # 底面法线
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),      # 顶面法线
            (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),  # 前面法线
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),      # 后面法线
            (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),  # 左面法线
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)       # 右面法线
        ]
        cube_mesh.GetNormalsAttr().Set(normals)
        cube_mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
        
        # 添加UV坐标
        uv_coords = [
            (0, 0), (1, 0), (1, 1), (0, 1),  # 底面UV
            (0, 0), (1, 0), (1, 1), (0, 1),  # 顶面UV
            (0, 0), (1, 0), (1, 1), (0, 1),  # 前面UV
            (0, 0), (1, 0), (1, 1), (0, 1),  # 后面UV
            (0, 0), (1, 0), (1, 1), (0, 1),  # 左面UV
            (0, 0), (1, 0), (1, 1), (0, 1)   # 右面UV
        ]
        # 使用正确的API创建UV坐标
        primvars_api = UsdGeom.PrimvarsAPI(cube_prim)
        st_primvar = primvars_api.CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
        st_primvar.Set(uv_coords)
        
        # 创建材质
        material_prim = stage.DefinePrim("/TestCube/Materials/CubeMaterial", "Material")
        material = UsdShade.Material(material_prim)
        
        # 创建表面着色器
        shader_prim = stage.DefinePrim("/TestCube/Materials/CubeMaterial/surfaceShader", "Shader")
        shader = UsdShade.Shader(shader_prim)
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # 设置材质属性
        shader.CreateInput("baseColor", Sdf.ValueTypeNames.Color3f).Set((0.2, 0.6, 1.0))  # 蓝色
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(1.0)
        
        # 连接着色器到材质
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        
        # 将材质绑定到网格
        UsdShade.MaterialBindingAPI(cube_prim).Bind(material)
        
        # 保存USD文件
        stage.Save()
        
        # 创建USDZ包
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zip_file:
            zip_file.write(usd_file, "test_cube.usd")
        
        print(f"✅ 测试USDZ文件创建成功: {output_path}")
        file_size = os.path.getsize(output_path)
        print(f"📏 文件大小: {file_size:,} 字节")
        
        return True

if __name__ == "__main__":
    output_file = "test_cube.usdz"
    success = create_simple_test_usdz(output_file)
    
    if success:
        print(f"\n🎯 测试文件已创建: {output_file}")
        print("💡 请尝试在您的USDZ查看器中打开此文件")
        print("   如果此文件能正常显示，说明查看器工作正常")
        print("   如果此文件也看不到，可能是查看器或设备的问题")
    else:
        print("❌ 创建测试文件失败")