# 🔧 Crystal3D 配置指南

Crystal3D 支持多种配置选项，可以通过环境变量灵活调整服务行为。

## 📖 快速配置

### 基础配置

```bash
# 设置服务端口（默认8000）
set PORT=9000

# 设置主机地址（默认0.0.0.0，监听所有接口）
set HOST=127.0.0.1

# 设置公开访问URL（用于外网访问）
set PUBLIC_URL=http://your-domain.com

# 设置公网IP访问
set PUBLIC_URL=http://123.45.67.89:8000
```

### 二维码配置

```bash
# 设置二维码使用的基础URL
set QR_BASE_URL=http://your-external-ip:8000

# 禁用二维码功能
set ENABLE_QR_CODE=false
```

### AR预览配置

```bash
# 禁用AR预览功能（推荐用于桌面环境）
set ENABLE_AR_PREVIEW=false
```

## 🌐 网络配置详解

### 1. 本地开发
```bash
# 默认配置，只能本机访问
# 无需设置额外环境变量
python main.py
```
访问地址：`http://localhost:8000`

### 2. 局域网共享
```bash
# 默认配置已支持局域网访问
python main.py
```
- 本机访问：`http://localhost:8000`
- 局域网访问：`http://192.168.x.x:8000`（自动检测）

### 3. 公网访问
```bash
# 设置公网域名
set PUBLIC_URL=https://crystal3d.yourdomain.com
python main.py

# 或设置公网IP
set PUBLIC_URL=http://123.45.67.89:8000
python main.py
```

### 4. 不同网络环境的二维码
```bash
# 场景1：公网部署，二维码使用域名
set PUBLIC_URL=https://crystal3d.yourdomain.com
set QR_BASE_URL=https://crystal3d.yourdomain.com

# 场景2：公网部署，二维码使用IP
set PUBLIC_URL=http://123.45.67.89:8000
set QR_BASE_URL=http://123.45.67.89:8000

# 场景3：局域网部署，固定内网IP
set QR_BASE_URL=http://192.168.1.100:8000
```

## 🔧 功能开关

### AR预览功能
AR预览主要适用于iOS Safari浏览器，在桌面环境中体验有限。

```bash
# 禁用AR预览（推荐用于纯桌面环境）
set ENABLE_AR_PREVIEW=false

# 启用AR预览（默认，适用于移动设备）
set ENABLE_AR_PREVIEW=true
```

**建议场景：**
- ✅ 移动设备为主的环境：启用AR预览
- ❌ 纯桌面环境：禁用AR预览，减少混淆

### 二维码功能
二维码用于跨设备分享转换结果。

```bash
# 禁用二维码功能
set ENABLE_QR_CODE=false

# 启用二维码功能（默认）
set ENABLE_QR_CODE=true
```

## 📋 部署场景示例

### 场景1：公司内网部署
```bash
# 设置固定内网IP，便于同事访问
set PUBLIC_URL=http://192.168.10.100:8000
set QR_BASE_URL=http://192.168.10.100:8000
# 根据需要决定是否启用AR预览
set ENABLE_AR_PREVIEW=false
python main.py
```

### 场景2：云服务器部署
```bash
# 使用域名
set PUBLIC_URL=https://crystal3d.yourdomain.com
set QR_BASE_URL=https://crystal3d.yourdomain.com
python main.py

# 或使用公网IP
set PUBLIC_URL=http://123.45.67.89:8000
set QR_BASE_URL=http://123.45.67.89:8000
python main.py
```

### 场景3：本地开发调试
```bash
# 最小配置，快速启动
python main.py
# 自动使用局域网IP，支持手机访问测试
```

### 场景4：纯桌面演示环境
```bash
# 禁用移动端功能，简化界面
set ENABLE_AR_PREVIEW=false
set ENABLE_QR_CODE=false
set HOST=127.0.0.1  # 仅本机访问
python main.py
```

## 🚀 高级配置

### 端口配置
```bash
# 使用不同端口
set PORT=3000
python main.py

# 命令行指定端口（优先级更高）
python main.py 9000
```

### 安全配置
```bash
# 限制只能本机访问
set HOST=127.0.0.1

# 允许所有接口访问（默认）
set HOST=0.0.0.0
```

## 🔍 配置验证

启动服务后，系统会自动显示配置信息：

```
🌐 服务访问信息:
   本机访问: http://localhost:8000
   局域网访问: http://192.168.2.219:8000
   公开访问: http://your-domain.com  # 如果设置了PUBLIC_URL
   二维码使用: http://your-domain.com  # 如果启用了二维码功能

📱 手机访问步骤:
   1. 确保手机和电脑连接同一WiFi
   2. 手机浏览器打开: http://192.168.2.219:8000
   3. 或扫描转换结果页面的二维码

⚙️  配置选项:
   设置公开URL: set PUBLIC_URL=http://your-domain.com
   设置公网IP: set PUBLIC_URL=http://123.45.67.89:8000
   设置二维码URL: set QR_BASE_URL=http://your-ip:8000
   设置端口: set PORT=9000

💡 高级配置:
   禁用AR预览: set ENABLE_AR_PREVIEW=false
   禁用二维码: set ENABLE_QR_CODE=false
   设置主机: set HOST=127.0.0.1
```

## ❓ 常见问题

### Q: 二维码扫描显示"未有可用数据"？
**A:** 检查二维码URL配置：
1. 确保 `QR_BASE_URL` 使用的是外部可访问的地址
2. 避免使用 `localhost` 或 `127.0.0.1`
3. 确保防火墙允许相应端口访问

### Q: 如何在公网部署？
**A:** 设置公开URL：
```bash
set PUBLIC_URL=http://your-public-ip:8000
# 或
set PUBLIC_URL=https://your-domain.com
```

### Q: 如何禁用不需要的功能？
**A:** 使用功能开关：
```bash
set ENABLE_AR_PREVIEW=false  # 禁用AR预览
set ENABLE_QR_CODE=false     # 禁用二维码
```

### Q: 如何固定局域网IP？
**A:** 手动设置PUBLIC_URL：
```bash
set PUBLIC_URL=http://192.168.1.100:8000
``` 