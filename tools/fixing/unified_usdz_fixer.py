#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一USDZ修复工具

整合所有修复功能，确保USDZ文件完全符合Apple官方示例：
1. 材质修复：使用diffuseColor，智能推断元素颜色
2. 可见性修复：确保几何体可见，居中到原点
3. ARKit兼容性：正确的单位、法线、可见性设置
4. 结构修复：正确的文件结构和命名
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

class UnifiedUSDZFixer:
    """统一USDZ修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
        
        # 元素颜色映射
        self.element_colors = {
            'Li': (0.8, 0.5, 1.0),    # 锂 - 紫色
            'Co': (0.9, 0.4, 0.0),    # 钴 - 橙色
            'O': (1.0, 0.0, 0.0),     # 氧 - 红色
            'C': (0.3, 0.3, 0.3),     # 碳 - 深灰色
            'N': (0.0, 0.0, 1.0),     # 氮 - 蓝色
            'H': (1.0, 1.0, 1.0),     # 氢 - 白色
            'S': (1.0, 1.0, 0.0),     # 硫 - 黄色
            'P': (1.0, 0.5, 0.0),     # 磷 - 橙色
            'Fe': (0.9, 0.4, 0.0),    # 铁 - 橙红色
            'Ni': (0.3, 0.8, 0.3),    # 镍 - 绿色
            'Cu': (0.7, 0.4, 0.1),    # 铜 - 棕色
            'Zn': (0.5, 0.5, 0.7),    # 锌 - 蓝灰色
        }
    
    def fix_usdz_file(self, usdz_path: str, output_path: str = None) -> bool:
        """
        统一修复USDZ文件
        
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
        
        logger.info(f"开始统一USDZ修复: {usdz_path}")
        
        try:
            # 检查是否为USDZ文件
            if usdz_path.endswith('.usdz'):
                return self._fix_usdz_file(usdz_path, output_path)
            else:
                # 直接处理USD文件
                return self._fix_usd_file(usdz_path, output_path)
                
        except Exception as e:
            logger.error(f"统一修复时出错: {e}")
            return False
    
    def _fix_usdz_file(self, usdz_path: str, output_path: str) -> bool:
        """修复USDZ文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 解压USDZ文件
            logger.info("解压USDZ文件...")
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
        """修复USD Stage"""
        try:
            # 打开USD stage
            stage = Usd.Stage.Open(usd_path)
            if not stage:
                logger.error(f"无法打开USD文件: {usd_path}")
                return False
            
            logger.info(f"USD文件信息:")
            logger.info(f"  根层: {stage.GetRootLayer().identifier}")
            
            # 1. 修复单位设置
            self._fix_units(stage)
            
            # 2. 修复根节点和默认Prim
            self._fix_root_and_default_prim(stage)
            
            # 3. 修复材质（确保使用diffuseColor）
            self._fix_materials(stage)
            
            # 4. 修复几何体（可见性、法线、居中）
            self._fix_geometry(stage)
            
            # 5. 移除不兼容的属性
            self._remove_incompatible_properties(stage)
            
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
    
    def _fix_units(self, stage: Usd.Stage):
        """修复单位设置"""
        try:
            current_units = UsdGeom.GetStageMetersPerUnit(stage)
            logger.info(f"当前单位: {current_units} 米/单位")
            
            # 对于分子结构，0.01米/单位更合适（1单位=1厘米）
            target_units = 0.01
            if abs(current_units - target_units) > 0.001:
                UsdGeom.SetStageMetersPerUnit(stage, target_units)
                self.fixes_applied.append(f"单位从 {current_units} 改为 {target_units} 米/单位")
                logger.info(f"✓ 单位已修复为 {target_units} 米/单位")
            else:
                logger.info(f"✓ 单位设置正确")
                
        except Exception as e:
            error_msg = f"修复单位设置失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _fix_root_and_default_prim(self, stage: Usd.Stage):
        """修复根节点和默认Prim"""
        try:
            # 确保有默认Prim
            default_prim = stage.GetDefaultPrim()
            if not default_prim:
                # 如果没有默认prim，设置第一个有效prim为默认
                for prim in stage.GetPseudoRoot().GetChildren():
                    if prim.GetTypeName():
                        stage.SetDefaultPrim(prim)
                        default_prim = prim
                        logger.info(f"设置默认Prim: {prim.GetPath()}")
                        self.fixes_applied.append("设置默认Prim")
                        break
            
            # 确保根节点可见
            if default_prim and default_prim.IsA(UsdGeom.Imageable):
                imageable = UsdGeom.Imageable(default_prim)
                visibility_attr = imageable.GetVisibilityAttr()
                
                if not visibility_attr or visibility_attr.Get() != UsdGeom.Tokens.inherited:
                    imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
                    logger.info(f"修复根节点可见性: {default_prim.GetPath()}")
                    self.fixes_applied.append("修复根节点可见性")
                    
        except Exception as e:
            error_msg = f"修复根节点失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _fix_materials(self, stage: Usd.Stage):
        """修复材质，确保使用diffuseColor并智能推断颜色"""
        try:
            materials_fixed = 0
            
            # 遍历所有材质
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    material = UsdShade.Material(prim)
                    material_name = prim.GetName()
                    logger.info(f"检查材质: {material_name}")
                    
                    # 首先清理重复的shader
                    self._clean_duplicate_shaders(material, material_name)
                    
                    try:
                        # 获取surface shader
                        surface_output = material.GetSurfaceOutput()
                        if surface_output:
                            # 安全地获取连接源，避免ConnectableAPI错误
                            try:
                                connected_source = surface_output.GetConnectedSource()
                                if connected_source and len(connected_source) >= 2:
                                    shader_prim = connected_source[0]
                                    if shader_prim and shader_prim.IsValid():
                                        shader = UsdShade.Shader(shader_prim)
                                        
                                        # 确保shader类型正确
                                        shader_id = shader.GetIdAttr()
                                        if not shader_id or shader_id.Get() != "UsdPreviewSurface":
                                            shader.GetIdAttr().Set("UsdPreviewSurface")
                                            self.fixes_applied.append(f"设置 {material_name} shader类型为UsdPreviewSurface")
                                        
                                        # 处理颜色属性
                                        self._fix_material_color(shader, material_name)
                                        
                                        # 移除不兼容的属性
                                        self._remove_incompatible_material_attributes(shader_prim, material_name)
                                        
                                        materials_fixed += 1
                                else:
                                    logger.info(f"  材质 {material_name} 没有连接的shader，跳过")
                            except Exception as shader_error:
                                logger.warning(f"  获取材质 {material_name} 的shader连接时出错: {shader_error}")
                                # 尝试创建新的shader
                                self._create_default_shader(material, material_name)
                                materials_fixed += 1
                        else:
                            logger.info(f"  材质 {material_name} 没有surface输出，创建默认shader")
                            self._create_default_shader(material, material_name)
                            materials_fixed += 1
                    except Exception as material_error:
                        logger.warning(f"  处理材质 {material_name} 时出错: {material_error}")
                        continue
            
            if materials_fixed > 0:
                logger.info(f"✓ 修复了 {materials_fixed} 个材质")
            else:
                logger.info("✓ 所有材质都正确")
                
        except Exception as e:
            error_msg = f"修复材质失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _fix_material_color(self, shader: UsdShade.Shader, material_name: str):
        """修复材质颜色属性"""
        base_color_input = shader.GetInput('baseColor')
        diffuse_input = shader.GetInput('diffuseColor')
        
        # 智能推断元素颜色
        inferred_color = self._infer_element_color(material_name)
        
        if base_color_input and base_color_input.HasValue():
            # 有baseColor，转换为diffuseColor
            base_color_value = base_color_input.Get()
            logger.info(f"  发现baseColor: {base_color_value}，转换为diffuseColor")
            
            if not diffuse_input:
                diffuse_input = shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f)
            
            diffuse_input.Set(base_color_value)
            shader.GetPrim().RemoveProperty('inputs:baseColor')
            
            logger.info(f"  ✓ 转换为diffuseColor: {base_color_value}")
            self.fixes_applied.append(f"材质 {material_name} 从baseColor转换为diffuseColor")
            
        elif diffuse_input and diffuse_input.HasValue():
            # 已经有diffuseColor，确保没有baseColor
            if base_color_input:
                shader.GetPrim().RemoveProperty('inputs:baseColor')
                self.fixes_applied.append(f"材质 {material_name} 移除多余的baseColor")
            
            diffuse_value = diffuse_input.Get()
            logger.info(f"  ✓ 材质已使用diffuseColor: {diffuse_value}")
            
        else:
            # 既没有baseColor也没有diffuseColor，使用推断的颜色
            if not diffuse_input:
                diffuse_input = shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f)
            
            diffuse_input.Set(Gf.Vec3f(*inferred_color))
            logger.info(f"  ✓ 设置推断的diffuseColor: {inferred_color}")
            self.fixes_applied.append(f"材质 {material_name} 设置推断的diffuseColor")
    
    def _infer_element_color(self, material_name: str) -> tuple:
        """根据材质名称推断元素颜色"""
        material_name_upper = material_name.upper()
        
        # 检查是否包含已知元素
        for element, color in self.element_colors.items():
            if element.upper() in material_name_upper:
                logger.info(f"  推断元素: {element} -> 颜色: {color}")
                return color
        
        # 默认颜色（浅灰色）
        default_color = (0.8, 0.8, 0.8)
        logger.info(f"  使用默认颜色: {default_color}")
        return default_color
    
    def _create_default_shader(self, material: UsdShade.Material, material_name: str):
        """为材质创建默认shader"""
        try:
            # 创建shader prim - 使用surfaceShader作为标准名称
            shader_path = material.GetPrim().GetPath().AppendChild("surfaceShader")
            shader_prim = material.GetPrim().GetStage().DefinePrim(shader_path, "Shader")
            shader = UsdShade.Shader(shader_prim)
            
            # 设置shader类型
            shader.CreateIdAttr("UsdPreviewSurface")
            
            # 推断并设置颜色
            inferred_color = self._infer_element_color(material_name)
            diffuse_input = shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f)
            diffuse_input.Set(Gf.Vec3f(*inferred_color))
            
            # 连接到材质的surface输出 - 这是AR Quick Look要求的标准连接
            # surface是UsdPreviewSurface shader的标准输出端口
            material.CreateSurfaceOutput().ConnectToSource(shader, "surface")
            
            logger.info(f"  ✓ 为材质 {material_name} 创建了默认UsdPreviewSurface shader，颜色: {inferred_color}")
            self.fixes_applied.append(f"为材质 {material_name} 创建默认UsdPreviewSurface shader")
            
        except Exception as e:
            logger.warning(f"  创建默认shader失败: {e}")
    
    def _clean_duplicate_shaders(self, material: UsdShade.Material, material_name: str):
        """清理材质中的重复shader定义"""
        try:
            material_prim = material.GetPrim()
            shaders_to_remove = []
            surface_shader_path = None
            
            # 获取当前连接的surface shader路径
            surface_output = material.GetSurfaceOutput()
            if surface_output:
                try:
                    connected_source = surface_output.GetConnectedSource()
                    if connected_source and len(connected_source) >= 2:
                        surface_shader_path = connected_source[0].GetPath()
                except:
                    pass
            
            # 查找所有shader子节点
            for child in material_prim.GetChildren():
                if child.IsA(UsdShade.Shader):
                    child_path = child.GetPath()
                    child_name = child.GetName()
                    
                    # 如果这个shader不是连接到surface的shader，且名称是PBRShader，则标记删除
                    if (child_path != surface_shader_path and 
                        child_name == "PBRShader"):
                        shaders_to_remove.append(child_path)
                        logger.info(f"  标记删除重复shader: {child_path}")
            
            # 删除重复的shader
            stage = material_prim.GetStage()
            for shader_path in shaders_to_remove:
                stage.RemovePrim(shader_path)
                logger.info(f"  ✓ 删除重复shader: {shader_path}")
                self.fixes_applied.append(f"删除材质 {material_name} 的重复shader")
                
        except Exception as e:
            logger.warning(f"  清理重复shader失败: {e}")
    
    def _remove_incompatible_material_attributes(self, shader_prim: Usd.Prim, material_name: str):
        """移除不兼容的材质属性 - AR Quick Look只支持基本的UsdPreviewSurface属性"""
        # AR Quick Look支持的基本属性，其他都移除
        # 参考：https://developer.apple.com/documentation/arkit/usdz_schemas_for_ar
        incompatible_attrs = [
            'inputs:metallic',
            'inputs:roughness', 
            'inputs:clearcoat',
            'inputs:clearcoatRoughness',
            'inputs:opacity',
            'inputs:opacityThreshold',
            'inputs:ior',
            'inputs:normal',
            'inputs:displacement',
            'inputs:occlusion',
            'inputs:specularColor',
            'inputs:emissiveColor'
        ]
        
        removed_count = 0
        for attr_name in incompatible_attrs:
            if shader_prim.HasProperty(attr_name):
                shader_prim.RemoveProperty(attr_name)
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"  移除了 {removed_count} 个不兼容的材质属性")
            self.fixes_applied.append(f"移除 {material_name} 的不兼容属性")
    
    def _fix_geometry(self, stage: Usd.Stage):
        """修复几何体（可见性、法线、居中）"""
        try:
            # 查找所有网格
            meshes = []
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    meshes.append(prim)
            
            logger.info(f"找到 {len(meshes)} 个网格")
            
            if not meshes:
                logger.warning("未找到网格几何体")
                return
            
            # 修复每个网格
            for mesh_prim in meshes:
                self._fix_single_mesh(stage, mesh_prim)
                
        except Exception as e:
            error_msg = f"修复几何体失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _fix_single_mesh(self, stage: Usd.Stage, mesh_prim: Usd.Prim):
        """修复单个网格"""
        mesh_name = mesh_prim.GetName()
        logger.info(f"  修复网格: {mesh_name}")
        
        mesh = UsdGeom.Mesh(mesh_prim)
        
        # 1. 修复可见性
        self._fix_mesh_visibility(mesh_prim)
        
        # 2. 修复法线
        self._fix_mesh_normals(mesh)
        
        # 3. 居中到原点
        self._center_mesh_to_origin(mesh)
        
        # 4. 移除GeomSubsets
        self._remove_geom_subsets(stage, mesh_prim)
        
        # 5. 设置边界框
        self._set_mesh_extent(mesh)
    
    def _fix_mesh_visibility(self, mesh_prim: Usd.Prim):
        """修复网格可见性"""
        imageable = UsdGeom.Imageable(mesh_prim)
        
        # 修复可见性
        visibility_attr = imageable.GetVisibilityAttr()
        if not visibility_attr or visibility_attr.Get() != UsdGeom.Tokens.inherited:
            imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
            logger.info(f"    设置可见性为inherited")
            self.fixes_applied.append(f"修复 {mesh_prim.GetName()} 可见性")
        
        # 修复purpose
        purpose_attr = imageable.GetPurposeAttr()
        current_purpose = purpose_attr.Get() if purpose_attr else None
        
        if current_purpose and current_purpose != UsdGeom.Tokens.render:
            imageable.CreatePurposeAttr(UsdGeom.Tokens.render)
            logger.info(f"    设置purpose为render")
            self.fixes_applied.append(f"修复 {mesh_prim.GetName()} purpose")
    
    def _fix_mesh_normals(self, mesh: UsdGeom.Mesh):
        """修复网格法线"""
        points_attr = mesh.GetPointsAttr()
        faces_attr = mesh.GetFaceVertexIndicesAttr()
        face_counts_attr = mesh.GetFaceVertexCountsAttr()
        
        if not (points_attr and faces_attr and face_counts_attr):
            logger.warning(f"    网格缺少几何数据")
            return
        
        points = points_attr.Get()
        faces = faces_attr.Get()
        face_counts = face_counts_attr.Get()
        
        if not (points and faces and face_counts):
            logger.warning(f"    网格几何数据为空")
            return
        
        # 检查法线
        normals_attr = mesh.GetNormalsAttr()
        face_vertex_count = len(faces)
        
        needs_fix = False
        if normals_attr and normals_attr.HasValue():
            existing_normals = normals_attr.Get()
            if len(existing_normals) != face_vertex_count:
                logger.info(f"    法线数量不匹配，重新计算")
                needs_fix = True
        else:
            logger.info(f"    缺少法线数据，需要计算")
            needs_fix = True
        
        if needs_fix:
            normals = self._calculate_face_varying_normals(points, faces, face_counts)
            if normals and len(normals) == face_vertex_count:
                if not normals_attr:
                    normals_attr = mesh.CreateNormalsAttr()
                normals_attr.Set(normals)
                mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
                
                logger.info(f"    ✓ 设置了 {len(normals)} 个法线向量")
                self.fixes_applied.append(f"重新计算 {mesh.GetPrim().GetName()} 法线")
    
    def _calculate_face_varying_normals(self, points, face_indices, face_counts):
        """计算面顶点插值法线"""
        try:
            normals = []
            index_offset = 0
            
            for face_count in face_counts:
                if face_count >= 3:
                    # 获取面的前三个顶点
                    i0 = face_indices[index_offset]
                    i1 = face_indices[index_offset + 1]
                    i2 = face_indices[index_offset + 2]
                    
                    # 计算法线
                    p0 = Gf.Vec3f(points[i0])
                    p1 = Gf.Vec3f(points[i1])
                    p2 = Gf.Vec3f(points[i2])
                    
                    v1 = p1 - p0
                    v2 = p2 - p0
                    normal = v1 ^ v2
                    
                    if normal.GetLength() > 0:
                        normal = normal.GetNormalized()
                    else:
                        normal = Gf.Vec3f(0, 1, 0)
                    
                    # 为面的每个顶点添加法线
                    for _ in range(face_count):
                        normals.append(normal)
                else:
                    # 少于3个顶点的面使用默认法线
                    default_normal = Gf.Vec3f(0, 1, 0)
                    for _ in range(face_count):
                        normals.append(default_normal)
                
                index_offset += face_count
            
            return normals
            
        except Exception as e:
            logger.error(f"计算法线失败: {e}")
            return None
    
    def _center_mesh_to_origin(self, mesh: UsdGeom.Mesh):
        """将网格居中到原点"""
        points_attr = mesh.GetPointsAttr()
        if not points_attr:
            return
        
        points = points_attr.Get()
        if not points or len(points) == 0:
            return
        
        # 计算边界框和中心
        bbox = Gf.Range3d()
        for point in points:
            point_3d = Gf.Vec3d(float(point[0]), float(point[1]), float(point[2]))
            bbox.UnionWith(point_3d)
        
        min_pt = bbox.GetMin()
        max_pt = bbox.GetMax()
        center = (min_pt + max_pt) / 2.0
        size = max_pt - min_pt
        
        # 检查是否需要居中
        center_distance = (center[0]**2 + center[1]**2 + center[2]**2)**0.5
        max_dimension = max(size[0], size[1], size[2])
        
        if center_distance > max_dimension * 0.5:
            logger.info(f"    居中到原点（距离: {center_distance:.3f}）")
            
            # 居中顶点
            centered_points = []
            for point in points:
                new_point = Gf.Vec3f(
                    float(point[0]) - center[0],
                    float(point[1]) - center[1], 
                    float(point[2]) - center[2]
                )
                centered_points.append(new_point)
            
            points_attr.Set(centered_points)
            logger.info(f"    ✓ 模型已居中")
            self.fixes_applied.append(f"居中 {mesh.GetPrim().GetName()} 到原点")
    
    def _remove_geom_subsets(self, stage: Usd.Stage, mesh_prim: Usd.Prim):
        """移除GeomSubset分组"""
        subsets_removed = 0
        children_to_remove = []
        
        for child in mesh_prim.GetChildren():
            if child.IsA(UsdGeom.Subset):
                children_to_remove.append(child.GetPath())
                subsets_removed += 1
        
        for path in children_to_remove:
            stage.RemovePrim(path)
        
        if subsets_removed > 0:
            logger.info(f"    移除了 {subsets_removed} 个GeomSubset")
            self.fixes_applied.append(f"移除 {mesh_prim.GetName()} 的GeomSubset")
    
    def _set_mesh_extent(self, mesh: UsdGeom.Mesh):
        """设置网格边界框"""
        points_attr = mesh.GetPointsAttr()
        if not points_attr:
            return
        
        points = points_attr.Get()
        if not points or len(points) == 0:
            return
        
        # 计算边界框
        bbox = Gf.Range3d()
        for point in points:
            point_3d = Gf.Vec3d(float(point[0]), float(point[1]), float(point[2]))
            bbox.UnionWith(point_3d)
        
        min_pt = bbox.GetMin()
        max_pt = bbox.GetMax()
        
        # 设置extent
        extent_attr = mesh.GetExtentAttr()
        if not extent_attr:
            extent_attr = mesh.CreateExtentAttr()
        
        extent_attr.Set([min_pt, max_pt])
        logger.info(f"    设置边界框")
        self.fixes_applied.append(f"设置 {mesh.GetPrim().GetName()} 边界框")
    
    def _remove_incompatible_properties(self, stage: Usd.Stage):
        """移除不兼容的属性"""
        try:
            properties_removed = 0
            
            # 遍历所有prim，移除不兼容的属性
            for prim in stage.Traverse():
                # 移除displayColor依赖
                if prim.HasProperty('primvars:displayColor'):
                    prim.RemoveProperty('primvars:displayColor')
                    properties_removed += 1
                    self.fixes_applied.append(f"移除 {prim.GetName()} 的displayColor")
                
                if prim.HasProperty('primvars:displayOpacity'):
                    prim.RemoveProperty('primvars:displayOpacity')
                    properties_removed += 1
                    self.fixes_applied.append(f"移除 {prim.GetName()} 的displayOpacity")
            
            if properties_removed > 0:
                logger.info(f"✓ 移除了 {properties_removed} 个不兼容属性")
            else:
                logger.info("✓ 没有发现不兼容属性")
                
        except Exception as e:
            error_msg = f"移除不兼容属性失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
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
        print("用法: python unified_usdz_fixer.py <usdz_file> [output_file]")
        print("")
        print("功能:")
        print("  - 材质修复：使用diffuseColor，智能推断元素颜色")
        print("  - 可见性修复：确保几何体可见，居中到原点")
        print("  - ARKit兼容性：正确的单位、法线、可见性设置")
        print("  - 结构修复：正确的文件结构和命名")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(usdz_file):
        logger.error(f"文件不存在: {usdz_file}")
        sys.exit(1)
    
    # 创建修复器并执行修复
    fixer = UnifiedUSDZFixer()
    success = fixer.fix_usdz_file(usdz_file, output_file)
    
    if success:
        logger.info("✅ 统一USDZ修复成功")
        logger.info("")
        logger.info("修复内容:")
        logger.info("  ✓ 材质修复（diffuseColor + 智能颜色）")
        logger.info("  ✓ 可见性修复（居中 + 可见性）")
        logger.info("  ✓ ARKit兼容性（单位 + 法线）")
        logger.info("  ✓ 结构修复（清理 + 优化）")
        
        if fixer.errors:
            logger.warning("注意事项:")
            for error in fixer.errors:
                logger.warning(f"  ⚠️ {error}")
        
        sys.exit(0)
    else:
        logger.error("❌ 统一USDZ修复失败")
        if fixer.errors:
            logger.error("错误详情:")
            for error in fixer.errors:
                logger.error(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()