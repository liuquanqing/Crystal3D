#!/usr/bin/env python3
"""
USD文件内容详细分析工具
"""
import zipfile
import tempfile
import os
from pathlib import Path

def analyze_usd_content(usdz_path):
    """分析USD文件的详细内容"""
    print(f"🔍 分析USD内容: {usdz_path}")
    print("=" * 60)
    
    try:
        with zipfile.ZipFile(usdz_path, 'r') as z:
            usdc_files = [f for f in z.namelist() if f.endswith('.usdc')]
            if not usdc_files:
                print("❌ 未找到USDC文件")
                return
            
            main_usdc = usdc_files[0]
            print(f"📄 分析文件: {main_usdc}")
            
            # 提取USDC文件到临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                usdc_path = os.path.join(temp_dir, main_usdc)
                with open(usdc_path, 'wb') as f:
                    f.write(z.read(main_usdc))
                
                # 尝试使用USD Python API读取
                try:
                    from pxr import Usd, UsdGeom, Gf
                    
                    stage = Usd.Stage.Open(usdc_path)
                    if not stage:
                        print("❌ 无法打开USD Stage")
                        return
                    
                    print("✅ 成功打开USD Stage")
                    
                    # 获取根层信息
                    root_layer = stage.GetRootLayer()
                    print(f"📋 根层信息:")
                    print(f"  🔹 标识符: {root_layer.identifier}")
                    print(f"  🔹 默认Prim: {stage.GetDefaultPrim().GetPath() if stage.GetDefaultPrim() else 'None'}")
                    
                    # 遍历所有Prim
                    print("\n🌳 Prim层次结构:")
                    prims = list(stage.Traverse())
                    print(f"  📊 总Prim数量: {len(prims)}")
                    
                    mesh_count = 0
                    xform_count = 0
                    material_count = 0
                    
                    for prim in prims:
                        prim_type = prim.GetTypeName()
                        path = prim.GetPath()
                        print(f"  📦 {path} ({prim_type})")
                        
                        if prim_type == "Mesh":
                            mesh_count += 1
                            # 检查Mesh的几何数据
                            mesh = UsdGeom.Mesh(prim)
                            if mesh:
                                points_attr = mesh.GetPointsAttr()
                                faces_attr = mesh.GetFaceVertexIndicesAttr()
                                face_counts_attr = mesh.GetFaceVertexCountsAttr()
                                
                                if points_attr:
                                    points = points_attr.Get()
                                    print(f"    🔸 顶点数: {len(points) if points else 0}")
                                
                                if faces_attr:
                                    faces = faces_attr.Get()
                                    print(f"    🔸 面索引数: {len(faces) if faces else 0}")
                                
                                if face_counts_attr:
                                    face_counts = face_counts_attr.Get()
                                    print(f"    🔸 面数: {len(face_counts) if face_counts else 0}")
                                
                                # 检查材质绑定
                                material_binding = UsdGeom.MaterialBindingAPI(prim)
                                if material_binding:
                                    material_rel = material_binding.GetDirectBindingRel()
                                    if material_rel and material_rel.GetTargets():
                                        print(f"    🎨 材质绑定: {material_rel.GetTargets()[0]}")
                        
                        elif prim_type == "Xform":
                            xform_count += 1
                        elif prim_type == "Material":
                            material_count += 1
                    
                    print(f"\n📊 统计信息:")
                    print(f"  🔹 Mesh数量: {mesh_count}")
                    print(f"  🔹 Xform数量: {xform_count}")
                    print(f"  🔹 Material数量: {material_count}")
                    
                    # 检查Stage元数据
                    print(f"\n🎬 Stage元数据:")
                    print(f"  🔹 上轴: {UsdGeom.GetStageUpAxis(stage)}")
                    print(f"  🔹 米每单位: {UsdGeom.GetStageMetersPerUnit(stage)}")
                    
                    # AR兼容性检查
                    print(f"\n🍎 AR兼容性分析:")
                    
                    if mesh_count == 0:
                        print("❌ 没有Mesh几何体 - 这是AR无法显示的主要原因!")
                        print("   💡 建议: 检查CIF转换过程中的几何体生成")
                    else:
                        print(f"✅ 包含 {mesh_count} 个Mesh几何体")
                    
                    if not stage.GetDefaultPrim():
                        print("⚠️  没有设置默认Prim")
                        print("   💡 建议: 设置defaultPrim以改善AR加载")
                    else:
                        print("✅ 已设置默认Prim")
                    
                    # 检查几何体是否有有效数据
                    has_valid_geometry = False
                    for prim in prims:
                        if prim.GetTypeName() == "Mesh":
                            mesh = UsdGeom.Mesh(prim)
                            points = mesh.GetPointsAttr().Get() if mesh.GetPointsAttr() else None
                            faces = mesh.GetFaceVertexIndicesAttr().Get() if mesh.GetFaceVertexIndicesAttr() else None
                            
                            if points and faces and len(points) > 0 and len(faces) > 0:
                                has_valid_geometry = True
                                break
                    
                    if not has_valid_geometry:
                        print("❌ 没有有效的几何数据 - AR无法显示空的Mesh!")
                        print("   💡 这是最可能的问题原因")
                    else:
                        print("✅ 包含有效的几何数据")
                    
                except ImportError:
                    print("⚠️  USD Python API未安装，无法详细分析")
                    print("   💡 建议: pip install usd-core")
                except Exception as e:
                    print(f"❌ USD分析失败: {e}")
                    
                    # 尝试简单的二进制分析
                    print("\n🔍 尝试二进制分析...")
                    with open(usdc_path, 'rb') as f:
                        content = f.read(1000)  # 读取前1000字节
                        print(f"📄 文件头: {content[:50]}")
                        
                        # 查找常见的USD关键字
                        keywords = [b'Mesh', b'points', b'faceVertexIndices', b'Material']
                        found_keywords = []
                        for keyword in keywords:
                            if keyword in content:
                                found_keywords.append(keyword.decode())
                        
                        if found_keywords:
                            print(f"✅ 找到关键字: {', '.join(found_keywords)}")
                        else:
                            print("❌ 未找到预期的USD关键字")
                
    except Exception as e:
        print(f"❌ 分析失败: {e}")

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
    analyze_usd_content(str(usdz_file))

if __name__ == "__main__":
    main()