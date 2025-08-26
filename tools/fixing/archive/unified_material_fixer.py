#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一材质修复工具
整合所有材质相关修复功能，确保与AR Quick Look官方示例一致

主要功能：
1. 使用diffuseColor而非baseColor（符合USD规范和AR Quick Look要求）
2. 创建标准的UsdPreviewSurface材质
3. 智能元素颜色推断
4. 移除不兼容的材质属性
5. 确保材质正确绑定
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path
from loguru import logger

try:
    from pxr import Usd, UsdGeom, UsdShade, UsdUtils, Sdf, Gf
except ImportError:
    logger.error("无法导入USD库，请确保已安装USD Python包")
    sys.exit(1)

# 标准CPK颜色（基于官方化学元素颜色）
STANDARD_CPK_COLORS = {
    'H': (1.0, 1.0, 1.0),      # 氢 - 白色
    'C': (0.2, 0.2, 0.2),      # 碳 - 黑色
    'N': (0.0, 0.0, 1.0),      # 氮 - 蓝色
    'O': (1.0, 0.0, 0.0),      # 氧 - 红色
    'F': (0.0, 1.0, 0.0),      # 氟 - 绿色
    'Na': (0.67, 0.36, 0.95),  # 钠 - 紫色
    'Mg': (0.54, 1.0, 0.0),    # 镁 - 绿色
    'Al': (0.75, 0.65, 0.65),  # 铝 - 灰色
    'Si': (0.94, 0.78, 0.63),  # 硅 - 棕色
    'P': (1.0, 0.5, 0.0),      # 磷 - 橙色
    'S': (1.0, 1.0, 0.19),     # 硫 - 黄色
    'Cl': (0.12, 0.94, 0.12),  # 氯 - 绿色
    'K': (0.56, 0.25, 0.83),   # 钾 - 紫色
    'Ca': (0.24, 1.0, 0.0),    # 钙 - 绿色
    'Ti': (0.75, 0.76, 0.78),  # 钛 - 银色
    'Cr': (0.54, 0.6, 0.78),   # 铬 - 蓝灰色
    'Mn': (0.61, 0.48, 0.78),  # 锰 - 紫色
    'Fe': (0.88, 0.4, 0.2),    # 铁 - 橙红色
    'Co': (0.94, 0.56, 0.63),  # 钴 - 粉红色
    'Ni': (0.31, 0.82, 0.31),  # 镍 - 绿色
    'Cu': (0.78, 0.5, 0.2),    # 铜 - 棕色
    'Zn': (0.49, 0.5, 0.69),   # 锌 - 蓝灰色
    'Li': (0.8, 0.5, 1.0),     # 锂 - 紫色
}

