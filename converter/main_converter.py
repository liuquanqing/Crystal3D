#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIF到USDZ主转换器
整合多种CIF解析器和USDZ转换器
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from loguru import logger

# 导入CIF转换器
try:
    from .reliable_cif_converter import ReliableCIFConverter
except ImportError:
    logger.warning("无法导入ReliableCIFConverter")
    ReliableCIFConverter = None

# 导入USDZ转换器
try:
    from .usdz_converter import USDZConverter
except ImportError:
    logger.warning("无法导入USDZConverter")
    USDZConverter = None

# TinyUSDZ转换器已禁用 - 保留代码以备将来使用
# try:
#     from .tinyusdz_converter import TinyUSDZConverter
# except ImportError:
#     logger.warning("无法导入TinyUSDZConverter")
#     TinyUSDZConverter = None
TinyUSDZConverter = None

try:
    from .apple_usd_converter import AppleUSDConverter
except ImportError:
    logger.warning("无法导入AppleUSDConverter")
    AppleUSDConverter = None

# 尝试导入Docker USD转换器（可选）
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
    from docker_usdzconvert import DockerUsdzConverter
    DOCKER_USD_AVAILABLE = True
except ImportError:
    DOCKER_USD_AVAILABLE = False
    DockerUsdzConverter = None


