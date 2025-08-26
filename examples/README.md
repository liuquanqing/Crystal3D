# 示例文件

这个目录包含一些示例CIF文件用于测试转换器功能。

## 文件说明

- `simple_crystal.cif` - 简单晶体结构示例（氯化钠）

## 使用方法

### 命令行测试

```bash
# 测试单个文件转换
python convert_tool.py convert single examples/simple_crystal.cif output/simple_crystal.usdz

# 测试批量转换
python convert_tool.py convert batch examples/ output/

# 验证CIF文件
python convert_tool.py validate examples/simple_crystal.cif
```

### Web API测试

```bash
# 启动服务
python main.py

# 使用curl测试
curl -X POST "http://localhost:8000/convert" \
     -F "file=@examples/simple_crystal.cif" \
     -o "output.usdz"
```

## 获取更多CIF文件

可以从以下网站下载更多CIF文件进行测试：

- [Crystallography Open Database (COD)](http://www.crystallography.net/cod/)
- [Cambridge Structural Database (CSD)](https://www.ccdc.cam.ac.uk/)
- [Inorganic Crystal Structure Database (ICSD)](https://icsd.fiz-karlsruhe.de/)
- [Materials Project](https://materialsproject.org/)

## 注意事项

1. 确保CIF文件格式正确
2. 复杂结构可能需要更长的转换时间
3. 大型结构文件可能需要调整球体分辨率以平衡质量和性能 