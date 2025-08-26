#!/usr/bin/env python3
"""
Crystal3D 配置管理
"""
import os
import socket
from typing import Optional

class Config:
    """应用配置类"""
    
    def __init__(self):
        # 服务器配置
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 8000))
        
        # 自动检测的IP地址
        self._local_ip = None
        self._public_url = None
        
        # 功能开关
        self.ENABLE_AR_PREVIEW = os.getenv("ENABLE_AR_PREVIEW", "true").lower() == "true"
        self.ENABLE_QR_CODE = os.getenv("ENABLE_QR_CODE", "true").lower() == "true"
    
    def get_local_ip(self) -> str:
        """获取本机局域网IP地址"""
        if self._local_ip is None:
            try:
                import netifaces
                # 优先使用netifaces获取网络接口
                interfaces = netifaces.interfaces()
                best_ip = None
                
                for interface in interfaces:
                    try:
                        addrs = netifaces.ifaddresses(interface)
                        if netifaces.AF_INET in addrs:
                            for addr_info in addrs[netifaces.AF_INET]:
                                ip = addr_info['addr']
                                # 优先选择192.168.x.x网段
                                if ip.startswith('192.168.'):
                                    self._local_ip = ip
                                    return self._local_ip
                                # 其次选择10.x.x.x网段
                                elif ip.startswith('10.') and not best_ip:
                                    best_ip = ip
                                # 最后选择172.16-31.x.x网段
                                elif ip.startswith('172.') and not best_ip:
                                    octets = ip.split('.')
                                    if len(octets) >= 2 and 16 <= int(octets[1]) <= 31:
                                        best_ip = ip
                    except:
                        continue
                
                if best_ip:
                    self._local_ip = best_ip
                    return self._local_ip
                    
            except ImportError:
                # netifaces不可用，使用原有方法
                pass
            except Exception:
                pass
            
            try:
                # 尝试连接到一个外部地址来获取本机IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                self._local_ip = s.getsockname()[0]
                s.close()
            except Exception:
                # 备用方法：获取hostname对应的IP
                try:
                    self._local_ip = socket.gethostbyname(socket.gethostname())
                except Exception:
                    self._local_ip = "127.0.0.1"
        return self._local_ip
    
    def get_public_url(self, use_localhost: bool = False) -> str:
        """获取公开访问的URL"""
        if use_localhost:
            return f"http://localhost:{self.PORT}"
        
        # 优先使用环境变量设置的公开URL
        public_url = os.getenv("PUBLIC_URL")
        if public_url:
            return public_url.rstrip('/')
        
        # 使用局域网IP
        local_ip = self.get_local_ip()
        return f"http://{local_ip}:{self.PORT}"
    
    def get_qr_base_url(self) -> str:
        """获取二维码使用的基础URL"""
        # 优先使用环境变量
        qr_url = os.getenv("QR_BASE_URL")
        if qr_url:
            return qr_url.rstrip('/')
        
        # 使用公开URL
        return self.get_public_url()
    
    def set_public_url(self, url: str):
        """设置公开URL（运行时）"""
        os.environ["PUBLIC_URL"] = url.rstrip('/')
        self._public_url = None  # 重置缓存
    
    def set_qr_base_url(self, url: str):
        """设置二维码基础URL（运行时）"""
        os.environ["QR_BASE_URL"] = url.rstrip('/')
    
    def get_all_access_urls(self) -> dict:
        """获取所有访问URL"""
        local_ip = self.get_local_ip()
        return {
            "localhost": f"http://localhost:{self.PORT}",
            "local_network": f"http://{local_ip}:{self.PORT}",
            "public": self.get_public_url(),
            "qr_code": self.get_qr_base_url() if self.ENABLE_QR_CODE else None
        }
    
    def print_access_info(self):
        """打印访问信息"""
        local_ip = self.get_local_ip()
        urls = self.get_all_access_urls()
        
        print(f"\n🌐 服务访问信息:")
        print(f"   本机访问: {urls['localhost']}")
        print(f"   局域网访问: {urls['local_network']}")
        
        if urls['public'] != urls['local_network']:
            print(f"   公开访问: {urls['public']}")
        
        if self.ENABLE_QR_CODE and urls['qr_code']:
            print(f"   二维码使用: {urls['qr_code']}")
        
        print(f"\n📱 手机访问步骤:")
        print(f"   1. 确保手机和电脑连接同一WiFi")
        print(f"   2. 手机浏览器打开: {urls['local_network']}")
        if self.ENABLE_QR_CODE:
            print(f"   3. 或扫描转换结果页面的二维码")
        
        print(f"\n⚙️  配置选项:")
        print(f"   设置公开URL: set PUBLIC_URL=http://your-domain.com")
        print(f"   设置公网IP: set PUBLIC_URL=http://123.45.67.89:8000")
        print(f"   设置二维码URL: set QR_BASE_URL=http://your-ip:8000")
        print(f"   设置端口: set PORT=9000")
        
        if not self.ENABLE_AR_PREVIEW:
            print(f"   ⚠️  AR预览功能已禁用 (ENABLE_AR_PREVIEW=false)")
        if not self.ENABLE_QR_CODE:
            print(f"   ⚠️  二维码功能已禁用 (ENABLE_QR_CODE=false)")
        
        print(f"\n💡 高级配置:")
        print(f"   禁用AR预览: set ENABLE_AR_PREVIEW=false")
        print(f"   禁用二维码: set ENABLE_QR_CODE=false")
        print(f"   设置主机: set HOST=127.0.0.1")

# 全局配置实例
config = Config()