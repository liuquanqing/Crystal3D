#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台路径兼容性处理模块
处理Windows、macOS、Linux系统的路径差异
"""

import os
import sys
import platform
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
import re
import urllib.parse

class PathCompatibility:
    """路径兼容性处理类"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_posix = self.system in ["linux", "darwin"]
        
        # 路径分隔符
        self.native_sep = os.sep
        self.alt_sep = os.altsep
        
        # 路径长度限制
        self.max_path_length = self._get_max_path_length()
        
    def _get_max_path_length(self):
        """获取系统最大路径长度"""
        if self.is_windows:
            # Windows默认260字符限制，但可以通过注册表启用长路径支持
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\FileSystem")
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                winreg.CloseKey(key)
                return 32767 if value else 260
            except:
                return 260
        else:
            # Unix系统通常支持4096字符
            return 4096
            
    def normalize_path(self, path):
        """标准化路径"""
        if not path:
            return path
            
        # 转换为Path对象
        if isinstance(path, str):
            path_obj = Path(path)
        elif isinstance(path, Path):
            path_obj = path
        else:
            path_obj = Path(str(path))
            
        # 解析相对路径和符号链接
        try:
            normalized = path_obj.resolve()
        except (OSError, RuntimeError):
            # 如果路径不存在，使用绝对路径
            normalized = path_obj.absolute()
            
        return normalized
        
    def to_posix_path(self, path):
        """转换为POSIX风格路径"""
        normalized = self.normalize_path(path)
        return normalized.as_posix()
        
    def to_windows_path(self, path):
        """转换为Windows风格路径"""
        normalized = self.normalize_path(path)
        return str(normalized).replace('/', '\\')
        
    def to_native_path(self, path):
        """转换为当前系统的原生路径格式"""
        normalized = self.normalize_path(path)
        return str(normalized)
        
    def to_uri(self, path):
        """转换为URI格式"""
        normalized = self.normalize_path(path)
        return normalized.as_uri()
        
    def from_uri(self, uri):
        """从URI转换为路径"""
        if uri.startswith('file://'):
            # 解析file:// URI
            parsed = urllib.parse.urlparse(uri)
            path = urllib.parse.unquote(parsed.path)
            
            if self.is_windows and path.startswith('/'):
                # Windows路径需要移除开头的斜杠
                path = path[1:]
                
            return Path(path)
        else:
            return Path(uri)
            
    def is_absolute(self, path):
        """检查是否为绝对路径"""
        path_obj = Path(path)
        return path_obj.is_absolute()
        
    def is_relative(self, path):
        """检查是否为相对路径"""
        return not self.is_absolute(path)
        
    def make_relative(self, path, base=None):
        """创建相对路径"""
        if base is None:
            base = Path.cwd()
        else:
            base = Path(base)
            
        path_obj = Path(path)
        
        try:
            return path_obj.relative_to(base)
        except ValueError:
            # 如果无法创建相对路径，返回绝对路径
            return path_obj.absolute()
            
    def join_paths(self, *paths):
        """安全地连接路径"""
        if not paths:
            return Path()
            
        result = Path(paths[0])
        for path in paths[1:]:
            if path:
                result = result / path
                
        return result
        
    def safe_filename(self, filename):
        """创建安全的文件名"""
        if not filename:
            return filename
            
        # 移除或替换非法字符
        if self.is_windows:
            # Windows非法字符
            illegal_chars = r'[<>:"/\|?*]'
            reserved_names = {
                'CON', 'PRN', 'AUX', 'NUL',
                'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
            }
        else:
            # Unix系统非法字符
            illegal_chars = r'[/\0]'
            reserved_names = set()
            
        # 替换非法字符
        safe_name = re.sub(illegal_chars, '_', filename)
        
        # 检查保留名称
        name_without_ext = safe_name.split('.')[0].upper()
        if name_without_ext in reserved_names:
            safe_name = f"_{safe_name}"
            
        # 限制长度
        max_filename_length = 255  # 大多数文件系统的限制
        if len(safe_name) > max_filename_length:
            name, ext = os.path.splitext(safe_name)
            max_name_length = max_filename_length - len(ext)
            safe_name = name[:max_name_length] + ext
            
        return safe_name
        
    def check_path_length(self, path):
        """检查路径长度是否超出限制"""
        path_str = str(path)
        return len(path_str) <= self.max_path_length
        
    def shorten_path(self, path, max_length=None):
        """缩短路径长度"""
        if max_length is None:
            max_length = self.max_path_length
            
        path_obj = Path(path)
        path_str = str(path_obj)
        
        if len(path_str) <= max_length:
            return path_obj
            
        # 尝试使用相对路径
        try:
            relative_path = path_obj.relative_to(Path.cwd())
            if len(str(relative_path)) <= max_length:
                return relative_path
        except ValueError:
            pass
            
        # 缩短路径组件
        parts = path_obj.parts
        if len(parts) <= 1:
            return path_obj  # 无法进一步缩短
            
        # 保留根目录和文件名，缩短中间部分
        root = parts[0]
        filename = parts[-1]
        middle_parts = parts[1:-1]
        
        # 计算可用长度
        available_length = max_length - len(root) - len(filename) - 2  # 2个分隔符
        
        if available_length <= 0:
            # 极端情况，只保留根目录和文件名
            return Path(root) / filename
            
        # 缩短中间部分
        shortened_middle = []
        current_length = 0
        
        for part in middle_parts:
            if current_length + len(part) + 1 <= available_length:
                shortened_middle.append(part)
                current_length += len(part) + 1
            else:
                # 添加省略号并停止
                if current_length + 4 <= available_length:  # "..." + separator
                    shortened_middle.append("...")
                break
                
        # 重新构建路径
        result_parts = [root] + shortened_middle + [filename]
        return Path(*result_parts)
        
    def create_temp_path(self, prefix="temp", suffix="", directory=None):
        """创建临时路径"""
        import tempfile
        
        if directory is None:
            directory = Path(tempfile.gettempdir())
        else:
            directory = Path(directory)
            
        # 确保目录存在
        directory.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{prefix}_{unique_id}{suffix}"
        
        return directory / self.safe_filename(filename)
        
    def ensure_directory(self, path):
        """确保目录存在"""
        path_obj = Path(path)
        
        if path_obj.is_file():
            # 如果是文件路径，获取父目录
            path_obj = path_obj.parent
            
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            print(f"创建目录失败: {path_obj}, 错误: {e}")
            return False
            
    def copy_with_path_handling(self, src, dst):
        """带路径处理的文件复制"""
        import shutil
        
        src_path = self.normalize_path(src)
        dst_path = self.normalize_path(dst)
        
        # 确保目标目录存在
        self.ensure_directory(dst_path.parent)
        
        # 检查路径长度
        if not self.check_path_length(dst_path):
            dst_path = self.shorten_path(dst_path)
            print(f"目标路径过长，已缩短为: {dst_path}")
            
        try:
            shutil.copy2(src_path, dst_path)
            return dst_path
        except (OSError, PermissionError) as e:
            print(f"文件复制失败: {src_path} -> {dst_path}, 错误: {e}")
            return None
            
    def get_path_info(self, path):
        """获取路径信息"""
        path_obj = self.normalize_path(path)
        
        info = {
            "original": str(path),
            "normalized": str(path_obj),
            "posix": path_obj.as_posix(),
            "uri": path_obj.as_uri(),
            "is_absolute": path_obj.is_absolute(),
            "exists": path_obj.exists(),
            "is_file": path_obj.is_file() if path_obj.exists() else None,
            "is_dir": path_obj.is_dir() if path_obj.exists() else None,
            "parent": str(path_obj.parent),
            "name": path_obj.name,
            "stem": path_obj.stem,
            "suffix": path_obj.suffix,
            "parts": path_obj.parts,
            "length": len(str(path_obj)),
            "within_limit": self.check_path_length(path_obj)
        }
        
        return info
        
    def convert_path_for_system(self, path, target_system=None):
        """为指定系统转换路径格式"""
        if target_system is None:
            target_system = self.system
            
        target_system = target_system.lower()
        path_obj = self.normalize_path(path)
        
        if target_system == "windows":
            return str(path_obj).replace('/', '\\')
        elif target_system in ["linux", "darwin", "posix"]:
            return path_obj.as_posix()
        else:
            return str(path_obj)
            
