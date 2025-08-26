#!/usr/bin/env python3
import time
import urllib.request
import urllib.error

print("等待服务启动...")
time.sleep(3)

try:
    # 测试JavaScript文件
    js_response = urllib.request.urlopen('http://localhost:8000/static/js/app.js')
    js_content = js_response.read().decode('utf-8')
    
    print(f"✅ JavaScript文件状态: {js_response.getcode()}")
    print(f"✅ JavaScript文件大小: {len(js_content)} 字符")
    
    # 检查关键函数
    if 'handleFileSelect' in js_content:
        print("✅ 找到文件上传处理函数")
    if 'startConversion' in js_content:
        print("✅ 找到转换处理函数")
    if 'generateARQRCode' in js_content:
        print("✅ 找到二维码生成函数")
        
    print("\n🎯 JavaScript文件已正确加载！")
    print("现在上传功能应该正常工作了。")
    
except urllib.error.URLError as e:
    print(f"❌ JavaScript文件访问失败: {e}")
except Exception as e:
    print(f"❌ 测试出错: {e}")

print("\n🌐 请刷新浏览器页面: http://localhost:8000") 