#!/usr/bin/env python3
"""
调试USDZ文件内容 - 检查是否包含完整的几何体
"""
import os
import zipfile
from pathlib import Path

def debug_usdz_content(usdz_path):
    """调试USDZ文件内容"""
    print(f"🔍 调试USDZ文件: {usdz_path}")
    print("=" * 60)
    
    if not os.path.exists(usdz_path):
        print(f"❌ 文件不存在: {usdz_path}")
        return
    
    file_size = os.path.getsize(usdz_path)
    print(f"📁 文件大小: {file_size} bytes ({file_size/1024:.1f} KB)")
    
    try:
        # 解压USDZ文件查看内容
        with zipfile.ZipFile(usdz_path, 'r') as z:
            files = z.namelist()
            print(f"\n📦 USDZ包含 {len(files)} 个文件:")
            
            for file in files:
                info = z.getinfo(file)
                print(f"  - {file} ({info.file_size} bytes)")
                
                # 如果是USD文件，读取内容分析
                if file.endswith('.usd') or file.endswith('.usda'):
                    print(f"\n📄 分析USD文件内容: {file}")
                    content = z.read(file).decode('utf-8', errors='ignore')
                    
                    # 统计几何体数量
                    mesh_count = content.count('def Mesh')
                    sphere_count = content.count('Sphere')
                    material_count = content.count('def Material')
                    
                    print(f"  - Mesh数量: {mesh_count}")
                    print(f"  - Sphere引用: {sphere_count}")
                    print(f"  - 材质数量: {material_count}")
                    
                    # 查找顶点和面数据
                    if 'points' in content:
                        points_start = content.find('points = [')
                        if points_start != -1:
                            points_end = content.find(']', points_start)
                            points_section = content[points_start:points_end+1]
                            # 简单计算顶点数量
                            vertex_count = points_section.count('(')
                            print(f"  - 顶点数量: {vertex_count}")
                    
                    if 'faceVertexIndices' in content:
                        faces_start = content.find('faceVertexIndices = [')
                        if faces_start != -1:
                            faces_end = content.find(']', faces_start)
                            faces_section = content[faces_start:faces_end+1]
                            # 简单计算面数量（每3个索引为一个三角形）
                            indices = faces_section.count(',')
                            face_count = indices // 3
                            print(f"  - 面数量: 约{face_count}")
                    
                    # 检查是否包含多个几何体
                    if 'Na' in content and 'Cl' in content:
                        na_count = content.count('Na')
                        cl_count = content.count('Cl')
                        print(f"  - Na引用: {na_count}")
                        print(f"  - Cl引用: {cl_count}")
                    
                    # 显示前500个字符
                    print(f"\n📝 USD文件前500个字符:")
                    print(content[:500])
                    print("...")
                    
    except Exception as e:
        print(f"❌ 解析USDZ文件失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    # 测试最新的USDZ文件
    test_files = [
        "user_test_nacl.usdz",
        "test_final_complete.usdz",
        "test_complete_fixed.usdz"
    ]
    
    for usdz_file in test_files:
        if os.path.exists(usdz_file):
            debug_usdz_content(usdz_file)
            print("\n" + "="*60 + "\n")
            break
    else:
        print("❌ 未找到USDZ测试文件")

if __name__ == "__main__":
    main()