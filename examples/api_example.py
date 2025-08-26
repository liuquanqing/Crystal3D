#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crystal3D API 使用示例

本脚本演示如何使用Crystal3D的RESTful API进行：
1. 文件上传
2. 转换任务提交
3. 结果下载
4. 批量处理

使用前请确保Crystal3D服务已启动：
    python3 main.py
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional


class Crystal3DClient:
    """Crystal3D API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """检查服务是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def upload_file(self, file_path: str) -> Optional[Dict]:
        """上传CIF文件"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'chemical/x-cif')}
                response = self.session.post(f"{self.base_url}/api/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 文件上传成功: {os.path.basename(file_path)}")
                print(f"   文件ID: {result.get('file_id')}")
                return result
            else:
                print(f"❌ 文件上传失败: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"❌ 上传异常: {str(e)}")
            return None
    
    def convert_to_usdz(self, file_id: str, **kwargs) -> Optional[Dict]:
        """转换为USDZ格式"""
        try:
            payload = {
                'file_id': file_id,
                **kwargs  # 支持自定义参数，如supercell, atom_scale等
            }
            
            response = self.session.post(
                f"{self.base_url}/api/convert",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 转换任务提交成功")
                print(f"   任务ID: {result.get('task_id')}")
                return result
            else:
                print(f"❌ 转换失败: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"❌ 转换异常: {str(e)}")
            return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """查询任务状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/task/{task_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 查询任务状态失败: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ 查询异常: {str(e)}")
            return None
    
    def download_result(self, task_id: str, output_dir: str = "./output") -> Optional[str]:
        """下载转换结果"""
        try:
            response = self.session.get(f"{self.base_url}/api/download/{task_id}")
            
            if response.status_code == 200:
                # 创建输出目录
                os.makedirs(output_dir, exist_ok=True)
                
                # 从响应头获取文件名
                filename = f"{task_id}.usdz"
                if 'content-disposition' in response.headers:
                    import re
                    cd = response.headers['content-disposition']
                    filename_match = re.search(r'filename="(.+)"', cd)
                    if filename_match:
                        filename = filename_match.group(1)
                
                output_path = os.path.join(output_dir, filename)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 文件下载成功: {output_path}")
                return output_path
            else:
                print(f"❌ 下载失败: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ 下载异常: {str(e)}")
            return None
    
    def wait_for_completion(self, task_id: str, timeout: int = 300) -> bool:
        """等待任务完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            
            if not status:
                return False
            
            state = status.get('status', 'unknown')
            
            if state == 'completed':
                print(f"✅ 任务完成: {task_id}")
                return True
            elif state == 'failed':
                print(f"❌ 任务失败: {task_id}")
                print(f"   错误信息: {status.get('error', 'Unknown error')}")
                return False
            elif state in ['pending', 'processing']:
                print(f"⏳ 任务进行中: {state}...")
                time.sleep(2)
            else:
                print(f"⚠️  未知任务状态: {state}")
                time.sleep(2)
        
        print(f"⏰ 任务超时: {task_id}")
        return False


def convert_single_file(client: Crystal3DClient, file_path: str, output_dir: str = "./output") -> bool:
    """转换单个文件"""
    print(f"\n🔄 开始转换: {os.path.basename(file_path)}")
    
    # 1. 上传文件
    upload_result = client.upload_file(file_path)
    if not upload_result:
        return False
    
    file_id = upload_result['file_id']
    
    # 2. 提交转换任务
    convert_result = client.convert_to_usdz(
        file_id,
        supercell=[2, 2, 2],  # 2x2x2超胞
        atom_scale=0.8,       # 原子半径缩放
        generate_qr=True      # 生成二维码
    )
    
    if not convert_result:
        return False
    
    task_id = convert_result['task_id']
    
    # 3. 等待完成
    if not client.wait_for_completion(task_id):
        return False
    
    # 4. 下载结果
    output_path = client.download_result(task_id, output_dir)
    return output_path is not None


def batch_convert(client: Crystal3DClient, input_dir: str, output_dir: str = "./output") -> None:
    """批量转换目录中的所有CIF文件"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 查找所有CIF文件
    cif_files = list(input_path.glob("*.cif"))
    
    if not cif_files:
        print(f"❌ 在目录中未找到CIF文件: {input_dir}")
        return
    
    print(f"📁 找到 {len(cif_files)} 个CIF文件")
    
    success_count = 0
    
    for cif_file in cif_files:
        try:
            if convert_single_file(client, str(cif_file), output_dir):
                success_count += 1
            else:
                print(f"❌ 转换失败: {cif_file.name}")
        except Exception as e:
            print(f"❌ 处理异常 {cif_file.name}: {str(e)}")
    
    print(f"\n📊 批量转换完成: {success_count}/{len(cif_files)} 成功")


def main():
    """主函数 - 演示API使用"""
    print("🚀 Crystal3D API 使用示例")
    print("=" * 40)
    
    # 创建客户端
    client = Crystal3DClient()
    
    # 检查服务状态
    print("🔍 检查服务状态...")
    if not client.health_check():
        print("❌ Crystal3D服务未启动，请先运行: python3 main.py")
        return
    
    print("✅ 服务状态正常")
    
    # 示例1: 转换单个文件
    example_file = "examples/LiCoO2.cif"
    if os.path.exists(example_file):
        print("\n📋 示例1: 转换单个文件")
        convert_single_file(client, example_file)
    
    # 示例2: 批量转换
    examples_dir = "examples"
    if os.path.exists(examples_dir):
        print("\n📋 示例2: 批量转换")
        batch_convert(client, examples_dir)
    
    print("\n🎉 API示例演示完成！")
    print("💡 查看输出目录 './output' 中的USDZ文件")


if __name__ == "__main__":
    main()