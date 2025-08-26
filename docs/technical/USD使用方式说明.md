# 🔍 USD-Core 使用方式说明

## ❌ **常见误解澄清**

**问题**: usd-core 是用的Docker里面的API吗？
**答案**: ❌ **不是！** usd-core是直接安装在本地Python环境中的。

## ✅ **实际情况**

### 1. usd-core是本地Python包

```cmd
# usd-core是通过pip直接安装的Python库
PS> pip show usd-core
Name: usd-core
Version: 25.8
Summary: Pixar's Universal Scene Description
Location: C:\Users\lqq\AppData\Roaming\Python\Python313\site-packages
```

### 2. 项目中的使用方式

项目中有多个USD转换器，但都是**本地Python API调用**：

#### 🔧 **转换器类型**

1. **USDZConverter** (`converter/usdz_converter.py`)
   ```python
   # 直接使用Python USD API
   from pxr import Usd, UsdUtils
   
   def convert_with_python_usd(self, obj_path: str, usdz_path: str):
       # 本地Python API调用，非Docker
   ```

2. **AppleUSDConverter** (`converter/apple_usd_converter.py`)
   ```python
   # 两种方式：
   # 1. 优先使用Apple的usdzconvert工具（如果安装）
   # 2. 回退到Python USD API
   from pxr import Usd, UsdUtils
   success = UsdUtils.CreateNewUsdzPackage(usd_path, usdz_path)
   ```

3. **TinyUSDZConverter** (`converter/tinyusdz_converter.py`)
   ```python
   # 使用本地tinyusdz源码
   # 项目自带的轻量级USD实现
   ```

### 3. Docker仅用于部署，不是API调用

- ✅ **Docker用途**: 将整个项目打包成容器
- ❌ **不是**: Docker作为USD API的中间层
- ✅ **实际**: USD库直接在容器内的Python环境中运行

## 🔬 **验证方法**

### 验证USD是本地库
```cmd
# 检查USD导入
python -c "from pxr import Usd; print('USD库位置:', Usd.__file__)"

# 检查UsdUtils
python -c "from pxr import UsdUtils; print('UsdUtils可用')"
```

### 检查转换器状态
```cmd
# 启动服务后查看转换器信息
curl http://localhost:8000/api/converters
```

## 📊 **架构对比**

### ❌ 误解的架构
```
本地Python → Docker API → USD处理 → 返回结果
```

### ✅ 实际架构

#### 本地运行时
```
本地Python → usd-core库 (本地安装) → USD处理 → 输出文件
```

#### Docker运行时
```
Docker容器内Python → usd-core库 (容器内安装) → USD处理 → 输出文件
```

## 🎯 **关键要点**

1. **usd-core是Python包**: 通过pip安装，直接在Python中导入使用
2. **无需Docker依赖**: 本地环境就能完整运行USD功能
3. **Docker仅用于部署**: 为了环境一致性和便于分发
4. **多重回退机制**: Apple工具 → USD Python API → TinyUSDZ

## 🛠️ **实际调用示例**

### 代码中的实际使用
```python
# converter/apple_usd_converter.py 第207行
from pxr import Usd, UsdUtils

# 直接本地API调用
success = UsdUtils.CreateNewUsdzPackage(usd_path, usdz_path)
```

### 无Docker环境测试
```cmd
# 不启动Docker，直接测试USD功能
python -c "
from pxr import UsdUtils
result = UsdUtils.CreateNewUsdzPackage('test.usd', 'test.usdz')
print('USD API工作正常:', result)
"
```

## 📋 **总结**

- ✅ **usd-core**: 本地Python库，直接API调用
- ❌ **不是**: Docker容器化的API服务
- ✅ **优势**: 更快的执行速度，无网络开销
- ✅ **部署**: 既可本地运行，也可Docker打包

**结论**: usd-core是标准的Python包，项目直接调用其API，Docker只是可选的部署方式。 