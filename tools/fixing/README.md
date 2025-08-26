# USDZ修复工具

## 主要工具

### unified_usdz_fixer.py - 统一USDZ修复工具 ⭐
**推荐使用的主要修复工具**

整合了所有修复功能，确保USDZ文件完全符合Apple官方示例：
- ✅ **材质修复**：使用diffuseColor，智能推断元素颜色，移除不兼容属性
- ✅ **可见性修复**：确保几何体可见，居中到原点
- ✅ **ARKit兼容性**：正确的单位(0.01米/单位)、法线、可见性设置
- ✅ **结构修复**：正确的文件结构和命名，移除displayColor等不兼容属性

```bash
# 使用方法
python tools/fixing/unified_usdz_fixer.py input.usdz [output.usdz]
```

### 其他工具

- `fix_arkit_compatibility.py` - ARKit兼容性修复
- `optimized_arkit_compatibility.py` - 优化的ARKit兼容性修复
- `fix_usdz_structure.py` - USDZ结构修复

## 重要说明

### AR Quick Look材质要求

根据Apple工程师的明确说明：

1. **不支持displayColor**：AR Quick Look/RealityKit不支持USD的displayColor和vertexColor属性
2. **必须使用UsdPreviewSurface**：颜色必须通过UsdPreviewSurface材质的diffuseColor属性定义
3. **surface是标准输出**：UsdPreviewSurface的surface输出端口是AR Quick Look要求的标准连接

### 支持的材质属性

AR Quick Look只支持UsdPreviewSurface的基本属性：
- ✅ `diffuseColor` - 漫反射颜色（主要颜色）
- ❌ `baseColor` - 会被转换为diffuseColor
- ❌ `metallic`, `roughness`, `opacity` 等 - 会被移除

## 历史文件

`archive/` 目录包含了已被统一工具替代的旧修复文件，保留用于参考。

## 使用建议

1. **优先使用** `unified_usdz_fixer.py` 进行所有修复
2. 修复后使用 `tools/checking/check_arkit_compatibility.py` 验证兼容性
3. 使用Quick Look预览测试实际效果