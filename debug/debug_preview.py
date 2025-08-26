#!/usr/bin/env python3
import time
import requests
import json
import os

print("🔍 开始全面诊断...")
time.sleep(2)

# 1. 检查服务状态
try:
    response = requests.get('http://localhost:8000/')
    print(f"✅ 服务运行正常: {response.status_code}")
except Exception as e:
    print(f"❌ 服务连接失败: {e}")
    exit(1)

# 2. 测试CIF文件上传和后端处理
print("\n📤 测试后端CIF处理...")
cif_file = "examples/simple_crystal.cif"

if not os.path.exists(cif_file):
    print(f"❌ 测试文件不存在: {cif_file}")
    exit(1)

try:
    with open(cif_file, 'rb') as f:
        files = {'file': (os.path.basename(cif_file), f, 'application/octet-stream')}
        data = {
            'sphere_resolution': 16,
            'bond_resolution': 8,
            'bond_radius': 0.1
        }
        
        print(f"📤 发送文件: {cif_file}")
        response = requests.post('http://localhost:8000/convert', files=files, data=data, timeout=30)
        
        print(f"📥 后端响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 后端转换成功")
            
            # 检查响应头
            metadata_header = response.headers.get('X-Conversion-Metadata')
            if metadata_header:
                print("✅ 找到转换元数据")
                try:
                    metadata = json.loads(metadata_header)
                    print(f"   - 原子数: {metadata.get('atom_count')}")
                    print(f"   - 分子式: {metadata.get('original_formula')}")
                    print(f"   - 转换器: {metadata.get('converter_used')}")
                except Exception as e:
                    print(f"❌ 元数据解析失败: {e}")
            else:
                print("❌ 没有转换元数据")
                
            # 检查文件大小
            file_size = len(response.content)
            print(f"✅ USDZ文件大小: {file_size} 字节")
            
            if file_size < 100:
                print("⚠️ USDZ文件太小，可能有问题")
                
        else:
            print(f"❌ 后端转换失败: {response.text}")
            
except Exception as e:
    print(f"❌ 后端测试失败: {e}")

# 3. 检查JavaScript文件完整性
print("\n🔍 检查JavaScript文件...")
js_files = [
    '/static/js/crystal_preview.js',
    '/static/js/advanced_crystal_preview.js', 
    '/static/js/app.js'
]

for js_file in js_files:
    try:
        js_response = requests.get(f'http://localhost:8000{js_file}')
        if js_response.status_code == 200:
            content = js_response.text
            print(f"✅ {js_file}: {len(content)} 字符")
            
            # 检查关键函数
            if 'AdvancedCrystalPreview' in content:
                print(f"   - 找到高级预览类")
            if 'THREE.Scene' in content:
                print(f"   - 找到Three.js使用")
            if 'loadStructureFromPymatgenStyle' in content:
                print(f"   - 找到结构加载函数")
                
        else:
            print(f"❌ {js_file}: 无法访问 ({js_response.status_code})")
    except Exception as e:
        print(f"❌ {js_file}: {e}")

# 4. 测试Three.js库访问
print("\n🌐 检查Three.js库...")
three_js_urls = [
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js'
]

for url in three_js_urls:
    try:
        lib_response = requests.get(url, timeout=10)
        if lib_response.status_code == 200:
            print(f"✅ {url}: 可访问")
        else:
            print(f"❌ {url}: 不可访问 ({lib_response.status_code})")
    except Exception as e:
        print(f"❌ {url}: {e}")

# 5. 创建简化的测试HTML文件
print("\n📝 创建调试测试页面...")
debug_html = """<!DOCTYPE html>
<html>
<head>
    <title>3D预览调试</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <h1>3D预览调试</h1>
    <div id="debug-container" style="width: 600px; height: 400px; border: 1px solid #ccc;"></div>
    
    <script>
        console.log('开始调试测试...');
        
        // 测试Three.js基本功能
        try {
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, 600/400, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer();
            
            renderer.setSize(600, 400);
            document.getElementById('debug-container').appendChild(renderer.domElement);
            
            // 创建一个简单的立方体
            const geometry = new THREE.BoxGeometry();
            const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
            const cube = new THREE.Mesh(geometry, material);
            scene.add(cube);
            
            camera.position.z = 5;
            
            function animate() {
                requestAnimationFrame(animate);
                cube.rotation.x += 0.01;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }
            animate();
            
            console.log('✅ Three.js基本功能正常');
            
        } catch (error) {
            console.error('❌ Three.js测试失败:', error);
        }
    </script>
</body>
</html>"""

with open('debug_test.html', 'w', encoding='utf-8') as f:
    f.write(debug_html)

print("✅ 调试页面已生成: debug_test.html")
print("\n🎯 建议:")
print("1. 用浏览器打开 debug_test.html 测试Three.js基本功能")
print("2. 打开浏览器开发者工具，查看控制台错误信息")
print("3. 在主页面上传文件时，观察控制台输出")
print("4. 检查网络选项卡中的资源加载情况")

print(f"\n🌐 测试地址:")
print(f"   主页面: http://localhost:8000")
print(f"   调试页面: file://{os.path.abspath('debug_test.html')}") 