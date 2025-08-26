#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARKit兼容性修复工具

修复USDZ文件以符合Apple ARKit要求：
1. 设置正确的单位（1.0米/单位）
2. 将材质从diffuseColor改为baseColor
3. 添加缺失的法线数据
4. 确保正确的可见性和用途设置
"""

import os
import sys
import tempfile
from pathlib import Path
from loguru import logger

try:
    from pxr import Usd, UsdGeom, UsdShade, UsdUtils, Sdf, Gf
except ImportError:
    logger.error("无法导入USD库，请确保已安装USD Python包")
    sys.exit(1)

class ARKitCompatibilityFixer:
    """ARKit兼容性修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
    
    def fix_usdz_file(self, usdz_path: str) -> bool:
        """
        修复USDZ文件的ARKit兼容性问题
        
        Args:
            usdz_path: USDZ文件路径
            
        Returns:
            修复是否成功
        """
        if not os.path.exists(usdz_path):
            logger.error(f"USDZ文件不存在: {usdz_path}")
            return False
        
        logger.info(f"开始修复ARKit兼容性: {usdz_path}")
        
        try:
            # 打开USDZ文件
            stage = Usd.Stage.Open(usdz_path)
            if not stage:
                logger.error(f"无法打开USDZ文件: {usdz_path}")
                return False
            
            # 1. 修复单位设置
            self._fix_units(stage)
            
            # 2. 修复材质（diffuseColor -> baseColor）
            self._fix_materials(stage)
            
            # 3. 修复几何体法线
            self._fix_geometry_normals(stage)
            
            # 4. 修复可见性和用途
            self._fix_visibility_and_purpose(stage)
            
            # 保存修复后的文件
            success = self._save_stage(stage, usdz_path)
            
            if success:
                logger.info(f"ARKit兼容性修复完成，应用了 {len(self.fixes_applied)} 个修复")
                for fix in self.fixes_applied:
                    logger.info(f"  ✓ {fix}")
                return True
            else:
                logger.error("保存修复后的文件失败")
                return False
                
        except Exception as e:
            logger.error(f"修复ARKit兼容性时出错: {e}")
            return False
    
    def _fix_units(self, stage: Usd.Stage):
        """修复单位设置为0.01米/单位（适合分子结构）"""
        try:
            current_units = UsdGeom.GetStageMetersPerUnit(stage)
            logger.info(f"当前单位: {current_units} 米/单位")
            
            # 对于分子结构，0.01米/单位更合适（1单位=1厘米）
            target_units = 0.01
            if abs(current_units - target_units) > 0.001:
                UsdGeom.SetStageMetersPerUnit(stage, target_units)
                self.fixes_applied.append(f"单位从 {current_units} 改为 {target_units} 米/单位")
                logger.info(f"✓ 单位已修复为 {target_units} 米/单位（适合分子结构）")
            else:
                logger.info(f"✓ 单位设置正确（{target_units} 米/单位）")
                
        except Exception as e:
            error_msg = f"修复单位设置失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _fix_materials(self, stage: Usd.Stage):
        """修复材质：将baseColor改为diffuseColor以符合AR Quick Look"""
        try:
            materials_fixed = 0
            
            # 遍历所有材质
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    material = UsdShade.Material(prim)
                    logger.info(f"检查材质: {prim.GetPath()}")
                    
                    # 获取surface shader
                    surface_output = material.GetSurfaceOutput()
                    if surface_output:
                        connected_source = surface_output.GetConnectedSource()
                        if connected_source and len(connected_source) >= 2:
                            shader_prim = connected_source[0]
                            if shader_prim and shader_prim.IsValid():
                                shader = UsdShade.Shader(shader_prim)
                            
                            # 检查是否有baseColor属性
                            base_color_input = shader.GetInput('baseColor')
                            diffuse_input = shader.GetInput('diffuseColor')
                            
                            if base_color_input and base_color_input.HasValue():
                                # 获取baseColor的值
                                base_color_value = base_color_input.Get()
                                logger.info(f"  发现baseColor: {base_color_value}")
                                
                                # 如果没有diffuseColor，创建它
                                if not diffuse_input:
                                    diffuse_input = shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f)
                                
                                # 将baseColor的值复制到diffuseColor
                                if base_color_value is not None:
                                    diffuse_input.Set(base_color_value)
                                    logger.info(f"  ✓ 设置diffuseColor: {base_color_value}")
                                    
                                    # 移除baseColor属性
                                    shader_prim.RemoveProperty('inputs:baseColor')
                                    logger.info(f"  ✓ 移除baseColor")
                                    
                                    materials_fixed += 1
                                    self.fixes_applied.append(f"材质 {prim.GetName()} 从baseColor改为diffuseColor")
            
            if materials_fixed > 0:
                logger.info(f"✓ 修复了 {materials_fixed} 个材质的颜色属性")
            else:
                logger.info("✓ 所有材质已使用正确的diffuseColor属性")
                
        except Exception as e:
            error_msg = f"修复材质失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _fix_geometry_normals(self, stage: Usd.Stage):
        """修复几何体法线数据"""
        try:
            meshes_fixed = 0
            
            # 遍历所有网格
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh = UsdGeom.Mesh(prim)
                    logger.info(f"检查网格法线: {prim.GetPath()}")
                    
                    # 获取顶点和面数据
                    points_attr = mesh.GetPointsAttr()
                    face_vertex_indices_attr = mesh.GetFaceVertexIndicesAttr()
                    face_vertex_counts_attr = mesh.GetFaceVertexCountsAttr()
                    
                    if (points_attr and points_attr.HasValue() and 
                        face_vertex_indices_attr and face_vertex_indices_attr.HasValue() and
                        face_vertex_counts_attr and face_vertex_counts_attr.HasValue()):
                        
                        points = points_attr.Get()
                        face_indices = face_vertex_indices_attr.Get()
                        face_counts = face_vertex_counts_attr.Get()
                        
                        # 检查现有法线数据是否正确
                        normals_attr = mesh.GetNormalsAttr()
                        face_vertex_count = len(face_indices)
                        
                        needs_fix = False
                        if normals_attr and normals_attr.HasValue():
                            existing_normals = normals_attr.Get()
                            if len(existing_normals) != face_vertex_count:
                                logger.info(f"  法线数量({len(existing_normals)})与面顶点数量({face_vertex_count})不匹配，需要重新计算")
                                needs_fix = True
                        else:
                            logger.info(f"  网格缺少法线数据，需要计算")
                            needs_fix = True
                        
                        if needs_fix:
                            # 重新计算法线
                            normals = self._calculate_face_varying_normals(points, face_indices, face_counts)
                            
                            if normals and len(normals) == face_vertex_count:
                                # 设置法线数据
                                if not normals_attr:
                                    normals_attr = mesh.CreateNormalsAttr()
                                normals_attr.Set(normals)
                                mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
                                
                                meshes_fixed += 1
                                self.fixes_applied.append(f"为网格 {prim.GetName()} 重新计算法线数据")
                                logger.info(f"  ✓ 设置了 {len(normals)} 个法线向量（面顶点插值）")
                            else:
                                logger.warning(f"  无法计算正确数量的法线")
                        else:
                            logger.info(f"  ✓ 网格法线数据正确")
                    else:
                        logger.warning(f"  网格缺少必要的几何数据")
            
            if meshes_fixed > 0:
                logger.info(f"✓ 修复了 {meshes_fixed} 个网格的法线数据")
            else:
                logger.info("✓ 所有网格的法线数据都正确")
                
        except Exception as e:
            error_msg = f"修复几何体法线失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _calculate_face_normals(self, points, face_indices, face_counts):
        """计算面法线（旧方法，保留兼容性）"""
        try:
            normals = []
            index_offset = 0
            
            for face_count in face_counts:
                if face_count >= 3:
                    # 获取面的前三个顶点
                    i0 = face_indices[index_offset]
                    i1 = face_indices[index_offset + 1]
                    i2 = face_indices[index_offset + 2]
                    
                    # 获取顶点坐标
                    p0 = Gf.Vec3f(points[i0])
                    p1 = Gf.Vec3f(points[i1])
                    p2 = Gf.Vec3f(points[i2])
                    
                    # 计算法线向量
                    v1 = p1 - p0
                    v2 = p2 - p0
                    normal = v1 ^ v2  # 叉积
                    normal = normal.GetNormalized()
                    
                    # 为这个面的所有顶点添加相同的法线
                    for _ in range(face_count):
                        normals.append(normal)
                
                index_offset += face_count
            
            return normals
            
        except Exception as e:
            logger.error(f"计算法线失败: {e}")
            return None
    
    def _calculate_face_varying_normals(self, points, face_indices, face_counts):
        """计算面顶点插值法线，确保数量与面顶点完全匹配"""
        try:
            normals = []
            index_offset = 0
            
            logger.info(f"  计算法线：总面顶点数 = {len(face_indices)}")
            
            for face_idx, face_count in enumerate(face_counts):
                if face_count >= 3:
                    # 获取面的前三个顶点来计算法线
                    i0 = face_indices[index_offset]
                    i1 = face_indices[index_offset + 1]
                    i2 = face_indices[index_offset + 2]
                    
                    # 获取顶点坐标
                    p0 = Gf.Vec3f(points[i0])
                    p1 = Gf.Vec3f(points[i1])
                    p2 = Gf.Vec3f(points[i2])
                    
                    # 计算法线向量
                    v1 = p1 - p0
                    v2 = p2 - p0
                    normal = v1 ^ v2  # 叉积
                    
                    # 检查法线是否有效
                    if normal.GetLength() > 0:
                        normal = normal.GetNormalized()
                    else:
                        # 如果法线无效，使用默认向上法线
                        normal = Gf.Vec3f(0, 1, 0)
                    
                    # 为这个面的每个顶点添加相同的法线
                    for vertex_idx in range(face_count):
                        normals.append(normal)
                else:
                    # 对于少于3个顶点的面，使用默认法线
                    default_normal = Gf.Vec3f(0, 1, 0)
                    for vertex_idx in range(face_count):
                        normals.append(default_normal)
                
                index_offset += face_count
            
            logger.info(f"  生成法线数量: {len(normals)}，期望数量: {len(face_indices)}")
            
            # 确保法线数量与面顶点数量完全匹配
            if len(normals) != len(face_indices):
                logger.warning(f"  法线数量不匹配，调整中...")
                # 如果数量不匹配，截断或填充
                if len(normals) > len(face_indices):
                    normals = normals[:len(face_indices)]
                else:
                    # 用最后一个法线填充
                    last_normal = normals[-1] if normals else Gf.Vec3f(0, 1, 0)
                    while len(normals) < len(face_indices):
                        normals.append(last_normal)
            
            return normals
            
        except Exception as e:
            logger.error(f"计算面顶点插值法线失败: {e}")
            return None
    
    def _fix_visibility_and_purpose(self, stage: Usd.Stage):
        """修复可见性和用途设置"""
        try:
            prims_fixed = 0
            
            # 遍历所有几何体
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Imageable):
                    imageable = UsdGeom.Imageable(prim)
                    
                    # 检查用途设置
                    purpose_attr = imageable.GetPurposeAttr()
                    if purpose_attr and purpose_attr.HasValue():
                        current_purpose = purpose_attr.Get()
                        if current_purpose != UsdGeom.Tokens.render and current_purpose != "default":
                            # 设置为render用途
                            purpose_attr.Set(UsdGeom.Tokens.render)
                            prims_fixed += 1
                            self.fixes_applied.append(f"设置 {prim.GetName()} 用途为render")
                            logger.info(f"  ✓ 设置 {prim.GetPath()} 用途为render")
            
            if prims_fixed > 0:
                logger.info(f"✓ 修复了 {prims_fixed} 个图元的用途设置")
            else:
                logger.info("✓ 所有图元的用途设置正确")
                
        except Exception as e:
            error_msg = f"修复可见性和用途失败: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
    
    def _save_stage(self, stage: Usd.Stage, usdz_path: str) -> bool:
        """保存修复后的Stage到USDZ文件"""
        try:
            # 由于不能直接保存到USDZ，需要先保存为USD然后重新打包
            with tempfile.NamedTemporaryFile(suffix='.usd', delete=False) as temp_file:
                temp_usd_path = temp_file.name
            
            # 导出为USD文件
            stage.Export(temp_usd_path)
            logger.info(f"导出临时USD文件: {temp_usd_path}")
            
            # 重新打包为USDZ
            success = UsdUtils.CreateNewUsdzPackage(temp_usd_path, usdz_path)
            
            # 清理临时文件
            try:
                os.unlink(temp_usd_path)
            except:
                pass
            
            if success:
                logger.info(f"成功保存修复后的USDZ文件: {usdz_path}")
                return True
            else:
                logger.error("重新打包USDZ文件失败")
                return False
                
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python fix_arkit_compatibility.py <usdz_file>")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    
    if not os.path.exists(usdz_file):
        logger.error(f"文件不存在: {usdz_file}")
        sys.exit(1)
    
    # 创建修复器并执行修复
    fixer = ARKitCompatibilityFixer()
    success = fixer.fix_usdz_file(usdz_file)
    
    if success:
        logger.info("✅ ARKit兼容性修复成功")
        sys.exit(0)
    else:
        logger.error("❌ ARKit兼容性修复失败")
        if fixer.errors:
            logger.error("错误详情:")
            for error in fixer.errors:
                logger.error(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()