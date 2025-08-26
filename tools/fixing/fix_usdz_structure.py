#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USDZ文件结构修复工具
修复USDZ文件中的文件命名和结构问题
"""

import os
import sys
import tempfile
import shutil
import zipfile
from pathlib import Path
from loguru import logger
from pxr import Usd, UsdGeom, Sdf

class USDZStructureFixer:
    """USDZ结构修复器类"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
    
    def fix_usdz_structure(self, usdz_path: str) -> bool:
        """
        修复USDZ文件的结构，直接修改原文件
        
        Args:
            usdz_path: USDZ文件路径
            
        Returns:
            修复是否成功
        """
        if not os.path.exists(usdz_path):
            logger.error(f"USDZ文件不存在: {usdz_path}")
            return False
        
        logger.info(f"开始修复USDZ结构: {usdz_path}")
        
        try:
            # 检查是否需要修复
            if self._check_structure_validity(usdz_path):
                logger.info("USDZ结构已经正确，无需修复")
                return True
            
            # 执行结构修复
            return self._perform_structure_fix(usdz_path)
                
        except Exception as e:
            logger.error(f"修复USDZ结构时出错: {e}")
            return False
    
    def _check_structure_validity(self, usdz_path: str) -> bool:
        """检查USDZ结构是否有效"""
        try:
            with zipfile.ZipFile(usdz_path, 'r') as zf:
                file_list = zf.namelist()
                
                # 检查是否有临时文件名
                for filename in file_list:
                    if filename.startswith('tmp') and filename.endswith('.usd'):
                        logger.info(f"发现临时USD文件名: {filename}")
                        return False
                    
                # 检查是否有正确的USD文件
                usd_files = [f for f in file_list if f.endswith('.usd') or f.endswith('.usdc')]
                if not usd_files:
                    logger.warning("未找到USD文件")
                    return False
                
                # 检查主USD文件是否有合理的名称
                main_usd = usd_files[0]
                if main_usd.startswith('tmp') or len(main_usd.split('.')[0]) < 3:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"检查USDZ结构时出错: {e}")
            return False
    
    def _perform_structure_fix(self, usdz_path: str) -> bool:
        """执行结构修复"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. 解压USDZ文件
                logger.info("解压USDZ文件...")
                with zipfile.ZipFile(usdz_path, 'r') as zf:
                    zf.extractall(temp_path)
                
                # 2. 查找USD文件
                usd_files = list(temp_path.glob('*.usd*'))
                if not usd_files:
                    logger.error("未找到USD文件")
                    return False
                
                main_usd = usd_files[0]
                logger.info(f"找到USD文件: {main_usd.name}")
                
                # 3. 确定正确的文件名
                base_name = Path(usdz_path).stem
                if base_name.startswith('final_'):
                    base_name = base_name[6:]  # 移除 'final_' 前缀
                correct_usd_name = f"{base_name}.usd"
                
                # 4. 重命名USD文件（如果需要）
                if main_usd.name != correct_usd_name:
                    new_usd_path = temp_path / correct_usd_name
                    main_usd.rename(new_usd_path)
                    logger.info(f"重命名USD文件: {main_usd.name} -> {correct_usd_name}")
                    main_usd = new_usd_path
                    self.fixes_applied.append(f"重命名USD文件为 {correct_usd_name}")
                
                # 5. 验证USD文件内容
                if not self._validate_usd_content(str(main_usd)):
                    logger.error("USD文件内容验证失败")
                    return False
                
                # 6. 重新创建USDZ文件（无压缩）
                logger.info("重新创建USDZ文件...")
                with zipfile.ZipFile(usdz_path, 'w', zipfile.ZIP_STORED) as zf:
                    # 添加所有文件
                    for file_path in temp_path.iterdir():
                        if file_path.is_file():
                            zf.write(file_path, file_path.name)
                
                # 7. 验证修复后的文件
                file_size = os.path.getsize(usdz_path)
                logger.info(f"USDZ结构修复完成: {usdz_path} ({file_size:,} 字节)")
                
                if self.fixes_applied:
                    logger.info(f"应用了 {len(self.fixes_applied)} 个修复:")
                    for fix in self.fixes_applied:
                        logger.info(f"  ✓ {fix}")
                
                return True
                
        except Exception as e:
            logger.error(f"执行结构修复时出错: {e}")
            return False
    
    def _validate_usd_content(self, usd_path: str) -> bool:
        """验证USD文件内容"""
        try:
            stage = Usd.Stage.Open(usd_path)
            if not stage:
                logger.error(f"无法打开USD文件: {usd_path}")
                return False
            
            # 检查是否有几何体
            has_geometry = False
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh = UsdGeom.Mesh(prim)
                    points = mesh.GetPointsAttr().Get()
                    if points and len(points) > 0:
                        has_geometry = True
                        logger.info(f"验证USD内容: 找到网格，包含 {len(points)} 个顶点")
                        break
            
            if not has_geometry:
                logger.warning("USD文件中未找到有效的几何体")
                return False
            
            # 设置默认Prim（如果没有的话）
            if not stage.GetDefaultPrim():
                root_prims = [p for p in stage.GetPseudoRoot().GetChildren() if p.GetTypeName()]
                if root_prims:
                    stage.SetDefaultPrim(root_prims[0])
                    stage.Save()
                    logger.info(f"设置默认Prim: {root_prims[0].GetPath()}")
                    self.fixes_applied.append("设置默认Prim")
            
            return True
            
        except Exception as e:
            logger.error(f"验证USD内容时出错: {e}")
            return False

def fix_usdz_structure(input_usdz_path: str, output_usdz_path: str = None) -> bool:
    """
    修复USDZ文件结构
    
    Args:
        input_usdz_path: 输入USDZ文件路径
        output_usdz_path: 输出USDZ文件路径（可选）
        
    Returns:
        bool: 修复是否成功
    """
    if not os.path.exists(input_usdz_path):
        print(f"❌ 输入文件不存在: {input_usdz_path}")
        return False
    
    if output_usdz_path is None:
        output_usdz_path = input_usdz_path.replace('.usdz', '_fixed.usdz')
    
    print(f"🔧 修复USDZ文件结构: {input_usdz_path}")
    print(f"📤 输出文件: {output_usdz_path}")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 1. 提取USDZ文件
            print("📦 提取USDZ文件...")
            with zipfile.ZipFile(input_usdz_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # 2. 查找USD文件
            usd_files = list(temp_path.glob('*.usd*'))
            if not usd_files:
                print("❌ 未找到USD文件")
                return False
            
            original_usd = usd_files[0]
            print(f"📄 找到USD文件: {original_usd.name}")
            
            # 3. 确定正确的文件名
            base_name = Path(input_usdz_path).stem
            if base_name.startswith('final_'):
                base_name = base_name[6:]  # 移除 'final_' 前缀
            
            correct_usd_name = f"{base_name}.usd"
            correct_usd_path = temp_path / correct_usd_name
            
            print(f"🎯 目标USD文件名: {correct_usd_name}")
            
            # 4. 重命名USD文件
            if original_usd.name != correct_usd_name:
                print(f"📝 重命名: {original_usd.name} -> {correct_usd_name}")
                shutil.move(str(original_usd), str(correct_usd_path))
            else:
                correct_usd_path = original_usd
            
            # 5. 验证USD文件内容
            print("🔍 验证USD文件内容...")
            stage = Usd.Stage.Open(str(correct_usd_path))
            if not stage:
                print("❌ USD文件无效")
                return False
            
            # 检查几何体
            mesh_count = 0
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh_count += 1
                    mesh = UsdGeom.Mesh(prim)
                    points = mesh.GetPointsAttr().Get()
                    if points:
                        print(f"  🔷 网格 {prim.GetPath()}: {len(points)} 个顶点")
            
            print(f"  📊 总计: {mesh_count} 个网格")
            
            # 6. 设置默认Prim
            root_prims = [p for p in stage.GetPseudoRoot().GetChildren()]
            if root_prims and not stage.GetDefaultPrim():
                default_prim = root_prims[0]
                stage.SetDefaultPrim(default_prim)
                print(f"🎯 设置默认Prim: {default_prim.GetPath()}")
                stage.Save()
            
            # 7. 创建新的USDZ文件（无压缩）
            print("📦 创建新的USDZ文件（无压缩）...")
            with zipfile.ZipFile(output_usdz_path, 'w', zipfile.ZIP_STORED) as zip_ref:
                zip_ref.write(correct_usd_path, correct_usd_name)
            
            # 8. 验证输出文件
            if os.path.exists(output_usdz_path):
                file_size = os.path.getsize(output_usdz_path)
                print(f"✅ USDZ文件修复成功!")
                print(f"📏 文件大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                
                # 验证新文件
                with zipfile.ZipFile(output_usdz_path, 'r') as zip_ref:
                    files = zip_ref.namelist()
                    print(f"📁 包含文件: {files}")
                
                return True
            else:
                print("❌ 输出文件创建失败")
                return False
                
    except Exception as e:
        print(f"❌ 修复过程中发生错误: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python fix_usdz_structure.py <input_usdz_file> [output_usdz_file]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = fix_usdz_structure(input_file, output_file)
    if success:
        print("\n🎉 USDZ文件结构修复完成!")
    else:
        print("\n💥 USDZ文件结构修复失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()