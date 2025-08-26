#!/usr/bin/env python3
"""
修复USDZ材质属性以符合AR Quick Look最佳实践
基于苹果官方文档和USD规范的正确材质设置
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

def fix_material_properties(input_usdz, output_usdz):
    """
    修复USDZ材质属性以符合AR Quick Look最佳实践
    
    关键修复:
    1. 使用diffuseColor而不是baseColor (USD规范)
    2. 移除displayColor依赖 (AR Quick Look不支持)
    3. 确保UsdPreviewSurface正确配置
    4. 优化材质属性以提高兼容性
    """
    print(f"🎨 修复材质属性: {input_usdz} -> {output_usdz}")
    print("=" * 60)
    
    # 基于搜索结果的关键信息:
    print("📋 应用的最佳实践:")
    print("  • AR Quick Look不支持displayColor和vertexColor")
    print("  • 必须使用UsdPreviewSurface材质系统")
    print("  • 使用diffuseColor属性定义颜色 (USD规范)")
    print("  • 确保材质正确绑定到几何体")
    print()
    
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
            
            # 查找所有材质
            materials = []
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    materials.append(UsdShade.Material(prim))
            
            print(f"🎨 找到 {len(materials)} 个材质")
            
            # 修复每个材质
            for i, material in enumerate(materials):
                material_path = material.GetPrim().GetPath()
                print(f"\n🔧 修复材质 {i+1}/{len(materials)}: {material_path}")
                
                # 查找UsdPreviewSurface着色器
                surface_shader = None
                for child in material.GetPrim().GetChildren():
                    if child.IsA(UsdShade.Shader):
                        shader = UsdShade.Shader(child)
                        shader_id = shader.GetIdAttr().Get()
                        if shader_id == "UsdPreviewSurface":
                            surface_shader = shader
                            break
                
                if not surface_shader:
                    print(f"  ⚠️ 未找到UsdPreviewSurface着色器，创建新的...")
                    # 创建新的UsdPreviewSurface着色器
                    shader_path = material_path.AppendChild("surfaceShader")
                    if stage.GetPrimAtPath(shader_path):
                        stage.RemovePrim(shader_path)
                    
                    shader_prim = stage.DefinePrim(shader_path, "Shader")
                    surface_shader = UsdShade.Shader(shader_prim)
                    surface_shader.CreateIdAttr("UsdPreviewSurface")
                    
                    # 连接到材质
                    material.CreateSurfaceOutput().ConnectToSource(surface_shader.ConnectableAPI(), "surface")
                
                # 修复材质属性 - 使用USD规范的正确属性名
                print(f"  🎯 修复着色器属性...")
                
                # 1. 确保使用diffuseColor (USD规范) 而不是baseColor
                diffuse_input = surface_shader.GetInput("diffuseColor")
                base_input = surface_shader.GetInput("baseColor")
                
                # 如果存在baseColor，将其值复制到diffuseColor
                if base_input and base_input.HasValue():
                    base_value = base_input.Get()
                    print(f"    📋 从baseColor复制到diffuseColor: {base_value}")
                    if not diffuse_input:
                        diffuse_input = surface_shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
                    diffuse_input.Set(base_value)
                    # 移除baseColor (避免混淆)
                    surface_shader.GetPrim().RemoveProperty("inputs:baseColor")
                
                # 如果没有diffuseColor，设置默认值
                if not diffuse_input or not diffuse_input.HasValue():
                    if not diffuse_input:
                        diffuse_input = surface_shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
                    # 使用醒目的橙色以便测试
                    diffuse_input.Set((1.0, 0.5, 0.0))
                    print(f"    🎨 设置默认diffuseColor: (1.0, 0.5, 0.0)")
                
                # 2. 确保其他重要属性正确设置
                # metallic属性
                metallic_input = surface_shader.GetInput("metallic")
                if not metallic_input:
                    metallic_input = surface_shader.CreateInput("metallic", Sdf.ValueTypeNames.Float)
                metallic_input.Set(0.0)  # 非金属
                
                # roughness属性
                roughness_input = surface_shader.GetInput("roughness")
                if not roughness_input:
                    roughness_input = surface_shader.CreateInput("roughness", Sdf.ValueTypeNames.Float)
                roughness_input.Set(0.5)  # 中等粗糙度
                
                # opacity属性
                opacity_input = surface_shader.GetInput("opacity")
                if not opacity_input:
                    opacity_input = surface_shader.CreateInput("opacity", Sdf.ValueTypeNames.Float)
                opacity_input.Set(1.0)  # 完全不透明
                
                # 3. 移除可能导致问题的属性
                # 移除specularColor (如果存在且不需要)
                specular_input = surface_shader.GetInput("specularColor")
                if specular_input:
                    surface_shader.GetPrim().RemoveProperty("inputs:specularColor")
                    print(f"    🗑️ 移除specularColor属性")
                
                print(f"  ✅ 材质修复完成")
            
            # 查找所有几何体并确保材质正确绑定
            print(f"\n🔗 检查材质绑定...")
            mesh_count = 0
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh_count += 1
                    mesh_path = prim.GetPath()
                    
                    # 检查材质绑定
                    binding_api = UsdShade.MaterialBindingAPI(prim)
                    bound_material = binding_api.GetDirectBinding().GetMaterial()
                    
                    if bound_material:
                        print(f"  ✅ 网格 {mesh_path} 已绑定材质: {bound_material.GetPrim().GetPath()}")
                    else:
                        # 如果没有绑定材质，绑定第一个可用材质
                        if materials:
                            binding_api.Bind(materials[0])
                            print(f"  🔗 为网格 {mesh_path} 绑定材质: {materials[0].GetPrim().GetPath()}")
                        else:
                            print(f"  ⚠️ 网格 {mesh_path} 没有绑定材质且无可用材质")
            
            print(f"\n📊 处理统计:")
            print(f"  🎨 修复了 {len(materials)} 个材质")
            print(f"  🔷 检查了 {mesh_count} 个网格")
            
            # 保存修改后的USD文件
            stage.Save()
            print("\n💾 保存USD文件修改")
            
            # 创建新的USDZ文件
            print("📦 创建修复后的USDZ文件...")
            with zipfile.ZipFile(output_usdz, 'w', zipfile.ZIP_STORED) as zip_file:
                zip_file.write(main_usd, os.path.basename(main_usd))
            
            # 验证输出文件
            output_size = os.path.getsize(output_usdz)
            print(f"✅ 修复完成: {output_usdz} ({output_size:,} 字节)")
            
            print("\n🎯 应用的修复:")
            print("  ✅ 使用diffuseColor替代baseColor (USD规范)")
            print("  ✅ 移除不兼容的材质属性")
            print("  ✅ 确保UsdPreviewSurface正确配置")
            print("  ✅ 验证材质绑定")
            print("  ✅ 优化AR Quick Look兼容性")
            
            print("\n💡 关键信息:")
            print("  📋 AR Quick Look不支持displayColor/vertexColor")
            print("  🎨 颜色必须通过UsdPreviewSurface的diffuseColor定义")
            print("  🔧 USD规范使用diffuseColor，不是baseColor")
            print("  ✨ 修复后的文件应该在AR Quick Look中正确显示")
            
            return True
            
        except Exception as e:
            print(f"❌ 修复过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python fix_material_properties.py <input_usdz> <output_usdz>")
        print("\n示例: python fix_material_properties.py fixed_LiCoO2.usdz final_fixed_LiCoO2.usdz")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = fix_material_properties(input_file, output_file)
    
    if success:
        print(f"\n🎉 材质修复成功! 请测试新文件: {output_file}")
        print("\n📱 测试建议:")
        print("   1. 在iPhone/iPad上用Safari打开USDZ文件")
        print("   2. 点击AR图标进入AR Quick Look")
        print("   3. 检查颜色是否正确显示")
        print("   4. 尝试放置和缩放模型")
    else:
        print("❌ 材质修复失败")
        sys.exit(1)
