#!/usr/bin/env python3
"""
最简单的Jmol安装方法
"""
import os
import sys
import urllib.request
from pathlib import Path
import subprocess

def download_jmol_direct():
    """直接下载Jmol.jar - 多个备用源"""
    print("🚀 下载Jmol.jar...")
    
    # 多个下载源
    jmol_urls = [
        # GitHub mirror
        "https://github.com/BobHanson/Jmol-SwingJS/releases/download/v14.32.10/Jmol-14.32.10-binary.zip",
        # 备用直链
        "https://downloads.sourceforge.net/project/jmol/Jmol/Version%2014.32/Jmol-14.32.10-binary.zip",
        # 更老版本但稳定
        "https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.31/Jmol-14.31.53-binary.zip/download"
    ]
    
    tools_dir = Path("tools")
    tools_dir.mkdir(exist_ok=True)
    jar_path = tools_dir / "Jmol.jar"
    
    for i, url in enumerate(jmol_urls):
        try:
            print(f"🔄 尝试下载源 {i+1}: {url[:50]}...")
            zip_path = tools_dir / f"jmol_{i}.zip"
            
            # 下载
            urllib.request.urlretrieve(url, zip_path)
            
            if zip_path.exists() and zip_path.stat().st_size > 1000000:  # 至少1MB
                print(f"✅ 下载成功: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
                
                # 解压
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tools_dir)
                
                # 查找Jmol.jar
                for root, dirs, files in os.walk(tools_dir):
                    for file in files:
                        if file == "Jmol.jar":
                            src_jar = Path(root) / file
                            if jar_path.exists():
                                jar_path.unlink()
                            src_jar.rename(jar_path)
                            print(f"✅ Jmol.jar已安装到: {jar_path}")
                            
                            # 清理
                            zip_path.unlink()
                            cleanup_dirs(tools_dir)
                            return True
                
                zip_path.unlink()
            else:
                print(f"❌ 下载失败或文件过小")
                if zip_path.exists():
                    zip_path.unlink()
                    
        except Exception as e:
            print(f"❌ 下载源 {i+1} 失败: {e}")
            continue
    
    print("❌ 所有下载源都失败了")
    return False

def cleanup_dirs(tools_dir):
    """清理临时目录"""
    try:
        import shutil
        for item in tools_dir.iterdir():
            if item.is_dir() and ("jmol" in item.name.lower() or "Jmol" in item.name):
                shutil.rmtree(item, ignore_errors=True)
    except:
        pass

def test_jmol():
    """测试Jmol"""
    jar_path = Path("tools/Jmol.jar")
    
    if not jar_path.exists():
        print("❌ Jmol.jar未找到")
        return False
    
    print("🧪 测试Jmol...")
    
    try:
        result = subprocess.run([
            "java", "-jar", str(jar_path), "-n", "-s", 
            "print 'Jmol is working!'; quit;"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Jmol测试成功!")
            print(f"📊 文件大小: {jar_path.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print(f"❌ Jmol测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def create_test_cif():
    """创建测试CIF文件"""
    test_cif = Path("test_nacl.cif")
    cif_content = """data_NaCl
_cell_length_a 5.6402
_cell_length_b 5.6402  
_cell_length_c 5.6402
_cell_angle_alpha 90.0
_cell_angle_beta 90.0
_cell_angle_gamma 90.0
_space_group_name_H-M_alt 'F m -3 m'
_space_group_IT_number 225

loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Na1 Na 0.0 0.0 0.0
Cl1 Cl 0.5 0.0 0.0
"""
    with open(test_cif, "w", encoding="utf-8") as f:
        f.write(cif_content)
    
    return test_cif

def test_conversion():
    """测试CIF转OBJ"""
    jar_path = Path("tools/Jmol.jar")
    
    if not jar_path.exists():
        return False
    
    print("🔬 测试CIF转OBJ...")
    
    # 创建测试文件
    test_cif = create_test_cif()
    test_obj = Path("test_output.obj")
    
    try:
        # Jmol脚本
        script = f"""
load "{test_cif}";
spacefill 0.8;
color cpk;
write OBJ "{test_obj}";
quit;
"""
        
        script_file = Path("test_script.spt")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
        
        # 运行Jmol
        result = subprocess.run([
            "java", "-jar", str(jar_path), "-n", "-s", str(script_file)
        ], capture_output=True, text=True, timeout=30)
        
        if test_obj.exists():
            obj_size = test_obj.stat().st_size
            print(f"✅ CIF转OBJ成功! 输出文件: {obj_size} bytes")
            
            # 清理
            test_cif.unlink()
            test_obj.unlink()
            script_file.unlink()
            return True
        else:
            print(f"❌ OBJ文件未生成")
            print(f"Jmol输出: {result.stdout}")
            print(f"Jmol错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 转换测试异常: {e}")
        return False
    finally:
        # 清理文件
        for f in [test_cif, test_obj, Path("test_script.spt")]:
            if f.exists():
                f.unlink()

if __name__ == "__main__":
    print("🎯 Jmol快速安装")
    print("=" * 40)
    
    success = False
    
    if download_jmol_direct():
        if test_jmol():
            if test_conversion():
                print("\n🎉 Jmol完全安装成功!")
                print("✅ Java运行正常")
                print("✅ Jmol下载完成")
                print("✅ CIF转OBJ测试通过")
                print("\n🚀 现在您可以:")
                print("1. 运行服务: python main.py")
                print("2. 享受专业级CIF转换质量!")
                success = True
            else:
                print("\n⚠️ Jmol安装成功，但转换测试失败")
        else:
            print("\n⚠️ Jmol下载成功，但测试失败")
    
    if not success:
        print("\n❌ 安装失败")
        print("请手动下载Jmol:")
        print("1. 访问: https://jmol.sourceforge.net/")
        print("2. 下载Jmol.jar放到tools/目录")
        print("3. 运行: java -jar tools/Jmol.jar") 