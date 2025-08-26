#!/usr/bin/env python3
"""
USDZ文件AR兼容性检查工具
"""
import zipfile
import os
from pathlib import Path

def check_usdz_ar_compatibility(usdz_path):
    """检查USDZ文件的AR兼容性"""
    print(f"🔍 检查USDZ文件: {usdz_path}")
    print("=" * 60)
    
    if not os.path.exists(usdz_path):
        print("❌ 文件不存在")
        return False
    
    # 检查文件大小
    file_size = os.path.getsize(usdz_path)
    print(f"📁 文件大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    try:
        with zipfile.ZipFile(usdz_path, 'r') as z:
            files = z.namelist()
            print(f"📦 压缩包内容 ({len(files)} 个文件):")
            
            usdc_files = []
            usda_files = []
            texture_files = []
            other_files = []
            
            for file in files:
                print(f"  📄 {file}")
                if file.endswith('.usdc'):
                    usdc_files.append(file)
                elif file.endswith('.usda'):
                    usda_files.append(file)
                elif file.endswith(('.png', '.jpg', '.jpeg')):
                    texture_files.append(file)
                else:
                    other_files.append(file)
            
            print("\n📋 文件分类:")
            print(f"  🔹 USDC文件: {len(usdc_files)} 个")
            print(f"  🔹 USDA文件: {len(usda_files)} 个")
            print(f"  🔹 纹理文件: {len(texture_files)} 个")
            print(f"  🔹 其他文件: {len(other_files)} 个")
            
            # AR兼容性检查
            print("\n🍎 iOS AR Quick Look 兼容性检查:")
            
            # 检查1: 必须有USD文件
            if not usdc_files and not usda_files:
                print("❌ 缺少USD文件 (.usdc 或 .usda)")
                return False
            else:
                print("✅ 包含USD文件")
            
            # 检查2: 推荐使用USDC格式
            if usdc_files:
                print("✅ 使用USDC二进制格式 (推荐)")
            elif usda_files:
                print("⚠️  使用USDA文本格式 (可能不被所有设备支持)")
            
            # 检查3: 文件大小限制
            if file_size > 25 * 1024 * 1024:  # 25MB
                print("⚠️  文件大小超过25MB，可能影响AR性能")
            else:
                print("✅ 文件大小适中")
            
            # 检查USD文件内容
            if usdc_files:
                main_usd = usdc_files[0]
                print(f"\n🔍 检查主USD文件: {main_usd}")
                try:
                    usd_content = z.read(main_usd)
                    print(f"  📏 USD文件大小: {len(usd_content):,} bytes")
                    
                    # 检查是否为有效的USDC文件
                    if usd_content.startswith(b'PXR-USDC'):
                        print("✅ 有效的USDC二进制文件")
                    else:
                        print("❌ 无效的USDC文件格式")
                        
                except Exception as e:
                    print(f"❌ 读取USD文件失败: {e}")
            
            print("\n💡 AR预览建议:")
            print("1. 确保在iOS Safari浏览器中打开")
            print("2. 点击文件后选择'在AR中查看'")
            print("3. 允许相机权限")
            print("4. 在光线充足的环境中使用")
            print("5. 移动设备寻找平面进行放置")
            
            return True
            
    except zipfile.BadZipFile:
        print("❌ 不是有效的ZIP/USDZ文件")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def main():
    # 查找最新的USDZ文件
    results_dir = Path("conversion_results")
    if not results_dir.exists():
        print("❌ conversion_results目录不存在")
        return
    
    # 获取最新的转换结果
    latest_dir = None
    latest_time = 0
    
    for subdir in results_dir.iterdir():
        if subdir.is_dir():
            try:
                dir_time = subdir.stat().st_mtime
                if dir_time > latest_time:
                    latest_time = dir_time
                    latest_dir = subdir
            except:
                continue
    
    if not latest_dir:
        print("❌ 未找到转换结果")
        return
    
    # 查找USDZ文件
    usdz_files = list(latest_dir.glob("*.usdz"))
    if not usdz_files:
        print(f"❌ 在 {latest_dir} 中未找到USDZ文件")
        return
    
    usdz_file = usdz_files[0]
    check_usdz_ar_compatibility(str(usdz_file))

if __name__ == "__main__":
    main()