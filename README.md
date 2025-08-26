# Crystal3D - 晶体结构3D转换器

🎯 **专业的晶体结构文件转换解决方案**

将CIF（Crystallographic Information File）文件转换为USDZ格式，支持3D预览和iOS AR展示。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## 🚀 快速开始（30秒启动）

### Windows用户（推荐）
```bash
# 1. 下载项目
git clone <your-repo-url>
cd crystal3d-converter

# 2. 双击运行
一键启动.bat

# 3. 打开浏览器访问 http://localhost:8000
```

### macOS/Linux用户
```bash
# 1. 下载项目
git clone <your-repo-url>
cd crystal3d-converter

# 2. 一键安装和启动
./setup_usd_local.sh
python main.py

# 3. 打开浏览器访问 http://localhost:8000
```

### 使用示例
1. 上传CIF文件（支持拖拽）
2. 自动3D预览晶体结构
3. 点击"转换为USDZ"按钮
4. 下载USDZ文件或扫描QR码在iPhone上AR预览

## ✨ 特性

- 🔄 **智能转换**: CIF → OBJ → USDZ 完整转换链
- 🎨 **专业3D预览**: 基于Plotly.js的高质量晶体结构渲染
- 📱 **AR支持**: iOS Quick Look AR预览，QR码扫描
- 🛠️ **多种转换器**: 
  - 🥇 **Pymatgen**（推荐，Materials Project官方）
  - 🥈 **ASE**（科学计算标准库）
  - 🥉 **内置Python生成器**（备用方案）
- 🎯 **多种USDZ引擎**:
  - 🏆 **Apple官方USD工具**（最佳USDZ质量）
  - 🐳 **Docker专业USD**（可选高质量转换）
  - ⚡ **TinyUSDZ**（轻量级方案）
  - 🔧 **Pixar USD-Core**（Python API）
- 🌐 **Web界面**: 现代化的上传、预览、转换界面
- 🚀 **RESTful API**: 支持程序化调用
- 📦 **一键部署**: Docker支持，云服务器就绪
- 🎯 **跨平台**: Windows/Linux/macOS完全兼容

## 📦 安装方式

### 方法一：一键启动（推荐新手）

**Windows:**
```bash
# 双击运行
一键启动.bat
```

**macOS/Linux:**
```bash
# 一键安装和启动
./setup_usd_local.sh
python main.py
```

### 方法二：手动安装（推荐开发者）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd crystal3d-converter

# 2. 选择依赖安装方式（三选一）
pip install -r requirements.txt          # 完整功能
pip install -r requirements_minimal.txt  # 快速安装
pip install -r requirements_optimal.txt  # 生产推荐

# 3. 启动服务
python main.py

# 4. 访问 http://localhost:8000
```

### 方法三：Docker部署（推荐生产）

```bash
# 使用Docker Compose
docker-compose up -d

# 或直接使用Docker
docker build -t crystal3d .
docker run -p 8000:8000 crystal3d
```

## 📋 系统要求

### 最低要求
- **Python**: 3.8+ （推荐3.10+）
- **操作系统**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **内存**: 4GB RAM
- **磁盘**: 1GB可用空间

### 推荐配置
- **Python**: 3.10+
- **内存**: 8GB+ RAM
- **网络**: 稳定的网络连接（用于依赖下载）

### 可选增强
- **Apple USD工具**: macOS上的usdpython（最佳USDZ质量）
- **Docker Desktop**: 容器化部署
- **Git**: 版本控制和项目克隆

## 🔧 USD工具安装配置

### Apple USD工具（macOS推荐）

**安装步骤：**
1. 下载Apple USD工具包：
   - 访问 [Apple Developer USD Tools](https://developer.apple.com/augmented-reality/tools/)
   - 下载 `usdpython` 工具包
   - 解压到 `/Applications/usdpython/`

2. 验证安装：
   ```bash
   ls -la /Applications/usdpython/usdzconvert/usdzconvert
   # 应该显示可执行文件
   ```

3. 安装USD Python库：
   ```bash
   pip install usd-core
   ```

4. 测试pxr模块：
   ```bash
   python -c "import pxr; print('USD Python库安装成功')"
   ```

**环境变量配置（可选）：**
```bash
# 设置USD转换器路径
export USD_CONVERTER_PATH=/Applications/usdpython/usdzconvert/usdzconvert

