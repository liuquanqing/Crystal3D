"""
日志配置工具
"""
import os
import sys
from loguru import logger


def setup_logger(log_level: str = None):
    """设置日志配置"""
    if log_level is None:
        log_level = os.getenv('CIF_CONVERTER_LOG_LEVEL', 'INFO')
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 添加文件输出
    log_dir = os.getenv('CIF_CONVERTER_LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logger.add(
        os.path.join(log_dir, "cif_converter.log"),
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    return logger 