# 🚀 Crystal3D - 晶体结构3D转换器 完整部署指南

## 📋 项目状态

✅ **系统已完全可用！** 根据最新测试显示：
- ✅ CIF解析成功（Pymatgen + ASE）
- ✅ 3D预览正常（Plotly.js）
- ✅ OBJ生成成功（多转换器支持）
- ✅ USDZ转换成功（多引擎支持）
- ✅ Web界面完全正常
- ✅ AR预览功能就绪
- ✅ Docker USD可选增强

## 🎯 三种部署方式

### 方式一：一键启动（推荐新手）

```bash
# 1. Windows用户双击启动
一键启动.bat

# 2. 或手动启动
python main.py

# 3. 访问界面
http://localhost:8000
```

### 方式二：Docker部署（推荐生产）

```bash
# 1. 使用Docker Compose
docker-compose up -d

# 2. 或直接运行容器
docker run -p 8000:8000 crystal3d-converter

# 3. 访问服务
http://localhost:8000
```

### 方式三：服务器部署（推荐企业）

```bash
# 1. 环境准备
sudo apt update && sudo apt install python3 python3-pip nginx

# 2. 项目部署
git clone https://your-repo/crystal3d-converter.git
cd crystal3d-converter
pip3 install -r requirements_optimal.txt

# 3. 生产启动
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## 🔧 当前系统配置

### ✅ 已正常工作的功能

#### **CIF解析系统**
1. **Pymatgen转换器** - Materials Project官方标准
   - 精确的晶体结构解析
   - 自动化学键计算
   - 专业材料科学支持

2. **ASE转换器** - 科学计算备用方案
   - 原子模拟环境标准
   - 广泛的文件格式支持
   - 可靠的结构处理

3. **内置解析器** - 保底方案
   - 纯Python实现
   - 基础CIF解析功能
   - 确保系统可用性

#### **USDZ转换系统**
1. **Apple USD** - 最佳质量（如果可用）
   - 苹果官方usdzconvert工具
   - 完美iOS AR兼容性
   - 最优USDZ质量

2. **Docker USD** - 专业方案（可选）
   - 基于Docker容器的专业转换
   - 跨平台一致性保证
   - 高质量专业输出

3. **TinyUSDZ** - 轻量级方案
   - 快速轻量级转换
   - 纯C++高性能库
   - 良好的降级兼容

4. **Pixar USD-Core** - Python原生
   - Pixar官方Python API
   - 直接USD格式操作
   - 最后保底方案

#### **Web和API系统**
- ✅ FastAPI高性能Web框架
- ✅ 现代化文件上传界面
- ✅ 实时3D预览（Plotly.js）
- ✅ RESTful API完整支持
- ✅ QR码AR预览功能

## 📦 依赖配置策略

### 🎯 针对不同环境的优化配置

#### 开发环境
```bash
# 完整功能，包含调试工具
pip install -r requirements.txt
```
- 包含：pymatgen, ase, usd-core, matplotlib, plotly
- 优势：功能完整，调试方便
- 适用：本地开发测试

#### 生产环境
```bash
# 优化配置，提高成功率
pip install -r requirements_optimal.txt
```
- 核心：pymatgen, ase, 基础Web框架
- 优势：安装成功率高，功能稳定
- 适用：服务器部署

#### 快速安装
```bash
# 最小依赖，避免编译问题
pip install -r requirements_minimal.txt
```
- 基础：ase, web框架，无复杂编译
- 优势：安装快速，兼容性好
- 适用：网络环境差的场景

## 🏗️ 部署步骤详解

### 步骤1: 环境准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip git

# macOS
brew install python git

# Windows
# 安装 Python 3.8+ 和 Git
```

### 步骤2: 项目获取

```bash
# 克隆项目
git clone https://your-repo/crystal3d-converter.git
cd crystal3d-converter

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

### 步骤3: 依赖安装

```bash
# 根据环境选择依赖文件
pip install -r requirements_optimal.txt  # 推荐

# 验证安装
python -c "from converter.main_converter import CIFToUSDZConverter; print('安装成功:', bool(CIFToUSDZConverter()))"
```

### 步骤4: 配置检查

```bash
# 检查转换器可用性
python -c "
from converter.main_converter import CIFToUSDZConverter
c = CIFToUSDZConverter()
print('CIF转换器:', list(c.cif_converters.keys()))
print('USDZ转换器:', list(c.usdz_converters.keys()))
"
```

### 步骤5: 启动服务

```bash
# 开发模式
python main.py

# 生产模式
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# 后台运行
nohup python main.py > /dev/null 2>&1 &
```

## 🐳 Docker部署

### 基础Docker部署

```bash
# 构建镜像
docker build -t crystal3d-converter .

