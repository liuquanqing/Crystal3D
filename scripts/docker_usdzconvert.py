#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker USDZ转换器 - 优化版
基于专用USD Docker镜像的高质量USDZ转换工具
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import json
import time
from loguru import logger

class DockerUsdzConverter:
    """Docker USDZ转换器 - 可选增强功能"""
    
    def __init__(self, docker_image="michaelgold/usdzconvert:0.66-usd-22.05b"):
        """
        初始化Docker USDZ转换器
        
        Args:
            docker_image: Docker镜像名称
        """
        self.docker_image = docker_image
        self.is_available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """检查Docker和镜像可用性"""
        return self.check_docker_available() and self._ensure_image()
        
    def check_docker_available(self) -> bool:
        """检查Docker是否可用"""
        try:
            # 检查Docker守护进程
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True, timeout=10)
            logger.info(f"✓ Docker可用: {result.stdout.strip()}")
            
            # 检查Docker守护进程是否运行
            result = subprocess.run(["docker", "info"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning("Docker守护进程未运行，请启动Docker Desktop")
                return False
                
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning("Docker响应超时")
            return False
        except FileNotFoundError:
            logger.info("Docker未安装 - 将使用本地USD转换器")
            return False
        except Exception as e:
            logger.info(f"Docker不可用: {e} - 将使用本地USD转换器")
            return False
    
    def _ensure_image(self) -> bool:
        """确保Docker镜像可用，如果不存在则尝试拉取"""
        try:
            # 检查镜像是否存在
            if self._check_image_exists():
                logger.info(f"✓ Docker镜像已存在: {self.docker_image}")
                return True
            
            # 镜像不存在，询问是否拉取
            logger.info(f"Docker镜像不存在: {self.docker_image}")
            return self._pull_image_if_needed()
            
        except Exception as e:
            logger.warning(f"镜像检查失败: {e}")
            return False
    
    def _check_image_exists(self) -> bool:
        """检查Docker镜像是否存在"""
        try:
            result = subprocess.run([
                "docker", "images", "--format", "{{.Repository}}:{{.Tag}}"
            ], capture_output=True, text=True, check=True, timeout=15)
            
            images = result.stdout.strip().split('\n')
            return self.docker_image in images
            
        except Exception:
            return False
    
    def _pull_image_if_needed(self) -> bool:
        """拉取Docker镜像（可选）"""
        try:
            logger.info("正在拉取USD Docker镜像...")
            logger.info("这可能需要几分钟时间，请耐心等待...")
            
            # 拉取镜像
            result = subprocess.run([
                "docker", "pull", self.docker_image
            ], capture_output=True, text=True, timeout=600)  # 10分钟超时
            
            if result.returncode == 0:
                logger.success(f"✓ Docker镜像拉取成功: {self.docker_image}")
                return True
            else:
                logger.warning(f"Docker镜像拉取失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning("Docker镜像拉取超时")
            return False
        except Exception as e:
            logger.warning(f"Docker镜像拉取失败: {e}")
            return False
    
    def convert_obj_to_usdz(self, obj_path: str, usdz_path: str) -> Tuple[bool, str]:
        """
        转换OBJ文件为USDZ
        
        Args:
            obj_path: 输入OBJ文件路径
            usdz_path: 输出USDZ文件路径
            
        Returns:
            (success: bool, message: str) 元组
        """
        if not self.is_available:
            return False, "Docker USD转换器不可用"
            
        obj_file = Path(obj_path)
        if not obj_file.exists():
            return False, f"输入OBJ文件不存在: {obj_path}"
        
        usdz_file = Path(usdz_path)
        usdz_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        try:
            # 复制文件到临时目录
            temp_obj = temp_path / obj_file.name
            shutil.copy2(obj_file, temp_obj)
            
            # 复制相关文件（MTL、纹理等）
            self._copy_related_files(obj_file, temp_path)
            
            logger.info(f"开始Docker USDZ转换: {obj_file.name}")
            
            # 构建Docker命令
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{temp_path}:/workspace",
                "-w", "/workspace",
                self.docker_image,
                obj_file.name
            ]
            
            # 执行转换
            result = subprocess.run(docker_cmd, 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # 检查输出文件
                expected_output = temp_path / obj_file.with_suffix('.usdz').name
                if expected_output.exists():
                    # 复制到目标位置
                    shutil.copy2(expected_output, usdz_file)
                    
                    file_size = usdz_file.stat().st_size
                    logger.success(f"✓ Docker USDZ转换成功: {usdz_file} ({file_size} bytes)")
                    return True, f"Docker USDZ转换成功，文件大小: {file_size} bytes"
                else:
                    return False, "Docker转换未生成USDZ文件"
            else:
                error_msg = result.stderr or result.stdout or "Docker转换失败"
                logger.warning(f"Docker转换失败: {error_msg}")
                return False, f"Docker转换失败: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Docker转换超时（300秒）"
        except Exception as e:
            logger.error(f"Docker转换出错: {e}")
            return False, f"Docker转换出错: {str(e)}"
        finally:
            # 清理临时目录
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def _copy_related_files(self, obj_file: Path, temp_path: Path):
        """复制OBJ相关文件（MTL、纹理等）"""
        try:
            # 复制MTL文件
            mtl_file = obj_file.with_suffix('.mtl')
            if mtl_file.exists():
                shutil.copy2(mtl_file, temp_path / mtl_file.name)
                logger.debug(f"已复制MTL文件: {mtl_file.name}")
            
            # 复制纹理文件
            texture_extensions = ['.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tiff']
            for ext in texture_extensions:
                texture_files = list(obj_file.parent.glob(f"*{ext}"))
                for texture_file in texture_files:
                    shutil.copy2(texture_file, temp_path / texture_file.name)
                    logger.debug(f"已复制纹理文件: {texture_file.name}")
                    
        except Exception as e:
            logger.warning(f"复制相关文件时出错: {e}")
    
    def batch_convert(self, obj_files: List[str], output_dir: Optional[str] = None) -> List[Dict]:
        """批量转换OBJ文件"""
        if not self.is_available:
            return [{"error": "Docker USD转换器不可用"}]
            
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        success_count = 0
        
        logger.info(f"开始Docker批量转换 {len(obj_files)} 个文件")
        
        for i, obj_file in enumerate(obj_files, 1):
            logger.info(f"[{i}/{len(obj_files)}] 处理文件: {obj_file}")
            
            obj_path = Path(obj_file)
            if output_dir:
                output_file = output_path / obj_path.with_suffix('.usdz').name
            else:
                output_file = obj_path.with_suffix('.usdz')
            
            success, message = self.convert_obj_to_usdz(str(obj_path), str(output_file))
            
            if success:
                success_count += 1
            
            results.append({
                'input': str(obj_file),
                'output': str(output_file) if success else None,
                'success': success,
                'message': message
            })
        
        logger.info(f"Docker批量转换完成: {success_count}/{len(obj_files)} 个文件成功")
        return results
    
    def get_info(self) -> Dict[str, any]:
        """获取转换器信息"""
        return {
            'name': 'Docker USD转换器',
            'type': 'docker',
            'docker_image': self.docker_image,
            'available': self.is_available,
            'features': [
                '专业USD转换',
                '高质量输出',
                '完整材质支持',
                '纹理自动处理'
            ]
        }
    
    def get_converter_info(self) -> Dict[str, any]:
        """获取转换器信息（兼容主转换器接口）"""
        info = self.get_info()
        return {
            'available': info['available'],
            'version': f"Docker {self.docker_image}",
            'description': '使用Docker环境中的Apple官方usdzconvert工具进行高质量USDZ转换',
            'features': info['features']
        }

def test_docker_converter():
    """测试Docker转换器"""
    logger.info("=== Docker USD转换器测试 ===")
    
    converter = DockerUsdzConverter()
    
    if not converter.is_available:
        logger.warning("Docker USD转换器不可用，跳过测试")
        logger.info("提示：安装Docker Desktop并拉取镜像以启用高级USD功能")
        return False
    
    # 查找测试文件
    current_dir = Path('.')
    test_files = list(current_dir.glob('*.obj'))
    
    if not test_files:
        logger.info("未找到测试用的OBJ文件")
        return False
    
    logger.info(f"找到 {len(test_files)} 个OBJ文件进行测试")
    
    # 测试单个转换
    test_file = test_files[0]
    output_file = test_file.with_suffix('.docker.usdz')
    
    success, message = converter.convert_obj_to_usdz(str(test_file), str(output_file))
    
    if success:
        logger.success(f"✓ Docker转换测试成功: {message}")
        return True
    else:
        logger.error(f"✗ Docker转换测试失败: {message}")
        return False

def main():
    """主函数"""
    test_docker_converter()

if __name__ == "__main__":
    main()