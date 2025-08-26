"""CIF转USDZ转换服务主入口"""
import os
import sys
import uvicorn
from api.routes import app
from utils import setup_logger
from config import config

# 设置日志
logger = setup_logger()

if __name__ == "__main__":
    # 从环境变量或命令行参数获取端口
    port = config.PORT
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            config.PORT = port  # 更新配置
        except ValueError:
            logger.warning(f"无效的端口参数: {sys.argv[1]}，使用默认端口 {port}")
    
    logger.info(f"启动Crystal3D转换服务，端口: {port}...")
    
    # 打印访问信息
    config.print_access_info()
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=port,
        reload=False,
        log_level="info"
    )