# 运行容器
docker run -d \
  --name crystal3d-converter \
  -p 8000:8000 \
  crystal3d-converter

# 检查状态
docker logs crystal3d-converter
```

### Docker Compose部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  crystal3d-converter:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - SPHERE_RESOLUTION=20
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped
```

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### Docker增强配置

```bash
# 启用Docker USD增强（可选）
docker pull michaelgold/usdzconvert:0.66-usd-22.05b

# 验证Docker USD可用性
python -c "
from scripts.docker_usdzconvert import DockerUsdzConverter
converter = DockerUsdzConverter()
print('Docker USD可用:', converter.is_available)
"
```

## ⚙️ 高级配置

### 环境变量配置

```bash
# 服务配置
export PORT=8000
export HOST=0.0.0.0
export WORKERS=4

# 转换质量配置
export SPHERE_RESOLUTION=20      # 球体细分度(1-50)
export INCLUDE_BONDS=true        # 是否显示化学键
export SCALE_FACTOR=1.0          # 模型缩放因子

# 可选增强
export DOCKER_USD_AVAILABLE=true  # 启用Docker USD
export USD_CONVERTER_PATH=/usr/local/bin/usdzconvert  # Apple USD路径
```

### Nginx反向代理

```nginx
# /etc/nginx/sites-available/crystal3d-converter
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传大小限制
    client_max_body_size 100M;

    # 静态文件缓存
    location /static/ {
        alias /path/to/crystal3d-converter/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### SSL/HTTPS配置

```bash
# 使用Certbot获取SSL证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 性能优化

### 生产环境优化

```bash
# 使用Gunicorn多进程
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --preload \
         main:app

# 配置进程数量（一般为CPU核心数*2）
WORKERS=$(nproc --all)
gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker main:app
```

### 内存优化

```bash
# 低内存环境配置
export SPHERE_RESOLUTION=10
export INCLUDE_BONDS=false
export MAX_FILE_SIZE_MB=50

# 启用最小依赖模式
pip install -r requirements_minimal.txt
```

### 磁盘优化

```bash
# 配置临时文件清理
export CLEANUP_TEMP_FILES=true
export TEMP_FILE_LIFETIME=3600  # 1小时后清理

# 使用SSD存储临时文件
export TEMP_DIR=/fast-storage/temp
```

## 🔍 监控和维护

### 健康检查

```bash
# API健康检查
curl http://localhost:8000/health

# 详细状态检查
curl http://localhost:8000/info
```

### 日志管理

```bash
# 查看应用日志
tail -f logs/app.log

# 转换日志
tail -f logs/converter.log

# 系统日志
journalctl -u crystal3d-converter -f
```

### 备份策略

```bash
# 备份配置文件
tar -czf backup-$(date +%Y%m%d).tar.gz \
    requirements*.txt \
    main.py \
    config.py \
    docker-compose.yml

# 定期备份
echo "0 2 * * * cd /path/to/crystal3d-converter && tar -czf backup-\$(date +\%Y\%m\%d).tar.gz *.py *.txt *.yml" | crontab -
```

## 🐛 故障排除

### 常见部署问题

1. **依赖安装失败**
   ```bash
   # 升级pip和setuptools
   pip install --upgrade pip setuptools wheel
   
   # 使用conda解决编译问题
   conda install -c conda-forge pymatgen ase
   ```

2. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep :8000
   
   # 使用其他端口
   export PORT=8001
   ```

3. **权限问题**
   ```bash
   # 设置正确权限
   chmod +x main.py
   chown -R www-data:www-data /path/to/crystal3d-converter
   ```

4. **Docker问题**
   ```bash
   # 检查Docker状态
   systemctl status docker
   
   # 重启Docker服务
   sudo systemctl restart docker
   ```

### 性能问题诊断

```bash
# 内存使用监控
ps aux | grep python | grep main.py

# 磁盘空间检查
df -h /tmp

# 网络连接检查
netstat -an | grep :8000
```

## 🎉 部署验证

### 功能验证清单

- [ ] Web界面正常访问 (http://localhost:8000)
- [ ] API文档可用 (http://localhost:8000/docs)
- [ ] 文件上传功能正常
- [ ] 3D预览显示正确
- [ ] USDZ转换成功
- [ ] AR预览QR码生成
- [ ] 健康检查通过

### 测试脚本

```bash
# 运行完整测试套件
python tests/test_conversion.py
python tests/test_converter_quality.py

# API功能测试
curl -X POST "http://localhost:8000/convert" \
     -F "file=@examples/simple_crystal.cif" \
     -o "test_output.usdz"
```

---

🎯 **部署完成！您的Crystal3D晶体结构3D转换服务现已就绪！**

系统将自动选择最佳可用的转换器，确保在任何环境下都能提供稳定的转换服务。 