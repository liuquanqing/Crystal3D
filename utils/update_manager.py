import subprocess
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger
from pathlib import Path

class PackageUpdateManager:
    """软件包更新管理器"""
    
    def __init__(self):
        self.safe_packages = {
            'fastapi', 'uvicorn', 'plotly', 'numpy', 'requests',
            'loguru', 'jinja2', 'python-multipart', 'qrcode',
            'pillow', 'pydantic'
        }
        self.critical_packages = {
            'ase', 'pymatgen'  # 这些包更新需要特别小心
        }
        
    def check_pip_available(self) -> bool:
        """检查pip是否可用"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"检查pip可用性失败: {e}")
            return False
    
    def get_installed_packages(self) -> Dict[str, str]:
        """获取已安装的包列表"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return {pkg['name'].lower(): pkg['version'] for pkg in packages}
        except Exception as e:
            logger.error(f"获取已安装包列表失败: {e}")
        return {}
    
    def check_package_dependencies(self, package_name: str) -> List[str]:
        """检查包的依赖关系"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name],
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('Requires:'):
                        deps = line.replace('Requires:', '').strip()
                        if deps:
                            return [dep.strip() for dep in deps.split(',')]
            return []
        except Exception as e:
            logger.error(f"检查{package_name}依赖失败: {e}")
            return []
    
    def simulate_update(self, package_name: str) -> Dict[str, Any]:
        """模拟更新（干运行）"""
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--dry-run', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'would_install': self._parse_dry_run_output(result.stdout)
            }
        except Exception as e:
            logger.error(f"模拟更新{package_name}失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_dry_run_output(self, output: str) -> List[str]:
        """解析干运行输出"""
        packages = []
        lines = output.split('\n')
        for line in lines:
            if 'Would install' in line or 'Would upgrade' in line:
                # 提取包名
                parts = line.split()
                for part in parts:
                    if '==' in part:
                        pkg_name = part.split('==')[0]
                        packages.append(pkg_name)
        return packages
    
    async def update_package(self, package_name: str, force: bool = False) -> Dict[str, Any]:
        """更新单个包"""
        package_name = package_name.lower()
        
        # 安全检查
        if not force and package_name not in self.safe_packages:
            if package_name in self.critical_packages:
                return {
                    'success': False,
                    'error': f'{package_name}是关键包，需要手动更新以避免兼容性问题',
                    'suggestion': f'请手动执行: pip install --upgrade {package_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'{package_name}不在安全更新列表中',
                    'suggestion': '如需更新，请使用force=True参数'
                }
        
        try:
            # 先进行模拟更新
            sim_result = self.simulate_update(package_name)
            if not sim_result['success']:
                return {
                    'success': False,
                    'error': f'模拟更新失败: {sim_result.get("error", "未知错误")}'
                }
            
            # 执行实际更新
            logger.info(f"开始更新包: {package_name}")
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', package_name]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            success = process.returncode == 0
            
            result = {
                'success': success,
                'package': package_name,
                'output': stdout.decode() if stdout else '',
                'error': stderr.decode() if stderr else '',
                'simulation': sim_result.get('would_install', [])
            }
            
            if success:
                logger.info(f"包{package_name}更新成功")
            else:
                logger.error(f"包{package_name}更新失败: {result['error']}")
            
            return result
            
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': '更新超时（5分钟）',
                'package': package_name
            }
        except Exception as e:
            logger.error(f"更新{package_name}时发生异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'package': package_name
            }
    
    async def update_multiple_packages(self, packages: List[str], force: bool = False) -> Dict[str, Any]:
        """批量更新包"""
        results = {}
        failed_packages = []
        successful_packages = []
        
        for package in packages:
            result = await self.update_package(package, force)
            results[package] = result
            
            if result['success']:
                successful_packages.append(package)
            else:
                failed_packages.append(package)
        
        return {
            'success': len(failed_packages) == 0,
            'total': len(packages),
            'successful': len(successful_packages),
            'failed': len(failed_packages),
            'successful_packages': successful_packages,
            'failed_packages': failed_packages,
            'details': results
        }
    
    def get_update_recommendations(self) -> Dict[str, Any]:
        """获取更新建议"""
        recommendations = {
            'safe_to_update': [],
            'requires_caution': [],
            'manual_update_required': []
        }
        
        installed = self.get_installed_packages()
        
        for package in installed:
            if package in self.safe_packages:
                recommendations['safe_to_update'].append(package)
            elif package in self.critical_packages:
                recommendations['requires_caution'].append(package)
            else:
                recommendations['manual_update_required'].append(package)
        
        return recommendations

# 全局实例
update_manager = PackageUpdateManager()