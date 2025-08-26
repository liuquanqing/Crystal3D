#!/usr/bin/env python3
import os
from pathlib import Path
import sys

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("🔍 开始调试USDZ转换...")
    
    try:
        from converter.main_converter import CIFToUSDZConverter
        
        # 创建转换器
        converter = CIFToUSDZConverter()
        
        # 转换测试
        cif_file = "examples/simple_crystal.cif"
        output_file = "debug_test.usdz"
        
        print(f"📂 输入: {cif_file}")
        print(f"📦 输出: {output_file}")
        
        if not os.path.exists(cif_file):
            print(f"❌ CIF文件不存在: {cif_file}")
            return
        
        # 执行转换
        result = converter.convert(cif_file, output_file, clean_temp=False)
        
        print(f"🎯 转换结果: {result}")
        
        # 检查输出文件
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ USDZ文件生成: {size} bytes")
            
            # 尝试检查USD内容
            try:
                from pxr import Usd
                stage = Usd.Stage.Open(output_file)
                if stage:
                    print("✅ USD Stage可以打开")
                    for prim in stage.Traverse():
                        print(f"  - {prim.GetPath()}: {prim.GetTypeName()}")
                else:
                    print("❌ USD Stage无法打开")
            except Exception as e:
                print(f"❌ USD检查失败: {e}")
        else:
            print("❌ USDZ文件未生成")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 