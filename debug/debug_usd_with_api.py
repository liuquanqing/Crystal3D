#!/usr/bin/env python3
"""
使用USD Python API调试USDZ文件内容
"""
import os
import sys

def debug_usd_with_api(usdz_path):
    """使用USD API调试USDZ文件"""
    print(f"🔍 使用USD API调试: {usdz_path}")
    print("=" * 60)
    
    try:
        # 尝试导入USD库
        from pxr import Usd, UsdGeom, UsdShade, Sdf
        print("✅ USD Python API可用")
        
        # 打开USD stage
        stage = Usd.Stage.Open(usdz_path)
        if not stage:
            print(f"❌ 无法打开USD文件: {usdz_path}")
            return
        
        print(f"✅ 成功打开USD Stage")
        
        # 获取所有prims
        all_prims = list(stage.Traverse())
        print(f"📊 总共找到 {len(all_prims)} 个prims")
        
        # 分析不同类型的prims
        mesh_prims = []
        material_prims = []
        other_prims = []
        
        for prim in all_prims:
            prim_type = prim.GetTypeName()
            prim_path = str(prim.GetPath())
            
            if prim_type == 'Mesh':
                mesh_prims.append((prim_path, prim))
            elif prim_type == 'Material':
                material_prims.append((prim_path, prim))
            else:
                other_prims.append((prim_path, prim_type))
        
        print(f"\n📐 Mesh数量: {len(mesh_prims)}")
        for path, mesh_prim in mesh_prims:
            print(f"  - {path}")
            
            # 获取mesh的详细信息
            mesh = UsdGeom.Mesh(mesh_prim)
            if mesh:
                points_attr = mesh.GetPointsAttr()
                faces_attr = mesh.GetFaceVertexIndicesAttr()
                
                if points_attr:
                    points = points_attr.Get()
                    if points:
                        print(f"    顶点数: {len(points)}")
                
                if faces_attr:
                    faces = faces_attr.Get()
                    if faces:
                        print(f"    面索引数: {len(faces)}")
                        print(f"    估计面数: {len(faces)//3}")
        
        print(f"\n🎨 材质数量: {len(material_prims)}")
        for path, mat_prim in material_prims:
            print(f"  - {path}")
        
        print(f"\n📦 其他prims: {len(other_prims)}")
        for path, prim_type in other_prims[:10]:  # 只显示前10个
            print(f"  - {path} ({prim_type})")
        if len(other_prims) > 10:
            print(f"  ... 还有{len(other_prims)-10}个")
        
        # 检查根prim
        root_prim = stage.GetDefaultPrim()
        if root_prim:
            print(f"\n🌳 默认根prim: {root_prim.GetPath()}")
        
        return True
        
    except ImportError:
        print("❌ USD Python API不可用")
        print("尝试使用备用方法...")
        return False
    except Exception as e:
        print(f"❌ USD API调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_obj_to_usd_conversion():
    """调试OBJ到USD的转换过程"""
    print("\n🔧 调试OBJ到USD转换过程")
    print("=" * 60)
    
    obj_file = "test_jmol_fixed.obj"
    if not os.path.exists(obj_file):
        print(f"❌ OBJ文件不存在: {obj_file}")
        return
    
    # 分析OBJ文件结构
    print(f"📂 分析OBJ文件: {obj_file}")
    
    vertices = []
    faces = []
    groups = []
    materials = []
    current_group = None
    current_material = None
    
    with open(obj_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line.startswith('v '):
                vertices.append(line)
            elif line.startswith('f '):
                faces.append((line, current_group, current_material))
            elif line.startswith('g '):
                current_group = line.split()[1] if len(line.split()) > 1 else None
                if current_group not in groups:
                    groups.append(current_group)
            elif line.startswith('usemtl '):
                current_material = line.split()[1] if len(line.split()) > 1 else None
                if current_material not in materials:
                    materials.append(current_material)
            
            # 只处理前1000行以避免内存问题
            if line_num > 1000:
                break
    
    print(f"📊 OBJ文件分析结果（前1000行）:")
    print(f"  - 顶点数: {len(vertices)}")
    print(f"  - 面数: {len(faces)}")
    print(f"  - 组数: {len(groups)}")
    print(f"  - 材质数: {len(materials)}")
    
    print(f"\n📋 前10个组:")
    for i, group in enumerate(groups[:10]):
        print(f"  {i+1}. {group}")
    
    print(f"\n🎨 前10个材质:")
    for i, material in enumerate(materials[:10]):
        print(f"  {i+1}. {material}")
    
    # 统计每个组的面数
    group_face_counts = {}
    for face, group, material in faces:
        if group:
            group_face_counts[group] = group_face_counts.get(group, 0) + 1
    
    print(f"\n📊 各组面数统计:")
    for group, count in sorted(group_face_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {group}: {count} 个面")

def main():
    """主函数"""
    # 首先调试OBJ文件
    debug_obj_to_usd_conversion()
    
    # 然后调试USDZ文件
    test_files = [
        "user_test_nacl.usdz",
        "test_final_complete.usdz",
        "test_complete_fixed.usdz"
    ]
    
    for usdz_file in test_files:
        if os.path.exists(usdz_file):
            success = debug_usd_with_api(usdz_file)
            if success:
                break
    else:
        print("❌ 未找到可调试的USDZ文件")

if __name__ == "__main__":
    main()