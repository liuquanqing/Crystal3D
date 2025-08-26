#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime

def organize_conversion_output():
    """整理转换输出文件到专门的文件夹"""
    
    # 创建输出文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"conversion_results_{timestamp}"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"✅ 创建输出文件夹: {os.path.abspath(output_folder)}")
    
    # 查找并移动文件
    files_moved = 0
    
    # 1. 查找当前目录的USDZ文件
    for file in os.listdir('.'):
        if file.endswith('.usdz') and ('nacl' in file.lower() or 'test' in file.lower()):
            src = file
            dst = os.path.join(output_folder, file)
            shutil.copy2(src, dst)
            print(f"📁 USDZ文件: {os.path.abspath(dst)} ({os.path.getsize(dst)} bytes)")
            files_moved += 1
    
    # 2. 查找可能的OBJ文件
    for file in os.listdir('.'):
        if file.endswith('.obj') and ('nacl' in file.lower() or 'test' in file.lower()):
            src = file
            dst = os.path.join(output_folder, file)
            shutil.copy2(src, dst)
            print(f"📁 OBJ文件: {os.path.abspath(dst)} ({os.path.getsize(dst)} bytes)")
            files_moved += 1
    
    # 3. 查找MTL文件
    for file in os.listdir('.'):
        if file.endswith('.mtl') and ('nacl' in file.lower() or 'test' in file.lower()):
            src = file
            dst = os.path.join(output_folder, file)
            shutil.copy2(src, dst)
            print(f"📁 MTL文件: {os.path.abspath(dst)} ({os.path.getsize(dst)} bytes)")
            files_moved += 1
    
    # 4. 复制原始CIF文件
    if os.path.exists('test_nacl.cif'):
        dst = os.path.join(output_folder, 'original_nacl.cif')
        shutil.copy2('test_nacl.cif', dst)
        print(f"📁 原始CIF文件: {os.path.abspath(dst)} ({os.path.getsize(dst)} bytes)")
        files_moved += 1
    
    print(f"\n📊 总结:")
    print(f"   - 输出文件夹: {os.path.abspath(output_folder)}")
    print(f"   - 移动文件数: {files_moved}")
    
    # 显示文件夹内容
    if files_moved > 0:
        print(f"\n📋 文件夹内容:")
        for file in sorted(os.listdir(output_folder)):
            file_path = os.path.join(output_folder, file)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   - {file} ({size_mb:.2f} MB)")
    
    return output_folder

def show_conversion_info():
    """显示转换过程的详细信息"""
    print("\n🔍 转换过程分析:")
    print("\n根据服务器日志，转换过程如下:")
    print("1️⃣ 输入文件: test_nacl.cif")
    print("2️⃣ 临时CIF文件: C:\\Users\\lqq\\AppData\\Local\\Temp\\cif_conv_75381060.cif")
    print("3️⃣ 中间OBJ文件: C:\\Users\\lqq\\AppData\\Local\\Temp\\cif_conv_7157936e.obj")
    print("   - 顶点数: 19,422")
    print("   - 面数: 37,280")
    print("   - 材质数: 6")
    print("4️⃣ 最终USDZ文件: C:\\Users\\lqq\\AppData\\Local\\Temp\\cif_conv_91b520dc.usdz")
    print("   - 文件大小: 242,027 bytes (0.23 MB)")
    print("5️⃣ 下载到本地: F:\\项目\\自动转化\\test_nacl_output.usdz")
    
    print("\n💡 文件位置说明:")
    print("   - 中间文件(OBJ): 存储在系统临时目录，转换完成后自动清理")
    print("   - 最终文件(USDZ): 通过HTTP响应下载到指定位置")
    print("   - 建议: 创建专门的输出文件夹来管理转换结果")

if __name__ == "__main__":
    show_conversion_info()
    print("\n" + "="*60)
    output_folder = organize_conversion_output()
    print("\n✅ 文件整理完成！")