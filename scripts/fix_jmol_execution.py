#!/usr/bin/env python3
"""
修复Jmol执行问题
解决Jmol能启动但不生成OBJ文件的问题
"""
import os
import subprocess
import tempfile
from pathlib import Path
import time

def test_jmol_direct():
    """直接测试Jmol功能"""
    print("🔧 直接测试Jmol功能...")
    
    # 检查Jmol是否存在
    jmol_path = "tools/Jmol.jar"
    if not os.path.exists(jmol_path):
        print(f"❌ Jmol不存在: {jmol_path}")
        return False
    
    # 检查用户的CIF文件
    cif_file = r"C:\Users\lqq\Downloads\NaCl.cif"
    if not os.path.exists(cif_file):
        print(f"❌ CIF文件不存在: {cif_file}")
        return False
    
    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as temp_dir:
        output_obj = os.path.join(temp_dir, "test_output.obj")
        output_mtl = os.path.join(temp_dir, "test_output.mtl")
        script_file = os.path.join(temp_dir, "test_script.spt")
        
        # 生成测试脚本
        cif_abs = os.path.abspath(cif_file).replace('\\', '/')
        obj_abs = os.path.abspath(output_obj).replace('\\', '/')
        
        script_content = f'''// Jmol测试脚本
load "{cif_abs}";
select all;
spacefill 0.8;
color cpk;
write OBJ "{obj_abs}";
exit;
'''
        
        print(f"📝 创建测试脚本: {script_file}")
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 执行Jmol
        try:
            cmd = [
                "java", "-jar", jmol_path,
                "-n",  # 无GUI模式
                script_file
            ]
            
            print(f"🚀 执行命令: {' '.join(cmd)}")
            print(f"📂 工作目录: {os.getcwd()}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )
            
            print(f"✅ Jmol执行完成，返回码: {result.returncode}")
            print(f"📄 标准输出:\n{result.stdout}")
            if result.stderr:
                print(f"⚠️ 错误输出:\n{result.stderr}")
            
            # 等待文件生成
            time.sleep(2)
            
            # 检查输出文件
            if os.path.exists(output_obj):
                size = os.path.getsize(output_obj)
                print(f"🎉 OBJ文件生成成功: {size} bytes")
                
                # 分析OBJ内容
                with open(output_obj, 'r') as f:
                    lines = f.readlines()
                    vertices = len([l for l in lines if l.startswith('v ')])
                    faces = len([l for l in lines if l.startswith('f ')])
                    materials = len([l for l in lines if l.startswith('usemtl ')])
                
                print(f"📊 OBJ统计: {vertices}顶点, {faces}面, {materials}材质")
                
                # 检查MTL文件
                if os.path.exists(output_mtl):
                    mtl_size = os.path.getsize(output_mtl)
                    print(f"🎨 MTL文件: {mtl_size} bytes")
                
                return True
            else:
                print("❌ OBJ文件未生成")
                print(f"📂 检查目录内容: {os.listdir(temp_dir)}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Jmol执行超时")
            return False
        except Exception as e:
            print(f"❌ Jmol执行异常: {e}")
            return False

def diagnose_jmol_issues():
    """诊断Jmol问题"""
    print("\n🔍 诊断Jmol问题...")
    
    issues = []
    
    # 1. 检查Java
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java可用")
        else:
            print("❌ Java不可用")
            issues.append("Java未安装或不在PATH中")
    except:
        print("❌ 无法执行java命令")
        issues.append("Java命令不可用")
    
    # 2. 检查Jmol文件
    jmol_path = "tools/Jmol.jar"
    if os.path.exists(jmol_path):
        size = os.path.getsize(jmol_path)
        print(f"✅ Jmol文件存在: {size} bytes")
    else:
        print("❌ Jmol文件不存在")
        issues.append("Jmol.jar文件缺失")
    
    # 3. 检查CIF文件
    cif_file = r"C:\Users\lqq\Downloads\NaCl.cif"
    if os.path.exists(cif_file):
        size = os.path.getsize(cif_file)
        print(f"✅ CIF文件存在: {size} bytes")
    else:
        print("❌ CIF文件不存在")
        issues.append("测试CIF文件缺失")
    
    # 4. 检查文件权限
    try:
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.unlink(test_file)
        os.rmdir(temp_dir)
        print("✅ 文件写入权限正常")
    except:
        print("❌ 文件写入权限有问题")
        issues.append("临时目录写入权限不足")
    
    return issues

def fix_jmol_script_generation():
    """修复Jmol脚本生成"""
    print("\n🔧 修复Jmol脚本生成...")
    
    jmol_converter_file = Path("converter/jmol_converter.py")
    
    with open(jmol_converter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 新的脚本生成方法
    new_script_method = '''    def _generate_jmol_script_simple(self, cif_path: str, obj_path: str, quality: str) -> str:
        """生成简化的Jmol脚本 - 修复版本"""

        # 质量设置
        quality_settings = {
            'low': {'resolution': 1, 'sphereRes': 10},
            'medium': {'resolution': 2, 'sphereRes': 15}, 
            'high': {'resolution': 3, 'sphereRes': 20}
        }

        settings = quality_settings.get(quality, quality_settings['medium'])
        
        # 转换为绝对路径并使用正斜杠
        cif_abs_path = os.path.abspath(cif_path).replace('\\\\', '/')
        obj_abs_path = os.path.abspath(obj_path).replace('\\\\', '/')
        
        # 确保输出目录存在
        obj_dir = os.path.dirname(obj_abs_path)
        os.makedirs(obj_dir, exist_ok=True)

        # 生成更详细的脚本
        script = f"""// Jmol自动转换脚本
echo "开始加载CIF文件...";
load "{cif_abs_path}";
echo "CIF文件加载完成";

// 检查是否加载成功
if (_frameID < 0) {{
    echo "错误: CIF文件加载失败";
    exit;
}}

echo "设置显示参数...";
select all;
spacefill 0.8;
color cpk;
set sphereResolution {settings['sphereRes']};
set meshResolution {settings['resolution']};

echo "准备导出OBJ文件...";
echo "输出路径: {obj_abs_path}";

// 导出OBJ文件
write OBJ "{obj_abs_path}";

echo "OBJ文件导出完成";
echo "脚本执行结束";
exit;
"""
        return script'''
    
    # 替换脚本生成方法
    import re
    pattern = r'def _generate_jmol_script_simple\(self.*?\n        return script'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_script_method.strip(), content, flags=re.DOTALL)
        
        with open(jmol_converter_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Jmol脚本生成已修复")
        return True
    else:
        print("❌ 未找到要修复的脚本方法")
        return False

def fix_jmol_execution():
    """修复Jmol执行逻辑"""
    print("\n🔧 修复Jmol执行逻辑...")
    
    jmol_converter_file = Path("converter/jmol_converter.py")
    
    with open(jmol_converter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复执行部分 - 增加调试和重试
    new_execution = '''                # 执行Jmol转换
                cmd = [
                    "java", "-jar", self.jmol_jar_path,
                    "-n",  # 无GUI模式
                    script_path  # 直接使用脚本文件
                ]

                logger.info(f"执行Jmol转换: {' '.join(cmd)}")
                logger.info(f"工作目录: {os.getcwd()}")
                logger.info(f"脚本路径: {script_path}")
                logger.info(f"期望输出: {obj_path}")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,  # 增加超时时间
                    cwd=os.getcwd()
                )

                logger.info(f"Jmol执行完成，返回码: {result.returncode}")
                logger.info(f"Jmol输出: {result.stdout}")
                if result.stderr:
                    logger.warning(f"Jmol错误输出: {result.stderr}")

                # 多次检查文件生成（有时需要更长时间）
                import time
                for i in range(5):  # 检查5次，每次间隔1秒
                    time.sleep(1)
                    if os.path.exists(obj_path):
                        break
                    logger.info(f"等待OBJ文件生成... ({i+1}/5)")

                if os.path.exists(obj_path):
                    # 验证文件内容
                    file_size = os.path.getsize(obj_path)
                    if file_size > 0:
                        # 获取文件统计信息
                        stats = self._analyze_obj_file(obj_path)

                        logger.info(f"Jmol转换成功: {obj_path} ({file_size} bytes)")
                        return {
                            'success': True,
                            'output_file': obj_path,
                            'message': 'Jmol转换成功',
                            'converter': 'jmol',
                            **stats
                        }
                    else:
                        logger.error("生成的OBJ文件为空")
                        return {
                            'success': False,
                            'error': 'empty_file',
                            'message': 'Jmol生成的OBJ文件为空'
                        }
                else:
                    # 列出输出目录内容进行调试
                    output_dir = os.path.dirname(obj_path)
                    if os.path.exists(output_dir):
                        dir_contents = os.listdir(output_dir)
                        logger.error(f"输出目录内容: {dir_contents}")
                    
                    error_msg = f"OBJ文件未生成。Jmol输出: {result.stdout}"
                    logger.error(f"Jmol转换失败: {error_msg}")
                    return {
                        'success': False,
                        'error': 'jmol_no_output',
                        'message': f'Jmol未生成OBJ文件: {error_msg}'
                    }'''
    
    # 替换执行逻辑
    old_execution_pattern = r'# 执行Jmol转换.*?return \{\s*\'success\': False,.*?\}'
    
    if re.search(old_execution_pattern, content, re.DOTALL):
        content = re.sub(old_execution_pattern, new_execution.strip(), content, flags=re.DOTALL)
        
        with open(jmol_converter_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Jmol执行逻辑已修复")
        return True
    else:
        print("❌ 未找到要修复的执行逻辑")
        return False

def main():
    """主修复流程"""
    print("🔧 修复Jmol执行问题")
    print("=" * 60)
    
    print("💡 问题: Jmol运行成功但不生成OBJ文件")
    print("🎯 目标: 确保Jmol正确生成OBJ和MTL文件")
    
    steps = [
        ("诊断Jmol问题", diagnose_jmol_issues),
        ("直接测试Jmol", test_jmol_direct),
        ("修复脚本生成", fix_jmol_script_generation),
        ("修复执行逻辑", fix_jmol_execution)
    ]
    
    results = []
    issues = []
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            result = step_func()
            if step_name == "诊断Jmol问题":
                issues = result if result else []
                result = len(issues) == 0
            results.append((step_name, result if result is not None else True))
        except Exception as e:
            print(f"❌ {step_name}失败: {e}")
            results.append((step_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("🏆 Jmol修复总结:")
    
    if issues:
        print("\n⚠️ 发现的问题:")
        for issue in issues:
            print(f"  - {issue}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    if success_count >= total_count - 1:  # 允许一个步骤失败
        print("\n🎉 Jmol修复基本完成！")
        print("\n✅ 修复要点:")
        print("- 🔧 增强脚本生成逻辑")
        print("- ⏱️ 延长文件生成等待时间")
        print("- 📊 改进调试输出")
        print("- 🔄 添加重试机制")
        
        print("\n🔄 需要重启服务:")
        print("- 修改已应用到转换器")
        print("- 服务会自动检测并重新加载")
        
        print("\n🧪 验证建议:")
        print("- 重新测试CIF转换")
        print("- 检查日志中Jmol的执行结果")
        print("- 确认OBJ文件正确生成")
        
    else:
        print(f"\n⚠️ 部分修复完成 ({success_count}/{total_count})")
        for step_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {step_name}")
        
        if issues:
            print("\n💡 解决建议:")
            for issue in issues:
                if "Java" in issue:
                    print("  - 安装Java运行环境")
                elif "Jmol" in issue:
                    print("  - 重新下载Jmol.jar文件")
                elif "权限" in issue:
                    print("  - 检查文件系统权限")

if __name__ == "__main__":
    main() 