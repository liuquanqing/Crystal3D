# 贡献指南

感谢您对Crystal3D项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了bug或有功能建议：

1. 检查[Issues](https://github.com/yourusername/crystal3d-converter/issues)确保问题未被报告
2. 创建新的Issue，包含：
   - 清晰的标题和描述
   - 重现步骤（如果是bug）
   - 期望的行为
   - 系统环境信息
   - 相关的错误日志或截图

### 提交代码

1. **Fork项目**
   ```bash
   git clone https://github.com/yourusername/crystal3d-converter.git
   cd crystal3d-converter
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行开发**
   - 遵循现有的代码风格
   - 添加必要的测试
   - 更新相关文档

4. **测试您的更改**
   ```bash
   python -m pytest tests/
   python test_system.py
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **推送到您的Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建Pull Request**
   - 提供清晰的PR标题和描述
   - 链接相关的Issues
   - 描述您的更改内容

## 📝 代码规范

### Python代码风格

- 遵循PEP 8规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 保持函数简洁，单一职责

### 提交信息规范

使用[Conventional Commits](https://www.conventionalcommits.org/)格式：

```
type(scope): description

[optional body]

[optional footer]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(converter): add support for new CIF format
fix(api): resolve file upload timeout issue
docs(readme): update installation instructions
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_converter.py -v

# 运行系统测试
python test_system.py
```

### 添加测试

- 为新功能添加单元测试
- 确保测试覆盖率不降低
- 测试文件命名：`test_*.py`
- 测试函数命名：`test_*`

## 📚 文档

### 更新文档

- 更新README.md（如果适用）
- 添加或更新API文档
- 更新配置说明
- 添加使用示例

### 文档风格

- 使用清晰简洁的语言
- 提供代码示例
- 包含必要的截图或图表
- 保持中英文一致性

## 🔍 代码审查

### 审查清单

- [ ] 代码遵循项目规范
- [ ] 包含适当的测试
- [ ] 文档已更新
- [ ] 没有引入新的依赖（除非必要）
- [ ] 性能没有明显下降
- [ ] 安全性考虑

### 审查过程

1. 自动化测试通过
2. 代码审查通过
3. 维护者批准
4. 合并到主分支

## 🚀 发布流程

### 版本号规范

遵循[语义化版本](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- MAJOR：不兼容的API修改
- MINOR：向下兼容的功能性新增
- PATCH：向下兼容的问题修正

### 发布步骤

1. 更新版本号
2. 更新CHANGELOG.md
3. 创建发布标签
4. 发布到GitHub Releases

## 💬 社区

### 沟通渠道

- GitHub Issues：bug报告和功能请求
- GitHub Discussions：一般讨论和问答
- Pull Requests：代码贡献讨论

### 行为准则

- 保持友善和专业
- 尊重不同观点
- 建设性地提供反馈
- 帮助新贡献者

## 🎯 贡献领域

我们特别欢迎以下方面的贡献：

### 核心功能
- 新的CIF解析器支持
- USDZ转换质量优化
- 性能改进
- 错误处理增强

### 用户体验
- Web界面改进
- 3D预览功能增强
- 移动端适配
- 国际化支持

### 文档和示例
- 使用教程
- API文档
- 示例项目
- 视频教程

### 测试和质量
- 单元测试
- 集成测试
- 性能测试
- 安全测试

## 📋 开发环境设置

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/crystal3d-converter.git
cd crystal3d-converter

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements_dev.txt  # 开发依赖

# 4. 运行测试
python -m pytest tests/

# 5. 启动开发服务器
python main.py
```

### 开发工具推荐

- **IDE**: VS Code, PyCharm
- **代码格式化**: black, autopep8
- **代码检查**: flake8, pylint
- **类型检查**: mypy
- **测试**: pytest

## ❓ 常见问题

### Q: 如何设置开发环境？
A: 参考上面的"开发环境设置"部分。

### Q: 我的PR什么时候会被审查？
A: 通常在1-3个工作日内，复杂的PR可能需要更长时间。

### Q: 如何报告安全漏洞？
A: 请通过GitHub的安全报告功能私下报告。

### Q: 可以贡献翻译吗？
A: 当然！我们欢迎多语言支持的贡献。

---

再次感谢您的贡献！每一个贡献都让Crystal3D变得更好。 🙏