# 本地USD环境完整安装指南

本指南提供了在项目中安装和使用完整USD库的方法，让其他开发者可以直接运行USDZ验证工具。

## 🎯 目标

- 在本地环境安装完整的USD库作为Python依赖
- 提供独立的USDZ文件验证工具
- 无需依赖系统级的usdpython环境
- 便于团队协作和部署

## 📦 安装步骤

### 1. 安装Python依赖

```bash
# 安装项目所有依赖（包括USD库）
pip install -r requirements.txt

# 或者单独安装USD库
pip install usd-core
```

### 2. 验证安装

```bash
# 测试USD库是否正确安装
python -c "from pxr import Usd; print('USD库安装成功')"
```

## 🔧 使用方法

### 本地USD验证工具

项目提供了独立的USD验证脚本 `usd_checker.py`：

```bash
# 基本用法
python usd_checker.py <usdz文件路径>

# 示例
python usd_checker.py temp/example.usdz
python usd_checker.py /path/to/your/file.usdz
```

### 验证输出示例

```
🔍 开始ARKit兼容性检查...
==================================================
✅ USD库安装正常
📁 文件: /path/to/file.usdz
📊 根层: file.usdz
🎯 默认Prim: Model (Xform)
🔺 网格数量: 1
🎨 材质数量: 4
✅ USDZ文件结构验证通过
==================================================
🎉 ARKit兼容性检查完成 - 文件可用
```

## 📋 依赖说明

### 核心USD依赖

在 `requirements.txt` 中已包含：

```
# USD/3D处理
usd-core>=23.11,<25.0.0
```

### 版本兼容性

- **Python**: 3.8+
- **USD**: 23.11 - 24.x
- **操作系统**: macOS, Linux, Windows

## 🚀 集成到项目

### 在Python代码中使用

```python
from pxr import Usd, UsdGeom, UsdShade

# 打开USDZ文件
stage = Usd.Stage.Open("path/to/file.usdz")
if stage:
    print(f"成功打开: {stage.GetRootLayer().GetDisplayName()}")
```

### 在主应用中集成

可以将USD验证功能集成到主应用 `main.py` 中：

```python
import subprocess
import sys

def validate_usdz(file_path):
    """验证USDZ文件"""
    try:
        result = subprocess.run(
            [sys.executable, "usd_checker.py", file_path],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"验证失败: {e}")
        return False
```

## 🔄 与系统环境对比

| 特性 | 本地USD库 | 系统usdpython |
|------|-----------|---------------|
| 安装复杂度 | ⭐⭐ 简单 | ⭐⭐⭐⭐ 复杂 |
| 依赖管理 | ✅ pip管理 | ❌ 手动管理 |
| 团队协作 | ✅ 统一环境 | ❌ 环境差异 |
| 部署便利性 | ✅ 容器化友好 | ❌ 需要额外配置 |
| 功能完整性 | ⭐⭐⭐ 基础功能 | ⭐⭐⭐⭐⭐ 完整功能 |

## 🛠️ 故障排除

### 常见问题

1. **ImportError: No module named 'pxr'**
   ```bash
   pip install usd-core
   ```

2. **版本冲突**
   ```bash
   pip uninstall usd-core
   pip install usd-core==24.11
   ```

3. **权限问题**
   ```bash
   pip install --user usd-core
   ```

### 环境检查

```bash
# 检查USD安装
python -c "import pxr; print(pxr.__file__)"

# 检查版本
python -c "from pxr import Tf; print(Tf.GetBuildConfiguration())"
```

## 📁 文件结构

```
项目根目录/
├── usd_checker.py          # 本地USD验证工具
├── requirements.txt        # 包含USD依赖
├── docs/
│   └── USD_LOCAL_SETUP.md  # 本文档
└── tools/
    └── usdpython/          # 备用系统环境工具
```

## 🎉 优势总结

1. **简化部署**: 通过pip安装，无需复杂的系统配置
2. **统一环境**: 团队成员使用相同的USD版本
3. **容器友好**: 易于Docker化部署
4. **依赖透明**: 所有依赖在requirements.txt中明确列出
5. **开发便利**: 支持标准的Python开发工作流

## 📞 支持

如有问题，请检查：
1. Python版本是否兼容（3.8+）
2. 是否正确安装了requirements.txt中的依赖
3. 网络连接是否正常（pip安装需要）

---

*最后更新: 2024年*