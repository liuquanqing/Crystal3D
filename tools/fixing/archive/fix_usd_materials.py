#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USD材质修复工具
专门修复USDZ文件中的材质颜色问题
"""

import os
import tempfile
import zipfile
from pathlib import Path
from converter.material_standardizer import MaterialStandardizer

try:
    from pxr import Usd, UsdShade, UsdGeom, Sdf, Gf
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("警告: USD Python绑定不可用")

class USDMaterialFixer:
    """USD材质修复器"""
    
    def __init__(self):
        if not USD_AVAILABLE:
            raise ImportError("USD Python绑定不可用")
        self.standardizer = MaterialStandardizer()
    
    def fix_usdz_materials(self, usdz_path: str, output_path: str = None) -> bool:
        """修复USDZ文件中的材质"""
        if not os.path.exists(usdz_path):
            print(f"❌ 文件不存在: {usdz_path}")
            return False
        
        if output_path is None:
            output_path = usdz_path.replace('.usdz', '_fixed_materials.usdz')
        
        print(f"🔧 修复USD材质: {usdz_path}")
        
        try:
            # 1. 解压USDZ文件
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 解压
                with zipfile.ZipFile(usdz_path, 'r') as zf:
                    zf.extractall(temp_path)
                
                # 找到主USD文件
                usd_files = list(temp_path.glob('*.usd*'))
                if not usd_files:
                    print("❌ 未找到USD文件")
                    return False
                
                main_usd = usd_files[0]
                print(f"📄 处理USD文件: {main_usd.name}")
                
                # 2. 修复材质
                success = self._fix_usd_materials(str(main_usd))
                if not success:
                    print("❌ 材质修复失败")
                    return False
                
                # 3. 重新打包
                self._repack_usdz(temp_path, output_path)
                
                print(f"✅ 材质修复完成: {output_path}")
                return True
                
        except Exception as e:
            print(f"❌ 修复过程中出错: {e}")
            return False
    
    def _fix_usd_materials(self, usd_path: str) -> bool:
        """修复USD文件中的材质"""
        try:
            # 打开USD stage
            stage = Usd.Stage.Open(usd_path)
            if not stage:
                print(f"❌ 无法打开USD文件: {usd_path}")
                return False
            
            print(f"📋 USD文件信息:")
            print(f"   根层: {stage.GetRootLayer().identifier}")
            print(f"   原语数量: {len(list(stage.Traverse()))}")
            
            # 查找所有材质
            materials = []
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    materials.append(prim)
            
            print(f"   材质数量: {len(materials)}")
            
            if not materials:
                print("⚠️ 未找到材质，创建新材质...")
                self._create_materials_from_geometry(stage)
            else:
                print("🎨 修复现有材质...")
                for material in materials:
                    self._fix_material(material)
            
            # 保存修改 - 使用更安全的保存方式
            try:
                # 获取原始文件大小
                original_size = os.path.getsize(usd_path)
                print(f"   原始文件大小: {original_size/1024:.1f} KB")
                
                # 保存到临时文件，然后替换原文件
                temp_usd_path = usd_path + ".tmp"
                stage.GetRootLayer().Export(temp_usd_path)
                
                # 检查新文件大小
                new_size = os.path.getsize(temp_usd_path)
                print(f"   修复后文件大小: {new_size/1024:.1f} KB")
                
                # 如果新文件太小，可能有问题
                if new_size < original_size * 0.5:  # 如果新文件小于原文件的50%
                    print(f"⚠️ 警告：修复后文件大小显著减小，可能丢失数据")
                    print(f"   原始: {original_size/1024:.1f} KB -> 修复后: {new_size/1024:.1f} KB")
                
                # 替换原文件
                os.replace(temp_usd_path, usd_path)
                print("💾 USD文件已保存")
                return True
                
            except Exception as save_error:
                print(f"❌ 保存USD文件时出错: {save_error}")
                # 尝试使用原始保存方法
                stage.Save()
                print("💾 使用备用方法保存USD文件")
                return True
            
        except Exception as e:
            print(f"❌ 修复USD材质时出错: {e}")
            return False
    
    def _fix_material(self, material_prim):
        """修复单个材质"""
        material_name = material_prim.GetName()
        print(f"   🎨 修复材质: {material_name}")
        
        # 推断元素
        element = self._infer_element_from_material_name(material_name)
        if not element:
            print(f"     ⚠️ 无法推断元素，使用默认颜色")
            color = (0.5, 0.5, 0.5)
        else:
            color = self.standardizer.get_standard_color(element)
            print(f"     🔍 元素: {element}, 颜色: {color}")
        
        # 创建或更新UsdPreviewSurface
        material = UsdShade.Material(material_prim)
        
        # 查找现有的surface shader
        surface_output = material.GetSurfaceOutput()
        if surface_output.HasConnectedSource():
            source_info = surface_output.GetConnectedSource()
            shader_prim = source_info[0].GetPrim()
        else:
            # 创建新的surface shader
            shader_path = material_prim.GetPath().AppendChild("surface")
            shader_prim = material_prim.GetStage().DefinePrim(shader_path, "Shader")
            shader = UsdShade.Shader(shader_prim)
            shader.CreateIdAttr("UsdPreviewSurface")
            
            # 连接到材质输出
            shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
            material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        
        # 设置颜色属性
        shader = UsdShade.Shader(shader_prim)
        
        # 设置diffuseColor (AR Quick Look兼容)
        diffuse_color_input = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
        diffuse_color_input.Set(Gf.Vec3f(color[0], color[1], color[2]))
        
        # 设置其他PBR属性
        metallic_input = shader.CreateInput("metallic", Sdf.ValueTypeNames.Float)
        metallic_input.Set(0.0)
        
        roughness_input = shader.CreateInput("roughness", Sdf.ValueTypeNames.Float)
        roughness_input.Set(0.5)
        
        opacity_input = shader.CreateInput("opacity", Sdf.ValueTypeNames.Float)
        opacity_input.Set(1.0)
        
        print(f"     ✅ 材质已更新")
    
    def _create_materials_from_geometry(self, stage):
        """从几何体创建材质"""
        # 查找所有mesh
        meshes = []
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                meshes.append(prim)
        
        print(f"   找到 {len(meshes)} 个mesh")
        
        # 为每个mesh创建材质
        materials_scope = stage.DefinePrim("/Materials", "Scope")
        
        for i, mesh_prim in enumerate(meshes):
            mesh_name = mesh_prim.GetName()
            print(f"     🔷 处理mesh: {mesh_name}")
            
            # 推断元素
            element = self._infer_element_from_material_name(mesh_name)
            if not element:
                element = f"Element{i+1}"
            
            # 创建材质
            material_name = f"{element}_Material"
            material_path = materials_scope.GetPath().AppendChild(material_name)
            material_prim = stage.DefinePrim(material_path, "Material")
            
            # 设置材质属性
            self._fix_material(material_prim)
            
            # 绑定材质到mesh
            mesh = UsdGeom.Mesh(mesh_prim)
            material = UsdShade.Material(material_prim)
            UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)
            
            print(f"     ✅ 已绑定材质: {material_name}")
    
    def _infer_element_from_material_name(self, name: str) -> str:
        """从名称推断元素"""
        # 清理名称
        clean_name = name.replace('_MAT', '').replace('_Material', '').replace('atom_', '')
        
        # 常见元素映射
        element_map = {
            'oxygen': 'O', 'lithium': 'Li', 'cobalt': 'Co',
            'sodium': 'Na', 'chlorine': 'Cl', 'iron': 'Fe',
            'copper': 'Cu', 'zinc': 'Zn', 'carbon': 'C',
            'nitrogen': 'N', 'hydrogen': 'H'
        }
        
        # 检查直接匹配
        for key, element in element_map.items():
            if key.lower() in clean_name.lower():
                return element
        
        # 检查是否是元素符号
        if clean_name in self.standardizer.STANDARD_CPK_COLORS:
            return clean_name
        
        # 尝试提取元素符号
        import re
        match = re.search(r'([A-Z][a-z]?)', clean_name)
        if match:
            element = match.group(1)
            if element in self.standardizer.STANDARD_CPK_COLORS:
                return element
        
        return None
    
    def _repack_usdz(self, temp_dir: Path, output_path: str):
        """重新打包USDZ文件，保留所有原始文件"""
        # 使用无压缩模式，保持原始文件大小
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zf:
            # 按照特定顺序添加文件，确保USD文件在前
            usd_files = []
            other_files = []
            
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    if file_path.suffix.lower() in ['.usd', '.usda', '.usdc']:
                        usd_files.append(file_path)
                    else:
                        other_files.append(file_path)
            
            # 先添加USD文件
            for file_path in usd_files:
                arcname = file_path.relative_to(temp_dir)
                file_size_kb = file_path.stat().st_size / 1024
                zf.write(file_path, arcname)
                print(f"   📄 添加USD文件: {arcname} ({file_size_kb:.1f} KB)")
            
            # 再添加其他文件（OBJ、MTL、纹理等）
            for file_path in other_files:
                arcname = file_path.relative_to(temp_dir)
                file_size_kb = file_path.stat().st_size / 1024
                zf.write(file_path, arcname)
                print(f"   📎 添加资源文件: {arcname} ({file_size_kb:.1f} KB)")
        
        # 验证文件大小
        file_size = os.path.getsize(output_path)
        print(f"📦 已重新打包: {output_path} ({file_size/1024:.1f} KB)")
        
        # 验证USDZ内容
        with zipfile.ZipFile(output_path, 'r') as zf:
            print(f"📋 USDZ包内容:")
            for info in zf.infolist():
                print(f"   - {info.filename}: {info.file_size/1024:.1f} KB (压缩后: {info.compress_size/1024:.1f} KB)")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python fix_usd_materials.py <usdz_file> [output_file]")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not USD_AVAILABLE:
        print("❌ USD Python绑定不可用")
        sys.exit(1)
    
    fixer = USDMaterialFixer()
    success = fixer.fix_usdz_materials(usdz_file, output_file)
    
    if success:
        print("\n🎯 材质修复完成！")
    else:
        print("\n❌ 材质修复失败")
        sys.exit(1)

if __name__ == '__main__':
    main()