class CIFToUSDZConverter:
    """
    CIF到USDZ主转换器
    整合多种CIF解析器和USDZ转换器，提供智能转换策略
    """
    
    def __init__(self):
        """初始化转换器"""
        self.temp_dir = None
        
        # 初始化CIF转换器
        self.cif_converters = {}
        if ReliableCIFConverter:
            try:
                self.cif_converters['reliable'] = ReliableCIFConverter()
                logger.info("ReliableCIFConverter 初始化成功")
            except Exception as e:
                logger.warning(f"ReliableCIFConverter 初始化失败: {e}")
        
        # 初始化USDZ转换器
        self.usdz_converters = {}
        if USDZConverter:
            try:
                self.usdz_converters['pixar_usd'] = USDZConverter()
                logger.info("USDZConverter 初始化成功")
            except Exception as e:
                logger.warning(f"USDZConverter 初始化失败: {e}")
        
        # TinyUSDZConverter已禁用 - 保留代码以备将来使用
        # if TinyUSDZConverter:
        #     try:
        #         self.usdz_converters['tinyusdz'] = TinyUSDZConverter()
        #         logger.info("TinyUSDZConverter 初始化成功")
        #     except Exception as e:
        #         logger.warning(f"TinyUSDZConverter 初始化失败: {e}")
        
        if AppleUSDConverter:
            try:
                self.usdz_converters['apple_usd'] = AppleUSDConverter()
                logger.info("AppleUSDConverter 初始化成功")
            except Exception as e:
                logger.warning(f"AppleUSDConverter 初始化失败: {e}")
        
        # 初始化Docker USD转换器（可选）
        if DOCKER_USD_AVAILABLE and DockerUsdzConverter:
            try:
                docker_converter = DockerUsdzConverter()
                if hasattr(docker_converter, 'is_available') and docker_converter.is_available:
                    self.usdz_converters['docker_usd'] = docker_converter
                    logger.info("DockerUsdzConverter 初始化成功")
                else:
                    logger.warning("DockerUsdzConverter 不可用")
            except Exception as e:
                logger.warning(f"DockerUsdzConverter 初始化失败: {e}")
        
        logger.info(f"转换器初始化完成: CIF转换器={list(self.cif_converters.keys())}, USDZ转换器={list(self.usdz_converters.keys())}")
    
    def get_converter_status(self) -> Dict[str, Any]:
        """
        获取转换器状态信息
        
        Returns:
            转换器状态字典
        """
        status = {
            'cif_converters': {},
            'usdz_converters': {},
            'available': len(self.cif_converters) > 0 and len(self.usdz_converters) > 0
        }
        
        # CIF转换器状态
        for name, converter in self.cif_converters.items():
            try:
                if hasattr(converter, 'get_converter_info'):
                    status['cif_converters'][name] = converter.get_converter_info()
                else:
                    status['cif_converters'][name] = {
                        'name': name,
                        'available': True,
                        'description': f'{name} CIF转换器'
                    }
            except Exception as e:
                status['cif_converters'][name] = {
                    'name': name,
                    'available': False,
                    'error': str(e)
                }
        
        # USDZ转换器状态
        for name, converter in self.usdz_converters.items():
            try:
                if hasattr(converter, 'get_converter_info'):
                    status['usdz_converters'][name] = converter.get_converter_info()
                elif hasattr(converter, 'is_available'):
                    status['usdz_converters'][name] = {
                        'name': name,
                        'available': converter.is_available(),
                        'description': f'{name} USDZ转换器'
                    }
                else:
                    status['usdz_converters'][name] = {
                        'name': name,
                        'available': True,
                        'description': f'{name} USDZ转换器'
                    }
            except Exception as e:
                status['usdz_converters'][name] = {
                    'name': name,
                    'available': False,
                    'error': str(e)
                }
        
        return status
    
    def convert_cif_to_usdz(self, cif_file_path: str, output_path: str, 
                           options: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        将CIF文件转换为USDZ格式
        
        Args:
            cif_file_path: CIF文件路径
            output_path: 输出USDZ文件路径
            options: 转换选项
            
        Returns:
            (成功标志, 消息, 详细信息)
        """
        if not os.path.exists(cif_file_path):
            return False, f"CIF文件不存在: {cif_file_path}", {}
        
        if not self.cif_converters:
            return False, "没有可用的CIF转换器", {}
        
        if not self.usdz_converters:
            return False, "没有可用的USDZ转换器", {}
        
        options = options or {}
        conversion_info = {
            'cif_file': cif_file_path,
            'output_file': output_path,
            'steps': []
        }
        
        try:
            # 创建临时目录
            self.temp_dir = tempfile.mkdtemp(prefix='cif_to_usdz_')
            logger.info(f"创建临时目录: {self.temp_dir}")
            
            # 步骤1: CIF转OBJ
            obj_file_path, cif_success, cif_message, cif_info = self._convert_cif_to_obj(
                cif_file_path, options
            )
            conversion_info['steps'].append({
                'step': 'cif_to_obj',
                'success': cif_success,
                'message': cif_message,
                'details': cif_info
            })
            
            if not cif_success:
                return False, f"CIF转换失败: {cif_message}", conversion_info
            
            # 步骤2: OBJ转USDZ
            usdz_success, usdz_message, usdz_info = self._convert_obj_to_usdz(
                obj_file_path, output_path, options
            )
            conversion_info['steps'].append({
                'step': 'obj_to_usdz',
                'success': usdz_success,
                'message': usdz_message,
                'details': usdz_info
            })
            
            if not usdz_success:
                return False, f"USDZ转换失败: {usdz_message}", conversion_info
            
            # 验证输出文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                conversion_info['output_size'] = file_size
                logger.info(f"转换成功完成: {output_path} ({file_size} bytes)")
                return True, "转换成功完成", conversion_info
            else:
                return False, "输出文件未生成", conversion_info
                
        except Exception as e:
            error_msg = f"转换过程中发生错误: {str(e)}"
            logger.error(error_msg)
            conversion_info['error'] = error_msg
            return False, error_msg, conversion_info
            
        finally:
            # 不在这里清理临时目录，让调用者决定何时清理
            pass
    
    def _convert_cif_to_obj(self, cif_file_path: str, options: Dict[str, Any]) -> Tuple[str, bool, str, Dict[str, Any]]:
        """
        将CIF文件转换为OBJ格式
        
        Returns:
            (OBJ文件路径, 成功标志, 消息, 详细信息)
        """
        # 优先使用reliable转换器
        converter_name = 'reliable'
        if converter_name not in self.cif_converters:
            converter_name = list(self.cif_converters.keys())[0]
        
        converter = self.cif_converters[converter_name]
        logger.info(f"使用CIF转换器: {converter_name}")
        
        try:
            # 准备输出路径
            obj_filename = Path(cif_file_path).stem + '.obj'
            obj_file_path = os.path.join(self.temp_dir, obj_filename)
            
            # 执行转换
            if hasattr(converter, 'convert_cif_to_obj'):
                result = converter.convert_cif_to_obj(
                    cif_file_path, obj_file_path, options.get('preferred_converter'), 
                    options.get('include_bonds', True), 
                    options.get('scale_factor', 1.0)
                )
                success = result.get('success', False)
                message = result.get('error') if not success else f"转换成功，使用了 {result.get('converter_used')} 转换器"
                details = result
                return obj_file_path, success, message, details
            else:
                return obj_file_path, False, f"转换器 {converter_name} 不支持convert_cif_to_obj方法", {}
                
        except Exception as e:
            error_msg = f"CIF转换器 {converter_name} 执行失败: {str(e)}"
            logger.error(error_msg)
            return "", False, error_msg, {}
    
    def _convert_obj_to_usdz(self, obj_file_path: str, output_path: str, 
                            options: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        将OBJ文件转换为USDZ格式
        
        Returns:
            (成功标志, 消息, 详细信息)
        """
        conversion_attempts = []
        
        try:
            # 查找材质文件
            mtl_file_path = obj_file_path.replace('.obj', '.mtl')
            if not os.path.exists(mtl_file_path):
                mtl_file_path = None
            
            # 定义转换器优先级列表：Pixar USD第一，Apple USD第二，Docker第三
            # TinyUSDZ已禁用 - 从优先级列表中移除
            converter_priority = [
                {
                    'name': 'Pixar USD',
                    'key': 'pixar_usd',
                    'method': 'convert_obj_to_usdz'
                },
                # {
                #     'name': 'TinyUSDZ', 
                #     'key': 'tinyusdz',
                #     'method': 'convert_obj_to_usdz'
                # },
                {
                    'name': 'Apple USD',
                    'key': 'apple_usd', 
                    'method': 'convert_obj_to_usdz'
                },
                {
                    'name': 'Docker USD',
                    'key': 'docker_usd',
                    'method': 'convert_obj_to_usdz'
                }
            ]
            
            # 按优先级尝试每个转换器
            for converter_info in converter_priority:
                converter_key = converter_info['key']
                converter_name = converter_info['name']
                
                # 检查转换器是否可用
                if converter_key not in self.usdz_converters:
                    logger.info(f"{converter_name}转换器未配置，跳过")
                    conversion_attempts.append({
                        'converter': converter_name,
                        'success': False,
                        'message': '转换器未配置',
                        'error_type': 'not_configured'
                    })
                    continue
                
                converter = self.usdz_converters[converter_key]
                
                # 检查转换器可用性
                try:
                    if hasattr(converter, 'is_available'):
                        if not converter.is_available():
                            logger.info(f"{converter_name}转换器不可用，跳过")
                            conversion_attempts.append({
                                'converter': converter_name,
                                'success': False,
                                'message': '转换器不可用',
                                'error_type': 'unavailable'
                            })
                            continue
                except Exception as e:
                    logger.warning(f"检查{converter_name}转换器可用性时出错: {e}")
                
                try:
                    logger.info(f"尝试使用{converter_name}转换器")
                    
                    # 执行转换
                    if hasattr(converter, converter_info['method']):
                        convert_result = getattr(converter, converter_info['method'])(
                            obj_file_path, output_path, mtl_file_path
                        )
                        
                        # 处理不同的返回格式
                        if isinstance(convert_result, tuple):
                            success, message = convert_result
                        elif isinstance(convert_result, dict):
                            success = convert_result.get('success', False)
                            message = convert_result.get('message', '未知结果')
                        else:
                            success = bool(convert_result)
                            message = '转换完成' if success else '转换失败'
                        
                        conversion_attempts.append({
                            'converter': converter_name,
                            'success': success,
                            'message': message,
                            'error_type': None if success else 'conversion_failed'
                        })
                        
                        if success and os.path.exists(output_path):
                            logger.info(f"{converter_name}转换成功: {output_path}")
                            return True, f"{converter_name}转换成功", {
                                'converter': converter_key,
                                'converter_name': converter_name,
                                'conversion_attempts': conversion_attempts
                            }
                        else:
                            logger.warning(f"{converter_name}转换失败: {message}")
                    else:
                        error_msg = f"转换器 {converter_name} 不支持{converter_info['method']}方法"
                        logger.warning(error_msg)
                        conversion_attempts.append({
                            'converter': converter_name,
                            'success': False,
                            'message': error_msg,
                            'error_type': 'method_not_supported'
                        })
                        
                except Exception as e:
                    error_msg = f"{converter_name}转换器执行异常: {str(e)}"
                    logger.error(error_msg)
                    conversion_attempts.append({
                        'converter': converter_name,
                        'success': False,
                        'message': error_msg,
                        'error_type': 'exception'
                    })
            
            # 所有转换器都失败了
            failed_converters = [attempt['converter'] for attempt in conversion_attempts if not attempt['success']]
            error_summary = f"所有USDZ转换器都失败了: {', '.join(failed_converters)}"
            
            logger.error(error_summary)
            for attempt in conversion_attempts:
                if not attempt['success']:
                    logger.error(f"  - {attempt['converter']}: {attempt['message']}")
            
            return False, error_summary, {
                'conversion_attempts': conversion_attempts
            }
                
        except Exception as e:
            error_msg = f"USDZ转换过程中发生严重错误: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, {
                'conversion_attempts': conversion_attempts
            }
    
    def _cleanup_temp_dir(self):
        """
        清理临时目录
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"清理临时目录: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}")
            finally:
                self.temp_dir = None
    
    def __del__(self):
        """析构函数，确保清理临时目录"""
        self._cleanup_temp_dir()