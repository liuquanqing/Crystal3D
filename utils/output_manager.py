#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出文件管理模块
自动创建和管理转换结果的输出文件夹
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

class OutputManager:
    """输出文件管理器"""
    
    def __init__(self, base_output_dir: str = "conversion_results"):
        """
        初始化输出管理器
        
        Args:
            base_output_dir: 基础输出目录
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # 创建索引文件
        self.index_file = self.base_output_dir / "conversion_index.json"
        self._load_index()
    
    def _load_index(self):
        """加载转换索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except:
                self.index = {"conversions": [], "total_count": 0}
        else:
            self.index = {"conversions": [], "total_count": 0}
    
    def _save_index(self):
        """保存转换索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _generate_session_id(self, filename: str) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        return f"{timestamp}_{file_hash}"
    
    def create_conversion_session(self, original_filename: str, 
                                conversion_settings: Dict = None) -> Tuple[str, Path]:
        """
        创建转换会话，返回会话ID和输出目录
        
        Args:
            original_filename: 原始文件名
            conversion_settings: 转换设置
            
        Returns:
            (session_id, output_dir_path)
        """
        session_id = self._generate_session_id(original_filename)
        output_dir = self.base_output_dir / session_id
        output_dir.mkdir(exist_ok=True)
        
        # 创建会话元数据
        session_metadata = {
            "session_id": session_id,
            "original_filename": original_filename,
            "created_at": datetime.now().isoformat(),
            "conversion_settings": conversion_settings or {},
            "status": "created",
            "files": {}
        }
        
        # 保存会话元数据
        metadata_file = output_dir / "session_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(session_metadata, f, ensure_ascii=False, indent=2)
        
        return session_id, output_dir
    
    def create_output_directory(self, base_name: str) -> str:
        """
        为转换创建输出目录（简化版本，兼容现有API）
        
        Args:
            base_name: 基础文件名
            
        Returns:
            输出目录路径
        """
        session_id = self._generate_session_id(base_name)
        output_dir = self.base_output_dir / session_id
        output_dir.mkdir(exist_ok=True)
        return str(output_dir)
    
    def save_file_to_session(self, session_id: str, file_path: str, 
                           file_type: str, description: str = "") -> str:
        """
        保存文件到会话目录
        
        Args:
            session_id: 会话ID
            file_path: 源文件路径
            file_type: 文件类型 (original_cif, intermediate_obj, final_usdz, etc.)
            description: 文件描述
            
        Returns:
            保存后的文件路径
        """
        session_dir = self.base_output_dir / session_id
        if not session_dir.exists():
            raise ValueError(f"会话目录不存在: {session_id}")
        
        # 生成目标文件名
        original_name = Path(file_path).name
        base_name = Path(file_path).stem
        extension = Path(file_path).suffix
        
        # 根据文件类型生成合适的文件名
        if file_type == "original_cif":
            target_name = f"original_{original_name}"
        elif file_type == "intermediate_obj":
            target_name = f"intermediate_{base_name}.obj"
        elif file_type == "intermediate_mtl":
            target_name = f"intermediate_{base_name}.mtl"
        elif file_type == "final_usdz":
            target_name = f"final_{base_name}.usdz"
        else:
            target_name = f"{file_type}_{original_name}"
        
        target_path = session_dir / target_name
        
        # 复制文件
        if os.path.exists(file_path):
            shutil.copy2(file_path, target_path)
            
            # 更新会话元数据
            self._update_session_metadata(session_id, {
                "files": {
                    file_type: {
                        "filename": target_name,
                        "path": str(target_path),
                        "size_bytes": os.path.getsize(target_path),
                        "size_mb": round(os.path.getsize(target_path) / (1024 * 1024), 3),
                        "description": description,
                        "saved_at": datetime.now().isoformat()
                    }
                }
            })
            
            return str(target_path)
        else:
            raise FileNotFoundError(f"源文件不存在: {file_path}")
    
    def _update_session_metadata(self, session_id: str, updates: Dict):
        """更新会话元数据"""
        session_dir = self.base_output_dir / session_id
        metadata_file = session_dir / "session_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        # 深度合并更新
        def deep_merge(base_dict, update_dict):
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_merge(metadata, updates)
        metadata["updated_at"] = datetime.now().isoformat()
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def complete_conversion_session(self, session_id: str, 
                                  conversion_result: Dict, 
                                  final_usdz_path: str = None):
        """
        完成转换会话
        
        Args:
            session_id: 会话ID
            conversion_result: 转换结果
            final_usdz_path: 最终USDZ文件路径
        """
        # 保存最终USDZ文件
        if final_usdz_path and os.path.exists(final_usdz_path):
            self.save_file_to_session(session_id, final_usdz_path, "final_usdz", "最终转换结果")
        
        # 更新会话状态
        self._update_session_metadata(session_id, {
            "status": "completed" if conversion_result.get('success') else "failed",
            "conversion_result": conversion_result,
            "completed_at": datetime.now().isoformat()
        })
        
        # 更新全局索引
        session_dir = self.base_output_dir / session_id
        metadata_file = session_dir / "session_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                session_metadata = json.load(f)
            
            # 添加到全局索引
            self.index["conversions"].append({
                "session_id": session_id,
                "original_filename": session_metadata.get("original_filename"),
                "status": session_metadata.get("status"),
                "created_at": session_metadata.get("created_at"),
                "completed_at": session_metadata.get("completed_at"),
                "output_dir": str(session_dir),
                "success": conversion_result.get('success', False)
            })
            
            self.index["total_count"] += 1
            self._save_index()
    
    def get_session_info(self, session_id: str) -> Dict:
        """获取会话信息"""
        session_dir = self.base_output_dir / session_id
        metadata_file = session_dir / "session_metadata.json"
        
        if not metadata_file.exists():
            raise ValueError(f"会话不存在: {session_id}")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_recent_conversions(self, limit: int = 10) -> List[Dict]:
        """列出最近的转换记录"""
        conversions = sorted(
            self.index["conversions"], 
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        return conversions[:limit]
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """清理旧的会话目录"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for conversion in self.index["conversions"]:
            try:
                created_at = datetime.fromisoformat(conversion["created_at"])
                if created_at < cutoff_date:
                    session_dir = Path(conversion["output_dir"])
                    if session_dir.exists():
                        shutil.rmtree(session_dir)
                        cleaned_count += 1
            except:
                continue
        
        # 更新索引，移除已清理的会话
        self.index["conversions"] = [
            conv for conv in self.index["conversions"]
            if Path(conv["output_dir"]).exists()
        ]
        self._save_index()
        
        return cleaned_count
    
    def get_statistics(self) -> Dict:
        """获取转换统计信息"""
        total_conversions = len(self.index["conversions"])
        successful_conversions = sum(1 for conv in self.index["conversions"] if conv.get("success"))
        
        return {
            "total_conversions": total_conversions,
            "successful_conversions": successful_conversions,
            "success_rate": round(successful_conversions / total_conversions * 100, 2) if total_conversions > 0 else 0,
            "base_output_dir": str(self.base_output_dir),
            "index_file": str(self.index_file)
        }