# 全局实例
path_compat = PathCompatibility()

# 便捷函数
def normalize_path(path):
    """标准化路径的便捷函数"""
    return path_compat.normalize_path(path)
    
def to_posix(path):
    """转换为POSIX路径的便捷函数"""
    return path_compat.to_posix_path(path)
    
def to_native(path):
    """转换为原生路径的便捷函数"""
    return path_compat.to_native_path(path)
    
def safe_join(*paths):
    """安全连接路径的便捷函数"""
    return path_compat.join_paths(*paths)
    
def safe_filename(filename):
    """创建安全文件名的便捷函数"""
    return path_compat.safe_filename(filename)
    
def ensure_dir(path):
    """确保目录存在的便捷函数"""
    return path_compat.ensure_directory(path)

if __name__ == "__main__":
    # 测试代码
    pc = PathCompatibility()
    
    test_paths = [
        "C:\\Users\\Test\\Documents\\file.txt",
        "/home/user/documents/file.txt",
        "./relative/path/file.txt",
        "../parent/file.txt",
        "file:///C:/Users/Test/file.txt",
        "file:///home/user/file.txt"
    ]
    
    print("=== 路径兼容性测试 ===")
    print(f"当前系统: {pc.system}")
    print(f"最大路径长度: {pc.max_path_length}")
    print()
    
    for test_path in test_paths:
        print(f"测试路径: {test_path}")
        try:
            info = pc.get_path_info(test_path)
            print(f"  标准化: {info['normalized']}")
            print(f"  POSIX: {info['posix']}")
            print(f"  长度: {info['length']} (限制内: {info['within_limit']})")
            print()
        except Exception as e:
            print(f"  错误: {e}")
            print()