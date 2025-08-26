#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARKit兼容性配置

基于Apple官方文档和最佳实践的ARKit USDZ文件配置
参考资料:
- Apple ARKit Documentation
- USDZ File Format Specification
- ARKit Performance Guidelines
"""

import os
from typing import Dict, List, Optional

class ARKitConfig:
    """ARKit兼容性配置类"""
    
    # ARKit推荐的文件大小限制
    MAX_FILE_SIZE_MB = 25  # ARKit推荐的最大文件大小
    MAX_TEXTURE_SIZE = 2048  # 最大纹理尺寸
    MAX_POLYGON_COUNT = 100000  # 推荐的最大多边形数量
    
    # 支持的纹理格式（按优先级排序）
    SUPPORTED_TEXTURE_FORMATS = [
        'jpg',   # 推荐：文件小，兼容性好
        'jpeg',  # 同上
        'png',   # 支持透明度，但文件较大
    ]
    
    # ARKit兼容的usdzconvert参数
    USDZCONVERT_PARAMS = {
        'verbose': ['-v'],  # 详细输出
        # usdzconvert 0.66版本不支持-textures和-quality参数
        # 材质参数将通过其他方式设置
    }
    
    # 材质优化参数
    MATERIAL_OPTIMIZATION = {
        'compress_textures': True,
        'max_texture_resolution': 1024,
        'use_pbr_materials': True,  # 使用物理基础渲染材质
        'optimize_for_mobile': True,
    }
    
    # 几何体优化参数
    GEOMETRY_OPTIMIZATION = {
        'max_vertices': 50000,
        'max_triangles': 100000,
        'simplify_mesh': True,
        'remove_duplicate_vertices': True,
        'optimize_vertex_order': True,
    }
    
    @classmethod
    def get_usdzconvert_command(cls, input_file: str, output_file: str, 
                               custom_params: Optional[Dict] = None) -> List[str]:
        """生成ARKit兼容的usdzconvert命令
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            custom_params: 自定义参数
            
        Returns:
            完整的命令参数列表
        """
        cmd = ['usdzconvert', input_file, output_file]
        
        # 添加基础ARKit兼容参数
        for param_group in cls.USDZCONVERT_PARAMS.values():
            cmd.extend(param_group)
        
        # 添加自定义参数
        if custom_params:
            for key, value in custom_params.items():
                if isinstance(value, list):
                    cmd.extend(value)
                else:
                    cmd.extend([key, str(value)])
        
        return cmd
    
    @classmethod
    def validate_file_size(cls, file_path: str) -> bool:
        """验证文件大小是否符合ARKit要求
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否符合大小要求
        """
        if not os.path.exists(file_path):
            return False
            
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return file_size_mb <= cls.MAX_FILE_SIZE_MB
    
    @classmethod
    def get_optimization_recommendations(cls, file_path: str) -> List[str]:
        """获取文件优化建议
        
        Args:
            file_path: 文件路径
            
        Returns:
            优化建议列表
        """
        recommendations = []
        
        if not os.path.exists(file_path):
            recommendations.append("文件不存在")
            return recommendations
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > cls.MAX_FILE_SIZE_MB:
            recommendations.append(f"文件过大 ({file_size_mb:.1f}MB > {cls.MAX_FILE_SIZE_MB}MB)")
            recommendations.append("建议：压缩纹理、简化几何体、减少多边形数量")
        
        if file_size_mb > 10:
            recommendations.append("文件较大，可能影响加载性能")
            recommendations.append("建议：优化纹理分辨率、使用JPEG格式")
        
        return recommendations

# ARKit材质配置
class ARKitMaterialConfig:
    """ARKit材质配置"""
    
    # PBR材质参数
    PBR_MATERIAL_PARAMS = {
        'metallic': 0.0,      # 金属度
        'roughness': 0.5,     # 粗糙度
        'clearcoat': 0.0,     # 清漆
        'opacity': 1.0,       # 不透明度
    }
    
    # 颜色空间配置
    COLOR_SPACE = {
        'diffuse': 'sRGB',    # 漫反射颜色空间
        'normal': 'linear',   # 法线贴图颜色空间
        'metallic': 'linear', # 金属度贴图颜色空间
        'roughness': 'linear',# 粗糙度贴图颜色空间
    }
    
    @classmethod
    def get_material_template(cls, material_name: str, diffuse_color: tuple) -> str:
        """生成ARKit兼容的材质模板
        
        Args:
            material_name: 材质名称
            diffuse_color: 漫反射颜色 (r, g, b)
            
        Returns:
            材质定义字符串
        """
        r, g, b = diffuse_color
        
        return f"""
# ARKit兼容材质: {material_name}
newmtl {material_name}
Ka {r:.3f} {g:.3f} {b:.3f}  # 环境光
Kd {r:.3f} {g:.3f} {b:.3f}  # 漫反射
Ks 0.100 0.100 0.100       # 镜面反射
Ns 10.000                   # 镜面指数
Ni 1.000                    # 折射率
d 1.000                     # 透明度
illum 2                     # 光照模型
"""

# 导出配置
__all__ = ['ARKitConfig', 'ARKitMaterialConfig']