"""
CIF转USDZ命令行转换工具
"""
import os
import sys
import click
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from converter.main_converter import CIFToUSDZConverter
from utils import setup_logger, is_valid_cif_file


@click.group()
@click.option('--log-level', default='INFO', help='日志级别 (DEBUG, INFO, WARNING, ERROR)')
def cli(log_level):
    """CIF转USDZ自动转换工具"""
    setup_logger(log_level)


@cli.group()
def convert():
    """转换命令组"""
    pass


@convert.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--sphere-resolution', default=20, help='原子球体细分级别')
@click.option('--bond-resolution', default=8, help='化学键圆柱体细分级别')
@click.option('--no-bonds', is_flag=True, help='不包含化学键')
@click.option('--scale', default=1.0, help='模型缩放因子')
def single(input_file, output_file, sphere_resolution, bond_resolution, no_bonds, scale):
    """转换单个CIF文件"""
    try:
        click.echo(f"开始转换: {input_file} -> {output_file}")
        
        # 验证输入文件
        if not is_valid_cif_file(input_file):
            click.echo("错误: 无效的CIF文件格式", err=True)
            sys.exit(1)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 创建转换器
        converter = CIFToUSDZConverter(
            sphere_resolution=sphere_resolution,
            bond_cylinder_resolution=bond_resolution,
            include_bonds=not no_bonds,
            scale_factor=scale
        )
        
        # 执行转换
        result = converter.convert(input_file, output_file)
        
        if result['success']:
            click.echo(f"✓ 转换成功: {output_file}")
            click.echo(f"  原子数量: {result['metadata'].get('atom_count', 0)}")
            click.echo(f"  顶点数量: {result['metadata'].get('vertices_count', 0)}")
            click.echo(f"  面数量: {result['metadata'].get('faces_count', 0)}")
            click.echo(f"  文件大小: {result['metadata'].get('file_size_mb', 0):.2f} MB")
        else:
            click.echo(f"✗ 转换失败: {result['message']}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"转换过程中发生错误: {e}", err=True)
        sys.exit(1)


@convert.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('output_dir', type=click.Path())
@click.option('--pattern', default='*.cif', help='文件匹配模式')
@click.option('--sphere-resolution', default=20, help='原子球体细分级别')
@click.option('--bond-resolution', default=8, help='化学键圆柱体细分级别')
@click.option('--no-bonds', is_flag=True, help='不包含化学键')
@click.option('--scale', default=1.0, help='模型缩放因子')
def batch(input_dir, output_dir, pattern, sphere_resolution, bond_resolution, no_bonds, scale):
    """批量转换目录中的CIF文件"""
    try:
        click.echo(f"开始批量转换: {input_dir} -> {output_dir}")
        click.echo(f"文件模式: {pattern}")
        
        # 创建转换器
        converter = CIFToUSDZConverter(
            sphere_resolution=sphere_resolution,
            bond_cylinder_resolution=bond_resolution,
            include_bonds=not no_bonds,
            scale_factor=scale
        )
        
        # 执行批量转换
        result = converter.batch_convert(input_dir, output_dir, pattern)
        
        click.echo(f"\n批量转换完成:")
        click.echo(f"  总文件数: {result['total_files']}")
        click.echo(f"  成功转换: {result['successful_conversions']}")
        click.echo(f"  转换失败: {result['failed_conversions']}")
        
        # 显示详细结果
        if result['results']:
            click.echo("\n详细结果:")
            for item in result['results']:
                status = "✓" if item['success'] else "✗"
                click.echo(f"  {status} {os.path.basename(item['input_file'])}: {item['message']}")
        
        if result['failed_conversions'] > 0:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"批量转换过程中发生错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='服务器主机地址')
@click.option('--port', default=8000, help='服务器端口')
@click.option('--reload', is_flag=True, help='启用自动重载（开发模式）')
def serve(host, port, reload):
    """启动Web服务"""
    click.echo(f"启动CIF转USDZ转换服务...")
    click.echo(f"服务地址: http://{host}:{port}")
    click.echo(f"API文档: http://{host}:{port}/docs")
    
    try:
        # 导入应用
        from api.routes import app
        
        uvicorn.run(
            "api.routes:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        click.echo("\n服务已停止")
    except Exception as e:
        click.echo(f"启动服务失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """显示转换器信息"""
    try:
        converter = CIFToUSDZConverter()
        info = converter.get_conversion_info()
        
        click.echo("CIF转USDZ转换器信息:")
        click.echo(f"  版本: {info['converter_version']}")
        click.echo(f"  球体细分级别: {info['sphere_resolution']}")
        click.echo(f"  键连细分级别: {info['bond_cylinder_resolution']}")
        click.echo(f"  包含化学键: {info['include_bonds']}")
        click.echo(f"  缩放因子: {info['scale_factor']}")
        click.echo(f"  USD转换工具可用: {info['usd_converter_available']}")
        if info['usd_converter_path']:
            click.echo(f"  USD转换工具路径: {info['usd_converter_path']}")
        
    except Exception as e:
        click.echo(f"获取信息失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('cif_file', type=click.Path(exists=True))
def validate(cif_file):
    """验证CIF文件"""
    try:
        if is_valid_cif_file(cif_file):
            click.echo(f"✓ {cif_file} 是有效的CIF文件")
            
            # 尝试解析并显示详细信息
            from converter.cif_parser import CIFParser
            parser = CIFParser()
            
            if parser.parse_file(cif_file):
                click.echo(f"  化学式: {parser.metadata.get('formula', 'Unknown')}")
                click.echo(f"  原子数量: {parser.metadata.get('num_atoms', 0)}")
                click.echo(f"  晶格参数: a={parser.metadata.get('lattice_parameters', {}).get('a', 0):.3f}")
                click.echo(f"  体积: {parser.metadata.get('volume', 0):.3f} Ų")
                click.echo(f"  元素: {', '.join(parser.metadata.get('elements', []))}")
        else:
            click.echo(f"✗ {cif_file} 不是有效的CIF文件", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"验证过程中发生错误: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 