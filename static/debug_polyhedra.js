// 多面体调试脚本
// 在浏览器控制台中运行此脚本来调试多面体显示问题

function debugPolyhedra() {
    console.log('🔍 开始多面体调试...');
    
    // 1. 检查DOM元素
    const showPolyhedra = document.getElementById('showPolyhedra');
    console.log('📋 DOM检查:');
    console.log('  showPolyhedra元素:', showPolyhedra);
    console.log('  showPolyhedra.checked:', showPolyhedra ? showPolyhedra.checked : 'N/A');
    
    // 2. 检查crystalPreview实例
    console.log('🔬 crystalPreview检查:');
    console.log('  crystalPreview存在:', !!window.crystalPreview);
    
    if (window.crystalPreview) {
        console.log('  renderParams:', window.crystalPreview.renderParams);
        console.log('  currentStructure存在:', !!window.crystalPreview.currentStructure);
        
        if (window.crystalPreview.currentStructure) {
            const structure = window.crystalPreview.currentStructure;
            console.log('  结构信息:');
            console.log('    原子数:', structure.atoms ? structure.atoms.length : 'N/A');
            console.log('    多面体数:', structure.polyhedra ? structure.polyhedra.length : 'N/A');
            console.log('    多面体数据:', structure.polyhedra);
        }
    }
    
    // 3. 手动触发多面体显示
    if (window.crystalPreview && showPolyhedra) {
        console.log('🔄 手动同步多面体设置...');
        
        // 强制设置为显示多面体
        showPolyhedra.checked = true;
        window.crystalPreview.renderParams.showPolyhedra = true;
        
        console.log('  设置后的状态:');
        console.log('    showPolyhedra.checked:', showPolyhedra.checked);
        console.log('    renderParams.showPolyhedra:', window.crystalPreview.renderParams.showPolyhedra);
        
        // 触发重新渲染
        if (window.crystalPreview.currentStructure) {
            console.log('🎨 触发重新渲染...');
            window.crystalPreview.updateRender(true);
        }
    }
    
    // 4. 检查Plotly图表
    const plotContainer = document.getElementById('crystal-preview');
    if (plotContainer) {
        console.log('📊 Plotly检查:');
        console.log('  容器存在:', !!plotContainer);
        console.log('  容器内容:', plotContainer.innerHTML.length > 0 ? '有内容' : '空');
        
        // 检查Plotly数据
        if (window.Plotly && plotContainer._fullData) {
            console.log('  Plotly数据traces数量:', plotContainer._fullData.length);
            plotContainer._fullData.forEach((trace, i) => {
                console.log(`    Trace ${i}:`, trace.name, trace.type);
            });
        }
    }
    
    console.log('✅ 多面体调试完成');
}

// 自动运行调试
if (typeof window !== 'undefined') {
    // 等待页面加载完成后运行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(debugPolyhedra, 2000);
        });
    } else {
        setTimeout(debugPolyhedra, 1000);
    }
}

// 导出调试函数供手动调用
if (typeof window !== 'undefined') {
    window.debugPolyhedra = debugPolyhedra;
}

console.log('🔧 多面体调试脚本已加载，可以手动调用 debugPolyhedra() 函数');