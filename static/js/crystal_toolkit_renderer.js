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
            includeBonds: true,
            showPolyhedra: true,
            polyhedronOpacity: 0.3
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
                        this.createFullscreenControls(); // 创建全屏控制面板
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
                    this.removeFullscreenControls(); // 移除全屏控制面板
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
    
    // 创建全屏控制面板
    createFullscreenControls() {
        // 检查是否已存在控制面板
        if (document.getElementById('fullscreenRenderControls')) {
            return;
        }
        
        // 确保只在全屏模式下创建
        if (!document.fullscreenElement) {
            console.log('⚠️ 非全屏模式，跳过创建控制面板');
            return;
        }
        
        const previewCard = this.container.closest('.card');
        if (!previewCard) return;
        
        // 创建控制面板容器
        const controlsPanel = document.createElement('div');
        controlsPanel.id = 'fullscreenRenderControls';
        controlsPanel.style.cssText = `
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1000;
            min-width: 600px;
            max-width: 80vw;
        `;
        
        // 创建控制面板内容
        controlsPanel.innerHTML = `
            <div style="display: flex; gap: 30px; align-items: center; justify-content: center;">
                <!-- 球体大小控制 -->
                <div style="flex: 1; min-width: 200px;">
                    <label style="display: block; font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 8px;">
                        <i class="bi bi-circle-fill" style="color: #3b82f6;"></i> 球体大小
                    </label>
                    <input type="range" id="fullscreenScaleFactor" 
                           min="0.3" max="3" step="0.1" value="${this.renderParams.scaleFactor}"
                           style="width: 100%; margin-bottom: 4px;">
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #6b7280;">
                        <span>小</span>
                        <span>当前: <span id="fullscreenScaleValue" style="font-weight: 600;">${this.renderParams.scaleFactor.toFixed(1)}</span></span>
                        <span>大</span>
                    </div>
                </div>
                
                <!-- 显示选项 -->
                <div style="flex: 1; min-width: 250px;">
                    <label style="display: block; font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 8px;">
                        <i class="bi bi-eye" style="color: #10b981;"></i> 显示选项
                    </label>
                    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="fullscreenShowAtoms" ${this.renderParams.showAtoms ? 'checked' : ''}>
                            <i class="bi bi-circle-fill" style="color: #3b82f6;"></i> 原子
                        </label>
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="fullscreenShowBonds" ${this.renderParams.showBonds ? 'checked' : ''}>
                            <i class="bi bi-dash-lg" style="color: #6b7280;"></i> 化学键
                        </label>
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="fullscreenShowUnitCell" ${this.renderParams.showUnitCell ? 'checked' : ''}>
                            <i class="bi bi-bounding-box" style="color: #06b6d4;"></i> 晶胞
                        </label>
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="fullscreenShowPolyhedra" ${this.renderParams.showPolyhedra ? 'checked' : ''}>
                            <i class="bi bi-hexagon" style="color: #8b5cf6;"></i> 多面体
                        </label>
                    </div>
                </div>
                
                <!-- 多面体透明度控制 -->
                <div style="flex: 1; min-width: 200px; display: ${this.renderParams.showPolyhedra ? 'block' : 'none'};" id="fullscreenPolyhedronOpacityControl">
                    <label style="display: block; font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 8px;">
                        <i class="bi bi-transparency" style="color: #8b5cf6;"></i> 多面体透明度
                    </label>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <input type="range" id="fullscreenPolyhedronOpacity" min="0.1" max="1.0" step="0.1" value="${this.renderParams.polyhedronOpacity}" style="flex: 1; height: 6px; background: linear-gradient(to right, #8b5cf6, #a78bfa); border-radius: 3px; outline: none;">
                        <span id="fullscreenPolyhedronOpacityValue" style="font-size: 11px; font-weight: 600; color: #8b5cf6; min-width: 30px;">${this.renderParams.polyhedronOpacity.toFixed(1)}</span>
                    </div>
                </div>
                
                <!-- 视角控制 -->
                <div style="flex: 0 0 auto;">
                    <label style="display: block; font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 8px;">
                        <i class="bi bi-arrows-move" style="color: #f59e0b;"></i> 视角控制
                    </label>
                    <div style="display: flex; gap: 8px;">
                        <button id="fullscreenResetBtn" 
                                style="padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; font-size: 12px;"
                                title="重置视角">
                            <i class="bi bi-house-fill"></i>
                        </button>
                        <button id="fullscreenSnapshotBtn" 
                                style="padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; font-size: 12px;"
                                title="保存截图">
                            <i class="bi bi-camera-fill"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // 添加到全屏容器
        previewCard.appendChild(controlsPanel);
        
        // 绑定事件
        this.bindFullscreenControls();
        
        console.log('🎛️ 全屏控制面板已创建');
    }
    
    // 移除全屏控制面板
    removeFullscreenControls() {
        const controlsPanel = document.getElementById('fullscreenRenderControls');
        if (controlsPanel) {
            controlsPanel.remove();
            console.log('🗑️ 全屏控制面板已移除');
        }
    }
    
    // 绑定全屏控制面板事件
    bindFullscreenControls() {
        // 球体大小控制
        const scaleSlider = document.getElementById('fullscreenScaleFactor');
        const scaleValue = document.getElementById('fullscreenScaleValue');
        if (scaleSlider && scaleValue) {
            scaleSlider.addEventListener('input', (e) => {
                this.renderParams.scaleFactor = parseFloat(e.target.value);
                scaleValue.textContent = parseFloat(e.target.value).toFixed(1);
                
                // 同步更新原有控制面板的值
                const originalScaleSlider = document.getElementById('scaleFactor');
                const originalScaleValue = document.getElementById('scaleValue');
                if (originalScaleSlider) {
                    originalScaleSlider.value = e.target.value;
                }
                if (originalScaleValue) {
                    originalScaleValue.textContent = parseFloat(e.target.value).toFixed(1);
                }
                
                this.updateRender(true);
            });
        }
        
        // 显示选项
        const showAtoms = document.getElementById('fullscreenShowAtoms');
        const showBonds = document.getElementById('fullscreenShowBonds');
        const showUnitCell = document.getElementById('fullscreenShowUnitCell');
        const showPolyhedra = document.getElementById('fullscreenShowPolyhedra');
        
        if (showAtoms) {
            showAtoms.addEventListener('change', (e) => {
                this.renderParams.showAtoms = e.target.checked;
                
                // 同步更新原有控制面板的值
                const originalShowAtoms = document.getElementById('showAtoms');
                if (originalShowAtoms) {
                    originalShowAtoms.checked = e.target.checked;
                }
                
                this.updateRender(true);
            });
        }
        
        if (showBonds) {
            showBonds.addEventListener('change', (e) => {
                this.renderParams.showBonds = e.target.checked;
                
                // 同步更新原有控制面板的值
                const originalShowBonds = document.getElementById('showBonds');
                if (originalShowBonds) {
                    originalShowBonds.checked = e.target.checked;
                }
                
                this.updateRender(true);
            });
        }
        
        if (showUnitCell) {
            showUnitCell.addEventListener('change', (e) => {
                this.renderParams.showUnitCell = e.target.checked;
                
                // 同步更新原有控制面板的值
                const originalShowUnitCell = document.getElementById('showUnitCell');
                if (originalShowUnitCell) {
                    originalShowUnitCell.checked = e.target.checked;
                }
                
                this.updateRender(true);
            });
        }
        
        if (showPolyhedra) {
            showPolyhedra.addEventListener('change', (e) => {
                this.renderParams.showPolyhedra = e.target.checked;
                
                // 显示/隐藏透明度控制
                const opacityControl = document.getElementById('fullscreenPolyhedronOpacityControl');
                if (opacityControl) {
                    opacityControl.style.display = e.target.checked ? 'block' : 'none';
                }
                
                // 同步更新原有控制面板的值
                const originalShowPolyhedra = document.getElementById('showPolyhedra');
                if (originalShowPolyhedra) {
                    originalShowPolyhedra.checked = e.target.checked;
                }
                
                this.updateRender(true);
            });
        }
        
        // 多面体透明度控制
        const polyhedronOpacity = document.getElementById('fullscreenPolyhedronOpacity');
        const polyhedronOpacityValue = document.getElementById('fullscreenPolyhedronOpacityValue');
        if (polyhedronOpacity && polyhedronOpacityValue) {
            polyhedronOpacity.addEventListener('input', (e) => {
                this.renderParams.polyhedronOpacity = parseFloat(e.target.value);
                polyhedronOpacityValue.textContent = parseFloat(e.target.value).toFixed(1);
                
                // 同步更新原有控制面板的值
                const originalPolyhedronOpacity = document.getElementById('polyhedronOpacity');
                const originalPolyhedronOpacityValue = document.getElementById('polyhedronOpacityValue');
                if (originalPolyhedronOpacity) {
                    originalPolyhedronOpacity.value = e.target.value;
                }
                if (originalPolyhedronOpacityValue) {
                    originalPolyhedronOpacityValue.textContent = parseFloat(e.target.value).toFixed(1);
                }
                
                this.updateRender(true);
            });
        }
        
        // 视角控制按钮
        const resetBtn = document.getElementById('fullscreenResetBtn');
        const snapshotBtn = document.getElementById('fullscreenSnapshotBtn');
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetCamera();
            });
        }
        
        if (snapshotBtn) {
            snapshotBtn.addEventListener('click', () => {
                this.takeSnapshot();
            });
        }
        
        console.log('🔗 全屏控制面板事件已绑定');
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
                
                // 同步更新全屏控制面板的值
                const fullscreenScaleSlider = document.getElementById('fullscreenScaleFactor');
                const fullscreenScaleValue = document.getElementById('fullscreenScaleValue');
                if (fullscreenScaleSlider) {
                    fullscreenScaleSlider.value = e.target.value;
                }
                if (fullscreenScaleValue) {
                    fullscreenScaleValue.textContent = parseFloat(e.target.value).toFixed(1);
                }
                
                this.updateRender(true); // 保持相机位置，不影响视角
            });
        }
        
        // 显示选项
        const showAtoms = document.getElementById('showAtoms');
        const showBonds = document.getElementById('showBonds');
        const showUnitCell = document.getElementById('showUnitCell');
        const showPolyhedra = document.getElementById('showPolyhedra');
        const includeBonds = document.getElementById('includeBonds');
        
        if (showAtoms) {
            // 初始化复选框状态
            showAtoms.checked = this.renderParams.showAtoms;
            showAtoms.addEventListener('change', (e) => {
                this.renderParams.showAtoms = e.target.checked;
                
                // 同步更新全屏控制面板的值
                const fullscreenShowAtoms = document.getElementById('fullscreenShowAtoms');
                if (fullscreenShowAtoms) {
                    fullscreenShowAtoms.checked = e.target.checked;
                }
                
                this.updateRender(true); // 保持相机位置
            });
        }
        
        if (showBonds) {
            // 初始化复选框状态
            showBonds.checked = this.renderParams.showBonds;
            showBonds.addEventListener('change', (e) => {
                this.renderParams.showBonds = e.target.checked;
                
                // 同步更新全屏控制面板的值
                const fullscreenShowBonds = document.getElementById('fullscreenShowBonds');
                if (fullscreenShowBonds) {
                    fullscreenShowBonds.checked = e.target.checked;
                }
                
                this.updateRender(true); // 保持相机位置
            });
        }
        
        if (showUnitCell) {
            // 初始化复选框状态
            showUnitCell.checked = this.renderParams.showUnitCell;
            showUnitCell.addEventListener('change', (e) => {
                this.renderParams.showUnitCell = e.target.checked;
                
                // 同步更新全屏控制面板的值
                const fullscreenShowUnitCell = document.getElementById('fullscreenShowUnitCell');
                if (fullscreenShowUnitCell) {
                    fullscreenShowUnitCell.checked = e.target.checked;
                }
                
                this.updateRender(true); // 保持相机位置
            });
        }
        
        if (showPolyhedra) {
            // 初始化复选框状态
            showPolyhedra.checked = this.renderParams.showPolyhedra;
            showPolyhedra.addEventListener('change', (e) => {
                this.renderParams.showPolyhedra = e.target.checked;
                
                // 同步更新全屏控制面板的值
                const fullscreenShowPolyhedra = document.getElementById('fullscreenShowPolyhedra');
                if (fullscreenShowPolyhedra) {
                    fullscreenShowPolyhedra.checked = e.target.checked;
                }
                
                // 控制透明度滑块的显示/隐藏
                const polyhedronOpacityControl = document.getElementById('polyhedronOpacityControl');
                if (polyhedronOpacityControl) {
                    polyhedronOpacityControl.style.display = e.target.checked ? 'block' : 'none';
                }
                
                this.updateRender(true); // 保持相机位置
            });
        }
        
        // 多面体透明度控制
        const polyhedronOpacity = document.getElementById('polyhedronOpacity');
        if (polyhedronOpacity) {
            // 初始化滑块状态
            polyhedronOpacity.value = this.renderParams.polyhedronOpacity;
            const polyhedronOpacityValue = document.getElementById('polyhedronOpacityValue');
            if (polyhedronOpacityValue) {
                polyhedronOpacityValue.textContent = this.renderParams.polyhedronOpacity;
            }
            
            polyhedronOpacity.addEventListener('input', (e) => {
                this.renderParams.polyhedronOpacity = parseFloat(e.target.value);
                
                // 更新显示的数值
                if (polyhedronOpacityValue) {
                    polyhedronOpacityValue.textContent = e.target.value;
                }
                
                // 同步更新全屏控制面板的值
                const fullscreenPolyhedronOpacity = document.getElementById('fullscreenPolyhedronOpacity');
                const fullscreenPolyhedronOpacityValue = document.getElementById('fullscreenPolyhedronOpacityValue');
                if (fullscreenPolyhedronOpacity) {
                    fullscreenPolyhedronOpacity.value = e.target.value;
                }
                if (fullscreenPolyhedronOpacityValue) {
                    fullscreenPolyhedronOpacityValue.textContent = e.target.value;
                }
                
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
        console.log('🔍 检查多面体数据:', structure.polyhedra);
        console.log('🔍 多面体数据类型:', typeof structure.polyhedra);
        console.log('🔍 多面体数据长度:', structure.polyhedra ? structure.polyhedra.length : 'undefined');
        
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
            // 保存当前结构引用，供其他函数使用
            this.currentStructure = structure;
            
            // 🎯 首先计算结构边界框并设置centerOffset，这必须在生成Plotly数据之前完成
            console.log('📏 计算结构边界框和centerOffset...');
            const bounds = this.calculateStructureBounds(structure);
            console.log('🎯 centerOffset已设置:', this.centerOffset);
            
            // 生成Plotly数据（现在centerOffset已正确设置）
            console.log('📊 生成Plotly数据...');
            const plotData = this.generatePlotlyData(structure);
            console.log('📈 Plotly数据:', plotData);
            
            // 计算最佳相机位置
            const optimalCamera = this.calculateOptimalCamera(bounds);
            
            // Crystal Toolkit风格布局 - 优化居中显示，恢复坐标轴显示
            const layout = {
                scene: {
                    xaxis: { 
                        title: 'X (Å)', 
                        showgrid: true,
                        showline: true,
                        zeroline: true,
                        showticklabels: true,
                        gridcolor: '#e0e0e0',
                        linecolor: '#666666',
                        zerolinecolor: '#999999'
                        // 移除固定range，让Plotly自动计算以确保居中
                    },
                    yaxis: { 
                        title: 'Y (Å)', 
                        showgrid: true,
                        showline: true,
                        zeroline: true,
                        showticklabels: true,
                        gridcolor: '#e0e0e0',
                        linecolor: '#666666',
                        zerolinecolor: '#999999'
                        // 移除固定range，让Plotly自动计算以确保居中
                    },
                    zaxis: { 
                        title: 'Z (Å)', 
                        showgrid: true,
                        showline: true,
                        zeroline: true,
                        showticklabels: true,
                        gridcolor: '#e0e0e0',
                        linecolor: '#666666',
                        zerolinecolor: '#999999'
                        // 移除固定range，让Plotly自动计算以确保居中
                    },
                    aspectmode: 'cube',
                    aspectratio: { x: 1, y: 1, z: 1 },
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
            
            // 🔍 验证Plotly渲染后的实际状态
            setTimeout(() => {
                const actualLayout = this.container.layout;
                if (actualLayout && actualLayout.scene && actualLayout.scene.camera) {
                    console.log('✅ Plotly渲染后的实际相机状态:', {
                        '实际camera.center': actualLayout.scene.camera.center,
                        '实际camera.eye': actualLayout.scene.camera.eye,
                        '实际camera.up': actualLayout.scene.camera.up,
                        '期望camera.center': optimalCamera.center,
                        '期望camera.eye': optimalCamera.eye
                    });
                    
                    // 检查center是否被正确设置
                    const actualCenter = actualLayout.scene.camera.center;
                    const expectedCenter = optimalCamera.center;
                    const centerMatch = actualCenter && 
                        Math.abs(actualCenter.x - expectedCenter.x) < 0.001 &&
                        Math.abs(actualCenter.y - expectedCenter.y) < 0.001 &&
                        Math.abs(actualCenter.z - expectedCenter.z) < 0.001;
                    
                    console.log('🎯 相机center设置验证:', {
                        '是否匹配': centerMatch,
                        '差异': actualCenter ? {
                            x: Math.abs(actualCenter.x - expectedCenter.x),
                            y: Math.abs(actualCenter.y - expectedCenter.y),
                            z: Math.abs(actualCenter.z - expectedCenter.z)
                        } : '无法获取实际center'
                    });
                } else {
                    console.warn('⚠️ 无法获取Plotly渲染后的相机状态');
                }
            }, 100);
            
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
                    
                    // 计算缩放因子（滚轮向上放大，向下缩小）- 优化缩放敏感度和步进控制
                    // 根据当前距离动态调整缩放步进，距离越近步进越小，保持平滑缩放
                    const baseZoomIn = 0.85;  // 放大时的基础因子
                    const baseZoomOut = 1.15; // 缩小时的基础因子
                    
                    // 动态调整缩放步进：距离越近，步进越小
                    const distanceRatio = Math.max(0.1, Math.min(1.0, currentDistance / 10));
                    const zoomIn = baseZoomIn + (1 - baseZoomIn) * (1 - distanceRatio) * 0.3;
                    const zoomOut = baseZoomOut - (baseZoomOut - 1) * (1 - distanceRatio) * 0.3;
                    
                    const zoomFactor = event.deltaY > 0 ? zoomOut : zoomIn;
                    const newDistance = currentDistance * zoomFactor;
                    
                    // 限制距离范围 - 允许极大的放大倍数
                    const minDistance = 0.01;  // 进一步减小最小距离，允许更大放大倍数
                    const maxDistance = 150;   // 增加最大距离范围
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
                    console.warn(`⚠️ 元素 ${element} 的原子数组无效:`, atoms);
                    return;
                }
                
                const x = [], y = [], z = [], text = [];
                
                atoms.forEach((atom, index) => {
                    // 安全检查原子数据
                    if (!atom || !Array.isArray(atom.cartesian) || atom.cartesian.length < 3) {
                        console.warn(`⚠️ 元素 ${element} 第${index}个原子的笛卡尔坐标无效:`, atom);
                        return;
                    }
                    
                    x.push(atom.cartesian[0]);
                    y.push(atom.cartesian[1]);
                    z.push(atom.cartesian[2]);
                    text.push(`${element} (${atom.cartesian[0].toFixed(2)}, ${atom.cartesian[1].toFixed(2)}, ${atom.cartesian[2].toFixed(2)})`);
                });
                
                // 只有当有有效坐标时才添加trace
                if (x.length > 0) {
                    const atomTrace = {
                        type: 'scatter3d',
                        mode: 'markers',
                        x: x, y: y, z: z,
                        text: text,
                        hoverinfo: 'text',
                        marker: {
                            size: this.calculateOptimalAtomSize(element, structure),
                            color: this.getElementColor(element),
                            opacity: 0.9,
                            line: {
                                color: '#000000',
                                width: 0.5
                            }
                        },
                        name: element,
                        showlegend: false
                    };
                    
                    traces.push(atomTrace);
                    console.log(`✅ 添加了 ${atoms.length} 个 ${element} 原子`);
                } else {
                    console.warn(`⚠️ 元素 ${element} 没有有效的原子坐标`);
                }
            });
        }
        
        // 2. 化学键渲染（如果启用）
        if (this.renderParams.showBonds && this.renderParams.includeBonds) {
            console.log('🔗 开始处理化学键...');
            const bonds = this.calculateBonds(structure);
            
            if (bonds.length > 0) {
                const bondTrace = this.createBondTrace(bonds);
                traces.push(bondTrace);
                console.log(`✅ 添加了 ${bonds.length} 个化学键`);
            } else {
                console.log('ℹ️ 没有找到化学键');
            }
        }
        
        // 3. 多面体渲染（如果启用）
        console.log('🔍 多面体渲染检查:');
        console.log('  - showPolyhedra:', this.renderParams.showPolyhedra);
        console.log('  - structure.polyhedra存在:', !!structure.polyhedra);
        console.log('  - structure.polyhedra是数组:', Array.isArray(structure.polyhedra));
        console.log('  - structure.polyhedra内容:', structure.polyhedra);
        
        if (this.renderParams.showPolyhedra && structure.polyhedra && Array.isArray(structure.polyhedra)) {
            console.log('🔷 开始处理多面体...');
            const polyhedronTraces = this.createPolyhedronTraces(structure.polyhedra);
            traces.push(...polyhedronTraces);
            console.log(`✅ 添加了 ${polyhedronTraces.length} 个多面体`);
        } else {
            console.log('❌ 多面体渲染条件不满足');
        }

        // 4. 晶胞渲染（如果启用）
        if (this.renderParams.showUnitCell) {
            console.log('📦 开始处理晶胞...');
            const unitCellTrace = this.createUnitCellTrace(structure.lattice);
            traces.push(unitCellTrace);
            console.log('✅ 添加了晶胞边框');
        }

        console.log(`🎯 总共生成了 ${traces.length} 个Plotly traces`);
        return traces;
    }
    
    updateRender(keepCamera = true) {
        if (!this.currentStructure) {
            console.warn('⚠️ 没有当前结构，无法更新渲染');
            return;
        }
        
        console.log('🔄 更新渲染，保持相机位置:', keepCamera);
        
        // 保存当前相机位置和坐标轴范围（如果需要）
        let currentCamera = null;
        let currentAxisRanges = null;
        if (keepCamera && this.container && this.container.layout && this.container.layout.scene) {
            // 🎯 深拷贝相机的所有参数，确保完整保存eye、center、up
            const camera = this.container.layout.scene.camera;
            if (camera) {
                currentCamera = {
                    eye: camera.eye ? { ...camera.eye } : null,
                    center: camera.center ? { ...camera.center } : null,
                    up: camera.up ? { ...camera.up } : null
                };
                console.log('🎥 保存当前完整相机状态:', currentCamera);
            }
            
            // 🎯 保存当前坐标轴范围，防止切换显示选项时尺度变化
            const scene = this.container.layout.scene;
            if (scene.xaxis && scene.yaxis && scene.zaxis) {
                currentAxisRanges = {
                    xaxis: {
                        range: scene.xaxis.range ? [...scene.xaxis.range] : null
                    },
                    yaxis: {
                        range: scene.yaxis.range ? [...scene.yaxis.range] : null
                    },
                    zaxis: {
                        range: scene.zaxis.range ? [...scene.zaxis.range] : null
                    }
                };
                console.log('📏 保存当前坐标轴范围:', currentAxisRanges);
            }
        }
        
        // 重新生成数据
        const plotData = this.generatePlotlyData(this.currentStructure);
        
        // 更新图表数据
        Plotly.react(this.container, plotData, this.container.layout, this.container.config);
        
        // 恢复相机位置和坐标轴范围（如果需要）
        if (keepCamera) {
            setTimeout(() => {
                const relayoutData = {};
                
                // 恢复相机位置
                if (currentCamera) {
                    relayoutData['scene.camera'] = currentCamera;
                }
                
                // 🎯 恢复坐标轴范围，确保尺度不变
                if (currentAxisRanges) {
                    if (currentAxisRanges.xaxis.range) {
                        relayoutData['scene.xaxis.range'] = currentAxisRanges.xaxis.range;
                    }
                    if (currentAxisRanges.yaxis.range) {
                        relayoutData['scene.yaxis.range'] = currentAxisRanges.yaxis.range;
                    }
                    if (currentAxisRanges.zaxis.range) {
                        relayoutData['scene.zaxis.range'] = currentAxisRanges.zaxis.range;
                    }
                    console.log('📏 恢复坐标轴范围:', relayoutData);
                }
                
                if (Object.keys(relayoutData).length > 0) {
                    Plotly.relayout(this.container, relayoutData);
                }
            }, 50);
        }
        
        console.log('✅ 渲染更新完成');
    }
    
    resizeToContainer(resetCamera = true) {
        if (!this.container) return;
        
        console.log('📐 调整图表大小以适应容器，重置相机:', resetCamera);
        
        // 获取容器当前尺寸
        const containerRect = this.container.getBoundingClientRect();
        console.log('📦 容器当前尺寸:', containerRect);
        
        // 保存当前相机位置（如果不重置相机）
        let currentCamera = null;
        if (!resetCamera && this.container.layout && this.container.layout.scene) {
            currentCamera = this.container.layout.scene.camera;
        }
        
        // 调整图表尺寸
        const updateData = {
            width: containerRect.width,
            height: containerRect.height
        };
        
        // 如果需要重置相机，重新计算最佳相机位置
        if (resetCamera && this.currentStructure) {
            const bounds = this.calculateStructureBounds(this.currentStructure);
            const optimalCamera = this.calculateOptimalCamera(bounds);
            updateData['scene.camera'] = optimalCamera;
            this.optimalCamera = optimalCamera;
        }
        
        Plotly.relayout(this.container, updateData);
        
        // 恢复相机位置（如果不重置相机）
        if (!resetCamera && currentCamera) {
            setTimeout(() => {
                Plotly.relayout(this.container, {
                    'scene.camera': currentCamera
                });
            }, 50);
        }
        
        console.log('✅ 图表大小调整完成');
    }
    
    groupAtomsByElement(structure) {
        const atomsByElement = {};
        
        if (!structure.sites || !Array.isArray(structure.sites)) {
            console.error('❌ 结构中没有有效的原子位点数据');
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
        let origin = [0, 0, 0];
        const a = matrix[0], b = matrix[1], c = matrix[2];
        
        // 🎯 应用中心偏移到单元格原点
        if (this.centerOffset) {
            origin = [
                -this.centerOffset.x,
                -this.centerOffset.y,
                -this.centerOffset.z
            ];
        }
        
        // 计算所有顶点，应用中心偏移
        const applyOffset = (point) => {
            if (this.centerOffset) {
                return [
                    point[0] - this.centerOffset.x,
                    point[1] - this.centerOffset.y,
                    point[2] - this.centerOffset.z
                ];
            }
            return point;
        };
        
        const vertices = {
            origin: applyOffset([0, 0, 0]),
            a: applyOffset(a),
            b: applyOffset(b),
            c: applyOffset(c),
            ab: applyOffset([a[0] + b[0], a[1] + b[1], a[2] + b[2]]),
            ac: applyOffset([a[0] + c[0], a[1] + c[1], a[2] + c[2]]),
            bc: applyOffset([b[0] + c[0], b[1] + c[1], b[2] + c[2]]),
            abc: applyOffset([a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]])
        };
        
        return [
            [vertices.origin, vertices.a], [vertices.origin, vertices.b], [vertices.origin, vertices.c],
            [vertices.a, vertices.ab], [vertices.a, vertices.ac],
            [vertices.b, vertices.ab], [vertices.b, vertices.bc],
            [vertices.c, vertices.ac], [vertices.c, vertices.bc],
            [vertices.ab, vertices.abc], [vertices.ac, vertices.abc], [vertices.bc, vertices.abc]
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
        
        // 🎯 应用中心偏移，将结构居中到原点
        if (this.centerOffset) {
            cartesian[0] -= this.centerOffset.x;
            cartesian[1] -= this.centerOffset.y;
            cartesian[2] -= this.centerOffset.z;
        }
        
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
        // 使用更合理的原子半径，基于离子半径和共价半径的平衡
        const radii = {
            'H': 0.8, 'Li': 1.2, 'Be': 0.9, 'B': 1.0, 'C': 1.0,
            'N': 0.9, 'O': 0.8, 'F': 0.7, 'Na': 1.4, 'Mg': 1.1,
            'Al': 1.2, 'Si': 1.3, 'P': 1.2, 'S': 1.2, 'Cl': 1.1,
            'K': 1.8, 'Ca': 1.5, 'Fe': 1.3, 'Cu': 1.1, 'Zn': 1.1,
            'Co': 1.2, 'Ni': 1.1, 'Mn': 1.3, 'Cr': 1.2, 'Ti': 1.4,
            'V': 1.3, 'Sc': 1.4, 'Y': 1.6, 'Zr': 1.5, 'Nb': 1.4
        };
        return radii[element] || 1.0;
    }
    
    // 智能计算原子显示大小，确保不重叠且显示效果良好
    calculateOptimalAtomSize(element, structure) {
        const baseRadius = this.getElementRadius(element);
        const scaleFactor = this.renderParams.scaleFactor;
        
        // 计算结构的最小原子间距离
        const minDistance = this.calculateMinimumAtomDistance(structure);
        
        // 基础大小计算：使用更大的基础倍数提高可见性
        let baseSize = baseRadius * scaleFactor * 15; // 从8增加到15
        
        // 根据最小距离调整大小，确保不重叠
        if (minDistance > 0) {
            // 计算安全的最大球体大小（球体直径不应超过最小距离的80%）
            const maxSafeSize = (minDistance * 0.8) * 10; // 转换为Plotly单位
            
            // 如果基础大小会导致重叠，则限制大小
            if (baseSize > maxSafeSize) {
                baseSize = maxSafeSize;
            }
        }
        
        // 根据结构特征进一步调整
        const characteristics = this.analyzeStructureCharacteristics(structure);
        
        // 根据原子数量调整：原子越多，单个原子应该相对更小
        if (characteristics.atomCount > 100) {
            baseSize *= 0.7;
        } else if (characteristics.atomCount > 50) {
            baseSize *= 0.85;
        } else if (characteristics.atomCount < 10) {
            baseSize *= 1.3; // 少量原子时可以显示更大
        }
        
        // 根据结构密度调整
        if (characteristics.density > 0.1) {
            baseSize *= 0.8; // 高密度结构使用更小的球体
        } else if (characteristics.density < 0.01) {
            baseSize *= 1.2; // 低密度结构可以使用更大的球体
        }
        
        // 确保最小可见大小
        const minSize = 8;
        const maxSize = 50;
        
        const finalSize = Math.max(minSize, Math.min(maxSize, baseSize));
        
        console.log(`🎯 ${element} 原子大小计算:`, {
            基础半径: baseRadius,
            缩放因子: scaleFactor,
            最小距离: minDistance?.toFixed(2),
            基础大小: (baseRadius * scaleFactor * 15).toFixed(1),
            最终大小: finalSize.toFixed(1),
            原子数量: characteristics.atomCount,
            密度: characteristics.density.toFixed(4)
        });
        
        return finalSize;
    }
    
    // 计算结构中原子间的最小距离
    calculateMinimumAtomDistance(structure) {
        if (!structure.sites || structure.sites.length < 2) {
            return null;
        }
        
        let minDistance = Infinity;
        const sites = structure.sites;
        
        // 计算所有原子对之间的距离
        for (let i = 0; i < sites.length; i++) {
            for (let j = i + 1; j < sites.length; j++) {
                const site1 = sites[i];
                const site2 = sites[j];
                
                if (!site1.coords || !site2.coords) continue;
                
                const cart1 = this.fractionalToCartesian(site1.coords, structure.lattice);
                const cart2 = this.fractionalToCartesian(site2.coords, structure.lattice);
                
                const distance = Math.sqrt(
                    Math.pow(cart1[0] - cart2[0], 2) +
                    Math.pow(cart1[1] - cart2[1], 2) +
                    Math.pow(cart1[2] - cart2[2], 2)
                );
                
                if (distance > 0.1 && distance < minDistance) { // 忽略过小的距离（可能是同一原子）
                    minDistance = distance;
                }
            }
        }
        
        return minDistance === Infinity ? null : minDistance;
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
        let allCartesian = [];

        // 🔧 直接计算原始笛卡尔坐标，不应用centerOffset
        structure.sites.forEach(site => {
            // 直接进行分数坐标到笛卡尔坐标的转换，不使用centerOffset
            const matrix = structure.lattice.matrix || structure.lattice;
            const cartesian = [
                site.coords[0] * matrix[0][0] + site.coords[1] * matrix[1][0] + site.coords[2] * matrix[2][0],
                site.coords[0] * matrix[0][1] + site.coords[1] * matrix[1][1] + site.coords[2] * matrix[2][1],
                site.coords[0] * matrix[0][2] + site.coords[1] * matrix[1][2] + site.coords[2] * matrix[2][2]
            ];
            
            allCartesian.push(cartesian);
            minX = Math.min(minX, cartesian[0]);
            minY = Math.min(minY, cartesian[1]);
            minZ = Math.min(minZ, cartesian[2]);
            maxX = Math.max(maxX, cartesian[0]);
            maxY = Math.max(maxY, cartesian[1]);
            maxZ = Math.max(maxZ, cartesian[2]);
        });

        // 计算几何中心（所有原子坐标的平均值）
        const geometricCenter = {
            x: allCartesian.reduce((sum, coord) => sum + coord[0], 0) / allCartesian.length,
            y: allCartesian.reduce((sum, coord) => sum + coord[1], 0) / allCartesian.length,
            z: allCartesian.reduce((sum, coord) => sum + coord[2], 0) / allCartesian.length
        };

        // 计算边界框中心
        const boundingCenter = {
            x: (minX + maxX) / 2,
            y: (minY + maxY) / 2,
            z: (minZ + maxZ) / 2
        };

        // 使用几何中心作为结构中心，这样更准确
        const center = geometricCenter;
        
        // 🎯 设置centerOffset，用于后续的坐标转换
        this.centerOffset = center;

        const size = {
            x: maxX - minX,
            y: maxY - minY,
            z: maxZ - minZ
        };

        console.log('📏 结构边界框:', { 
            min: {x: minX, y: minY, z: minZ}, 
            max: {x: maxX, y: maxY, z: maxZ}, 
            boundingCenter, 
            geometricCenter,
            finalCenter: center,
            size 
        });

        return {
            min: { x: minX, y: minY, z: minZ },
            max: { x: maxX, y: maxY, z: maxZ },
            center,
            size
        };
    }

    // 分析结构特征，用于智能相机距离计算
    analyzeStructureCharacteristics(structure) {
        if (!structure.sites || structure.sites.length === 0) {
            return {
                atomCount: 0,
                density: 0,
                structureType: 'unknown',
                complexity: 'low'
            };
        }

        const atomCount = structure.sites.length;
        const { size } = this.calculateStructureBounds(structure);
        const volume = size.x * size.y * size.z;
        const density = atomCount / Math.max(volume, 1); // 原子密度

        // 分析元素组成
        const elements = new Set();
        structure.sites.forEach(site => {
            if (site.species && Array.isArray(site.species)) {
                site.species.forEach(spec => {
                    if (spec.element) {
                        elements.add(spec.element);
                    }
                });
            }
        });

        // 判断结构类型
        let structureType = 'unknown';
        const elementArray = Array.from(elements);
        
        if (elementArray.includes('Na') && elementArray.includes('Cl')) {
            structureType = 'ionic_simple'; // NaCl类型
        } else if (elementArray.includes('Li') && (elementArray.includes('Co') || elementArray.includes('Ni') || elementArray.includes('Mn'))) {
            structureType = 'layered_oxide'; // LiCoO2类型
        } else if (elementArray.length === 1) {
            structureType = 'elemental'; // 单质
        } else if (elementArray.length === 2) {
            structureType = 'binary'; // 二元化合物
        } else if (elementArray.length >= 3) {
            structureType = 'complex'; // 复杂化合物
        }

        // 判断复杂度
        let complexity = 'low';
        if (atomCount > 50) {
            complexity = 'high';
        } else if (atomCount > 20 || elementArray.length > 3) {
            complexity = 'medium';
        }

        console.log('🔬 结构特征分析:', {
            atomCount,
            density: density.toFixed(4),
            structureType,
            complexity,
            elements: elementArray,
            volume: volume.toFixed(2)
        });

        return {
            atomCount,
            density,
            structureType,
            complexity,
            elements: elementArray,
            volume
        };
    }

    // 根据结构边界框和特征计算最佳相机位置
    calculateOptimalCamera(bounds) {
        const { center, size } = bounds;
        
        // 分析结构特征
        const characteristics = this.analyzeStructureCharacteristics(this.currentStructure);
        
        // 计算结构的最大尺寸和有效尺寸
        const maxSize = Math.max(size.x, size.y, size.z);
        const avgSize = (size.x + size.y + size.z) / 3;
        const minSize = Math.min(size.x, size.y, size.z);
        
        // 获取canvas的实际尺寸
        const canvasWidth = this.container ? this.container.offsetWidth : 800;
        const canvasHeight = this.container ? this.container.offsetHeight : 600;
        const canvasAspectRatio = canvasWidth / canvasHeight;
        
        // 基础距离系数，根据结构类型智能调整 - 大幅减小以显著提高显示尺寸
        let distanceCoeff = 0.6; // 从1.0进一步减小到0.6
        
        // 根据结构类型调整
        switch (characteristics.structureType) {
            case 'ionic_simple': // NaCl等简单离子化合物
                distanceCoeff = 0.4; // 从0.8减小到0.4
                break;
            case 'layered_oxide': // LiCoO2等层状氧化物
                distanceCoeff = 0.5; // 从0.9减小到0.5
                break;
            case 'elemental': // 单质
                distanceCoeff = 0.3; // 从0.7减小到0.3
                break;
            case 'binary': // 二元化合物
                distanceCoeff = 0.4; // 从0.8减小到0.4
                break;
            case 'complex': // 复杂化合物
                distanceCoeff = 0.7; // 从1.1减小到0.7
                break;
            default:
                distanceCoeff = 0.6;
        }
        
        // 根据原子数量调整 - 大幅优化小结构的显示
        if (characteristics.atomCount > 100) {
            distanceCoeff *= 1.0; // 从1.2减小到1.0
        } else if (characteristics.atomCount > 50) {
            distanceCoeff *= 0.9; // 从1.1减小到0.9
        } else if (characteristics.atomCount < 20) {
            distanceCoeff *= 0.3; // 从0.6减小到0.3，大幅优化小结构
        } else if (characteristics.atomCount < 10) {
            distanceCoeff *= 0.2; // 从0.5减小到0.2，极小结构显示得非常大
        }
        
        // 根据密度调整
        if (characteristics.density > 0.1) {
            distanceCoeff *= 1.1; // 高密度结构稍远
        } else if (characteristics.density < 0.01) {
            distanceCoeff *= 0.9; // 低密度结构可以更近
        }
        
        // 根据结构形状调整（长宽比）
        const aspectRatio = maxSize / minSize;
        if (aspectRatio > 3) {
            distanceCoeff *= 1.2; // 细长结构需要更远
        } else if (aspectRatio < 1.5) {
            distanceCoeff *= 0.95; // 接近球形的结构可以更近
        }
        
        // 根据canvas大小调整
        if (Math.min(canvasWidth, canvasHeight) > 600) {
            distanceCoeff *= 0.9; // 大canvas可以更近
        } else if (Math.min(canvasWidth, canvasHeight) < 400) {
            distanceCoeff *= 1.2; // 小canvas需要稍远一些
        }
        
        // 根据canvas宽高比调整
        if (canvasAspectRatio > 1.5) {
            distanceCoeff *= 1.05; // 宽屏需要稍远一些
        } else if (canvasAspectRatio < 0.8) {
            distanceCoeff *= 1.1; // 竖屏需要稍远一些
        }
        
        // 使用平均尺寸而不是最大尺寸，获得更好的视觉效果
        const effectiveSize = (maxSize * 0.6 + avgSize * 0.4);
        const cameraDistance = Math.max(effectiveSize * distanceCoeff, 2);
        
        // 使用等距离的相机位置，确保完美居中
        const normalizedDistance = cameraDistance / Math.sqrt(3);
        
        // 🎯 强制设置相机center为原点，确保与画布中心对齐
        const camera = {
            eye: {
                x: normalizedDistance,
                y: normalizedDistance,
                z: normalizedDistance
            },
            center: {
                x: 0,
                y: 0,
                z: 0
            },
            up: { x: 0, y: 0, z: 1 }
        };
        
        console.log('🔧 相机center强制设置为原点以确保居中:', {
            '原始几何中心': center,
            '强制center': camera.center,
            '调整后eye位置': camera.eye
        });
        
        console.log('📷 智能自适应相机设置:', {
            camera,
            结构类型: characteristics.structureType,
            原子数量: characteristics.atomCount,
            密度: characteristics.density.toFixed(4),
            复杂度: characteristics.complexity,
            结构尺寸: { max: maxSize.toFixed(2), avg: avgSize.toFixed(2), min: minSize.toFixed(2) },
            有效尺寸: effectiveSize.toFixed(2),
            canvas尺寸: `${canvasWidth}x${canvasHeight}`,
            距离系数: distanceCoeff.toFixed(2),
            最终距离: cameraDistance.toFixed(2)
        });
        
        // 🔍 详细的居中调试信息
        console.log('🎯 居中调试信息:', {
            '结构几何中心': center,
            '相机center设置': camera.center,
            '相机eye位置': camera.eye,
            '画布中心应该是': { x: canvasWidth/2, y: canvasHeight/2 },
            '画布尺寸': { width: canvasWidth, height: canvasHeight },
            '结构是否应该居中': '几何中心应与画布中心重合'
        });
        
        return camera;
    }

    // 创建多面体Plotly traces
    createPolyhedronTraces(polyhedraData) {
        const traces = [];
        
        if (!Array.isArray(polyhedraData) || polyhedraData.length === 0) {
            console.warn('⚠️ 多面体数据无效或为空');
            return traces;
        }
        
        console.log('🔷 处理多面体数据:', polyhedraData);
        
        // 多面体颜色映射
        const polyhedronColors = {
            'octahedral': '#4CAF50',      // 绿色
            'tetrahedral': '#2196F3',     // 蓝色
            'square_planar': '#FF9800',   // 橙色
            'trigonal_bipyramidal': '#9C27B0', // 紫色
            'square_pyramidal': '#F44336',      // 红色
            'trigonal_planar': '#00BCD4',       // 青色
            'linear': '#795548',                // 棕色
            'default': '#607D8B'                // 蓝灰色
        };
        
        polyhedraData.forEach((polyhedron, index) => {
            try {
                if (!polyhedron.center_coords || !polyhedron.neighbor_coords) {
                    console.warn(`⚠️ 多面体 ${index} 缺少必要的坐标数据:`, polyhedron);
                    return;
                }
                
                const centerCoords = polyhedron.center_coords;
                const neighborCoords = polyhedron.neighbor_coords;
                const geometryType = polyhedron.geometry_type || 'default';
                
                // 转换坐标到笛卡尔坐标系（如果需要）
                const center = Array.isArray(centerCoords) ? centerCoords : [0, 0, 0];
                const neighbors = Array.isArray(neighborCoords) ? neighborCoords : [];
                
                if (neighbors.length === 0) {
                    console.warn(`⚠️ 多面体 ${index} 没有邻居原子坐标`);
                    return;
                }
                
                // 应用中心偏移（与原子坐标保持一致）
                const adjustedCenter = this.centerOffset ? [
                    center[0] - this.centerOffset.x,
                    center[1] - this.centerOffset.y,
                    center[2] - this.centerOffset.z
                ] : center;
                
                const adjustedNeighbors = neighbors.map(coord => {
                    return this.centerOffset ? [
                        coord[0] - this.centerOffset.x,
                        coord[1] - this.centerOffset.y,
                        coord[2] - this.centerOffset.z
                    ] : coord;
                });
                
                // 创建多面体的凸包
                const polyhedronTrace = this.createPolyhedronMesh3D(
                    adjustedCenter, 
                    adjustedNeighbors, 
                    geometryType, 
                    polyhedronColors
                );
                
                if (polyhedronTrace) {
                    traces.push(polyhedronTrace);
                }
                
            } catch (error) {
                console.warn(`❌ 创建多面体 ${index} 失败:`, error);
            }
        });
        
        console.log(`🔷 成功创建了 ${traces.length} 个多面体traces`);
        return traces;
    }
    
    // 创建单个多面体的3D网格
    createPolyhedronMesh3D(center, neighbors, geometryType, colorMap) {
        try {
            // 所有顶点（中心 + 邻居）
            const allPoints = [center, ...neighbors];
            
            // 使用简化的凸包算法创建多面体面
            const faces = this.calculateConvexHull(allPoints);
            
            if (faces.length === 0) {
                console.warn('⚠️ 无法为多面体创建面');
                return null;
            }
            
            // 提取所有面的顶点坐标
            const x = [], y = [], z = [];
            const i = [], j = [], k = []; // 面的顶点索引
            
            // 创建顶点数组
            allPoints.forEach(point => {
                x.push(point[0]);
                y.push(point[1]);
                z.push(point[2]);
            });
            
            // 创建面的索引
            faces.forEach(face => {
                if (face.length >= 3) {
                    // 三角化面（如果面有超过3个顶点）
                    for (let t = 1; t < face.length - 1; t++) {
                        i.push(face[0]);
                        j.push(face[t]);
                        k.push(face[t + 1]);
                    }
                }
            });
            
            // 选择颜色
            const color = colorMap[geometryType] || colorMap.default;
            
            // 创建Plotly mesh3d trace
            const trace = {
                type: 'mesh3d',
                x: x,
                y: y,
                z: z,
                i: i,
                j: j,
                k: k,
                color: color,
                opacity: this.renderParams.polyhedronOpacity,
                name: `${geometryType} polyhedron`,
                showlegend: false,
                hoverinfo: 'text',
                text: `${geometryType} coordination polyhedron`,
                lighting: {
                    ambient: 0.4,
                    diffuse: 0.8,
                    specular: 0.2,
                    roughness: 0.1
                },
                lightposition: {
                    x: 100,
                    y: 200,
                    z: 0
                }
            };
            
            return trace;
            
        } catch (error) {
            console.warn('❌ 创建多面体网格失败:', error);
            return null;
        }
    }
    
    // 简化的凸包算法（用于创建多面体面）
    calculateConvexHull(points) {
        if (points.length < 4) {
            return [];
        }
        
        try {
            // 简化版本：为小型多面体创建基本面
            // 这里使用一个简化的方法，实际应用中可能需要更复杂的凸包算法
            const faces = [];
            const n = points.length;
            
            // 对于小型多面体，创建基本的三角面
            if (n <= 6) {
                // 简单情况：创建连接中心点（索引0）和其他点的面
                for (let i = 1; i < n - 1; i++) {
                    faces.push([0, i, i + 1]);
                }
                // 闭合最后一个面
                if (n > 2) {
                    faces.push([0, n - 1, 1]);
                }
            } else {
                // 复杂情况：使用更复杂的面生成逻辑
                // 这里简化为基本的扇形面
                for (let i = 1; i < n - 1; i++) {
                    faces.push([0, i, i + 1]);
                }
                faces.push([0, n - 1, 1]);
            }
            
            return faces;
            
        } catch (error) {
            console.warn('❌ 计算凸包失败:', error);
            return [];
        }
    }
}

// 全局导出
window.CrystalToolkitRenderer = CrystalToolkitRenderer;