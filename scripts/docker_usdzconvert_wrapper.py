#!/usr/bin/env python3
"""
Docker-style USDZ Converter Wrapper
使用现有的usdzconvert_webui作为后端，提供类似Docker的API接口
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
import argparse

class USdzConvertWrapper:
    def __init__(self, webui_url="http://192.168.2.219:80"):
        self.webui_url = webui_url
        self.session = requests.Session()
    
    def convert_file(self, input_file, output_file, ios12_mode=True):
        """
        转换文件到USDZ格式
        
        Args:
            input_file (str): 输入文件路径
            output_file (str): 输出文件路径
            ios12_mode (bool): 是否使用iOS12兼容模式
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_file):
                print(f"Error: Input file {input_file} not found")
                return False
            
            # 准备上传文件
            with open(input_file, 'rb') as f:
                files = {'file': (os.path.basename(input_file), f, 'application/octet-stream')}
                
                # 准备转换参数
                data = {
                    'ios12_mode': str(ios12_mode).lower(),
                    'output_format': 'usdz'
                }
                
                print(f"Converting {input_file} to USDZ format...")
                if ios12_mode:
                    print("Converting in iOS12 compatibility mode.")
                
                # 发送转换请求
                response = self.session.post(
                    f"{self.webui_url}/convert",
                    files=files,
                    data=data,
                    timeout=300  # 5分钟超时
                )
                
                if response.status_code == 200:
                    # 保存转换结果
                    output_dir = os.path.dirname(output_file)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    with open(output_file, 'wb') as out_f:
                        out_f.write(response.content)
                    
                    print(f"Output file: {output_file}")
                    print("Conversion completed successfully!")
                    return True
                else:
                    print(f"Error: Conversion failed with status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            return False
    
    def check_health(self):
        """
        检查WebUI服务是否可用
        
        Returns:
            bool: 服务是否可用
        """
        try:
            response = self.session.get(f"{self.webui_url}/", timeout=10)
            return response.status_code == 200
        except:
            return False

def main():
    parser = argparse.ArgumentParser(description='USDZ Converter Wrapper')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('output_file', help='Output USDZ file path')
    parser.add_argument('-iOS12', '--ios12', action='store_true', 
                       help='Convert in iOS12 compatibility mode')
    parser.add_argument('--webui-url', default='http://192.168.2.219:80',
                       help='WebUI service URL')
    
    args = parser.parse_args()
    
    # 创建转换器实例
    converter = USdzConvertWrapper(args.webui_url)
    
    # 检查服务是否可用
    if not converter.check_health():
        print(f"Error: WebUI service at {args.webui_url} is not available")
        print("Please make sure usdzconvert_webui is running")
        sys.exit(1)
    
    # 执行转换
    success = converter.convert_file(
        args.input_file, 
        args.output_file, 
        args.ios12
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()