class UnifiedMaterialFixer:
    """统一材质修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
    
    def fix_usdz_materials(self, usdz_path: str, output_path: str = None) -> bool:
        """
        修复USDZ文件中的材质，确保与AR Quick Look兼容
        
        Args:
            usdz_path: USDZ文件路径
            output_path: 输出路径（可选）
            
        Returns:
            修复是否成功
        """
        if not os.path.exists(usdz_path):
            logger.error(f"USDZ文件不存在: {usdz_path}")
            return False
        
        if output_path is None:
            output_path = usdz_path
        
        logger.info(f"开始统一材质修复: {usdz_path}")
        
        try:
            # 检查是否为USDZ文件
            if usdz_path.endswith('.usdz'):
                return self._fix_usdz_file(usdz_path, output_path)
            else:
                # 直接处理USD文件
                return self._fix_usd_file(usdz_path, output_path)
                
        except Exception as e:
            logger.error(f"修复材质时出错: {e}")
            return False
    
    def _fix_usdz_file(self, usdz_path: str, output_path: str) -> bool:
        """修复USDZ文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 解压USDZ文件
            with zipfile.ZipFile(usdz_path, 'r') as zf:
                zf.extractall(temp_path)
            
            # 找到主USD文件
            usd_files = list(temp_path.glob('*.usd*'))
            if not usd_files:
                logger.error("未找到USD文件")
                return False
            
            main_usd = usd_files[0]
            logger.info(f"处理USD文件: {main_usd.name}")
            
            # 修复USD文件
            success = self._fix_usd_stage(str(main_usd))
            if not success:
                return False
            
            # 重新打包
            return self._repack_usdz(temp_path, output_path)
    
    def _fix_usd_file(self, usd_path: str, output_path: str) -> bool:
        """直接修复USD文件"""
        success = self._fix_usd_stage(usd_path)
        if success and output_path != usd_path:
            # 如果需要输出到不同路径
            import shutil
            shutil.copy2(usd_path, output_path)
        return success
    
    def _fix_usd_stage(self, usd_path: str) -> bool:
        """修复USD Stage中的材质"""
        try:
            # 打开USD stage
            stage = Usd.Stage.Open(usd_path)
            if not stage:
                logger.error(f"无法打开USD文件: {usd_path}")
                return False
            
            logger.info(f"USD文件信息:")
            logger.info(f"  根层: {stage.GetRootLayer().identifier}")
            logger.info(f"  原语数量: {len(list(stage.Traverse()))}")
            
            # 查找所有材质和几何体
            materials = []
            meshes = []
            
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    materials.append(prim)
                elif prim.IsA(UsdGeom.Mesh):
                    meshes.append(prim)
            
            logger.info(f"  材质数量: {len(materials)}")
            logger.info(f"  网格数量: {len(meshes)}")
            
            # 如果没有材质，创建新材质
            if not materials:
                logger.info("未找到材质，创建新材质...")
                materials = self._create_materials_from_geometry(stage, meshes)
            else:
                logger.info("修复现有材质...")
                for material_prim in materials:
                    self._fix_material(stage, material_prim)
            
            # 确保所有网格都绑定了材质
            self._ensure_material_bindings(stage, meshes, materials)
            
            # 保存修改
            stage.Save()
            logger.info("USD文件已保存")
            
            if self.fixes_applied:
                logger.info(f"应用了 {len(self.fixes_applied)} 个修复:")
                for fix in self.fixes_applied:
                    logger.info(f"  ✓ {fix}")
            
            return True
            
        except Exception as e:
            logger.error(f"修复USD Stage时出错: {e}")
            return False
    
    def _fix_material(self, stage: Usd.Stage, material_prim: Usd.Prim):
        """修复单个材质"""
        material_name = material_prim.GetName()
        logger.info(f"  修复材质: {material_name}")
        
        # 推断元素和颜色
        element = self._infer_element_from_name(material_name)
        if element and element in STANDARD_CPK_COLORS:
            color = STANDARD_CPK_COLORS[element]
            logger.info(f"    推断元素: {element}, 颜色: {color}")
        else:
            # 使用默认橙色（醒目且易于识别）
            color = (1.0, 0.5, 0.0)
            logger.info(f"    使用默认颜色: {color}")
        
        # 创建或更新UsdPreviewSurface
        material = UsdShade.Material(material_prim)
        
        # 查找或创建surface shader
        surface_shader = self._get_or_create_surface_shader(stage, material)
        
        # 设置材质属性（符合AR Quick Look要求）
        self._set_material_properties(surface_shader, color)
        
        self.fixes_applied.append(f"修复材质 {material_name}")
    
    def _get_or_create_surface_shader(self, stage: Usd.Stage, material: UsdShade.Material) -> UsdShade.Shader:
        """获取或创建surface shader"""
        # 查找现有的surface shader
        surface_output = material.GetSurfaceOutput()
        if surface_output.HasConnectedSource():
            source_info = surface_output.GetConnectedSource()
            shader_prim = source_info[0].GetPrim()
            if shader_prim and shader_prim.IsA(UsdShade.Shader):
                return UsdShade.Shader(shader_prim)
        
        # 创建新的surface shader
        shader_path = material.GetPrim().GetPath().AppendChild("surfaceShader")
        if stage.GetPrimAtPath(shader_path):
            stage.RemovePrim(shader_path)
        
        shader_prim = stage.DefinePrim(shader_path, "Shader")
        shader = UsdShade.Shader(shader_prim)
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # 连接到材质输出
        shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        
        logger.info(f"    创建新的UsdPreviewSurface shader")
        return shader
    
    def _set_material_properties(self, shader: UsdShade.Shader, color: tuple):
        """设置材质属性（符合AR Quick Look和USD规范）"""
        # 移除可能存在的baseColor（避免冲突）
        if shader.GetInput("baseColor"):
            shader.GetPrim().RemoveProperty("inputs:baseColor")
            logger.info(f"    移除baseColor属性")
        
        # 设置diffuseColor（AR Quick Look和USD规范要求）
        diffuse_input = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
        diffuse_input.Set(Gf.Vec3f(color[0], color[1], color[2]))
        logger.info(f"    设置diffuseColor: {color}")
        
        # 设置其他PBR属性
        metallic_input = shader.CreateInput("metallic", Sdf.ValueTypeNames.Float)
        metallic_input.Set(0.0)  # 非金属
        
        roughness_input = shader.CreateInput("roughness", Sdf.ValueTypeNames.Float)
        roughness_input.Set(0.5)  # 中等粗糙度
        
        opacity_input = shader.CreateInput("opacity", Sdf.ValueTypeNames.Float)
        opacity_input.Set(1.0)  # 完全不透明
        
        # 移除可能导致问题的属性
        problematic_inputs = ["specularColor", "emissiveColor"]
        for input_name in problematic_inputs:
            if shader.GetInput(input_name):
                shader.GetPrim().RemoveProperty(f"inputs:{input_name}")
                logger.info(f"    移除 {input_name} 属性")
    
    def _create_materials_from_geometry(self, stage: Usd.Stage, meshes: list) -> list:
        """从几何体创建材质"""
        materials = []
        
        # 创建Materials scope
        materials_scope_path = "/Materials"
        if not stage.GetPrimAtPath(materials_scope_path):
            materials_scope = stage.DefinePrim(materials_scope_path, "Scope")
        else:
            materials_scope = stage.GetPrimAtPath(materials_scope_path)
        
        logger.info(f"为 {len(meshes)} 个网格创建材质...")
        
        for i, mesh_prim in enumerate(meshes):
            mesh_name = mesh_prim.GetName()
            logger.info(f"  处理网格: {mesh_name}")
            
            # 推断元素
            element = self._infer_element_from_name(mesh_name)
            if not element:
                element = f"Element{i+1}"
            
            # 创建材质
            material_name = f"{element}_Material"
            material_path = materials_scope.GetPath().AppendChild(material_name)
            
            # 如果材质已存在，使用唯一名称
            counter = 1
            while stage.GetPrimAtPath(material_path):
                material_name = f"{element}_Material_{counter}"
                material_path = materials_scope.GetPath().AppendChild(material_name)
                counter += 1
            
            material_prim = stage.DefinePrim(material_path, "Material")
            materials.append(material_prim)
            
            # 设置材质属性
            self._fix_material(stage, material_prim)
            
            # 绑定材质到网格
            material = UsdShade.Material(material_prim)
            UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)
            
            logger.info(f"    创建并绑定材质: {material_name}")
        
        return materials
    
    def _ensure_material_bindings(self, stage: Usd.Stage, meshes: list, materials: list):
        """确保所有网格都绑定了材质"""
        if not materials:
            return
        
        default_material = UsdShade.Material(materials[0])
        
        for mesh_prim in meshes:
            binding_api = UsdShade.MaterialBindingAPI(mesh_prim)
            bound_material = binding_api.GetDirectBinding().GetMaterial()
            
            if not bound_material:
                binding_api.Bind(default_material)
                logger.info(f"  为网格 {mesh_prim.GetPath()} 绑定默认材质")
                self.fixes_applied.append(f"绑定材质到 {mesh_prim.GetName()}")
    
    def _infer_element_from_name(self, name: str) -> str:
        """从名称推断元素符号"""
        # 清理名称
        clean_name = name.replace('_MAT', '').replace('_Material', '').replace('atom_', '')
        clean_name = clean_name.replace('_', '').replace('-', '')
        
        # 常见元素名称映射
        element_map = {
            'oxygen': 'O', 'lithium': 'Li', 'cobalt': 'Co',
            'sodium': 'Na', 'chlorine': 'Cl', 'iron': 'Fe',
            'copper': 'Cu', 'zinc': 'Zn', 'carbon': 'C',
            'nitrogen': 'N', 'hydrogen': 'H', 'phosphorus': 'P',
            'sulfur': 'S', 'potassium': 'K', 'calcium': 'Ca'
        }
        
        # 检查直接匹配
        for key, element in element_map.items():
            if key.lower() in clean_name.lower():
                return element
        
        # 检查是否是元素符号
        if clean_name in STANDARD_CPK_COLORS:
            return clean_name
        
        # 尝试提取元素符号
        import re
        match = re.search(r'([A-Z][a-z]?)', clean_name)
        if match:
            element = match.group(1)
            if element in STANDARD_CPK_COLORS:
                return element
        
        return None
    
    def _repack_usdz(self, temp_dir: Path, output_path: str) -> bool:
        """重新打包USDZ文件"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zf:
                # 按照特定顺序添加文件
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
                    zf.write(file_path, arcname)
                    logger.info(f"  添加USD文件: {arcname}")
                
                # 再添加其他文件
                for file_path in other_files:
                    arcname = file_path.relative_to(temp_dir)
                    zf.write(file_path, arcname)
                    logger.info(f"  添加资源文件: {arcname}")
            
            file_size = os.path.getsize(output_path)
            logger.info(f"重新打包完成: {output_path} ({file_size/1024:.1f} KB)")
            return True
            
        except Exception as e:
            logger.error(f"重新打包USDZ时出错: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python unified_material_fixer.py <usdz_file> [output_file]")
        print("")
        print("功能:")
        print("  - 使用diffuseColor替代baseColor（符合USD规范和AR Quick Look）")
        print("  - 创建标准UsdPreviewSurface材质")
        print("  - 智能元素颜色推断")
        print("  - 移除不兼容的材质属性")
        print("  - 确保材质正确绑定")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(usdz_file):
        logger.error(f"文件不存在: {usdz_file}")
        sys.exit(1)
    
    # 创建修复器并执行修复
    fixer = UnifiedMaterialFixer()
    success = fixer.fix_usdz_materials(usdz_file, output_file)
    
    if success:
        logger.info("✅ 统一材质修复成功")
        logger.info("")
        logger.info("修复内容:")
        logger.info("  ✓ 使用diffuseColor（符合AR Quick Look要求）")
        logger.info("  ✓ 创建标准UsdPreviewSurface材质")
        logger.info("  ✓ 应用标准CPK元素颜色")
        logger.info("  ✓ 移除不兼容属性")
        logger.info("  ✓ 确保材质绑定")
        sys.exit(0)
    else:
        logger.error("❌ 统一材质修复失败")
        if fixer.errors:
            logger.error("错误详情:")
            for error in fixer.errors:
                logger.error(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()