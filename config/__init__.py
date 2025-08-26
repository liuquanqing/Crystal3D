# Config package for ARKit compatibility settings
from .app_config import Config, config
from .arkit_config import ARKitConfig, ARKitMaterialConfig

# 导出主要配置对象
__all__ = ['Config', 'config', 'ARKitConfig', 'ARKitMaterialConfig']