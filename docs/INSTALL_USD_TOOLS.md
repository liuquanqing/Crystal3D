# USD转换工具安装指南

## 🎯 推荐方案：苹果官方usdpython工具包

为了获得最佳的USDZ转换质量，强烈推荐安装苹果官方的usdpython工具包。

### 📦 官方工具包下载

苹果官方usdpython工具包来源：[KarpelesLab/usdpython](https://github.com/KarpelesLab/usdpython)

这个包包含：
- `usdzconvert` - 官方USDZ转换工具
- `usdARKitChecker` - USDZ验证工具  
- USD Python库的预编译模块
- 示例脚本和工具

### 🖥️ 各平台安装方法

#### macOS (推荐)
```bash
# 1. 从GitHub下载最新的usdpython工具包
# 2. 解压到 /Applications/usdpython/
# 3. 设置环境变量
export PATH=$PATH:/Applications/usdpython/usdzconvert
export USD_CONVERTER_PATH="/Applications/usdpython/usdzconvert/usdzconvert"

# 4. 测试安装
/Applications/usdpython/usdzconvert/usdzconvert -h
```

#### Windows
```cmd
# 1. 下载usdpython工具包
# 2. 解压到 C:\Program Files\usdpython\
# 3. 设置环境变量
set USD_CONVERTER_PATH="C:\Program Files\usdpython\usdzconvert\usdzconvert"

# 4. 测试安装
"C:\Program Files\usdpython\usdzconvert\usdzconvert" -h
```

#### Linux
```bash
# 1. 下载并解压usdpython工具包
# 2. 安装到 /usr/local/usdpython/
sudo mkdir -p /usr/local/usdpython
sudo tar -xzf usdpython.tar.gz -C /usr/local/usdpython

# 3. 创建符号链接
sudo ln -s /usr/local/usdpython/usdzconvert/usdzconvert /usr/local/bin/usdzconvert

# 4. 设置环境变量
export USD_CONVERTER_PATH="/usr/local/bin/usdzconvert"
```

### 🔧 替代方案

如果无法安装官方工具，系统会自动使用以下备用方案：

#### 1. Xcode命令行工具 (仅macOS)
```bash
# 安装Xcode命令行工具
xcode-select --install

# 测试xcrun usdz_converter
xcrun usdz_converter --help
```

#### 2. Python USD API (已集成)
- 已自动安装`usd-core`包
- 作为最终备用方案使用
- 功能完整但转换质量可能不如官方工具

### ⚡ 转换工具优先级

系统会按以下优先级查找转换工具：

1. **苹果官方usdzconvert** (最佳质量) ⭐⭐⭐⭐⭐
2. **Xcode xcrun usdz_converter** (仅macOS) ⭐⭐⭐⭐
3. **Python USD API** (备用方案) ⭐⭐⭐

### 🎨 usdzconvert的优势

- **官方支持**：苹果维护，兼容性最佳
- **iOS优化**：专为iOS AR Quick Look优化
- **材质处理**：更好的PBR材质支持
- **文件压缩**：更高效的USDZ包生成
- **验证功能**：内置ARKit兼容性检查

### 📋 验证安装

安装完成后，重启应用服务器，查看日志：

```
✅ 成功日志：
INFO - 找到USD转换工具: /Applications/usdpython/usdzconvert/usdzconvert

❌ 备用方案日志：
WARNING - 未找到官方USD转换工具，将使用Python USD API作为备用方案
```

### 🔗 相关链接

- [KarpelesLab/usdpython GitHub](https://github.com/KarpelesLab/usdpython)
- [苹果WWDC USD介绍](https://developer.apple.com/videos/play/wwdc2019/602/)
- [USD官方文档](https://graphics.pixar.com/usd/docs/index.html) 