#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker USDZ AR兼容性调试工具
检查Docker转换器生成的USDZ文件是否符合iOS AR标准
"""

import sys
import os
import zipfile
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from converter.main_converter import CIFToUSDZConverter
from loguru import logger

def analyze_usdz_structure(usdz_path: str):
    """分析USDZ文件的内部结构"""
    print(f"\n🔍 分析USDZ文件结构: {usdz_path}")
    
    if not os.path.exists(usdz_path):
        print(f"❌ 文件不存在: {usdz_path}")
        return False
    
    file_size = os.path.getsize(usdz_path)
    print(f"📏 文件大小: {file_size} 字节")
    
    try:
        with zipfile.ZipFile(usdz_path, 'r') as zf:
            file_list = zf.namelist()
            print(f"\n📦 USDZ包含文件 ({len(file_list)}个):")
            
            for file_name in file_list:
                file_info = zf.getinfo(file_name)
                print(f"  📄 {file_name} ({file_info.file_size} 字节)")
            
            # 检查必要的文件
            has_usda = any(f.endswith('.usda') for f in file_list)
            has_usdc = any(f.endswith('.usdc') for f in file_list)
            has_usd = has_usda or has_usdc
            
            print(f"\n✅ AR兼容性检查:")
            print(f"  USD文件: {'✅' if has_usd else '❌'} ({'USDA' if has_usda else 'USDC' if has_usdc else '无'})")
            
            # 分析USD内容
            if has_usda:
                usda_files = [f for f in file_list if f.endswith('.usda')]
                for usda_file in usda_files:
                    print(f"\n📖 分析USD内容: {usda_file}")
                    usd_content = zf.read(usda_file).decode('utf-8')
                    analyze_usd_content(usd_content)
            
            return True
            
    except Exception as e:
        print(f"❌ 分析USDZ文件失败: {e}")
        return False

def analyze_usd_content(usd_content: str):
    """分析USD文件内容的AR兼容性"""
    lines = usd_content.split('\n')
    
    # 检查关键元素
    has_stage = any('def Xform' in line or 'def "' in line for line in lines)
    has_mesh = any('def Mesh' in line for line in lines)
    has_material = any('def Material' in line for line in lines)
    has_shader = any('def Shader' in line for line in lines)
    has_primvars = any('primvars:' in line for line in lines)
    has_points = any('point3f[] points' in line for line in lines)
    has_normals = any('normal3f[] normals' in line for line in lines)
    has_uvs = any('texCoord2f[]' in line for line in lines)
    has_indices = any('int[] faceVertexIndices' in line for line in lines)
    
    # 检查AR特定属性
    has_ar_metadata = any('customData' in line for line in lines)
    has_up_axis = any('upAxis' in line for line in lines)
    has_meters_per_unit = any('metersPerUnit' in line for line in lines)
    
    print(f"  🏗️ 几何结构:")
    print(f"    Stage定义: {'✅' if has_stage else '❌'}")
    print(f"    Mesh几何: {'✅' if has_mesh else '❌'}")
    print(f"    顶点数据: {'✅' if has_points else '❌'}")
    print(f"    法线数据: {'✅' if has_normals else '❌'}")
    print(f"    UV坐标: {'✅' if has_uvs else '❌'}")
    print(f"    面索引: {'✅' if has_indices else '❌'}")
    
    print(f"  🎨 材质系统:")
    print(f"    材质定义: {'✅' if has_material else '❌'}")
    print(f"    着色器: {'✅' if has_shader else '❌'}")
    print(f"    Primvars: {'✅' if has_primvars else '❌'}")
    
    print(f"  📱 AR兼容性:")
    print(f"    AR元数据: {'✅' if has_ar_metadata else '❌'}")
    print(f"    坐标轴设置: {'✅' if has_up_axis else '❌'}")
    print(f"    单位设置: {'✅' if has_meters_per_unit else '❌'}")
    
    # 显示部分内容用于调试
    print(f"\n📝 USD内容预览 (前20行):")
    for i, line in enumerate(lines[:20]):
        if line.strip():
            print(f"    {i+1:2d}: {line}")
    
    if len(lines) > 20:
        print(f"    ... (共{len(lines)}行)")

def test_docker_usdz_ar_compatibility():
    """测试Docker USDZ的AR兼容性"""
    print("=== Docker USDZ AR兼容性测试 ===")
    
    input_cif = "examples/NaCl.cif"
    output_usdz = "debug_docker_ar_test.usdz"
    temp_obj = "temp_debug.obj"
    
    if not os.path.exists(input_cif):
        print(f"❌ 测试文件不存在: {input_cif}")
        return
    
    print(f"\n🔄 使用Docker转换器转换: {input_cif}")
    
    try:
        # 首先生成OBJ文件
        converter = CIFToUSDZConverter()
        result = {
            'success': False,
            'message': '',
            'metadata': {},
            'temp_files': [],
            'steps_completed': []
        }
        
        # 解析CIF文件
        if not converter._parse_cif(input_cif, result):
            print(f"❌ CIF解析失败: {result['message']}")
            return
        
        # 设置输入文件路径到元数据中
        converter.conversion_metadata['input_file'] = input_cif
        
        # 生成OBJ文件 - 使用绝对路径
        temp_obj_abs = os.path.abspath(temp_obj)
        temp_dir = os.path.dirname(temp_obj_abs)
        
        # 确保目录存在
        os.makedirs(temp_dir, exist_ok=True)
        
        if not converter._generate_obj(temp_obj_abs, result):
            print(f"❌ OBJ生成失败: {result['message']}")
            return
        
        print(f"✅ OBJ文件生成成功: {temp_obj_abs}")
        temp_obj = temp_obj_abs  # 更新为绝对路径
        
        # 直接使用Docker转换器
        from scripts.docker_usdzconvert import DockerUsdzConverter
        docker_converter = DockerUsdzConverter()
        
        if not docker_converter.is_available:
            print("❌ Docker转换器不可用")
            return
        
        # 执行转换
        docker_result = docker_converter.convert_obj_to_usdz(temp_obj, output_usdz)
        
        if isinstance(docker_result, tuple):
            success, message = docker_result
        elif isinstance(docker_result, dict):
            success = docker_result.get('success', False)
            message = docker_result.get('message', '未知结果')
        else:
            success = bool(docker_result)
            message = '转换完成' if success else '转换失败'
        
        if success:
            print(f"✅ Docker转换成功")
            print(f"📝 使用的转换器: Docker USD")
            
            # 分析生成的USDZ文件
            if os.path.exists(output_usdz):
                analyze_usdz_structure(output_usdz)
                
                # 检查iOS AR兼容性问题
                print(f"\n🍎 iOS AR兼容性诊断:")
                diagnose_ios_ar_issues(output_usdz)
            else:
                print(f"❌ 输出文件未生成: {output_usdz}")
        else:
            print(f"❌ Docker转换失败: {message}")
            
    except Exception as e:
        print(f"💥 测试过程中发生异常: {e}")
        logger.exception("Docker USDZ AR测试异常")
    
    finally:
        # 清理测试文件
        for temp_file in [output_usdz, temp_obj]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"\n🧹 已清理测试文件: {temp_file}")
                except Exception as e:
                    print(f"⚠️ 清理文件失败: {e}")

def diagnose_ios_ar_issues(usdz_path: str):
    """诊断iOS AR兼容性问题"""
    issues = []
    
    try:
        with zipfile.ZipFile(usdz_path, 'r') as zf:
            file_list = zf.namelist()
            
            # 检查文件结构问题
            if not any(f.endswith('.usda') or f.endswith('.usdc') for f in file_list):
                issues.append("❌ 缺少USD文件")
            
            # 检查USD内容
            usda_files = [f for f in file_list if f.endswith('.usda')]
            if usda_files:
                usd_content = zf.read(usda_files[0]).decode('utf-8')
                
                # 常见的iOS AR问题
                if 'upAxis = "Y"' not in usd_content and 'upAxis = "Z"' not in usd_content:
                    issues.append("⚠️ 未设置坐标轴方向 (upAxis)")
                
                if 'metersPerUnit' not in usd_content:
                    issues.append("⚠️ 未设置单位比例 (metersPerUnit)")
                
                if 'def Mesh' not in usd_content:
                    issues.append("❌ 缺少Mesh几何定义")
                
                if 'point3f[] points' not in usd_content:
                    issues.append("❌ 缺少顶点数据")
                
                if 'int[] faceVertexIndices' not in usd_content:
                    issues.append("❌ 缺少面索引数据")
                
                if 'normal3f[] normals' not in usd_content:
                    issues.append("⚠️ 缺少法线数据 (可能影响光照)")
                
                if 'texCoord2f[]' not in usd_content:
                    issues.append("⚠️ 缺少UV坐标 (可能影响纹理)")
                
                # 检查材质系统
                if 'def Material' not in usd_content:
                    issues.append("⚠️ 缺少材质定义")
                
                if 'def Shader' not in usd_content:
                    issues.append("⚠️ 缺少着色器定义")
    
    except Exception as e:
        issues.append(f"❌ 分析文件时出错: {e}")
    
    if issues:
        print("  发现以下问题:")
        for issue in issues:
            print(f"    {issue}")
        
        print("\n💡 建议修复方案:")
        if any("坐标轴" in issue for issue in issues):
            print("    - 在USD文件中添加 upAxis = \"Y\" 或 upAxis = \"Z\"")
        if any("单位比例" in issue for issue in issues):
            print("    - 在USD文件中添加 metersPerUnit = 1.0")
        if any("法线" in issue for issue in issues):
            print("    - 确保生成顶点法线数据")
        if any("UV坐标" in issue for issue in issues):
            print("    - 添加纹理坐标映射")
        if any("材质" in issue for issue in issues):
            print("    - 添加完整的材质和着色器定义")
    else:
        print("  ✅ 未发现明显的iOS AR兼容性问题")

if __name__ == "__main__":
    test_docker_usdz_ar_compatibility()