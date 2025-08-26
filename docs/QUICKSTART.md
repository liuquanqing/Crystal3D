# Crystal3D - 晶体结构3D转换器 快速启动指南

## 🚀 一分钟快速开始

### 1. 获取项目

```bash
# 克隆或下载项目到本地
git clone https://your-repo/crystal3d-converter.git
cd crystal3d-converter
```

### 2. 选择安装方式

```bash
# 方式A: 完整功能（推荐开发）
pip install -r requirements.txt

# 方式B: 快速安装（网络环境差）
pip install -r requirements_minimal.txt

# 方式C: 生产优化（推荐部署）
pip install -r requirements_optimal.txt
```

### 3. 一键启动

```bash
# Windows用户（推荐）
一键启动.bat

# 或手动启动
python main.py

# 查看服务状态
curl http://localhost:8000/health
```

### 4. 访问服务

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **服务信息**: http://localhost:8000/info

## 📝 基本使用

### Web界面操作

1. **上传CIF文件**: 拖拽.cif文件到上传区域
2. **3D预览**: 自动显示晶体结构
3. **转换设置**: 调整球体细分度、是否显示化学键等
4. **生成USDZ**: 点击转换按钮
5. **下载结果**: 获取USDZ文件
6. **AR预览**: 用iPhone扫描QR码

### 命令行转换

```bash
# 单文件转换
python -m converter.main_converter examples/simple_crystal.cif output.usdz

# 检查转换器状态
python -c "from converter.main_converter import CIFToUSDZConverter; c = CIFToUSDZConverter(); print('可用转换器:', list(c.usdz_converters.keys()))"

# 测试转换流程
python tests/test_conversion.py
```

### API调用

```python
import requests

# 健康检查
response = requests.get('http://localhost:8000/health')
print(response.json())

# 文件转换
with open('crystal.cif', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/convert',
        files={'file': f}
    )
    
if response.status_code == 200:
    with open('output.usdz', 'wb') as f:
        f.write(response.content)
```

## 🔧 转换器说明

### CIF解析器（按优先级）

1. **Pymatgen** - Materials Project官方，最权威
2. **ASE** - 科学计算标准库，广泛支持
3. **内置解析器** - 保底方案，基础功能

### USDZ转换器（按优先级）

1. **Apple USD** - 苹果官方工具，最佳质量
2. **Docker USD** - 专业转换，需要Docker
3. **TinyUSDZ** - 轻量级方案
4. **Pixar USD** - Python原生API

## 🧪 功能测试

### 基础测试
```bash
# 快速功能测试
python -c "from converter.main_converter import CIFToUSDZConverter; print('系统初始化:', '成功' if CIFToUSDZConverter() else '失败')"

# 完整转换测试
python tests/test_converter_quality.py

# Web服务测试
python tests/test_conversion.py
```

### 依赖检查
```bash
# 检查核心库
python -c "import pymatgen, ase, usd; print('核心依赖: 正常')"

# 检查可选增强
python -c "
try:
    import matplotlib, plotly
    print('可视化库: 可用')
except ImportError:
    print('可视化库: 不可用（不影响核心功能）')
"
```

## 🐛 常见问题

### 依赖安装问题

**问题**: pymatgen安装失败
```bash
# 解决方案1: 使用conda
conda install -c conda-forge pymatgen

# 解决方案2: 使用最小依赖
pip install -r requirements_minimal.txt
```

**问题**: USD库安装问题
```bash
# 解决方案: 跳过USD，使用TinyUSDZ
pip install tinyusdz
```

### 运行时问题

**问题**: 端口被占用
```bash
# 解决方案: 更改端口
export PORT=8001
python main.py
```

**问题**: Docker不可用
```bash
# 解决方案: 系统会自动使用本地转换器
# 查看可用转换器
python -c "from converter.main_converter import CIFToUSDZConverter; c = CIFToUSDZConverter(); print(list(c.usdz_converters.keys()))"
```

**问题**: 内存不足
```bash
# 解决方案: 降低质量设置
export SPHERE_RESOLUTION=10
export INCLUDE_BONDS=false
python main.py
```

## 📊 性能优化

### 快速启动
```bash
# 使用最小依赖启动
pip install -r requirements_minimal.txt
export SPHERE_RESOLUTION=10
python main.py
```

### 高质量转换
```bash
# 安装完整依赖
pip install -r requirements.txt
export SPHERE_RESOLUTION=30
export INCLUDE_BONDS=true
python main.py
```

### Docker增强
```bash
# 启用Docker USD（可选）
docker pull michaelgold/usdzconvert:0.66-usd-22.05b
export DOCKER_USD_AVAILABLE=true
python main.py
```

## 🎯 下一步

1. **查看完整文档**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. **了解技术细节**: [technical/Docker架构分析和优化建议.md](technical/Docker架构分析和优化建议.md)
3. **部署到生产**: [DEPLOYMENT_GUIDE.md#生产环境](DEPLOYMENT_GUIDE.md#生产环境)

## 📞 获取帮助

- 🐛 遇到问题: [创建Issue](https://github.com/yourorg/crystal3d-converter/issues)
- 📖 查看文档: [docs/](../docs/)
- 🔧 调试工具: [debug/](../debug/)

---

🎉 **享受您的晶体结构3D可视化之旅！** 