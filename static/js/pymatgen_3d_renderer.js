/**
 * Pymatgen Plotly 渲染器 - 基于 Crystal Toolkit 的方法
 * 使用 Plotly.js 进行 3D 晶体结构可视化
 */

class PymatgenPlotlyRenderer {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentStructure = null;
        
        // CPK 颜色映射 (Crystal Toolkit 标准)
        this.cpkColors = {
            'H': '#FFFFFF',   'He': '#D9FFFF',  'Li': '#CC80FF',  'Be': '#C2FF00',
            'B': '#FFB5B5',   'C': '#909090',   'N': '#3050F8',   'O': '#FF0D0D',
            'F': '#90E050',   'Ne': '#B3E3F5',  'Na': '#AB5CF2',  'Mg': '#8AFF00',
            'Al': '#BFA6A6',  'Si': '#F0C8A0',  'P': '#FF8000',   'S': '#FFFF30',
            'Cl': '#1FF01F',  'Ar': '#80D1E3',  'K': '#8F40D4',   'Ca': '#3DFF00',
            'Sc': '#E6E6E6',  'Ti': '#BFC2C7',  'V': '#A6A6AB',   'Cr': '#8A99C7',
            'Mn': '#9C7AC7',  'Fe': '#E06633',  'Co': '#F090A0',  'Ni': '#50D050',
            'Cu': '#C88033',  'Zn': '#7D80B0',  'default': '#FF69B4'
        };
        