# 或在启动时指定
USD_CONVERTER_PATH=/Applications/usdpython/usdzconvert/usdzconvert python main.py
```

### 其他平台USD工具

**Windows/Linux:**
```bash
# 安装USD Python库
pip install usd-core

# 验证安装
python -c "import pxr; print('USD库可用')"
```

**Docker方案（跨平台）:**
```bash
# 使用Docker USD环境
docker-compose up -d
```

## 🛠️ 依赖文件说明

项目提供三个依赖文件，根据需求选择：

### `requirements.txt` - 完整功能
```bash
pip install -r requirements.txt
```
- 包含所有核心功能
- 科学计算库：pymatgen, ase, numpy
- USD处理：usd-core
- 可视化：matplotlib, plotly
- **推荐日常开发使用**

### `requirements_minimal.txt` - 快速安装
```bash
pip install -r requirements_minimal.txt
```
- 最小依赖集合
- 避免复杂编译过程
- 基础转换功能可用
- **推荐网络环境差时使用**

### `requirements_optimal.txt` - 生产推荐
```bash
pip install -r requirements_optimal.txt
```
- 优化的依赖组合
- 提高安装成功率
- 核心功能完整
- **推荐生产环境使用**

## 💻 使用方法

### Web界面使用

1. **启动服务**:
   ```bash
   # 使用一键启动脚本
   一键启动.bat  # Windows
   
   # 或手动启动
   python main.py
   ```

2. **打开浏览器**: http://localhost:8000

3. **上传CIF文件**: 拖拽或点击上传

4. **3D预览**: 自动渲染晶体结构

5. **转换USDZ**: 点击"转换为USDZ"

6. **AR预览**: 用iPhone扫描QR码

### API使用

```python
import requests

# 上传和转换
with open('crystal.cif', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/convert',
        files={'file': f}
    )

# 下载结果
if response.status_code == 200:
    with open('crystal.usdz', 'wb') as f:
        f.write(response.content)
```

### 命令行使用

```bash
# 单文件转换
python -m converter.main_converter input.cif output.usdz

# 批量转换
python scripts/batch_convert.py input_folder/ output_folder/

# 测试系统
python test_system.py
```

## 🎯 转换器详情

### CIF解析器（优先级顺序）

1. **Pymatgen** (推荐)
   - Materials Project官方库
   - 最权威的材料科学标准
   - 精确的晶体结构解析

2. **ASE** (备用)
   - 原子模拟环境标准库
   - 广泛科学计算支持
   - 可靠的结构处理

3. **内置解析器** (最后备用)
   - 纯Python实现
   - 基础CIF解析能力
   - 保证系统可用性

### USDZ转换器（优先级顺序）

1. **Apple USD** (最佳质量)
   - 苹果官方usdzconvert工具
   - 最优USDZ兼容性
   - 完美AR支持

2. **Docker USD** (专业选项)
   - 基于Docker的USD转换
   - 高质量专业输出
   - 跨平台一致性

3. **TinyUSDZ** (轻量级)
   - 轻量级USD库
   - 快速转换
   - 降级兼容方案

4. **Pixar USD-Core** (Python原生)
   - Pixar官方Python绑定
   - 原生USD API
   - 最后保底方案

## 🚀 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t crystal3d-converter .

# 运行容器
docker run -p 8000:8000 crystal3d-converter

# Docker Compose
docker-compose up -d
```

### 云服务器部署

```bash
# 1. 服务器配置
sudo apt update
sudo apt install python3 python3-pip nginx

# 2. 部署项目
git clone https://your-repo/crystal3d-converter.git
cd crystal3d-converter
pip3 install -r requirements_optimal.txt

# 3. 配置Nginx反向代理
sudo cp configs/nginx.conf /etc/nginx/sites-available/crystal3d-converter
sudo ln -s /etc/nginx/sites-available/crystal3d-converter /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# 4. 启动服务
python3 main.py
```

### 生产环境配置

