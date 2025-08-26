# 🚀 Crystal3D 快速开始指南

欢迎使用 Crystal3D - 晶体结构3D转换器！本指南将帮助您在几分钟内快速上手。

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **内存**: 建议 4GB 以上
- **磁盘空间**: 至少 2GB 可用空间

## ⚡ 30秒快速启动

### Windows 用户
```bash
# 1. 双击运行一键启动脚本
一键启动.bat
```

### macOS/Linux 用户
```bash
# 1. 给脚本执行权限并运行
chmod +x setup_usd_local.sh
./setup_usd_local.sh

# 2. 启动服务
python3 main.py
```

## 🎯 第一次使用

### 1. 访问Web界面
启动成功后，在浏览器中打开：
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 2. 上传CIF文件
1. 点击「选择文件」或直接拖拽CIF文件到上传区域
2. 等待文件上传和解析完成
3. 查看自动生成的3D晶体结构预览

### 3. 转换为USDZ
1. 在预览页面点击「转换为USDZ」按钮
2. 等待转换完成（通常需要几秒钟）
3. 下载生成的USDZ文件

### 4. AR预览（iPhone用户）
1. 使用iPhone相机扫描页面上的二维码
2. 或者直接在iPhone Safari中打开USDZ文件链接
3. 点击AR图标进入增强现实模式

## 📱 示例文件

项目提供了一些示例CIF文件供测试：

```bash
examples/
├── LiCoO2.cif          # 锂钴氧化物（电池材料）
├── diamond.cif         # 金刚石结构
├── quartz.cif          # 石英晶体
└── perovskite.cif      # 钙钛矿结构
```

### 使用示例文件
1. 在Web界面中上传 `examples/LiCoO2.cif`
2. 观察锂钴氧化物的层状结构
3. 转换为USDZ并在iPhone上查看AR效果

## 🔧 常见问题

### Q: 启动时提示Python版本过低
**A**: 请升级到Python 3.8+
```bash
# 检查Python版本
python3 --version

# macOS用户可使用Homebrew升级
brew install python

# 或访问官网下载: https://www.python.org/downloads/
```

### Q: 依赖安装失败
**A**: 尝试以下解决方案
```bash
# 1. 升级pip
python3 -m pip install --upgrade pip

# 2. 清理缓存
python3 -m pip cache purge

# 3. 使用国内镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# 4. 重新运行安装脚本
```

### Q: 端口8000被占用
**A**: 启动脚本会自动检测并使用8001端口，或手动指定端口
```bash
python3 main.py --port 8080
```

### Q: USDZ文件无法在iPhone上打开
**A**: 确保满足以下条件
- iPhone运行iOS 12+
- 使用Safari浏览器
- 文件大小不超过25MB
- 网络连接正常

## 🎨 高级功能

### 1. 批量转换
```bash
# 使用命令行工具批量转换
python3 tools/batch_convert.py --input examples/ --output output/
```

### 2. 自定义转换参数
```bash
# 调整晶胞重复次数
python3 main.py --supercell 2x2x2

# 设置原子半径缩放
python3 main.py --atom-scale 0.8
```

### 3. API调用
```python
import requests

# 上传CIF文件
with open('example.cif', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f}
    )

# 转换为USDZ
response = requests.post(
    'http://localhost:8000/api/convert',
    json={'file_id': 'your_file_id'}
)
```

## 📚 更多资源

- **完整文档**: [README.md](../README.md)
- **API参考**: http://localhost:8000/docs
- **示例代码**: [examples/](../examples/)
- **故障排除**: [README.md#故障排除](../README.md#故障排除)

## 🆘 获取帮助

如果遇到问题，请：
1. 查看 [README.md](../README.md) 中的详细文档
2. 检查 [故障排除指南](../README.md#故障排除)
3. 提交 GitHub Issue 获取技术支持

---

🎉 **恭喜！您已经掌握了Crystal3D的基本使用方法。现在开始探索晶体结构的3D世界吧！**