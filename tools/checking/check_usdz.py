#!/usr/bin/env python3
"""
检查USDZ文件内容
"""
import zipfile
import os

def check_usdz_file(usdz_file):
    if not os.path.exists(usdz_file):
        print(f"❌ 文件不存在: {usdz_file}")
        return
    
    print(f"📁 USDZ文件信息: {usdz_file}")
    print(f"📏 文件大小: {os.path.getsize(usdz_file)} 字节")
    
    try:
        with zipfile.ZipFile(usdz_file, 'r') as z:
            print("\n📦 压缩包内容:")
            for info in z.infolist():
                print(f"  📄 {info.filename}: {info.file_size} 字节")
            
            # 检查USD文件内容
            usd_files = [f for f in z.namelist() if f.endswith('.usd') or f.endswith('.usda')]
            
            for usd_file in usd_files[:2]:  # 只检查前2个USD文件
                print(f"\n=== {usd_file} 内容预览 ===")
                try:
                    content = z.read(usd_file).decode('utf-8')
                    print(content[:800] + ("..." if len(content) > 800 else ""))
                except Exception as e:
                    print(f"❌ 读取失败: {e}")
                    
    except Exception as e:
        print(f"❌ 检查USDZ文件失败: {e}")

if __name__ == "__main__":
    # 检查最新生成的USDZ文件
    usdz_files = ['test_nacl_fixed.usdz', 'test_nacl.usdz', 'test_output.usdz']
    
    for usdz_file in usdz_files:
        if os.path.exists(usdz_file):
            check_usdz_file(usdz_file)
            print("\n" + "="*60 + "\n")