```bash
# 使用Gunicorn + Nginx
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# 系统服务
sudo cp configs/crystal3d-converter.service /etc/systemd/system/
sudo systemctl enable crystal3d-converter
sudo systemctl start crystal3d-converter
```

## 📁 项目结构

```
crystal3d-converter/
├── 📁 api/                   # API路由和处理
├── 📁 converter/             # 核心转换器
├── 📁 config/                # 配置文件
├── 📁 static/                # 前端资源（HTML/CSS/JS）
├── 📁 docs/                  # 文档目录
├── 📁 examples/              # 示例CIF文件
├── 📁 tests/                 # 测试文件
├── 📁 scripts/               # 实用脚本
├── 📁 utils/                 # 工具函数
├── 📁 tinyusdz/              # TinyUSDZ库
├── main.py                   # 主程序入口
├── requirements.txt          # 完整依赖
├── requirements_minimal.txt  # 最小依赖
├── requirements_optimal.txt  # 优化依赖
├── setup.py                  # 安装配置
├── setup_usd_local.sh        # USD环境安装脚本
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker编排
├── 一键启动.bat              # Windows一键启动
└── README.md                # 本文档
```

### 核心目录说明
- **converter/**: 包含所有转换器逻辑，支持多种CIF解析器和USDZ生成器
- **api/**: RESTful API接口，支持文件上传和转换
- **static/**: Web界面，支持拖拽上传和3D预览
- **examples/**: 提供测试用的CIF文件样本
- **docs/**: 详细的使用和配置文档

## 🔧 配置选项

### 环境变量

```bash
# 服务配置
export PORT=8000                    # 服务端口
export HOST=0.0.0.0                # 绑定地址

# 转换器配置
export USD_CONVERTER_PATH=/usr/bin/usdzconvert  # USD工具路径
export DOCKER_USD_AVAILABLE=true   # Docker USD可用性

# 质量设置
export SPHERE_RESOLUTION=20         # 原子球体细分
export INCLUDE_BONDS=true          # 是否包含化学键
export SCALE_FACTOR=1.0            # 模型缩放
```

### 配置文件

创建`config.yaml`:

```yaml
# 服务器配置
server:
  host: "0.0.0.0"
  port: 8000
  workers: 1

# 转换器配置
converter:
  sphere_resolution: 20
  include_bonds: true
  scale_factor: 1.0

# 存储配置
storage:
  temp_dir: "/tmp"
  max_file_size: 100  # MB
  cleanup_after: 3600  # 秒
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 系统测试
python test_system.py

# 转换器测试
python tests/test_converter_quality.py

# API测试
python test_api.py

# 性能测试
python test_performance.py
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**:
   ```bash
   # 更改端口
   export PORT=8001
   python main.py
   ```

2. **依赖安装失败**:
   ```bash
   # 尝试最小依赖
   pip install -r requirements_minimal.txt
   
   # 或使用conda
   conda install -c conda-forge pymatgen ase
   ```

3. **Docker不可用**:
   ```bash
   # 系统会自动降级到本地转换器
   # 检查Docker状态
   docker --version
   ```

4. **内存不足**:
   ```bash
   # 减少球体细分
   export SPHERE_RESOLUTION=10
   
   # 禁用化学键
   export INCLUDE_BONDS=false
   ```

### 转换器检查

```bash
# 检查可用转换器
python -c "from converter.main_converter import CIFToUSDZConverter; c = CIFToUSDZConverter(); print('CIF转换器:', list(c.cif_converters.keys())); print('USDZ转换器:', list(c.usdz_converters.keys()))"
   ```

### 日志调试

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main.py

# 查看转换日志
tail -f logs/converter.log
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交修改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🙏 致谢

- [pymatgen](https://pymatgen.org/) - Materials Project官方材料科学库
- [ASE](https://wiki.fysik.dtu.dk/ase/) - 原子模拟环境
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [USD](https://openusd.org/) - Pixar通用场景描述
- [TinyUSDZ](https://github.com/lighttransport/tinyusdz) - 轻量级USD库

## 📞 支持

- 📧 Email: dev@example.com
- 💬 Issues: [GitHub Issues](https://github.com/yourorg/crystal3d-converter/issues)
- 📖 文档: [Wiki](https://github.com/yourorg/crystal3d-converter/wiki)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！