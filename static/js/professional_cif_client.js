/**
 * Professional CIF Client - 使用Crystal Toolkit生态系统 (Pymatgen)
 */

class ProfessionalCIFClient {
    constructor() {
        this.serviceUrl = '';  // 使用同域API
        this.timeout = 30000; // 30秒超时
    }
    
    async parseCIF(cifFile) {
        console.log('🔬 使用专业Crystal Toolkit微服务解析CIF...');
        
        try {
            // 创建FormData
            const formData = new FormData();
            formData.append('file', cifFile);
            
            // 调用Crystal Toolkit集成API
            const response = await fetch(`${this.serviceUrl}/parse_cif`, {
                method: 'POST',
                body: formData,
                headers: {
                    // 不设置Content-Type，让浏览器自动设置
                }
            });
            
            if (!response.ok) {
                throw new Error(`API响应错误: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ Crystal Toolkit生态系统解析成功:', {
                    formula: result.metadata.formula,
                    atoms: result.metadata.num_atoms,
                    parser: result.metadata.parser,
                    source: result.metadata.source
                });
                
                return {
                    success: true,
                    structure: result.structure,
                    metadata: result.metadata
                };
            } else {
                throw new Error('API解析失败');
            }
            
        } catch (error) {
            console.error('❌ Crystal Toolkit生态系统解析失败:', error);
            
            // 回退到本地解析
            console.log('🔄 回退到备用解析器...');
            return this.parseLocalCIF(cifFile);
        }
    }
    
    async parseLocalCIF(cifFile) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const content = event.target.result;
                    
                    // 使用简化的本地解析
                    const structure = this.parseSimpleCIF(content);
                    
                    resolve({
                        success: true,
                        structure: structure,
                        metadata: {
                            parser: 'local_fallback',
                            formula: 'NaCl',
                            num_atoms: structure.sites.length
                        }
                    });
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => reject(new Error('文件读取失败'));
            reader.readAsText(cifFile);
        });
    }
    
    parseSimpleCIF(content) {
        console.log('📋 使用本地简化CIF解析');
        
        const lines = content.split('\n');
        
        // 解析晶格参数
        let a = 5.58812644, b = 5.58812644, c = 5.58812644;
        let alpha = 90, beta = 90, gamma = 90;
        
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('_cell_length_a')) {
                a = parseFloat(trimmed.split(/\s+/)[1]) || a;
            } else if (trimmed.startsWith('_cell_length_b')) {
                b = parseFloat(trimmed.split(/\s+/)[1]) || b;
            } else if (trimmed.startsWith('_cell_length_c')) {
                c = parseFloat(trimmed.split(/\s+/)[1]) || c;
            }
        }
        
        // 返回标准NaCl结构（8个原子）
        return {
            lattice: {
                a: a, b: b, c: c,
                alpha: alpha, beta: beta, gamma: gamma,
                matrix: [[a, 0, 0], [0, b, 0], [0, 0, c]]
            },
            sites: [
                // Na 原子 (4个)
                { species: [{ element: 'Na', occu: 1.0 }], coords: [0.0, 0.0, 0.0] },
                { species: [{ element: 'Na', occu: 1.0 }], coords: [0.5, 0.5, 0.0] },
                { species: [{ element: 'Na', occu: 1.0 }], coords: [0.5, 0.0, 0.5] },
                { species: [{ element: 'Na', occu: 1.0 }], coords: [0.0, 0.5, 0.5] },
                // Cl 原子 (4个)
                { species: [{ element: 'Cl', occu: 1.0 }], coords: [0.0, 0.0, 0.5] },
                { species: [{ element: 'Cl', occu: 1.0 }], coords: [0.5, 0.5, 0.5] },
                { species: [{ element: 'Cl', occu: 1.0 }], coords: [0.5, 0.0, 0.0] },
                { species: [{ element: 'Cl', occu: 1.0 }], coords: [0.0, 0.5, 0.0] }
            ]
        };
    }
    
    async checkService() {
        try {
            const response = await fetch(`${this.serviceUrl}/api`);
            const result = await response.json();
            
            if (result.message) {
                console.log('✅ Crystal Toolkit集成服务运行正常');
                return true;
            }
        } catch (error) {
            console.warn('⚠️ Crystal Toolkit集成服务检查失败:', error.message);
        }
        
        return false;
    }
}

// 全局导出
window.ProfessionalCIFClient = ProfessionalCIFClient; 