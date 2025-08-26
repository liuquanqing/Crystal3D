/**
 * 真正的Crystal Toolkit风格渲染器
 * 基于Plotly但完全整合到容器内，支持所有预览参数
 */

class CrystalToolkitRenderer {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentStructure = null;
        this.controlsBound = false; // 防止重复绑定控件
        
        // 渲染参数（与UI控件同步）
        this.renderParams = {
            sphereResolution: 20,
            scaleFactor: 1.0,
            showAtoms: true,
            showBonds: true,
            showUnitCell: true,
            includeBonds: true
        };
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error('❌ 渲染容器不存在:', this.containerId);
            return;
        }
        
        // 检查Plotly
        if (typeof Plotly === 'undefined') {
            console.error('❌ Plotly.js未加载');
            return;
        }
        
        // 设置容器样式
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.position = 'relative';
        this.container.style.overflow = 'hidden';
        
        // 添加窗口大小变化监听器
        window.addEventListener('resize', () => {
            if (this.container && this.currentStructure) {
                setTimeout(() => {
                    this.resizeToContainer(false); // 窗口大小变化时不重置相机
                }, 100);
            }
        });
        
        // Plotly事件监听器将在渲染后绑定
        
        console.log('✅ Crystal Toolkit渲染器初始化成功');
    }
    
    // 设置标题栏3D工具栏
    setupCustomToolbar() {
        console.log('🔍 绑定标题栏3D工具栏...');
        
        // 旋转模式
        const rotateBtn = document.getElementById('btnHeaderRotate');
        if (rotateBtn) {
            rotateBtn.addEventListener('click', () => {
                this.setInteractionMode('rotate');
                this.setActiveButton(rotateBtn);
            });
        }
        
        // 平移模式
        const panBtn = document.getElementById('btnHeaderPan');
        if (panBtn) {
            panBtn.addEventListener('click', () => {
                this.setInteractionMode('pan');
                this.setActiveButton(panBtn);
            });
        }
        
        // 缩放模式
        const zoomBtn = document.getElementById('btnHeaderZoom');
        if (zoomBtn) {
            zoomBtn.addEventListener('click', () => {
                this.setInteractionMode('zoom');
                this.setActiveButton(zoomBtn);
            });
        }
        
        // 重置视角
        const resetBtn = document.getElementById('btnHeaderReset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetCamera();
            });
        }
        
        // 全屏切换
        const fullscreenBtn = document.getElementById('btnHeaderFullscreen');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => {
                this.toggleFullscreen();
            });
        }
        
        // 截图
        const snapshotBtn = document.getElementById('btnHeaderSnapshot');
        if (snapshotBtn) {
            snapshotBtn.addEventListener('click', () => {
                this.takeSnapshot();
            });
        }
        
        // 默认激活旋转模式
        if (rotateBtn) {
            this.setActiveButton(rotateBtn);
            this.setInteractionMode('rotate');
        }
        
        console.log('✅ 标题栏3D工具栏绑定完成');
    }
    
    // 设置按钮激活状态
    setActiveButton(activeBtn) {
        // 移除所有按钮的激活状态
        const allBtns = ['btnHeaderRotate', 'btnHeaderPan', 'btnHeaderZoom'];
        allBtns.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.classList.remove('active');
                btn.classList.add('btn-outline-light');
                btn.classList.remove('btn-light');
            }
        });
        
        // 设置当前按钮为激活状态
        if (activeBtn) {
            activeBtn.classList.add('active');
            activeBtn.classList.remove('btn-outline-light');
            activeBtn.classList.add('btn-light');
        }
    }
    
    // 设置交互模式
    setInteractionMode(mode) {
        if (!this.container) return;
        
        // 设置Plotly的拖拽模式（保持scrollZoom为false，使用自定义滚轮处理）
        const config = {
            scrollZoom: false,
            displayModeBar: false,
            responsive: true
        };
        
        // 根据模式设置不同的拖拽行为
        switch(mode) {
            case 'rotate':
                // 默认3D旋转模式
                Plotly.relayout(this.container, {
                    'scene.dragmode': 'orbit'
                });
                break;
            case 'pan':
                // 平移模式
                Plotly.relayout(this.container, {
                    'scene.dragmode': 'pan'
                });
                break;
            case 'zoom':
                // 缩放模式 (使用滚轮缩放)
                Plotly.relayout(this.container, {
                    'scene.dragmode': 'zoom'
                });
                break;
        }
        
        console.log(`🎮 切换到${mode}模式`);
    }
    
    // 重置相机视角
    resetCamera() {
        if (!this.container) return;
        
        // 使用存储的最佳相机设置，如果没有则使用默认值
        const cameraSettings = this.optimalCamera || {
            eye: { x: 1.5, y: 1.5, z: 1.5 },
            center: { x: 0, y: 0, z: 0 }
        };
        
        Plotly.relayout(this.container, {
            'scene.camera': cameraSettings
        });
        
        console.log('🏠 视角已重置到最佳位置');
    }
    
    // 切换全屏
    toggleFullscreen() {
        if (!this.container) return;
        
        // 获取最外层的预览卡片容器
        const previewCard = this.container.closest('.card');
        const targetElement = previewCard || this.container;
        
        if (!document.fullscreenElement) {
            // 进入全屏
            if (targetElement.requestFullscreen) {
                targetElement.requestFullscreen().then(() => {
                    setTimeout(() => {
                        this.resizeToContainer(false); // 全屏时不重置相机
                        console.log('📺 已进入全屏模式');
                    }, 200);
                }).catch(err => {
                    console.error('❌ 全屏请求失败:', err);
                });
            } else {
                console.warn('⚠️ 浏览器不支持全屏API');
            }
        } else {
            // 退出全屏
            document.exitFullscreen().then(() => {
                setTimeout(() => {
                    this.resizeToContainer(false); // 退出全屏时不重置相机
                    console.log('📱 已退出全屏模式');
                }, 200);
            });
        }
    }
    
    // 截图
    takeSnapshot() {
        if (!this.container) return;
        
        Plotly.downloadImage(this.container, {
            format: 'png',
            width: 1920,
            height: 1080,
            filename: `crystal_structure_${new Date().getTime()}`
        });
        
        console.log('📸 截图已保存');
    }
    
    // 绑定UI控件
    bindControls() {
        // 防止重复绑定
        if (this.controlsBound) {
            return;
        }
        this.controlsBound = true;
        
        // 球体分辨率
        const sphereResolution = document.getElementById('sphereResolution');
        const sphereValue = document.getElementById('sphereValue');
        if (sphereResolution && sphereValue) {
            // 初始化球体分辨率值
            sphereResolution.value = this.renderParams.sphereResolution;
            sphereValue.textContent = this.renderParams.sphereResolution;
            
            sphereResolution.addEventListener('input', (e) => {
                this.renderParams.sphereResolution = parseInt(e.target.value);
                sphereValue.textContent = e.target.value;
                this.updateRender(true); // 保持相机位置，不影响视角
            });
        }
        
        // 缩放因子
        const scaleFactor = document.getElementById('scaleFactor');
        const scaleValue = document.getElementById('scaleValue');
        if (scaleFactor && scaleValue) {
            // 初始化滑动条值
            scaleFactor.value = this.renderParams.scaleFactor;
            scaleValue.textContent = this.renderParams.scaleFactor.toFixed(1);
            
            scaleFactor.addEventListener('input', (e) => {
                this.renderParams.scaleFactor = parseFloat(e.target.value);
                scaleValue.textContent = parseFloat(e.target.value).toFixed(1);
                this.updateRender(true); // 保持相机位置，不影响视角
            });
        }
        
        // 显示选项
        const showAtoms = document.getElementById('showAtoms');
        const showBonds = document.getElementById('showBonds');
        const showUnitCell = document.getElementById('showUnitCell');
        const includeBonds = document.getElementById('includeBonds');
        
        if (showAtoms) {
            // 初始化复选框状态
            showAtoms.checked = this.renderParams.showAtoms;
            showAtoms.addEventListener('change', (e) => {
                this.renderParams.showAtoms = e.target.checked;
                this.updateRender(true); // 保持相机位置
            });
        }
        
        if (showBonds) {
            // 初始化复选框状态
            showBonds.checked = this.renderParams.showBonds;
            showBonds.addEventListener('change', (e) => {
                this.renderParams.showBonds = e.target.checked;
                this.updateRender(true); // 保持相机位置
            });
        }
        
        if (showUnitCell) {
            // 初始化复选框状态
            showUnitCell.checked = this.renderParams.showUnitCell;
            showUnitCell.addEventListener('change', (e) => {
                this.renderParams.showUnitCell = e.target.checked;
                this.updateRender(true); // 保持相机位置
            });
        }
        
        if (includeBonds) {
            // 初始化复选框状态
            includeBonds.checked = this.renderParams.includeBonds;
            includeBonds.addEventListener('change', (e) => {
                this.renderParams.includeBonds = e.target.checked;
                this.updateRender(true); // 保持相机位置，不影响视角
            });
        }
        
        console.log('🎛️ UI控件已绑定');
    }
    
    loadStructure(structure) {
        console.log('🔬 Crystal Toolkit加载结构...', structure);
        
        if (!this.container) {
            console.error('❌ 容器不存在:', this.containerId);
            return { success: false, error: 'Container not found' };
        }
        
        // 清空容器并重置样式
        this.container.innerHTML = '';
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.position = 'relative';
        this.container.style.overflow = 'hidden';
        console.log('🧹 容器已清空并重置样式');
        
        try {
            this.currentStructure = structure;
            
            // 生成Plotly数据
            console.log('📊 生成Plotly数据...');
            const plotData = this.generatePlotlyData(structure);
            console.log('📈 Plotly数据:', plotData);
            
            // 计算结构边界框并设置合适的相机位置
            const bounds = this.calculateStructureBounds(structure);
            const optimalCamera = this.calculateOptimalCamera(bounds);
            
            // Crystal Toolkit风格布局 - 无标题
            const layout = {
                scene: {
                    xaxis: { 
                        title: 'X (Å)', 
                        showgrid: false,
                        showline: false,
                        zeroline: false,
                        showticklabels: false
                    },
                    yaxis: { 
                        title: 'Y (Å)', 
                        showgrid: false,
                        showline: false,
                        zeroline: false,
                        showticklabels: false
                    },
                    zaxis: { 
                        title: 'Z (Å)', 
                        showgrid: false,
                        showline: false,
                        zeroline: false,
                        showticklabels: false
                    },
                    aspectmode: 'cube',
                    bgcolor: 'white',
                    camera: optimalCamera,
                    dragmode: 'orbit'
                },
                margin: { l: 0, r: 0, b: 0, t: 0, pad: 0 },
                paper_bgcolor: 'white',
                plot_bgcolor: 'white',
                showlegend: false,
                autosize: true
            };
            
            // Crystal Toolkit配置 - 隐藏默认工具栏，使用自定义工具栏
            const config = {
                displayModeBar: false, // 隐藏默认工具栏
                displaylogo: false,
                responsive: true,
                scrollZoom: false, // 禁用默认滚轮缩放，使用自定义处理
                staticPlot: false,
                fillFrame: true,
                frameMargins: 0,
                autosize: true
            };
            
            // 渲染到容器
            console.log('🎨 开始Plotly渲染...', this.container);
            console.log('📏 容器尺寸:', {
                width: this.container.offsetWidth,
                height: this.container.offsetHeight,
                clientWidth: this.container.clientWidth,
                clientHeight: this.container.clientHeight
            });
            
            Plotly.newPlot(this.container, plotData, layout, config);
            console.log('🎯 Plotly渲染完成');
            
            // 添加自定义滚轮事件处理，只影响相机距离，不改变原子大小
            this.container.addEventListener('wheel', (event) => {
                event.preventDefault();
                
                // 获取当前相机位置
                const currentLayout = this.container.layout;
                if (currentLayout && currentLayout.scene && currentLayout.scene.camera) {
                    const camera = currentLayout.scene.camera;
                    const center = camera.center || { x: 0, y: 0, z: 0 };
                    const eye = camera.eye;
                    
                    // 计算当前相机到中心的向量
                    const direction = {
                        x: eye.x - center.x,
                        y: eye.y - center.y,
                        z: eye.z - center.z
                    };
                    
                    // 计算当前距离
                    const currentDistance = Math.sqrt(
                        direction.x * direction.x + 
                        direction.y * direction.y + 
                        direction.z * direction.z
                    );
                    
                    // 计算缩放因子（滚轮向上放大，向下缩小）
                    const zoomFactor = event.deltaY > 0 ? 1.1 : 0.9;
                    const newDistance = currentDistance * zoomFactor;
                    
                    // 限制距离范围
                    const minDistance = 2;
                    const maxDistance = 50;
                    const clampedDistance = Math.max(minDistance, Math.min(maxDistance, newDistance));
                    
                    // 计算新的相机位置
                    const scale = clampedDistance / currentDistance;
                    const newEye = {
                        x: center.x + direction.x * scale,
                        y: center.y + direction.y * scale,
                        z: center.z + direction.z * scale
                    };
                    
                    // 更新相机位置
                    Plotly.relayout(this.container, {
                        'scene.camera.eye': newEye
                    });
                }
            });
            
            // 绑定Plotly事件监听器（移除自动scaleFactor更新，滚轮缩放只影响相机距离）
            this.container.on('plotly_relayout', (eventData) => {
                // 这里可以添加其他需要监听的布局变化事件
                // 但不再自动更新scaleFactor，保持原子大小独立于相机距离
            });
            
            // 存储最佳相机设置供resetCamera使用
            this.optimalCamera = optimalCamera;
            
            // 绑定控件
            this.bindControls();
            
            // 显示和绑定自定义工具栏
            this.setupCustomToolbar();
            
            // 一次性调整Canvas大小以匹配容器（不重置相机位置）
            setTimeout(() => {
                console.log('📐 最终调整Plotly图表大小...');
                
                // 获取容器实际尺寸
                const containerRect = this.container.getBoundingClientRect();
                console.log('📦 容器实际尺寸:', containerRect);
                
                // 只调整尺寸，不重置相机位置
                Plotly.relayout(this.container, {
                    width: containerRect.width,
                    height: containerRect.height
                });
                
                // 检查Canvas尺寸
                const canvas = this.container.querySelector('canvas');
                if (canvas) {
                    console.log('🎨 Canvas最终尺寸:', {
                        width: canvas.width,
                        height: canvas.height,
                        clientWidth: canvas.clientWidth,
                        clientHeight: canvas.clientHeight
                    });
                }
                
                console.log('✅ 图表大小调整完成，保持用户视角');
            }, 200);
            
            console.log('✅ Crystal Toolkit结构加载完成');
            
            return {
                success: true,
                atomCount: structure.sites.length,
                formula: structure.formula
            };
            
        } catch (error) {
            console.error('❌ Crystal Toolkit渲染失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    generatePlotlyData(structure) {
        console.log('🏗️ 开始生成Plotly数据，结构:', structure);
        const traces = [];
        
        // 1. 原子渲染（如果启用）
        if (this.renderParams.showAtoms) {
            console.log('⚛️ 开始处理原子...');
            const atomsByElement = this.groupAtomsByElement(structure);
            console.log('📊 按元素分组的原子:', atomsByElement);
            
            Object.entries(atomsByElement).forEach(([element, atoms]) => {
                // 安全检查原子数组
                if (!Array.isArray(atoms) || atoms.length === 0) {
                    console.warn(`⚠️ 元素 ${element} 的原子数据无效:`, atoms);
                    return;
                }
                
                const color = this.getElementColor(element);
                const radius = this.getElementRadius(element);
                
                // 过滤有效的原子数据
                const validAtoms = atoms.filter(atom => {
                    return atom && atom.cartesian && Array.isArray(atom.cartesian) && atom.cartesian.length >= 3;
                });
                
                if (validAtoms.length === 0) {
                    console.warn(`⚠️ 元素 ${element} 没有有效的原子数据`);
                    return;
                }
                
                console.log(`🎨 处理元素 ${element}:`, {
                    count: validAtoms.length,
                    color: color,
                    radius: radius,
                    positions: validAtoms.map(a => a.cartesian)
                });
                
                const trace = {
                    type: 'scatter3d',
                    mode: 'markers',
                    name: element,
                    x: validAtoms.map(atom => atom.cartesian[0]),
                    y: validAtoms.map(atom => atom.cartesian[1]),
                    z: validAtoms.map(atom => atom.cartesian[2]),
                    marker: {
                        size: Math.max(5, radius * 20 * this.renderParams.scaleFactor), // 动态调整原子大小
                        color: color,
                        opacity: 0.9,
                        line: {
                            color: '#333333',
                            width: 1
                        }
                    },
                    hovertemplate: `<b>${element}</b><br>` +
                                 'Position: (%{x:.3f}, %{y:.3f}, %{z:.3f})<extra></extra>',
                    showlegend: false
                };
                
                console.log(`✅ ${element} trace创建:`, trace);
                traces.push(trace);
            });
        }
        
        // 2. 化学键渲染（如果启用）
        if (this.renderParams.showBonds && this.renderParams.includeBonds) {
            const bonds = this.calculateBonds(structure);
            if (bonds.length > 0) {
                const bondTrace = this.createBondTrace(bonds);
                traces.push(bondTrace);
            }
        }
        
        // 3. 晶胞渲染（如果启用）
        if (this.renderParams.showUnitCell) {
            const unitCellTrace = this.createUnitCellTrace(structure.lattice);
            traces.push(unitCellTrace);
        }
        
        return traces;
    }
    
    // 调整大小以匹配容器
    resizeToContainer(resetCamera = true) {
        if (!this.container) return;
        
        console.log('📐 调整大小以匹配容器...');
        
        const containerRect = this.container.getBoundingClientRect();
        const isFullscreen = !!document.fullscreenElement;
        
        // 全屏时使用屏幕尺寸
        const targetWidth = isFullscreen ? window.innerWidth : containerRect.width;
        const targetHeight = isFullscreen ? window.innerHeight : containerRect.height;
        
        console.log(`📊 尺寸设置: ${targetWidth}x${targetHeight} (全屏: ${isFullscreen})`);
        
        const layoutUpdate = {
            width: targetWidth,
            height: targetHeight,
            autosize: !isFullscreen // 非全屏时启用自动调整
        };
        
        // 只在需要时重置相机
        if (resetCamera) {
            layoutUpdate['scene.camera'] = {
                eye: { x: 1.5, y: 1.5, z: 1.5 },
                center: { x: 0, y: 0, z: 0 }
            };
        }
        
        // 一次性调整布局，避免重复调用
        Plotly.relayout(this.container, layoutUpdate);
    }
    
    // 更新渲染（参数改变时调用）
    updateRender(preserveCamera = false) {
        if (!this.currentStructure) return;
        
        console.log('🔄 更新渲染参数:', this.renderParams);
        console.log('🎥 preserveCamera模式:', preserveCamera);
        
        // 重新生成数据
        const plotData = this.generatePlotlyData(this.currentStructure);
        
        // 获取当前相机位置（如果需要保持）
        let currentCamera = null;
        if (preserveCamera) {
            // 尝试多种方法获取当前相机状态
            try {
                // 方法1: 从_fullLayout获取
                if (this.container._fullLayout && this.container._fullLayout.scene && this.container._fullLayout.scene.camera) {
                    const camera = this.container._fullLayout.scene.camera;
                    if (camera.center && camera.eye && camera.up) {
                        currentCamera = {
                            center: {...camera.center},
                            eye: {...camera.eye},
                            up: {...camera.up}
                        };
                        console.log('🎥 从_fullLayout成功获取相机位置:', currentCamera);
                    }
                }
                
                // 方法2: 从layout获取
                if (!currentCamera && this.container.layout && this.container.layout.scene && this.container.layout.scene.camera) {
                    const camera = this.container.layout.scene.camera;
                    if (camera.center && camera.eye && camera.up) {
                        currentCamera = {
                            center: {...camera.center},
                            eye: {...camera.eye},
                            up: {...camera.up}
                        };
                        console.log('🎥 从layout成功获取相机位置:', currentCamera);
                    }
                }
                
                // 方法3: 使用Plotly的relayout获取当前状态
                if (!currentCamera) {
                    try {
                        const plotDiv = this.container;
                        if (plotDiv && plotDiv.data && plotDiv.layout) {
                            // 尝试从当前显示的图表获取相机信息
                            const currentLayout = plotDiv.layout;
                            if (currentLayout.scene && currentLayout.scene.camera) {
                                const camera = currentLayout.scene.camera;
                                if (camera.center && camera.eye && camera.up) {
                                    currentCamera = {
                                        center: {...camera.center},
                                        eye: {...camera.eye},
                                        up: {...camera.up}
                                    };
                                    console.log('🎥 从当前布局成功获取相机位置:', currentCamera);
                                }
                            }
                        }
                    } catch (e) {
                        console.warn('🎥 从当前布局获取相机失败:', e);
                    }
                }
                
                // 如果所有方法都失败，不设置相机（保持当前状态）
                if (!currentCamera) {
                    console.warn('🎥 无法获取当前相机位置，将跳过相机设置以保持当前视角');
                    // 不使用optimalCamera，这样可以避免重置视角
                }
                
            } catch (e) {
                console.error('🎥 获取相机位置时发生错误:', e);
                currentCamera = null; // 确保不会意外重置
            }
        }
        
        // 获取容器尺寸
        const containerRect = this.container.getBoundingClientRect();
        
        const layoutUpdate = {
            width: containerRect.width,
            height: containerRect.height,
            margin: { l: 0, r: 0, b: 0, t: 0, pad: 0 },
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            scene: {
                xaxis: { 
                    title: 'X (Å)', 
                    showgrid: false,
                    showline: false,
                    zeroline: false,
                    showticklabels: false
                },
                yaxis: { 
                    title: 'Y (Å)', 
                    showgrid: false,
                    showline: false,
                    zeroline: false,
                    showticklabels: false
                },
                zaxis: { 
                    title: 'Z (Å)', 
                    showgrid: false,
                    showline: false,
                    zeroline: false,
                    showticklabels: false
                },
                aspectmode: 'cube',
                bgcolor: 'white',
                dragmode: 'orbit'
            },
            showlegend: false
        };
        
        // 如果需要保持相机位置且有相机信息，添加到布局中
        if (preserveCamera && currentCamera) {
            layoutUpdate.scene.camera = currentCamera;
            console.log('🎥 保持相机位置模式，设置相机:', currentCamera);
        } else if (preserveCamera && !currentCamera) {
            console.log('🎥 保持相机模式但无法获取相机位置，将不设置相机以保持当前视角');
        }
        
        // 如果需要保持相机且无法获取相机信息，使用更温和的更新方式
        if (preserveCamera && !currentCamera) {
            console.log('🎥 保持相机模式但无法获取相机位置，使用restyle更新数据');
            // 只更新数据，不更新布局，这样可以保持当前相机位置
            Plotly.restyle(this.container, plotData).then(() => {
                console.log('🎥 数据更新完成，相机位置保持不变');
            }).catch(e => {
                console.error('🎥 Plotly.restyle失败:', e);
            });
        } else {
            // 使用react更新图表
            Plotly.react(this.container, plotData, layoutUpdate).then(() => {
                // 只有在成功获取到相机信息时才进行后续设置
                if (preserveCamera && currentCamera) {
                    console.log('🎥 React完成后再次确认相机位置');
                    setTimeout(() => {
                        Plotly.relayout(this.container, {
                            'scene.camera': currentCamera
                        }).then(() => {
                            console.log('🎥 最终相机位置设置成功');
                        }).catch(e => {
                            console.error('🎥 最终相机位置设置失败:', e);
                        });
                    }, 50);
                }
            }).catch(e => {
                console.error('🎥 Plotly.react失败:', e);
            });
        }

    }
    
    // 辅助方法
    groupAtomsByElement(structure) {
        const atomsByElement = {};
        
        // 安全检查结构数据
        if (!structure || !structure.sites || !Array.isArray(structure.sites)) {
            console.error('❌ 结构数据无效:', structure);
            return atomsByElement;
        }
        
        structure.sites.forEach((site, index) => {
            // 检查site数据
            if (!site || !site.species || !Array.isArray(site.species)) {
                console.warn(`⚠️ 第${index}个原子位点数据无效:`, site);
                return;
            }
            
            // 检查坐标数据
            if (!site.coords || !Array.isArray(site.coords) || site.coords.length < 3) {
                console.warn(`⚠️ 第${index}个原子位点坐标无效:`, site.coords);
                return;
            }
            
            site.species.forEach(spec => {
                // 检查物种数据
                if (!spec || !spec.element) {
                    console.warn(`⚠️ 第${index}个原子位点的物种数据无效:`, spec);
                    return;
                }
                
                // 清理元素名称：移除离子符号、数字等
                const element = spec.element.replace(/[0-9+\-]/g, '');
                
                if (!atomsByElement[element]) {
                    atomsByElement[element] = [];
                }
                
                const cartesian = this.fractionalToCartesian(site.coords, structure.lattice);
                
                atomsByElement[element].push({
                    index: index,
                    coords: site.coords,
                    cartesian: cartesian,
                    occupancy: spec.occu || 1.0
                });
            });
        });
        
        return atomsByElement;
    }
    
    calculateBonds(structure) {
        const bonds = [];
        
        // 计算所有原子间距离
        const distances = [];
        const positions = [];
        
        for (let i = 0; i < structure.sites.length; i++) {
            positions[i] = this.fractionalToCartesian(structure.sites[i].coords, structure.lattice);
        }
        
        for (let i = 0; i < positions.length; i++) {
            for (let j = i + 1; j < positions.length; j++) {
                const distance = Math.sqrt(
                    Math.pow(positions[j][0] - positions[i][0], 2) +
                    Math.pow(positions[j][1] - positions[i][1], 2) +
                    Math.pow(positions[j][2] - positions[i][2], 2)
                );
                distances.push(distance);
            }
        }
        
        if (distances.length === 0) return bonds;
        
        // 动态计算化学键阈值
        distances.sort((a, b) => a - b);
        const minDistance = distances[0];
        const avgDistance = distances.reduce((sum, d) => sum + d, 0) / distances.length;
        
        // 使用最小距离和平均距离的加权平均作为阈值
        let maxBondDistance = (minDistance * 0.3 + avgDistance * 0.7) * 1.2;
        
        // 确保阈值在合理范围内
        maxBondDistance = Math.max(1.0, Math.min(maxBondDistance, 50.0));
        
        console.log(`🔗 动态化学键阈值: ${maxBondDistance.toFixed(2)} Å (最小距离: ${minDistance.toFixed(2)} Å, 平均距离: ${avgDistance.toFixed(2)} Å)`);
        
        // 生成化学键
        for (let i = 0; i < positions.length; i++) {
            for (let j = i + 1; j < positions.length; j++) {
                const distance = Math.sqrt(
                    Math.pow(positions[j][0] - positions[i][0], 2) +
                    Math.pow(positions[j][1] - positions[i][1], 2) +
                    Math.pow(positions[j][2] - positions[i][2], 2)
                );
                
                if (distance < maxBondDistance) {
                    bonds.push({
                        start: positions[i],
                        end: positions[j],
                        distance: distance
                    });
                }
            }
        }
        
        console.log(`🔗 生成了 ${bonds.length} 个化学键`);
        return bonds;
    }
    
    createBondTrace(bonds) {
        const x = [], y = [], z = [];
        
        bonds.forEach(bond => {
            x.push(bond.start[0], bond.end[0], null);
            y.push(bond.start[1], bond.end[1], null);
            z.push(bond.start[2], bond.end[2], null);
        });
        
        return {
            type: 'scatter3d',
            mode: 'lines',
            x: x, y: y, z: z,
            line: {
                color: '#666666',
                width: Math.max(1, 4 * this.renderParams.scaleFactor)
            },
            hoverinfo: 'skip',
            showlegend: false
        };
    }
    
    createUnitCellTrace(lattice) {
        // 兼容两种格式：lattice.matrix 或直接是矩阵数组
        const matrix = lattice.matrix || lattice;
        const edges = this.getUnitCellEdges(matrix);
        
        const x = [], y = [], z = [];
        edges.forEach(edge => {
            x.push(edge[0][0], edge[1][0], null);
            y.push(edge[0][1], edge[1][1], null);
            z.push(edge[0][2], edge[1][2], null);
        });
        
        return {
            type: 'scatter3d',
            mode: 'lines',
            x: x, y: y, z: z,
            line: {
                color: '#000000',
                width: Math.max(1, 2 * this.renderParams.scaleFactor)
            },
            hoverinfo: 'skip',
            showlegend: false
        };
    }
    
    getUnitCellEdges(matrix) {
        const origin = [0, 0, 0];
        const a = matrix[0], b = matrix[1], c = matrix[2];
        
        return [
            [origin, a], [origin, b], [origin, c],
            [a, [a[0] + b[0], a[1] + b[1], a[2] + b[2]]],
            [a, [a[0] + c[0], a[1] + c[1], a[2] + c[2]]],
            [b, [b[0] + a[0], b[1] + a[1], b[2] + a[2]]],
            [b, [b[0] + c[0], b[1] + c[1], b[2] + c[2]]],
            [c, [c[0] + a[0], c[1] + a[1], c[2] + a[2]]],
            [c, [c[0] + b[0], c[1] + b[1], c[2] + b[2]]],
            [[a[0] + b[0], a[1] + b[1], a[2] + b[2]], 
             [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]]],
            [[a[0] + c[0], a[1] + c[1], a[2] + c[2]], 
             [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]]],
            [[b[0] + c[0], b[1] + c[1], b[2] + c[2]], 
             [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]]]
        ];
    }
    
    fractionalToCartesian(fracCoords, lattice) {
        // 安全检查
        if (!lattice) {
            return [0, 0, 0];
        }
        
        // 兼容两种格式：lattice.matrix 或直接是矩阵数组
        const matrix = lattice.matrix || lattice;
        
        // 检查矩阵结构
        if (!Array.isArray(matrix) || matrix.length < 3) {
            return [0, 0, 0];
        }
        
        // 检查每一行
        for (let i = 0; i < 3; i++) {
            if (!Array.isArray(matrix[i]) || matrix[i].length < 3) {
                return [0, 0, 0];
            }
        }
        
        // 检查分数坐标
        if (!Array.isArray(fracCoords) || fracCoords.length < 3) {
            console.error('❌ 分数坐标无效:', fracCoords);
            return [0, 0, 0];
        }
        
        // 分数坐标转换计算
        
        const cartesian = [
            fracCoords[0] * matrix[0][0] + fracCoords[1] * matrix[1][0] + fracCoords[2] * matrix[2][0],
            fracCoords[0] * matrix[0][1] + fracCoords[1] * matrix[1][1] + fracCoords[2] * matrix[2][1],
            fracCoords[0] * matrix[0][2] + fracCoords[1] * matrix[1][2] + fracCoords[2] * matrix[2][2]
        ];
        
        console.log('📍 笛卡尔坐标:', cartesian);
        return cartesian;
    }
    
    getElementColor(element) {
        // Crystal Toolkit/Materials Project标准CPK颜色 (CSS hex格式)
        const cpkColors = {
            'H': '#FFFFFF',   // 白色
            'He': '#D9FFFF',  // 淡青色
            'Li': '#CC80FF',  // 淡紫色
            'Be': '#C2FF00',  // 黄绿色
            'B': '#FFB5B5',   // 粉红色
            'C': '#909090',   // 灰色
            'N': '#3050F8',   // 蓝色
            'O': '#FF0D0D',   // 红色
            'F': '#90E050',   // 绿色
            'Ne': '#B3E3F5',  // 淡蓝色
            'Na': '#AB5CF2',  // 紫色
            'Mg': '#8AFF00',  // 亮绿色
            'Al': '#BFA6A6',  // 灰色
            'Si': '#F0C8A0',  // 黄褐色
            'P': '#FF8000',   // 橙色
            'S': '#FFFF30',   // 黄色
            'Cl': '#1FF01F',  // 绿色
            'Ar': '#80D1E3',  // 淡蓝色
            'K': '#8F40D4',   // 深紫色
            'Ca': '#3DFF00',  // 绿色
            'Sc': '#E6E6E6',  // 浅灰色
            'Ti': '#BFC2C7',  // 银灰色
            'V': '#A6A6AB',   // 灰色
            'Cr': '#8A99C7',  // 蓝灰色
            'Mn': '#9C7AC7',  // 紫灰色
            'Fe': '#E06633',  // 橙红色
            'Co': '#F090A0',  // 粉红色
            'Ni': '#50D050',  // 绿色
            'Cu': '#C88033',  // 铜色
            'Zn': '#7D80B0',  // 蓝灰色
            'Ga': '#C28F8F',  // 粉色
            'Ge': '#668F8F',  // 青色
            'As': '#BD80E3',  // 紫色
            'Se': '#FFA100',  // 橙色
            'Br': '#A62929',  // 棕红色
            'Kr': '#5CB8D1',  // 蓝色
            'Rb': '#702EB0',  // 紫色
            'Sr': '#00FF00',  // 绿色
            'Y': '#94FFFF',   // 青色
            'Zr': '#94E0E0',  // 青色
            'Nb': '#73C2C9',  // 蓝绿色
            'Mo': '#54B5B5',  // 青色
            'Tc': '#3B9E9E',  // 青色
            'Ru': '#248F8F',  // 青色
            'Rh': '#0A7D8C',  // 青色
            'Pd': '#006985',  // 蓝色
            'Ag': '#C0C0C0',  // 银色
            'Cd': '#FFD98F',  // 黄色
            'In': '#A67573',  // 棕色
            'Sn': '#668080',  // 灰色
            'Sb': '#9E63B5',  // 紫色
            'Te': '#D47A00',  // 橙色
            'I': '#940094',   // 紫色
            'Xe': '#429EB0',  // 蓝色
            'Cs': '#57178F',  // 深紫色
            'Ba': '#00C900',  // 绿色
            'La': '#70D4FF',  // 淡蓝色
            'Ce': '#FFFFC7',  // 淡黄色
            'Pr': '#D9FFC7',  // 淡绿色
            'Nd': '#C7FFC7',  // 淡绿色
            'Pm': '#A3FFC7',  // 淡绿色
            'Sm': '#8FFFC7',  // 淡绿色
            'Eu': '#61FFC7',  // 淡绿色
            'Gd': '#45FFC7',  // 淡绿色
            'Tb': '#30FFC7',  // 淡绿色
            'Dy': '#1FFFC7',  // 淡绿色
            'Ho': '#00FF9C',  // 绿色
            'Er': '#00E675',  // 绿色
            'Tm': '#00D452',  // 绿色
            'Yb': '#00BF38',  // 绿色
            'Lu': '#00AB24',  // 绿色
            'Hf': '#4DC2FF',  // 淡蓝色
            'Ta': '#4DA6FF',  // 蓝色
            'W': '#2194D6',   // 蓝色
            'Re': '#267DAB',  // 蓝色
            'Os': '#266696',  // 蓝色
            'Ir': '#175487',  // 蓝色
            'Pt': '#D0D0E0',  // 银灰色
            'Au': '#FFD123',  // 金色
            'Hg': '#B8B8D0',  // 银色
            'Tl': '#A6544D',  // 棕色
            'Pb': '#575961',  // 深灰色
            'Bi': '#9E4FB5',  // 紫色
            'Po': '#AB5C00',  // 棕色
            'At': '#754F45',  // 棕色
            'Rn': '#428296',  // 蓝色
            'Fr': '#420066',  // 深紫色
            'Ra': '#007D00',  // 绿色
            'Ac': '#70ABFA',  // 淡蓝色
            'Th': '#00BAFF',  // 青色
            'Pa': '#00A1FF',  // 蓝色
            'U': '#008FFF',   // 蓝色
            'Np': '#0080FF',  // 蓝色
            'Pu': '#006BFF',  // 蓝色
            'Am': '#545CF2',  // 蓝紫色
            'Cm': '#785CE3',  // 紫色
            'Bk': '#8A4FE3',  // 紫色
            'Cf': '#A136D4',  // 紫色
            'Es': '#B31FD4',  // 紫色
            'Fm': '#B31FBA',  // 紫色
            'Md': '#B30DA6',  // 紫色
            'No': '#BD0D87',  // 紫色
            'Lr': '#C70066',  // 紫红色
        };
        
        // 清理元素符号（去除数字和符号）
        const cleanElement = element.replace(/[0-9+\-]/g, '');
        
        return cpkColors[cleanElement] || '#808080'; // 默认灰色
    }
    
    getElementRadius(element) {
        const radii = {
            'H': 1.20, 'Li': 1.82, 'Be': 1.53, 'B': 1.92, 'C': 1.70,
            'N': 1.55, 'O': 1.52, 'F': 1.47, 'Na': 2.27, 'Mg': 1.73,
            'Al': 1.84, 'Si': 2.10, 'P': 1.80, 'S': 1.80, 'Cl': 1.75,
            'K': 2.75, 'Ca': 2.31, 'Fe': 2.00, 'Cu': 1.40, 'Zn': 1.39
        };
        return radii[element] || 1.50;
    }

    // 计算结构的边界框
    calculateStructureBounds(structure) {
        if (!structure.sites || structure.sites.length === 0) {
            return {
                min: { x: -5, y: -5, z: -5 },
                max: { x: 5, y: 5, z: 5 },
                center: { x: 0, y: 0, z: 0 },
                size: { x: 10, y: 10, z: 10 }
            };
        }

        let minX = Infinity, minY = Infinity, minZ = Infinity;
        let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

        // 遍历所有原子位置
         structure.sites.forEach(site => {
             const cartesian = this.fractionalToCartesian(site.abc, structure.lattice);
             minX = Math.min(minX, cartesian[0]);
             minY = Math.min(minY, cartesian[1]);
             minZ = Math.min(minZ, cartesian[2]);
             maxX = Math.max(maxX, cartesian[0]);
             maxY = Math.max(maxY, cartesian[1]);
             maxZ = Math.max(maxZ, cartesian[2]);
         });

        const center = {
            x: (minX + maxX) / 2,
            y: (minY + maxY) / 2,
            z: (minZ + maxZ) / 2
        };

        const size = {
            x: maxX - minX,
            y: maxY - minY,
            z: maxZ - minZ
        };

        console.log('📏 结构边界框:', { min: {x: minX, y: minY, z: minZ}, max: {x: maxX, y: maxY, z: maxZ}, center, size });

        return {
            min: { x: minX, y: minY, z: minZ },
            max: { x: maxX, y: maxY, z: maxZ },
            center,
            size
        };
    }

    // 根据结构边界框计算最佳相机位置
    calculateOptimalCamera(bounds) {
        const { center, size } = bounds;
        
        // 计算结构的最大尺寸
        const maxSize = Math.max(size.x, size.y, size.z);
        
        // 获取canvas的实际尺寸
        const canvasWidth = this.container ? this.container.offsetWidth : 800;
        const canvasHeight = this.container ? this.container.offsetHeight : 600;
        const canvasSize = Math.min(canvasWidth, canvasHeight);
        
        // 根据canvas大小动态调整距离系数
        // canvas越大，可以让结构显示得越大（距离系数越小）
        let distanceCoeff = 0.5; // 基础系数
        if (canvasSize > 600) {
            distanceCoeff = 0.3; // 大canvas使用更小的系数
        } else if (canvasSize < 400) {
            distanceCoeff = 0.7; // 小canvas使用稍大的系数避免过度放大
        }
        
        const distance = Math.max(maxSize * distanceCoeff, 2);
        
        // 根据canvas尺寸动态调整相机距离倍数
        let cameraDistanceMultiplier = 1.0;
        if (canvasSize > 600) {
            cameraDistanceMultiplier = 0.8; // 大canvas让结构更大
        } else if (canvasSize < 400) {
            cameraDistanceMultiplier = 1.3; // 小canvas保持适当距离
        }
        
        const cameraDistance = distance * cameraDistanceMultiplier;
        
        const camera = {
            eye: {
                x: center.x + cameraDistance,
                y: center.y + cameraDistance,
                z: center.z + cameraDistance
            },
            center: {
                x: center.x,
                y: center.y,
                z: center.z
            },
            up: { x: 0, y: 0, z: 1 } // 确保Z轴向上
        };
        
        console.log('📷 动态相机设置:', {
            camera,
            结构尺寸: maxSize,
            canvas尺寸: `${canvasWidth}x${canvasHeight}`,
            距离系数: distanceCoeff,
            距离倍数: cameraDistanceMultiplier,
            最终距离: cameraDistance
        });
        return camera;
    }
}

// 全局导出
window.CrystalToolkitRenderer = CrystalToolkitRenderer;