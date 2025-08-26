#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较转换器和直接测试的差异
"""

import os
import tempfile
import shutil
import subprocess
from pathlib import Path

def test_converter_method():
    """测试转换器方法"""
    print("=== 测试转换器方法 ===")
    
    # 检查CIF文件
    cif_file = "examples/NaCl.cif"
    if not os.path.exists(cif_file):
        print(f"❌ CIF文件不存在: {cif_file}")
        return
    
    print(f"✅ CIF文件存在: {cif_file}")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory(prefix="jmol_conv_") as temp_dir:
        print(f"📁 临时目录: {temp_dir}")
        
        # 复制CIF文件
        temp_cif = os.path.join(temp_dir, "input.cif")
        shutil.copy2(cif_file, temp_cif)
        print(f"📋 CIF文件已复制: {temp_cif}")
        
        # 生成脚本（模拟转换器的脚本生成）
        script_content = '''load "input.cif";
select all;
spacefill 0.8;
color cpk;
set sphereResolution 15;
set meshResolution 2;
write OBJ "output.obj";
exit;
'''
        
        script_path = os.path.join(temp_dir, 'convert.spt')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"📝 脚本文件已创建: {script_path}")
        print(f"📋 脚本内容:\n{script_content}")
        
        # 执行Jmol（模拟转换器的执行方式）
        jmol_jar = os.path.abspath("tools/Jmol.jar")
        cmd = [
            'java', '-jar', jmol_jar,
            '-n',  # 无显示模式
            '-s', 'convert.spt'  # 执行脚本文件
        ]
        
        print(f"🚀 执行命令: java -jar {jmol_jar} -n -s convert.spt")
        print(f"📂 工作目录: {temp_dir}")
        print()
        
        # 执行命令
        result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')
        
        print("📊 执行结果:")
        print(f"返回码: {result.returncode}")
        print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        
        # 检查临时目录内容
        print("\n📁 临时目录内容:")
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"  📄 {item} ({size} bytes)")
            else:
                print(f"  📁 {item}/")
        
        # 检查OBJ文件
        obj_path = os.path.join(temp_dir, "output.obj")
        if os.path.exists(obj_path):
            obj_size = os.path.getsize(obj_path)
            print(f"\n✅ OBJ文件已生成: {obj_path} ({obj_size} bytes)")
            
            # 复制到当前目录
            shutil.copy2(obj_path, "test_converter_method.obj")
            print(f"📋 OBJ文件已复制到: test_converter_method.obj")
            
            return True
        else:
            print(f"\n❌ OBJ文件未生成: {obj_path}")
            return False

def test_direct_method():
    """测试直接方法（之前成功的方法）"""
    print("\n=== 测试直接方法 ===")
    
    # 检查CIF文件
    cif_file = "examples/NaCl.cif"
    if not os.path.exists(cif_file):
        print(f"❌ CIF文件不存在: {cif_file}")
        return
    
    print(f"✅ CIF文件存在: {cif_file}")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory(prefix="jmol_direct_") as temp_dir:
        print(f"📁 临时目录: {temp_dir}")
        
        # 复制CIF文件
        temp_cif = os.path.join(temp_dir, "input.cif")
        shutil.copy2(cif_file, temp_cif)
        print(f"📋 CIF文件已复制: {temp_cif}")
        
        # 创建脚本文件（直接测试的脚本）
        script_content = '''load "input.cif";
select all;
spacefill 0.8;
color cpk;
write OBJ "output.obj";
exit;'''
        
        script_path = os.path.join(temp_dir, 'convert.spt')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"📝 脚本文件已创建: {script_path}")
        print(f"📋 脚本内容:\n{script_content}")
        
        # 执行Jmol
        jmol_jar = os.path.abspath("tools/Jmol.jar")
        cmd = [
            'java', '-jar', jmol_jar,
            '-n',  # 无显示模式
            '-s', 'convert.spt'  # 执行脚本文件
        ]
        
        print(f"🚀 执行命令: java -jar {jmol_jar} -n -s convert.spt")
        print(f"📂 工作目录: {temp_dir}")
        print()
        
        # 执行命令
        result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, encoding='utf-8')
        
        print("📊 执行结果:")
        print(f"返回码: {result.returncode}")
        print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        
        # 检查临时目录内容
        print("\n📁 临时目录内容:")
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"  📄 {item} ({size} bytes)")
            else:
                print(f"  📁 {item}/")
        
        # 检查OBJ文件
        obj_path = os.path.join(temp_dir, "output.obj")
        if os.path.exists(obj_path):
            obj_size = os.path.getsize(obj_path)
            print(f"\n✅ OBJ文件已生成: {obj_path} ({obj_size} bytes)")
            
            # 复制到当前目录
            shutil.copy2(obj_path, "test_direct_method.obj")
            print(f"📋 OBJ文件已复制到: test_direct_method.obj")
            
            return True
        else:
            print(f"\n❌ OBJ文件未生成: {obj_path}")
            return False

if __name__ == "__main__":
    print("🔍 比较转换器和直接测试的差异")
    print("=" * 50)
    
    # 测试两种方法
    converter_success = test_converter_method()
    direct_success = test_direct_method()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"转换器方法: {'✅ 成功' if converter_success else '❌ 失败'}")
    print(f"直接方法: {'✅ 成功' if direct_success else '❌ 失败'}")
    
    if direct_success and not converter_success:
        print("\n🔍 需要进一步分析转换器方法的问题")
    elif converter_success:
        print("\n🎉 转换器方法已修复！")