        // Van der Waals 半径 (Å)
        this.vdwRadii = {
            'H': 1.20, 'He': 1.40, 'Li': 1.82, 'Be': 1.53, 'B': 1.92, 'C': 1.70,
            'N': 1.55, 'O': 1.52, 'F': 1.47, 'Ne': 1.54, 'Na': 2.27, 'Mg': 1.73,
            'Al': 1.84, 'Si': 2.10, 'P': 1.80, 'S': 1.80, 'Cl': 1.75, 'Ar': 1.88,
            'K': 2.75, 'Ca': 2.31, 'Fe': 2.00, 'Cu': 1.40, 'Zn': 1.39,
            'default': 1.50
        };
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error('❌ 容器不存在');
            return;
        }
        
        // 检查 Plotly.js 是否加载
        if (typeof Plotly === 'undefined') {
            console.error('❌ Plotly.js 未加载');
            this.container.innerHTML = '<div class="text-center p-4"><p class="text-danger">需要加载 Plotly.js</p></div>';
            return;
        }
        
        console.log('✅ Pymatgen Plotly 渲染器初始化成功');
    }
    
    loadPymatgenStructure(structure) {
        console.log('🔬 使用 Plotly 加载 Pymatgen 结构...');
        console.log('📍 目标容器:', this.containerId, this.container);
        
        // 清空容器并重置样式
        if (this.container) {
            this.container.innerHTML = '';
            // 确保容器适合Plotly渲染
            this.container.style.width = '100%';
            this.container.style.height = '500px';
            this.container.style.position = 'relative';
            console.log('🧹 已清空容器并重置样式');
        }
        
        try {
            this.currentStructure = structure;
            
            // 生成 Plotly 数据
            const plotData = this.generatePlotlyData(structure);
            
            // 配置 Plotly 布局 (Crystal Toolkit 风格)
            const layout = {
                title: {
                    text: `${structure.formula} - Crystal Structure`,
                    font: { size: 16 }
                },
                scene: {
                    xaxis: { title: 'X (Å)', showgrid: true, gridcolor: '#E0E0E0' },
                    yaxis: { title: 'Y (Å)', showgrid: true, gridcolor: '#E0E0E0' },
                    zaxis: { title: 'Z (Å)', showgrid: true, gridcolor: '#E0E0E0' },
                    aspectmode: 'cube',
                    bgcolor: '#FAFAFA',
                    camera: {
                        eye: { x: 1.5, y: 1.5, z: 1.5 }
                    }
                },
                margin: { l: 0, r: 0, b: 0, t: 50 },
                paper_bgcolor: '#FFFFFF',
                plot_bgcolor: '#FFFFFF',
                autosize: true,
                width: null,
                height: 500
            };
            
            // 配置选项
            const config = {
                displayModeBar: true,
                modeBarButtonsToAdd: [
                    {
                        name: 'Screenshot',
                        icon: Plotly.Icons.camera,
                        click: () => this.takeScreenshot()
                    }
                ],
                displaylogo: false,
                responsive: true,
                scrollZoom: false, // 禁用默认滚轮缩放，保持与Crystal Toolkit一致
                showTips: false
            };
            
            // 渲染 Plotly 图表到指定容器
            Plotly.newPlot(this.container, plotData, layout, config);
            
            // 确保图表正确适应容器
            setTimeout(() => {
                Plotly.Plots.resize(this.container);
                console.log('📐 Plotly图表已调整大小');
            }, 100);
            
            const atomCount = structure.sites.length;
            console.log(`✅ Plotly 结构加载完成: ${atomCount} 个原子`);
            
            return {
                success: true,
                atomCount: atomCount,
                formula: structure.formula
            };
            
        } catch (error) {
            console.error('❌ Plotly 结构加载失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    generatePlotlyData(structure) {
        const traces = [];
        
        // 1. 渲染原子 (按元素分组)
        const atomsByElement = this.groupAtomsByElement(structure);
        
        Object.entries(atomsByElement).forEach(([element, atoms]) => {
            const color = this.cpkColors[element] || this.cpkColors.default;
            const radius = this.vdwRadii[element] || this.vdwRadii.default;
            
            traces.push({
                type: 'scatter3d',
                mode: 'markers',
                name: element,
                x: atoms.map(atom => atom.cartesian[0]),
                y: atoms.map(atom => atom.cartesian[1]),
                z: atoms.map(atom => atom.cartesian[2]),
                marker: {
                    size: radius * 8, // 缩放因子
                    color: color,
                    opacity: 0.8,
                    line: {
                        color: '#000000',
                        width: 1
                    }
                },
                text: atoms.map(atom => `${element} (${atom.coords[0].toFixed(3)}, ${atom.coords[1].toFixed(3)}, ${atom.coords[2].toFixed(3)})`),
                hovertemplate: '<b>%{text}</b><br>Position: (%{x:.3f}, %{y:.3f}, %{z:.3f})<extra></extra>'
            });
        });
        
        // 2. 渲染化学键
        const bonds = this.calculateBonds(structure);
        if (bonds.length > 0) {
            const bondTrace = this.createBondTrace(bonds);
            traces.push(bondTrace);
        }
        
        // 3. 渲染晶胞
        const unitCellTrace = this.createUnitCellTrace(structure.lattice);
        traces.push(unitCellTrace);
        
        return traces;
    }
    
    groupAtomsByElement(structure) {
        const atomsByElement = {};
        
        structure.sites.forEach((site, index) => {
            site.species.forEach(spec => {
                const element = spec.element.replace(/[0-9+-]/g, ''); // 清理元素符号
                
                if (!atomsByElement[element]) {
                    atomsByElement[element] = [];
                }
                
                const cartesian = this.fractionalToCartesian(site.coords, structure.lattice);
                
                atomsByElement[element].push({
                    index: index,
                    coords: site.coords,
                    cartesian: cartesian,
                    occupancy: spec.occu
                });
            });
        });
        
        return atomsByElement;
    }
    
    calculateBonds(structure) {
        const bonds = [];
        const maxBondDistance = 3.0; // 最大成键距离 (Å)
        
        for (let i = 0; i < structure.sites.length; i++) {
            for (let j = i + 1; j < structure.sites.length; j++) {
                const pos1 = this.fractionalToCartesian(structure.sites[i].coords, structure.lattice);
                const pos2 = this.fractionalToCartesian(structure.sites[j].coords, structure.lattice);
                
                const distance = Math.sqrt(
                    Math.pow(pos2[0] - pos1[0], 2) +
                    Math.pow(pos2[1] - pos1[1], 2) +
                    Math.pow(pos2[2] - pos1[2], 2)
                );
                
                if (distance < maxBondDistance) {
                    bonds.push({
                        start: pos1,
                        end: pos2,
                        distance: distance
                    });
                }
            }
        }
        
        return bonds;
    }
    
    createBondTrace(bonds) {
        const x = [], y = [], z = [];
        
        bonds.forEach(bond => {
            // 添加起点
            x.push(bond.start[0]);
            y.push(bond.start[1]);
            z.push(bond.start[2]);
            
            // 添加终点
            x.push(bond.end[0]);
            y.push(bond.end[1]);
            z.push(bond.end[2]);
            
            // 添加分隔符 (null)
            x.push(null);
            y.push(null);
            z.push(null);
        });
        
        return {
            type: 'scatter3d',
            mode: 'lines',
            name: 'Bonds',
            x: x,
            y: y,
            z: z,
            line: {
                color: '#808080',
                width: 3
            },
            hoverinfo: 'skip',
            showlegend: false
        };
    }
    
    createUnitCellTrace(lattice) {
        const matrix = lattice.matrix;
        const origin = [0, 0, 0];
        const a = matrix[0];
        const b = matrix[1];
        const c = matrix[2];
        
        // 定义晶胞的12条边
        const edges = [
            // 从原点出发的3条边
            [origin, a],
            [origin, b],
            [origin, c],
            // 平行于原点边的边
            [a, [a[0] + b[0], a[1] + b[1], a[2] + b[2]]],
            [a, [a[0] + c[0], a[1] + c[1], a[2] + c[2]]],
            [b, [b[0] + a[0], b[1] + a[1], b[2] + a[2]]],
            [b, [b[0] + c[0], b[1] + c[1], b[2] + c[2]]],
            [c, [c[0] + a[0], c[1] + a[1], c[2] + a[2]]],
            [c, [c[0] + b[0], c[1] + b[1], c[2] + b[2]]],
            // 远端的3条边
            [[a[0] + b[0], a[1] + b[1], a[2] + b[2]], [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]]],
            [[a[0] + c[0], a[1] + c[1], a[2] + c[2]], [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]]],
            [[b[0] + c[0], b[1] + c[1], b[2] + c[2]], [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]]]
        ];
        
        const x = [], y = [], z = [];
        
        edges.forEach(edge => {
            x.push(edge[0][0], edge[1][0], null);
            y.push(edge[0][1], edge[1][1], null);
            z.push(edge[0][2], edge[1][2], null);
        });
        
        return {
            type: 'scatter3d',
            mode: 'lines',
            name: 'Unit Cell',
            x: x,
            y: y,
            z: z,
            line: {
                color: '#000000',
                width: 2
            },
            hoverinfo: 'skip',
            showlegend: false
        };
    }
    
    fractionalToCartesian(fracCoords, lattice) {
        const matrix = lattice.matrix;
        return [
            fracCoords[0] * matrix[0][0] + fracCoords[1] * matrix[1][0] + fracCoords[2] * matrix[2][0],
            fracCoords[0] * matrix[0][1] + fracCoords[1] * matrix[1][1] + fracCoords[2] * matrix[2][1],
            fracCoords[0] * matrix[0][2] + fracCoords[1] * matrix[1][2] + fracCoords[2] * matrix[2][2]
        ];
    }
    
    takeScreenshot() {
        try {
            Plotly.downloadImage(this.container, {
                format: 'png',
                width: 1200,
                height: 800,
                filename: 'crystal_structure'
            });
        } catch (error) {
            console.error('截图失败:', error);
        }
    }
    
    updateDisplayOptions(options) {
        // 可以根据选项更新显示
        if (this.currentStructure) {
            this.loadPymatgenStructure(this.currentStructure);
        }
    }
}

// 全局导出
window.PymatgenPlotlyRenderer = PymatgenPlotlyRenderer;
