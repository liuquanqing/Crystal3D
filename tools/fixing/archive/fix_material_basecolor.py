#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
材质baseColor修复工具

专门修复USDZ文件中材质的diffuseColor到baseColor的转换
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

class MaterialBaseColorFixer:
    """材质baseColor修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
    
    def fix_usdz_materials(self, usdz_path: str) -> bool:
        """
        修复USDZ文件中的材质，将baseColor改为diffuseColor以符合AR Quick Look
        
        Args:
            usdz_path: USDZ文件路径
            
        Returns:
            修复是否成功
        """
        if not os.path.exists(usdz_path):
            logger.error(f"USDZ文件不存在: {usdz_path}")
            return False
        
        logger.info(f"开始修复材质baseColor: {usdz_path}")
        
        try:
            # 打开USDZ文件
            stage = Usd.Stage.Open(usdz_path)
            if not stage:
                logger.error(f"无法打开USDZ文件: {usdz_path}")
                return False
            
            # 修复材质
            self._fix_materials(stage)
            
            # 保存修复后的文件
            success = self._save_stage(stage, usdz_path)
            
            if success:
                logger.info(f"材质修复完成，应用了 {len(self.fixes_applied)} 个修复")
                for fix in self.fixes_applied:
                    logger.info(f"  ✓ {fix}")
                return True
            else:
                logger.error("保存修复后的文件失败")
                return False
                
        except Exception as e:
            logger.error(f"修复材质时出错: {e}")
            return False
    
    def _fix_materials(self, stage: Usd.Stage):
        """修复材质：将baseColor改为diffuseColor以符合AR Quick Look"""
        try:
            materials_fixed = 0
            
            # 遍历所有材质
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    material = UsdShade.Material(prim)
                    logger.info(f"检查材质: {prim.GetPath()}")
                    
                    # 查找所有shader
                    shaders = []
                    for child_prim in prim.GetChildren():
                        if child_prim.IsA(UsdShade.Shader):
                            shaders.append(UsdShade.Shader(child_prim))
                    
                    # 如果没有找到子shader，尝试通过surface output查找
                    if not shaders:
                        surface_output = material.GetSurfaceOutput()
                        if surface_output:
                            connections = surface_output.GetConnectedSources()
                            for connection in connections:
                                shader_prim = connection[0]
                                if shader_prim and shader_prim.IsA(UsdShade.Shader):
                                    shaders.append(UsdShade.Shader(shader_prim))
                    
                    # 修复每个shader
                    for shader in shaders:
                        shader_prim = shader.GetPrim()
                        logger.info(f"  检查shader: {shader_prim.GetPath()}")
                        
                        # 检查是否有baseColor属性
                        diffuse_input = shader.GetInput('diffuseColor')
                        base_color_input = shader.GetInput('baseColor')
                        
                        if base_color_input:
                            # 获取baseColor的值
                            base_color_value = base_color_input.Get()
                            logger.info(f"    发现baseColor: {base_color_value}")
                            
                            # 如果没有diffuseColor，创建它
                            if not diffuse_input:
                                diffuse_input = shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f)
                                logger.info(f"    创建diffuseColor输入")
                            
                            # 将baseColor的值复制到diffuseColor
                            if base_color_value is not None:
                                diffuse_input.Set(base_color_value)
                                logger.info(f"    ✓ 设置diffuseColor: {base_color_value}")
                                
                                # 移除baseColor属性
                                shader_prim.RemoveProperty('inputs:baseColor')
                                logger.info(f"    ✓ 移除baseColor")
                                
                                materials_fixed += 1
                                self.fixes_applied.append(f"材质 {prim.GetName()} 从baseColor改为diffuseColor")
                        else:
                            logger.info(f"    ✓ shader已使用diffuseColor或无baseColor")
            
            if materials_fixed > 0:
                logger.info(f"✓ 修复了 {materials_fixed} 个材质的颜色属性")
            else:
                logger.info("✓ 所有材质已使用正确的diffuseColor属性")
                
        except Exception as e:
            error_msg = f"修复材质失败: {e}"
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
        print("用法: python fix_material_basecolor.py <usdz_file>")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    
    if not os.path.exists(usdz_file):
        logger.error(f"文件不存在: {usdz_file}")
        sys.exit(1)
    
    # 创建修复器并执行修复
    fixer = MaterialBaseColorFixer()
    success = fixer.fix_usdz_materials(usdz_file)
    
    if success:
        logger.info("✅ 材质baseColor修复成功")
        sys.exit(0)
    else:
        logger.error("❌ 材质baseColor修复失败")
        if fixer.errors:
            logger.error("错误详情:")
            for error in fixer.errors:
                logger.error(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()