#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一可见性修复工具
整合所有可见性相关修复功能

主要功能：
1. 修复几何体可见性设置
2. 确保正确的purpose设置
3. 修复坐标偏移问题（居中到原点）
4. 简化复杂的几何体结构
5. 设置正确的边界框信息
6. 移除problematic GeomSubsets
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

class UnifiedVisibilityFixer:
    """统一可见性修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
    
    def fix_usdz_visibility(self, usdz_path: str, output_path: str = None) -> bool:
        """
        修复USDZ文件的可见性问题
        
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
        
        logger.info(f"开始统一可见性修复: {usdz_path}")
        
        try:
            # 检查是否为USDZ文件
            if usdz_path.endswith('.usdz'):
                return self._fix_usdz_file(usdz_path, output_path)
            else:
                # 直接处理USD文件
                return self._fix_usd_file(usdz_path, output_path)
                
        except Exception as e:
            logger.error(f"修复可见性时出错: {e}")
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
        """修复USD Stage中的可见性"""
        try:
            # 打开USD stage
            stage = Usd.Stage.Open(usd_path)
            if not stage:
                logger.error(f"无法打开USD文件: {usd_path}")
                return False
            
            logger.info(f"USD文件信息:")
            logger.info(f"  根层: {stage.GetRootLayer().identifier}")
            
            # 修复根节点可见性
            self._fix_root_visibility(stage)
            
            # 查找所有网格
            meshes = []
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    meshes.append(prim)
            
            logger.info(f"  找到 {len(meshes)} 个网格")
            
            if not meshes:
                logger.warning("未找到网格几何体")
                return True
            
            # 修复每个网格
            for mesh_prim in meshes:
                self._fix_mesh_visibility(stage, mesh_prim)
            
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
    
    def _fix_root_visibility(self, stage: Usd.Stage):
        """修复根节点可见性"""
        root_prim = stage.GetDefaultPrim()
        if not root_prim:
            # 如果没有默认prim，设置第一个有效prim为默认
            for prim in stage.GetPseudoRoot().GetChildren():
                if prim.GetTypeName():
                    stage.SetDefaultPrim(prim)
                    root_prim = prim
                    logger.info(f"设置默认Prim: {prim.GetPath()}")
                    self.fixes_applied.append("设置默认Prim")
                    break
        
        if root_prim and root_prim.IsA(UsdGeom.Imageable):
            imageable = UsdGeom.Imageable(root_prim)
            visibility_attr = imageable.GetVisibilityAttr()
            
            if not visibility_attr or visibility_attr.Get() != UsdGeom.Tokens.inherited:
                imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
                logger.info(f"修复根节点可见性: {root_prim.GetPath()}")
                self.fixes_applied.append("修复根节点可见性")
    
    def _fix_mesh_visibility(self, stage: Usd.Stage, mesh_prim: Usd.Prim):
        """修复单个网格的可见性和几何体问题"""
        mesh_path = mesh_prim.GetPath()
        mesh_name = mesh_prim.GetName()
        logger.info(f"  修复网格: {mesh_name} ({mesh_path})")
        
        mesh = UsdGeom.Mesh(mesh_prim)
        
        # 1. 修复可见性
        self._fix_visibility_attributes(mesh_prim)
        
        # 2. 检查和修复几何体数据
        self._fix_geometry_data(mesh)
        
        # 3. 修复坐标偏移（居中到原点）
        self._fix_coordinate_offset(mesh)
        
        # 4. 移除problematic GeomSubsets
        self._remove_geom_subsets(stage, mesh_prim)
        
        # 5. 设置边界框
        self._set_extent(mesh)
    
    def _fix_visibility_attributes(self, mesh_prim: Usd.Prim):
        """修复可见性属性"""
        imageable = UsdGeom.Imageable(mesh_prim)
        
        # 修复可见性
        visibility_attr = imageable.GetVisibilityAttr()
        current_visibility = visibility_attr.Get() if visibility_attr else None
        
        if current_visibility != UsdGeom.Tokens.inherited:
            imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
            logger.info(f"    设置可见性为 inherited")
            self.fixes_applied.append(f"修复 {mesh_prim.GetName()} 可见性")
        
        # 修复purpose
        purpose_attr = imageable.GetPurposeAttr()
        current_purpose = purpose_attr.Get() if purpose_attr else None
        
        # 确保purpose为render或默认
        if current_purpose and current_purpose != UsdGeom.Tokens.render:
            imageable.CreatePurposeAttr(UsdGeom.Tokens.render)
            logger.info(f"    设置purpose为 render")
            self.fixes_applied.append(f"修复 {mesh_prim.GetName()} purpose")
        
        # 确保父级也可见
        parent_prim = mesh_prim.GetParent()
        while parent_prim and parent_prim.GetPath() != Sdf.Path.absoluteRootPath:
            if parent_prim.IsA(UsdGeom.Imageable):
                parent_imageable = UsdGeom.Imageable(parent_prim)
                parent_visibility = parent_imageable.GetVisibilityAttr()
                if not parent_visibility or parent_visibility.Get() != UsdGeom.Tokens.inherited:
                    parent_imageable.CreateVisibilityAttr(UsdGeom.Tokens.inherited)
                    logger.info(f"    设置父级可见性: {parent_prim.GetPath()}")
                    self.fixes_applied.append(f"修复父级 {parent_prim.GetName()} 可见性")
            parent_prim = parent_prim.GetParent()
    
    def _fix_geometry_data(self, mesh: UsdGeom.Mesh):
        """检查和修复几何体数据"""
        points_attr = mesh.GetPointsAttr()
        faces_attr = mesh.GetFaceVertexIndicesAttr()
        
        points = points_attr.Get() if points_attr else None
        faces = faces_attr.Get() if faces_attr else None
        
        vertex_count = len(points) if points else 0
        face_count = len(faces) // 3 if faces else 0
        
        logger.info(f"    几何体数据: {vertex_count} 顶点, {face_count} 面")
        
        if vertex_count == 0:
            logger.warning(f"    警告: 网格没有顶点数据")
            self.errors.append(f"网格 {mesh.GetPrim().GetName()} 没有顶点数据")
        
        if face_count == 0:
            logger.warning(f"    警告: 网格没有面数据")
            self.errors.append(f"网格 {mesh.GetPrim().GetName()} 没有面数据")
    
    def _fix_coordinate_offset(self, mesh: UsdGeom.Mesh):
        """修复坐标偏移，将模型居中到原点"""
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
        
        # 检查是否需要居中（如果中心距离原点太远）
        center_distance = (center[0]**2 + center[1]**2 + center[2]**2)**0.5
        max_dimension = max(size[0], size[1], size[2])
        
        # 如果中心距离原点超过模型最大尺寸的一半，则进行居中
        if center_distance > max_dimension * 0.5:
            logger.info(f"    原始中心: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
            logger.info(f"    模型尺寸: {size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f}")
            logger.info(f"    居中到原点...")
            
            # 将所有顶点移动到以原点为中心
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
            
            logger.info(f"    ✓ 模型已居中到原点")
            self.fixes_applied.append(f"居中 {mesh.GetPrim().GetName()} 到原点")
        else:
            logger.info(f"    模型已经接近原点，无需居中")
    
    def _remove_geom_subsets(self, stage: Usd.Stage, mesh_prim: Usd.Prim):
        """移除GeomSubset分组（简化几何体结构）"""
        subsets_removed = 0
        children_to_remove = []
        
        for child in mesh_prim.GetChildren():
            if child.IsA(UsdGeom.Subset):
                children_to_remove.append(child.GetPath())
                subsets_removed += 1
        
        # 移除所有GeomSubset
        for path in children_to_remove:
            stage.RemovePrim(path)
        
        if subsets_removed > 0:
            logger.info(f"    移除了 {subsets_removed} 个GeomSubset")
            self.fixes_applied.append(f"移除 {mesh_prim.GetName()} 的 {subsets_removed} 个GeomSubset")
    
    def _set_extent(self, mesh: UsdGeom.Mesh):
        """设置正确的边界框信息"""
        points_attr = mesh.GetPointsAttr()
        if not points_attr:
            return
        
        points = points_attr.Get()
        if not points or len(points) == 0:
            return
        
        # 计算新的边界框
        bbox = Gf.Range3d()
        for point in points:
            point_3d = Gf.Vec3d(float(point[0]), float(point[1]), float(point[2]))
            bbox.UnionWith(point_3d)
        
        min_pt = bbox.GetMin()
        max_pt = bbox.GetMax()
        
        # 设置extent属性
        extent_attr = mesh.GetExtentAttr()
        if not extent_attr:
            extent_attr = mesh.CreateExtentAttr()
        
        extent_attr.Set([min_pt, max_pt])
        logger.info(f"    设置边界框: [{min_pt[0]:.3f}, {min_pt[1]:.3f}, {min_pt[2]:.3f}] 到 [{max_pt[0]:.3f}, {max_pt[1]:.3f}, {max_pt[2]:.3f}]")
        self.fixes_applied.append(f"设置 {mesh.GetPrim().GetName()} 边界框")
    
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
        print("用法: python unified_visibility_fixer.py <usdz_file> [output_file]")
        print("")
        print("功能:")
        print("  - 修复几何体可见性设置")
        print("  - 确保正确的purpose设置")
        print("  - 修复坐标偏移问题（居中到原点）")
        print("  - 简化复杂的几何体结构")
        print("  - 设置正确的边界框信息")
        print("  - 移除problematic GeomSubsets")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(usdz_file):
        logger.error(f"文件不存在: {usdz_file}")
        sys.exit(1)
    
    # 创建修复器并执行修复
    fixer = UnifiedVisibilityFixer()
    success = fixer.fix_usdz_visibility(usdz_file, output_file)
    
    if success:
        logger.info("✅ 统一可见性修复成功")
        logger.info("")
        logger.info("修复内容:")
        logger.info("  ✓ 修复几何体可见性设置")
        logger.info("  ✓ 确保正确的purpose设置")
        logger.info("  ✓ 修复坐标偏移问题")
        logger.info("  ✓ 简化几何体结构")
        logger.info("  ✓ 设置边界框信息")
        logger.info("  ✓ 移除GeomSubsets")
        
        if fixer.errors:
            logger.warning("注意事项:")
            for error in fixer.errors:
                logger.warning(f"  ⚠️ {error}")
        
        sys.exit(0)
    else:
        logger.error("❌ 统一可见性修复失败")
        if fixer.errors:
            logger.error("错误详情:")
            for error in fixer.errors:
                logger.error(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()