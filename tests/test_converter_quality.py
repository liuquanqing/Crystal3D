#!/usr/bin/env python3
"""
转换器质量测试脚本
测试和验证改进后的USDZ转换质量
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converter.main_converter import CIFToUSDZConverter
from converter.apple_usd_converter import AppleUSDConverter
from converter.tinyusdz_converter import TinyUSDZConverter
from converter.usdz_converter import USDZConverter
from loguru import logger

class ConverterQualityTester:
    """转换器质量测试器"""
    
    def __init__(self):
        self.test_results = []
        self.converters = {
            'apple_usd': AppleUSDConverter(),
            'tinyusdz': TinyUSDZConverter(),
            'docker_usd': USDZConverter()
        }
        
        # 测试文件
        self.test_files = {
            'cif': 'tests/test_nacl.cif',
            'obj': 'tests/test_simple.obj'
        }
        
        # 输出目录
        self.output_dir = Path('tests/quality_test_outputs')
        self.output_dir.mkdir(exist_ok=True)
    
    def test_converter_availability(self) -> Dict[str, Any]:
        """测试转换器可用性"""
        logger.info("=== 测试转换器可用性 ===")
        
        availability_results = {}
        
        for name, converter in self.converters.items():
            try:
                if hasattr(converter, 'get_converter_info'):
                    info = converter.get_converter_info()
                    availability_results[name] = {
                        'available': info.get('available', False),
                        'version': info.get('version', 'Unknown'),
                        'description': info.get('description', ''),
                        'features': info.get('features', [])
                    }
                else:
                    # 对于没有get_converter_info方法的转换器
                    if hasattr(converter, 'is_available'):
                        available = converter.is_available()
                    else:
                        available = True  # 假设可用
                    
                    availability_results[name] = {
                        'available': available,
                        'version': 'Unknown',
                        'description': f'{name} converter',
                        'features': []
                    }
                
                logger.info(f"{name}: {'可用' if availability_results[name]['available'] else '不可用'}")
                
            except Exception as e:
                logger.error(f"测试{name}转换器时出错: {e}")
                availability_results[name] = {
                    'available': False,
                    'error': str(e)
                }
        
        return availability_results
    
    def test_obj_conversion_quality(self) -> List[Dict[str, Any]]:
        """测试OBJ转换质量"""
        logger.info("=== 测试OBJ转换质量 ===")
        
        obj_file = self.test_files['obj']
        if not os.path.exists(obj_file):
            logger.error(f"测试OBJ文件不存在: {obj_file}")
            return []
        
        results = []
        
        for name, converter in self.converters.items():
            if not hasattr(converter, 'convert_obj_to_usdz'):
                continue
                
            output_file = self.output_dir / f"obj_test_{name}.usdz"
            
            logger.info(f"测试{name}转换器...")
            start_time = time.time()
            
            try:
                success, message = converter.convert_obj_to_usdz(
                    str(obj_file), 
                    str(output_file)
                )
                
                conversion_time = time.time() - start_time
                
                result = {
                    'converter': name,
                    'success': success,
                    'message': message,
                    'conversion_time': conversion_time,
                    'output_file': str(output_file),
                    'file_exists': os.path.exists(output_file)
                }
                
                if os.path.exists(output_file):
                    result['file_size_bytes'] = os.path.getsize(output_file)
                    result['file_size_mb'] = result['file_size_bytes'] / (1024 * 1024)
                
                results.append(result)
                
                logger.info(f"{name}: {'成功' if success else '失败'} - {message}")
                if success:
                    logger.info(f"  转换时间: {conversion_time:.2f}秒")
                    if 'file_size_mb' in result:
                        logger.info(f"  文件大小: {result['file_size_mb']:.2f}MB")
                
            except Exception as e:
                logger.error(f"{name}转换器异常: {e}")
                results.append({
                    'converter': name,
                    'success': False,
                    'error': str(e),
                    'conversion_time': time.time() - start_time
                })
        
        return results
    
    def test_cif_conversion_pipeline(self) -> Dict[str, Any]:
        """测试完整的CIF转换流程"""
        logger.info("=== 测试CIF转换流程 ===")
        
        cif_file = self.test_files['cif']
        if not os.path.exists(cif_file):
            logger.error(f"测试CIF文件不存在: {cif_file}")
            return {}
        
        output_file = self.output_dir / "cif_pipeline_test.usdz"
        
        main_converter = CIFToUSDZConverter()
        
        logger.info("开始完整CIF转换流程测试...")
        start_time = time.time()
        
        try:
            result = main_converter.convert(str(cif_file), str(output_file))
            conversion_time = time.time() - start_time
            
            pipeline_result = {
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'conversion_time': conversion_time,
                'metadata': result.get('metadata', {}),
                'steps_completed': result.get('steps_completed', []),
                'output_file': str(output_file),
                'file_exists': os.path.exists(output_file)
            }
            
            if os.path.exists(output_file):
                pipeline_result['file_size_bytes'] = os.path.getsize(output_file)
                pipeline_result['file_size_mb'] = pipeline_result['file_size_bytes'] / (1024 * 1024)
            
            logger.info(f"CIF流程: {'成功' if pipeline_result['success'] else '失败'}")
            logger.info(f"转换时间: {conversion_time:.2f}秒")
            
            if 'metadata' in result:
                metadata = result['metadata']
                if 'usdz_converter_used' in metadata:
                    logger.info(f"使用的USDZ转换器: {metadata['usdz_converter_used']}")
                if 'converter_used' in metadata:
                    logger.info(f"使用的OBJ转换器: {metadata['converter_used']}")
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"CIF转换流程异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'conversion_time': time.time() - start_time
            }
    
    def generate_quality_report(self, availability: Dict, obj_results: List, cif_result: Dict) -> Dict[str, Any]:
        """生成质量报告"""
        logger.info("=== 生成质量报告 ===")
        
        # 统计成功率
        obj_success_count = sum(1 for r in obj_results if r.get('success', False))
        obj_total_count = len(obj_results)
        
        # 找出最快的转换器
        successful_obj_results = [r for r in obj_results if r.get('success', False)]
        fastest_converter = None
        if successful_obj_results:
            fastest_converter = min(successful_obj_results, key=lambda x: x.get('conversion_time', float('inf')))
        
        # 找出文件最小的转换器
        smallest_file_converter = None
        if successful_obj_results:
            results_with_size = [r for r in successful_obj_results if 'file_size_bytes' in r]
            if results_with_size:
                smallest_file_converter = min(results_with_size, key=lambda x: x['file_size_bytes'])
        
        report = {
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'converter_availability': availability,
            'obj_conversion_results': {
                'total_converters': obj_total_count,
                'successful_converters': obj_success_count,
                'success_rate': obj_success_count / obj_total_count if obj_total_count > 0 else 0,
                'results': obj_results
            },
            'cif_pipeline_result': cif_result,
            'performance_analysis': {
                'fastest_converter': fastest_converter,
                'smallest_file_converter': smallest_file_converter
            },
            'recommendations': self._generate_recommendations(availability, obj_results, cif_result)
        }
        
        return report
    
    def _generate_recommendations(self, availability: Dict, obj_results: List, cif_result: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 检查转换器可用性
        available_converters = [name for name, info in availability.items() if info.get('available', False)]
        unavailable_converters = [name for name, info in availability.items() if not info.get('available', False)]
        
        if unavailable_converters:
            recommendations.append(f"建议安装或配置以下转换器以提高转换成功率: {', '.join(unavailable_converters)}")
        
        # 检查转换成功率
        successful_obj_results = [r for r in obj_results if r.get('success', False)]
        if len(successful_obj_results) == 0:
            recommendations.append("所有OBJ转换器都失败了，建议检查输入文件格式和转换器配置")
        elif len(successful_obj_results) < len(obj_results):
            failed_converters = [r['converter'] for r in obj_results if not r.get('success', False)]
            recommendations.append(f"以下转换器转换失败，建议检查配置: {', '.join(failed_converters)}")
        
        # 性能建议
        if successful_obj_results:
            avg_time = sum(r.get('conversion_time', 0) for r in successful_obj_results) / len(successful_obj_results)
            if avg_time > 30:
                recommendations.append("转换时间较长，建议优化转换参数或使用更快的转换器")
        
        # CIF流程建议
        if not cif_result.get('success', False):
            recommendations.append("CIF转换流程失败，建议检查CIF文件格式和转换器链配置")
        
        if not recommendations:
            recommendations.append("所有转换器工作正常，转换质量良好")
        
        return recommendations
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("开始转换器质量测试")
        
        # 测试转换器可用性
        availability = self.test_converter_availability()
        
        # 测试OBJ转换质量
        obj_results = self.test_obj_conversion_quality()
        
        # 测试CIF转换流程
        cif_result = self.test_cif_conversion_pipeline()
        
        # 生成质量报告
        report = self.generate_quality_report(availability, obj_results, cif_result)
        
        # 保存报告
        report_file = self.output_dir / "quality_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"质量报告已保存到: {report_file}")
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("转换器质量测试摘要")
        print("="*60)
        
        # 转换器可用性
        print("\n转换器可用性:")
        for name, info in report['converter_availability'].items():
            status = "✓ 可用" if info.get('available', False) else "✗ 不可用"
            print(f"  {name}: {status}")
        
        # OBJ转换结果
        obj_results = report['obj_conversion_results']
        print(f"\nOBJ转换测试: {obj_results['successful_converters']}/{obj_results['total_converters']} 成功")
        print(f"成功率: {obj_results['success_rate']:.1%}")
        
        # CIF流程结果
        cif_result = report['cif_pipeline_result']
        cif_status = "✓ 成功" if cif_result.get('success', False) else "✗ 失败"
        print(f"\nCIF转换流程: {cif_status}")
        
        # 性能分析
        perf = report['performance_analysis']
        if perf['fastest_converter']:
            fastest = perf['fastest_converter']
            print(f"\n最快转换器: {fastest['converter']} ({fastest['conversion_time']:.2f}秒)")
        
        if perf['smallest_file_converter']:
            smallest = perf['smallest_file_converter']
            print(f"最小文件: {smallest['converter']} ({smallest['file_size_mb']:.2f}MB)")
        
        # 建议
        print("\n改进建议:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)

def main():
    """主函数"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    tester = ConverterQualityTester()
    report = tester.run_all_tests()
    tester.print_summary(report)

if __name__ == '__main__':
    main()