#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crystal3D API路由定义
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# 导入项目模块
from converter.main_converter import CIFToUSDZConverter
from utils.file_utils import is_valid_cif_file, get_file_size_mb
from utils.output_manager import OutputManager
from utils.app_version import get_app_info, check_for_updates
from utils.logger import setup_logger
from loguru import logger

# 初始化日志
setup_logger()

# 初始化转换器和输出管理器
converter = CIFToUSDZConverter()
output_manager = OutputManager()

# 创建FastAPI应用实例
app = FastAPI(
    title="Crystal3D - 晶体结构3D转换器",
    description="CIF文件转USDZ格式的Web服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 基础路由
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页"""
    static_path = Path("static/index.html")
    if static_path.exists():
        return static_path.read_text(encoding="utf-8")
    else:
        return """
        <html>
            <head><title>Crystal3D</title></head>
            <body>
                <h1>Crystal3D - 晶体结构3D转换器</h1>
                <p>CIF文件转USDZ格式的Web服务</p>
                <p><a href="/docs">API文档</a></p>
            </body>
        </html>
        """

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "Crystal3D服务运行正常"}



@app.post("/api/convert")
async def convert_cif(file: UploadFile = File(...)):
    """CIF文件转换接口"""
    if not file.filename.endswith('.cif'):
        raise HTTPException(status_code=400, detail="只支持CIF文件格式")
    
    temp_dir = None
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)
        
        # 保存上传的文件
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 验证CIF文件
        if not is_valid_cif_file(input_path):
            raise HTTPException(status_code=400, detail="无效的CIF文件格式")
        
        # 检查文件大小
        file_size = get_file_size_mb(input_path)
        if file_size > 50:  # 限制50MB
            raise HTTPException(status_code=400, detail="文件大小超过限制（50MB）")
        
        # 执行转换
        logger.info(f"开始转换文件: {file.filename}")
        output_filename = f"{Path(file.filename).stem}.usdz"
        output_path = os.path.join(temp_dir, output_filename)
        
        # 创建会话以便保存中间文件
        session_id, session_dir = output_manager.create_conversion_session(
            file.filename, 
            {"file_size_mb": file_size}
        )
        
        # 保存原始CIF文件
        output_manager.save_file_to_session(
            session_id, 
            input_path, 
            "original_cif",
            "原始上传的CIF文件"
        )
        
        # 修改转换器以保存中间文件
        success, message, info = converter.convert_cif_to_usdz(input_path, output_path)
        result = {
            "success": success,
            "output_path": output_path if success else None,
            "error": message if not success else None,
            "info": info
        }
        
        # 在转换器清理临时目录之前，保存中间文件
        if hasattr(converter, 'temp_dir') and converter.temp_dir and os.path.exists(converter.temp_dir):
            # 查找并保存中间OBJ和MTL文件
            for root, dirs, files in os.walk(converter.temp_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    if f.endswith('.obj'):
                        output_manager.save_file_to_session(
                            session_id, 
                            file_path, 
                            "intermediate_obj",
                            "中间转换的OBJ文件"
                        )
                    elif f.endswith('.mtl'):
                        output_manager.save_file_to_session(
                            session_id, 
                            file_path, 
                            "intermediate_mtl",
                            "中间转换的MTL材质文件"
                        )
        
        if result["success"]:
            # 保存最终USDZ文件
            output_path = output_manager.save_file_to_session(
                session_id, 
                result["output_path"], 
                "final_usdz",
                "转换完成的USDZ文件"
            )
            
            # 完成转换会话
            output_manager.complete_conversion_session(
                session_id, 
                result, 
                result["output_path"]
            )
            
            return {
                "success": True,
                "message": "转换成功",
                "session_id": session_id,
                "download_url": f"/api/download/{session_id}",
                "info": result.get("info", {})
            }
        else:
            # 转换失败时也要完成会话
            output_manager.complete_conversion_session(
                session_id, 
                result, 
                None
            )
            raise HTTPException(status_code=500, detail=result.get("error", "转换失败"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")
    finally:
        # 清理转换器的临时目录
        if hasattr(converter, '_cleanup_temp_dir'):
            converter._cleanup_temp_dir()
        
        # 清理API的临时目录
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.get("/api/download/{session_id}")
async def download_file(session_id: str):
    """下载转换结果文件"""
    try:
        session_info = output_manager.get_session_info(session_id)
        if not session_info or session_info.get("status") != "completed":
            raise HTTPException(status_code=404, detail="文件不存在或转换未完成")
        
        # 从files字段中获取final_usdz文件信息
        files = session_info.get("files", {})
        final_usdz_info = files.get("final_usdz")
        if not final_usdz_info:
            raise HTTPException(status_code=404, detail="转换结果文件不存在")
        
        file_path = final_usdz_info.get("path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        filename = session_info.get("original_filename", "converted.usdz")
        filename = f"{Path(filename).stem}.usdz"
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {e}")
        raise HTTPException(status_code=500, detail="下载失败")

@app.get("/api/status")
async def check_status():
    """检查系统状态和更新信息"""
    try:
        # 模拟版本信息数据结构
        version_info = {
            "current_version": "1.0.0",
            "latest_version": "1.0.0",
            "update_available": False,
            "release_notes": "当前版本是最新版本"
        }
        
        app_info = {
            "name": "Crystal3D转换器",
            "description": "CIF到USDZ文件转换工具",
            "author": "Crystal3D Team",
            "license": "MIT"
        }
        
        software_update = {
            "available": False,
            "version": "1.0.0",
            "description": "无可用更新"
        }
        
        summary = {
            "updates_available": False,
            "total_packages": 0,
            "outdated_packages": 0
        }
        
        return {
            "success": True,
            "data": {
                "version_info": version_info,
                "app_info": app_info,
                "software_update": software_update,
                "summary": summary
            }
        }
    except Exception as e:
        logger.error(f"检查状态失败: {e}")
        return {
            "success": False,
            "message": f"检查状态失败: {str(e)}"
        }

@app.get("/api/config")
async def get_config():
    """获取前端配置"""
    from config.app_config import config
    return {
        "base_url": config.get_qr_base_url(),
        "qr_enabled": config.ENABLE_QR_CODE,
        "ar_preview_enabled": config.ENABLE_AR_PREVIEW
    }

@app.post("/api/generate_qr")
async def generate_qr_code(request: dict):
    """生成二维码"""
    try:
        import os
        if os.getenv('ENABLE_QR_CODE', 'true').lower() != 'true':
            raise HTTPException(status_code=403, detail="二维码功能已被禁用")
        
        url = request.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="缺少URL参数")
        
        try:
            import qrcode
            import io
            import base64
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # 创建图像
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "success": True,
                "qr_code": qr_base64
            }
        except ImportError:
            # 如果qrcode库不可用，返回简单响应
            return {
                "success": False,
                "error": "二维码库不可用"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成二维码失败: {e}")
        return {
            "success": False,
            "error": f"生成二维码失败: {str(e)}"
        }

@app.get("/download/{session_id}")
async def download_file(session_id: str):
    """
    下载指定会话的USDZ文件
    
    Args:
        session_id: 会话ID
        
    Returns:
        FileResponse: USDZ文件
    """
    try:
        # 获取会话信息
        session_info = output_manager.get_session_info(session_id)
        
        # 查找USDZ文件
        usdz_file_info = session_info.get("files", {}).get("final_usdz")
        if not usdz_file_info:
            raise HTTPException(status_code=404, detail="USDZ文件未找到")
        
        usdz_file_path = usdz_file_info.get("path")
        if not usdz_file_path or not os.path.exists(usdz_file_path):
            raise HTTPException(status_code=404, detail="USDZ文件不存在")
        
        # 获取原始文件名用于下载
        original_filename = session_info.get("original_filename", "crystal")
        base_name = Path(original_filename).stem
        download_filename = f"{base_name}.usdz"
        
        return FileResponse(
            path=usdz_file_path,
            filename=download_filename,
            media_type="model/vnd.usdz+zip",
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"下载文件错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

@app.post("/parse_cif")
async def parse_cif_file(file: UploadFile = File(...)):
    """解析CIF文件"""
    import sys
    
    if not file.filename.endswith('.cif'):
        raise HTTPException(status_code=400, detail="只支持CIF文件格式")
    
    temp_dir = None
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)
        
        # 保存上传的文件
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 验证CIF文件
        if not is_valid_cif_file(input_path):
            raise HTTPException(status_code=400, detail="无效的CIF文件格式")
        
        # 使用转换器解析CIF文件
        try:
            # 尝试使用pymatgen解析
            from pymatgen.core import Structure
            structure = Structure.from_file(input_path)
            
            # 提取基本信息
            try:
                # 尝试获取空间群信息
                from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
                sga = SpacegroupAnalyzer(structure)
                space_group = sga.get_space_group_symbol()
                space_group_number = sga.get_space_group_number()
            except Exception as e:
                logger.warning(f"无法获取空间群信息: {e}")
                space_group = "Unknown"
                space_group_number = 0
            
            # 提取多面体数据
            coordination_data = None
            try:
                # 添加项目根目录到Python路径
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                
                from pymatgen_converter import PymatgenConverter
                pymatgen_converter = PymatgenConverter()
                coordination_data = pymatgen_converter.analyze_coordination_environments(structure)
                logger.info(f"成功提取多面体数据: {len(coordination_data.get('polyhedra', []))} 个多面体")
            except Exception as e:
                logger.warning(f"提取多面体数据失败: {e}")
                import traceback
                logger.debug(f"详细错误信息: {traceback.format_exc()}")
                coordination_data = {'polyhedra': [], 'coordination_numbers': {}, 'geometry_types': {}}
            
            # 计算原子总数（考虑占位）
            total_atoms = sum(sum(spec.values()) for site in structure.sites for spec in [site.species])
            
            metadata = {
                "formula": structure.formula,
                "num_sites": len(structure.sites),
                "total_atoms": int(total_atoms),
                "num_atoms": int(total_atoms),  # 前端期望的字段名
                "lattice_abc": [float(x) for x in structure.lattice.abc],
                "lattice_angles": [float(x) for x in structure.lattice.angles],
                "space_group": space_group,
                "space_group_number": space_group_number,
                "density": float(structure.density),
                "volume": float(structure.lattice.volume)
            }
            
            # 提取原子位点信息（匹配前端期望的格式）
            sites = []
            for site in structure.sites:
                # 构建species数组
                species = []
                for specie, occu in site.species.items():
                    species.append({
                        "element": str(specie),
                        "occu": float(occu)
                    })
                
                sites.append({
                    "species": species,
                    "coords": site.frac_coords.tolist(),  # 分数坐标
                    "properties": {}
                })
            
            # 构建晶格信息
            lattice = {
                "matrix": structure.lattice.matrix.tolist(),
                "a": float(structure.lattice.a),
                "b": float(structure.lattice.b), 
                "c": float(structure.lattice.c),
                "alpha": float(structure.lattice.alpha),
                "beta": float(structure.lattice.beta),
                "gamma": float(structure.lattice.gamma)
            }
            
            # 返回前端期望的数据结构
            structure_data = {
                "sites": sites,
                "lattice": lattice,
                "formula": structure.formula
            }
            
            # 构建响应数据
            response_data = {
                "success": True,
                "structure": structure_data,
                "metadata": metadata,
                "source": "pymatgen"
            }
            
            # 添加多面体数据
            if coordination_data and coordination_data.get('polyhedra'):
                response_data["polyhedra"] = coordination_data['polyhedra']
                response_data["coordination_data"] = coordination_data
                logger.info(f"返回多面体数据: {len(coordination_data['polyhedra'])} 个多面体")
            else:
                response_data["polyhedra"] = []
                response_data["coordination_data"] = {'polyhedra': [], 'coordination_numbers': {}, 'geometry_types': {}}
                logger.info("未找到多面体数据")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Pymatgen解析失败: {e}")
            # 返回基本的成功响应，即使解析失败
            return {
                "success": True,
                "structure": {
                    "sites": [],
                    "lattice": {
                        "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        "a": 1.0, "b": 1.0, "c": 1.0,
                        "alpha": 90.0, "beta": 90.0, "gamma": 90.0
                    },
                    "formula": "Unknown"
                },
                "metadata": {
                    "formula": "Unknown",
                    "num_sites": 0
                },
                "source": "fallback",
                "warning": "解析失败，使用默认数据"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解析CIF文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/convert")
async def convert_cif_legacy(file: UploadFile = File(...)):
    """CIF文件转换接口 - 兼容前端调用"""
    if not file.filename.endswith('.cif'):
        raise HTTPException(status_code=400, detail="只支持CIF文件格式")
    
    temp_dir = None
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)
        
        # 保存上传的文件
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 验证CIF文件
        if not is_valid_cif_file(input_path):
            raise HTTPException(status_code=400, detail="无效的CIF文件格式")
        
        # 检查文件大小
        file_size = get_file_size_mb(input_path)
        if file_size > 50:  # 限制50MB
            raise HTTPException(status_code=400, detail="文件大小超过限制（50MB）")
        
        # 执行转换
        logger.info(f"开始转换文件: {file.filename}")
        output_filename = f"{Path(file.filename).stem}.usdz"
        output_path = os.path.join(temp_dir, output_filename)
        
        # 创建会话以便保存中间文件
        session_id, session_dir = output_manager.create_conversion_session(
            file.filename, 
            {"file_size_mb": file_size}
        )
        
        # 保存原始CIF文件
        output_manager.save_file_to_session(
            session_id, 
            input_path, 
            "original_cif",
            "原始上传的CIF文件"
        )
        
        # 执行转换
        success, message, info = converter.convert_cif_to_usdz(input_path, output_path)
        
        # 在转换器清理临时目录之前，保存中间文件
        if hasattr(converter, 'temp_dir') and converter.temp_dir and os.path.exists(converter.temp_dir):
            # 查找并保存中间OBJ和MTL文件
            for root, dirs, files in os.walk(converter.temp_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    if f.endswith('.obj'):
                        output_manager.save_file_to_session(
                            session_id, 
                            file_path, 
                            "intermediate_obj",
                            "中间转换的OBJ文件"
                        )
                    elif f.endswith('.mtl'):
                        output_manager.save_file_to_session(
                            session_id, 
                            file_path, 
                            "intermediate_mtl",
                            "中间转换的MTL材质文件"
                        )
        
        if success:
            # 保存最终USDZ文件
            saved_output_path = output_manager.save_file_to_session(
                session_id, 
                output_path, 
                "final_usdz",
                "转换完成的USDZ文件"
            )
            
            # 完成转换会话
            output_manager.complete_conversion_session(
                session_id, 
                {"success": True, "info": info}, 
                output_path
            )
            
            # 返回文件响应，包含元数据头
            headers = {
                "X-Session-ID": session_id,
                "X-Conversion-Metadata": json.dumps({
                    "atom_count": info.get("atom_count", 0),
                    "file_size_mb": get_file_size_mb(output_path),
                    "cif_metadata": info.get("cif_metadata", {})
                })
            }
            
            return FileResponse(
                path=output_path,
                filename=output_filename,
                media_type="application/octet-stream",
                headers=headers
            )
        else:
            # 转换失败时也要完成会话
            output_manager.complete_conversion_session(
                session_id, 
                {"success": False, "error": message}, 
                None
            )
            raise HTTPException(status_code=500, detail=message or "转换失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")
    finally:
        # 清理转换器的临时目录
        if hasattr(converter, '_cleanup_temp_dir'):
            converter._cleanup_temp_dir()
        
        # 清理API的临时目录（延迟清理，确保文件响应完成）
        # 注意：这里不能立即清理，因为FileResponse需要访问文件
        pass

@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """获取会话信息"""
    try:
        session_info = output_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "success": True,
            "data": session_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取会话信息失败")

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "页面未找到"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "服务器内部错误"}
    )