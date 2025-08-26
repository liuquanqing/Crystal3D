# CIF转USDZ转换工具 - 优化Docker配置
# 基于Python官方镜像，移除conda依赖，使用纯pip方案
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（移除Java，简化Docker镜像）
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 升级pip并设置国内源
RUN pip install --upgrade pip && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# 复制依赖文件（优化顺序）
COPY requirements_optimal.txt .
COPY requirements_minimal.txt .
COPY requirements.txt .

# 分层安装依赖 - 与本地脚本保持一致
RUN pip install --no-cache-dir -r requirements_optimal.txt || \
    pip install --no-cache-dir -r requirements_minimal.txt || \
    pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir fastapi uvicorn python-multipart aiofiles pymatgen ase pillow loguru

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p logs static examples output temp conversion_results user_files

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令 - 直接使用Python
CMD ["python", "main.py"] 