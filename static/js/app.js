// 🎯 极简应用 - 只用最靠谱的pymatgen + Plotly方案
let currentFile = null;
let convertedFileUrl = null;
let lastConversionSessionId = null;
let qrCodeInstance = null;
let crystalPreview = null;
let professionalClient = null;

// DOM元素缓存 - 避免重复查询和潜在冲突
let domElements = {};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    cacheDOMElements();
    setupEventListeners();
    initProfessionalClient();
    initPlotlyPreview();
    initPolyhedraControls();
    
    // 修复滚动问题
    fixScrollIssues();
});

// 修复页面滚动问题
function fixScrollIssues() {
    console.log('🔧 检查并修复滚动问题...');
    
    // 确保body和html可以滚动
    document.documentElement.style.overflow = 'auto';
    document.documentElement.style.height = 'auto';
    document.body.style.overflow = 'auto';
    document.body.style.height = 'auto';
    
    // 检查是否有元素处于全屏状态
    if (document.fullscreenElement) {
        console.log('⚠️ 检测到全屏元素，退出全屏模式');
        document.exitFullscreen().catch(err => {
            console.error('退出全屏失败:', err);
        });
    }
    
    // 移除可能阻止滚动的样式
    const containers = document.querySelectorAll('.container, .container-fluid');
    containers.forEach(container => {
        container.style.overflow = 'visible';
        container.style.height = 'auto';
    });
    
    console.log('✅ 滚动修复完成');
}

// 缓存DOM元素 - 避免重复查询
function cacheDOMElements() {
    domElements = {
        uploadArea: document.getElementById('uploadArea'),
        fileInput: document.getElementById('fileInput'),
        convertBtn: document.getElementById('convertBtn'),
        fileStatus: document.getElementById('fileStatus'),
        previewSection: document.getElementById('previewSection'),
        modelStats: document.getElementById('modelStats'),
        atomCount: document.getElementById('atomCount'),
        formulaDisplay: document.getElementById('formulaDisplay'),
        spaceGroup: document.getElementById('spaceGroup'),
        fileName: document.getElementById('fileName'),
        resultSection: document.getElementById('resultSection'),
        fileSize: document.getElementById('fileSize'),
        downloadLink: document.getElementById('downloadLink'),
        qrcode: document.getElementById('qrcode')
    };
    
    console.log('📦 DOM元素缓存完成:', Object.keys(domElements).length, '个元素');
}

// 设置事件监听器
function setupEventListeners() {
    console.log('🔧 设置事件监听器...');
    
    const { uploadArea, fileInput, convertBtn } = domElements;
    
    console.log('📍 元素检查:', {
        uploadArea: !!uploadArea,
        fileInput: !!fileInput,
        convertBtn: !!convertBtn
    });
    
    // 绑定检查更新按钮
    const checkUpdatesBtn = document.getElementById('refresh-versions-btn');
    if (checkUpdatesBtn) {
        checkUpdatesBtn.addEventListener('click', checkForUpdates);
    }
    
    // 绑定版本信息下拉组件
    const versionDropdownBtn = document.getElementById('version-dropdown-btn');
    const versionDropdown = document.getElementById('version-dropdown');
    if (versionDropdownBtn && versionDropdown) {
        versionDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            versionDropdown.classList.toggle('show');
        });
        
        // 点击外部关闭下拉菜单
        document.addEventListener('click', function(e) {
            if (!versionDropdownBtn.contains(e.target) && !versionDropdown.contains(e.target)) {
                versionDropdown.classList.remove('show');
            }
        });
    }
    
    // 绑定多面体控制事件
    setupPolyhedraControls();
    
    // 文件上传
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            console.log('🖱️ 上传区域被点击');
            if (fileInput) {
                fileInput.click();
                console.log('🔄 触发文件选择器');
            } else {
                console.error('❌ 文件输入元素不存在');
            }
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-primary');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('border-primary');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-primary');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
    } else {
        console.error('❌ 上传区域元素不存在');
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                console.log('📄 文件选择:', file.name);
                
                // 显示文件名
                updateFileInfo(file);
                
                handleFile(file);
            }
        });
    } else {
        console.error('❌ 文件输入元素不存在');
    }
    
    // 转换按钮
    if (convertBtn) {
        convertBtn.addEventListener('click', convertToUSDZ);
    } else {
        console.error('❌ 转换按钮元素不存在');
    }
}

// 初始化专业CIF客户端
function initProfessionalClient() {
    try {
        if (typeof ProfessionalCIFClient !== 'undefined') {
            professionalClient = new ProfessionalCIFClient();
            console.log('✅ 专业CIF客户端初始化成功');
        } else {
            console.warn('⚠️ 专业CIF客户端不可用');
        }
    } catch (error) {
        console.error('❌ 专业CIF客户端初始化失败:', error);
    }
}

// 初始化Plotly预览
function initPlotlyPreview() {
    console.log('🔧 初始化Plotly预览...');
    
    // 防止重复初始化
    if (crystalPreview !== null) {
        console.log('⚠️ Crystal Toolkit渲染器已存在，跳过重复初始化');
        return;
    }
    
    if (typeof Plotly === 'undefined') {
        console.error('❌ Plotly.js未加载');
        showAlert('需要加载Plotly.js', 'danger');
        return;
    }
    
    try {
        if (typeof CrystalToolkitRenderer !== 'undefined') {
            crystalPreview = new CrystalToolkitRenderer('modelPreview');
            console.log('✅ Crystal Toolkit渲染器初始化成功');
        } else {
            throw new Error('Plotly渲染器不可用');
        }
    } catch (error) {
        console.error('❌ Plotly渲染器初始化失败:', error);
        showAlert('3D预览功能初始化失败', 'danger');
    }
}

// 更新文件信息显示
function updateFileInfo(file) {
    const { fileName, uploadArea, fileStatus } = domElements;
    
    // 更新统计信息中的文件名
    if (fileName) {
        fileName.textContent = file.name;
    }
    
    // 更新上传区域显示
    if (uploadArea) {
        uploadArea.innerHTML = `
            <i class="bi bi-file-earmark-check display-4 text-success mb-3"></i>
            <h5 class="text-success">${file.name}</h5>
            <p class="text-muted">文件大小: ${formatFileSize(file.size)}</p>
            <small class="text-info">点击可重新选择文件</small>
        `;
    }
    
    // 显示文件状态
    if (fileStatus) {
        fileStatus.style.display = 'block';
    }
    
    // 更新预览标题
    const previewTitle = document.getElementById('previewTitle');
    if (previewTitle) {
        previewTitle.textContent = `${file.name} - 3D预览`;
    }
}

// 更新模型统计信息
function updateModelStats(metadata) {
    const { modelStats, atomCount, formulaDisplay, spaceGroup } = domElements;
    
    if (modelStats) {
        modelStats.style.display = 'block';
    }
    
    // 原子数量
    if (atomCount) {
        atomCount.textContent = metadata.num_atoms || '?';
    }
    
    // 分子式
    if (formulaDisplay) {
        formulaDisplay.textContent = metadata.formula || '?';
    }
    
    // 空间群
    if (spaceGroup) {
        spaceGroup.textContent = metadata.space_group || '?';
    }
    
    console.log('📊 统计信息已更新:', {
        atoms: metadata.num_atoms,
        formula: metadata.formula,
        spaceGroup: metadata.space_group
    });
}

// 处理文件上传
async function handleFile(file) {
    console.log('📁 处理文件:', file.name, file.size, 'bytes');
    
    if (!file.name.toLowerCase().endsWith('.cif')) {
        showAlert('请上传CIF格式文件', 'warning');
        return;
    }
    
    currentFile = file;
    
    // 显示预览区域
    showPreviewSection();
    
    // 启动3D预览
    await updatePreview();
}

// 显示预览区域
function showPreviewSection() {
    const { previewSection } = domElements;
    if (previewSection) {
        previewSection.style.display = 'block';
        // 使用requestAnimationFrame确保DOM更新后再添加动画类
        requestAnimationFrame(() => {
            previewSection.classList.add('show');
        });
        setTimeout(() => {
            previewSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
        console.log('✅ 预览区域已显示');
    } else {
        console.error('❌ previewSection 元素不存在');
    }
}

// 通用刷新动画函数
function startRefreshAnimation(buttonId, options = {}) {
    const btn = document.getElementById(buttonId);
    if (!btn || btn.disabled) return null;
    
    const icon = btn.querySelector('.refresh-icon, i');
    const originalTitle = btn.title;
    
    // 设置默认选项
    const config = {
        loadingTitle: '正在刷新...',
        enableStatusAnimation: false,
        scaleEffect: true,
        ...options
    };
    
    // 添加过渡效果
    btn.style.transition = 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    btn.disabled = true;
    btn.classList.add('refreshing');
    
    // 更新标题
    if (config.loadingTitle) {
        btn.title = config.loadingTitle;
    }
    
    // 图标动画
    if (icon && config.scaleEffect) {
        icon.style.transition = 'transform 0.3s ease';
        icon.style.transform = 'scale(0.8)';
        setTimeout(() => {
            icon.classList.add('spinning');
            icon.style.transform = 'scale(1)';
        }, 150);
    } else if (icon) {
        icon.classList.add('spinning');
    }
    
    // 状态图标动画（仅适用于系统刷新按钮）
    if (config.enableStatusAnimation) {
        const statusChecks = document.querySelectorAll('.status-check');
        statusChecks.forEach((check, index) => {
            setTimeout(() => {
                check.style.transition = 'all 0.3s ease';
                check.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    check.classList.add('status-loading');
                    check.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
                    check.style.transform = 'scale(1)';
                }, 100);
            }, index * 50);
        });
    }
    
    console.log(`✅ ${buttonId} 刷新动画已启动`);
    
    // 返回恢复函数
    return {
        originalTitle,
        restore: () => stopRefreshAnimation(buttonId, originalTitle, config)
    };
}

function stopRefreshAnimation(buttonId, originalTitle, config = {}) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    
    const icon = btn.querySelector('.refresh-icon, i');
    
    // 恢复按钮状态
    btn.style.transition = 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    btn.classList.remove('refreshing');
    
    // 恢复图标
    if (icon) {
        if (config.scaleEffect) {
            icon.style.transform = 'scale(1.1)';
            setTimeout(() => {
                icon.classList.remove('spinning');
                icon.style.transform = 'scale(1)';
            }, 200);
        } else {
            icon.classList.remove('spinning');
        }
    }
    
    // 恢复标题
    if (originalTitle) {
        btn.title = originalTitle;
    }
    
    // 恢复状态图标（仅适用于系统刷新按钮）
    if (config.enableStatusAnimation) {
        const statusChecks = document.querySelectorAll('.status-check');
        statusChecks.forEach((check, index) => {
            setTimeout(() => {
                check.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    check.classList.remove('status-loading');
                    check.style.transform = 'scale(1)';
                }, 100);
            }, index * 30);
        });
    }
    
    // 延迟启用按钮
    setTimeout(() => {
        btn.disabled = false;
    }, 300);
    
    console.log(`✅ ${buttonId} 刷新动画已恢复`);
}

// 更新3D预览
async function updatePreview() {
    if (!currentFile || !crystalPreview || !professionalClient) {
        console.warn('⚠️ 缺少必要组件');
        return;
    }
    
    // 使用通用刷新动画函数
    const refreshAnimation = startRefreshAnimation('manual-refresh-btn', {
        loadingTitle: '正在刷新预览...',
        scaleEffect: false
    });
    
    // 隐藏占位符
    const placeholder = document.querySelector('.preview-placeholder');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    
    console.log('🔬 使用纯pymatgen + Plotly渲染...');
    
    try {
        // 1. 使用专业pymatgen解析
        const parseResult = await professionalClient.parseCIF(currentFile);
        
        if (parseResult.success) {
            console.log('✅ pymatgen解析成功:', parseResult.metadata);
            
            // 检查是否包含多面体数据
            if (parseResult.polyhedra && parseResult.polyhedra.length > 0) {
                console.log(`🔷 发现 ${parseResult.polyhedra.length} 个多面体`);
                // 将多面体数据添加到结构中
                parseResult.structure.polyhedra = parseResult.polyhedra;
            }
            
            // 2. 使用Crystal Toolkit渲染
            const renderResult = crystalPreview.loadStructure(parseResult.structure);
            
            if (renderResult.success) {
                // 显示统计信息
                updateModelStats(parseResult.metadata);
                
                const { convertBtn: convertBtnElement } = domElements;
                
                const source = parseResult.metadata.source || 'pymatgen';
                showAlert(`✨ 3D结构预览已加载 (${source} + Plotly)`, 'success');
                
                // 启用转换按钮
                if (convertBtnElement) {
                    convertBtnElement.disabled = false;
                }
                
            } else {
                throw new Error(renderResult.error || 'Plotly渲染失败');
            }
        } else {
            throw new Error('pymatgen解析失败');
        }
        
    } catch (error) {
        console.error('❌ 预览失败:', error);
        showAlert('预览失败: ' + error.message, 'warning');
        
        // 显示占位符
        if (placeholder) {
            placeholder.style.display = 'flex';
        }
    } finally {
        // 使用通用函数恢复刷新动画
        if (refreshAnimation) {
            refreshAnimation.restore();
        }
    }
}

// 转换为USDZ
async function convertToUSDZ() {
    if (!currentFile) {
        showAlert('请先选择CIF文件', 'warning');
        return;
    }
    
    const { convertBtn } = domElements;
    if (convertBtn) {
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>转换中...';
    }
    
    try {
        const formData = new FormData();
        formData.append('file', currentFile);
        
        // 添加转换参数
        formData.append('sphere_resolution', '16');
        formData.append('scale_factor', '1.0');
        formData.append('include_bonds', 'true');
        
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            convertedFileUrl = URL.createObjectURL(blob);
            
            // 保存session ID用于二维码生成
            lastConversionSessionId = response.headers.get('X-Session-ID');
            console.log('🔍 从响应头获取会话ID:', lastConversionSessionId);
            console.log('📋 所有响应头:');
            for (let [key, value] of response.headers) {
                if (key.startsWith('x-') || key.startsWith('X-')) {
                    console.log(`  ${key}: ${value}`);
                }
            }
            
            // 解析元数据
            const metadata = JSON.parse(response.headers.get('X-Conversion-Metadata') || '{}');
            
            // 显示结果
            showResults(metadata);
            
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || '转换失败');
        }
        
    } catch (error) {
        console.error('转换失败:', error);
        showAlert('转换失败: ' + error.message, 'danger');
    } finally {
        convertBtn.disabled = false;
        convertBtn.innerHTML = '<i class="bi bi-arrow-repeat me-2"></i>转换为USDZ';
    }
}

// 显示转换结果
function showResults(metadata) {
    const { resultSection, fileSize, downloadLink, qrcode } = domElements;
    
    // 显示结果区域
    if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 更新文件大小信息（使用当前HTML结构）
    if (fileSize) {
        fileSize.textContent = formatFileSize(metadata.file_size_mb * 1024 * 1024 || 0);
    }
    
    // 设置下载链接
    if (downloadLink && convertedFileUrl) {
        downloadLink.href = convertedFileUrl;
        // 使用原始文件名（去掉.cif扩展名）而不是crystal_前缀
        const originalName = currentFile ? currentFile.name.replace(/\.cif$/i, '') : (metadata.cif_metadata?.formula || 'structure');
        downloadLink.download = `${originalName}.usdz`;
    }
    
    // 生成AR QR码
    generateARQRCode();
    
    // 显示成功消息
    const successMsg = `✅ 转换完成！生成了包含${metadata.atom_count || 0}个原子的3D模型`;
    showAlert(successMsg, 'success');
    
    console.log('📊 转换元数据:', metadata);
}

// 生成AR QR码
async function generateARQRCode() {
    console.log('🔍 开始生成二维码...');
    console.log('convertedFileUrl:', convertedFileUrl);
    console.log('lastConversionSessionId:', lastConversionSessionId);
    
    if (!convertedFileUrl) {
        console.warn('❌ convertedFileUrl 为空，退出二维码生成');
        return;
    }
    
    const { qrcode: qrContainer } = domElements;
    if (!qrContainer) {
        console.warn('❌ 未找到二维码容器元素');
        return;
    }
    
    qrContainer.innerHTML = '';
    
    // 从响应头中获取session ID
    const sessionId = lastConversionSessionId;
    if (!sessionId) {
        console.warn('❌ 未找到会话ID，无法生成二维码');
        console.warn('检查转换响应头是否包含 X-Session-ID');
        qrContainer.innerHTML = `
            <div class="text-center p-3">
                <i class="bi bi-qr-code text-muted" style="font-size: 48px;"></i>
                <p class="mt-2 text-muted">无法生成二维码</p>
                <small class="text-muted">调试：未找到会话ID</small>
            </div>
        `;
        return;
    }
    
    try {
        // 获取配置的base URL
        const configResponse = await fetch('/api/config');
        const config = await configResponse.json();
        const baseUrl = config.base_url || window.location.origin;
        
        // 生成可访问的下载链接 - 二维码直接下载文件
        const downloadUrl = `${baseUrl}/download/${sessionId}`;
        // 生成AR预览链接 - 左侧按钮使用
        const arPreviewUrl = `${baseUrl}/view?file=${encodeURIComponent(downloadUrl)}`;
        
        console.log('🔗 生成的URL:', {
            sessionId: sessionId,
            baseUrl: baseUrl,
            downloadUrl: downloadUrl,
            arPreviewUrl: arPreviewUrl,
            note: '二维码用downloadUrl，按钮用arPreviewUrl'
        });
        
        // 使用后端API生成二维码 - 直接下载链接
        fetch('/api/generate_qr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: downloadUrl })
        })
        .then(response => {
            console.log('📡 二维码API响应状态:', response.status);
            
            if (response.status === 403) {
                // 二维码功能被禁用
                throw new Error('二维码功能已被管理员禁用');
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📱 二维码API响应数据:', data);
            
            if (data.success && data.qr_code) {
                qrContainer.innerHTML = `
                    <div class="text-center">
                        <img src="data:image/png;base64,${data.qr_code}" 
                             alt="AR预览二维码" 
                             style="width: 180px; height: 180px; border-radius: 6px;">
                        <div class="mt-2">
                            <small class="text-muted d-block">iPhone iPad 扫码查看</small>
                        </div>
                    </div>
                `;
                
                // 更新AR预览链接
                const arPreviewLink = document.getElementById('arPreviewLink');
                if (arPreviewLink) {
                    arPreviewLink.href = arPreviewUrl;
                    console.log('🔗 更新AR预览链接:', arPreviewUrl);
                }
                
                console.log('✅ 二维码生成成功:', {
                    downloadUrl: downloadUrl,
                    arPreviewUrl: arPreviewUrl
                });
            } else {
                console.error('❌ 二维码API返回失败:', data);
                throw new Error(data.error || '二维码生成失败');
            }
        })
        .catch(error => {
            console.error('❌ 二维码生成失败:', error);
            qrContainer.innerHTML = `
                <div class="text-center p-3">
                    <i class="bi bi-qr-code text-muted" style="font-size: 48px;"></i>
                    <p class="mt-2 text-muted">二维码生成失败</p>
                    <small class="text-muted">${error.message}</small>
                </div>
            `;
        });
        
    } catch (error) {
        console.error('❌ 获取配置失败:', error);
        qrContainer.innerHTML = `
            <div class="text-center p-3">
                <i class="bi bi-qr-code text-muted" style="font-size: 48px;"></i>
                <p class="mt-2 text-muted">配置获取失败</p>
                <small class="text-muted">${error.message}</small>
            </div>
        `;
    }
}

// 显示警告消息
function showAlert(message, type = 'info', duration = 5000, options = {}) {
    const alertContainer = domElements.alertContainer || document.getElementById('alertContainer') || createAlertContainer();
    
    // 支持多行消息
    const formattedMessage = message.replace(/\n/g, '<br>');
    
    // 根据类型添加图标
    const icons = {
        'success': '<i class="bi bi-check-circle-fill me-2"></i>',
        'danger': '<i class="bi bi-exclamation-triangle-fill me-2"></i>',
        'warning': '<i class="bi bi-exclamation-circle-fill me-2"></i>',
        'info': '<i class="bi bi-info-circle-fill me-2"></i>'
    };
    
    const icon = icons[type] || icons['info'];
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    alert.style.border = 'none';
    alert.style.borderRadius = '8px';
    alert.style.marginBottom = '10px';
    
    alert.innerHTML = `
        <div class="d-flex align-items-start">
            ${icon}
            <div class="flex-grow-1">${formattedMessage}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        ${options.showProgress ? '<div class="progress mt-2" style="height: 3px;"><div class="progress-bar" role="progressbar" style="width: 100%; transition: width ' + duration + 'ms linear;"></div></div>' : ''}
    `;
    
    alertContainer.appendChild(alert);
    
    // 添加进入动画
    setTimeout(() => {
        alert.style.transform = 'translateX(0)';
    }, 10);
    
    // 如果显示进度条，启动进度动画
    if (options.showProgress) {
        const progressBar = alert.querySelector('.progress-bar');
        setTimeout(() => {
            progressBar.style.width = '0%';
        }, 100);
    }
    
    // 自动隐藏
    const hideTimeout = setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.add('fade-out');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 300);
        }
    }, duration);
    
    // 手动关闭时清除定时器
    const closeBtn = alert.querySelector('.btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            clearTimeout(hideTimeout);
        });
    }
    
    return alert;
}

// 创建警告容器
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.maxWidth = '400px';
    container.style.minWidth = '300px';
    
    // 添加CSS样式
    const style = document.createElement('style');
    style.textContent = `
        #alertContainer .alert {
            transform: translateX(100%);
            transition: transform 0.3s ease-out;
        }
        #alertContainer .alert.show {
            transform: translateX(0);
        }
        #alertContainer .alert.fade-out {
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease-in;
        }
        @media (max-width: 576px) {
            #alertContainer {
                left: 10px;
                right: 10px;
                top: 10px;
                max-width: none;
                min-width: auto;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(container);
    return container;
}

// 显示升级成功的特殊提示
function showUpgradeSuccessAlert(componentName, details = {}) {
    const message = `
        <strong>${componentName} 升级成功！</strong><br>
        ${details.oldVersion ? `从 v${details.oldVersion}` : ''}
        ${details.newVersion ? ` 升级到 v${details.newVersion}` : ''}
        ${details.features ? `<br><small class="text-muted">新功能: ${details.features}</small>` : ''}
    `;
    
    return showAlert(message, 'success', 6000, { showProgress: true });
}

// 显示批量升级结果
function showBatchUpgradeResult(results) {
    const { successful, failed, total } = results;
    
    if (successful === total) {
        const message = `
            <strong>🎉 所有组件升级成功！</strong><br>
            <small>共升级 ${total} 个组件</small>
        `;
        return showAlert(message, 'success', 8000, { showProgress: true });
    } else if (successful > 0) {
        const message = `
            <strong>部分升级完成</strong><br>
            成功: ${successful} 个，失败: ${failed} 个
        `;
        return showAlert(message, 'warning', 7000, { showProgress: true });
    } else {
        const message = `
            <strong>升级失败</strong><br>
            所有 ${total} 个组件升级失败
        `;
        return showAlert(message, 'danger', 6000);
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ===== 版本信息管理 =====

// 页面加载时获取版本信息
document.addEventListener('DOMContentLoaded', function() {
    // 立即开始后台加载系统信息，不阻塞页面渲染
    // 使用更短的延迟，优先保证用户体验
    setTimeout(() => {
        checkForUpdates(); // 后台静默加载
    }, 100); // 减少延迟到100ms
    
    // 定期自动检测更新（每天一次，强制刷新缓存）
    setInterval(() => checkForUpdates(true), 24 * 60 * 60 * 1000);
    
    // 当下拉菜单打开时优先显示缓存数据，提供即时响应
    const systemDropdown = document.getElementById('systemDropdown');
    if (systemDropdown) {
        systemDropdown.addEventListener('click', function() {
            const now = Date.now();
            
            // 如果有缓存数据且未过期，立即显示
            if (versionCache.data && (now - versionCache.timestamp) <= versionCache.ttl) {
                // 立即显示缓存的版本信息，提供快速响应
                displayVersionInfo(
                    versionCache.data.version_info,
                    versionCache.data.app_info,
                    versionCache.data.software_update
                );
                updateVersionStatus(versionCache.data.summary.updates_available);
            } else if (versionCache.data) {
                // 有过期缓存时，先显示缓存数据，然后后台更新
                displayVersionInfo(
                    versionCache.data.version_info,
                    versionCache.data.app_info,
                    versionCache.data.software_update
                );
                updateVersionStatus(versionCache.data.summary.updates_available);
                
                // 后台静默更新数据
                checkForUpdates(false).then(() => {
                    // 更新完成后刷新显示
                    if (versionCache.data) {
                        displayVersionInfo(
                            versionCache.data.version_info,
                            versionCache.data.app_info,
                            versionCache.data.software_update
                        );
                        updateVersionStatus(versionCache.data.summary.updates_available);
                    }
                });
            } else {
                // 没有缓存数据时才显示加载状态
                checkForUpdates(false);
            }
        });
    }
    
    // 使用事件委托处理动态生成的刷新按钮
    document.addEventListener('click', function(e) {
        if (e.target.closest('#refreshBtn')) {
            console.log('🔄 刷新按钮被点击了！');
            e.preventDefault();
            e.stopPropagation(); // 阻止事件冒泡，确保动画正常执行
            
            const btn = e.target.closest('#refreshBtn');
            
            // 如果已经在刷新中，直接返回
            if (btn.disabled) return;
            
            // Bootstrap 5的data-bs-auto-close="outside"属性已经处理了dropdown关闭逻辑
            // 无需额外的JavaScript代码来防止关闭
            
            // 使用通用刷新动画函数
            const refreshAnimation = startRefreshAnimation('refreshBtn', {
                loadingTitle: '正在刷新系统信息...',
                enableStatusAnimation: true,
                scaleEffect: true
            });
            
            // 强制刷新版本信息
            checkForUpdates(true).finally(() => {
                // 延迟恢复按钮状态，确保用户能看到刷新效果
                setTimeout(() => {
                    if (refreshAnimation) {
                        refreshAnimation.restore();
                    }
                }, 1000);
            });
            
            return false; // 确保事件不会继续传播
        }
    });
    
    // 刷新按钮的事件处理器已经包含了完整的事件阻止逻辑，无需额外的监听器
    
    // 初始化移动端下拉菜单
    initMobileDropdown();
    
    // 预加载优化：多重策略确保版本信息尽快可用
    
    // 策略1: 页面空闲时检查
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            // 如果还没有数据，再次尝试加载
            if (!versionCache.data) {
                checkForUpdates();
            }
        });
    }
    
    // 策略2: 页面完全加载后立即检查
    window.addEventListener('load', function() {
        // 页面完全加载后，如果还没有版本数据，立即获取
        if (!versionCache.data) {
            checkForUpdates();
        }
    });
    
    // 策略3: 网络空闲时预加载
    if ('navigator' in window && 'connection' in navigator) {
        const connection = navigator.connection;
        // 在良好网络条件下提前加载
        if (connection.effectiveType === '4g' || connection.effectiveType === '3g') {
            setTimeout(() => {
                if (!versionCache.data) {
                    checkForUpdates();
                }
            }, 50); // 网络良好时更快加载
        }
    }
});

// 移动端下拉菜单初始化
function initMobileDropdown() {
    const dropdown = document.querySelector('.version-dropdown');
    const dropdownBtn = document.querySelector('.version-dropdown-btn');
    const dropdownMenu = document.querySelector('.version-dropdown-menu');
    
    if (!dropdown || !dropdownBtn || !dropdownMenu) return;
    
    // 点击按钮切换下拉菜单
    dropdownBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const isShown = dropdown.classList.contains('show');
        
        // 关闭其他可能打开的下拉菜单
        document.querySelectorAll('.version-dropdown.show').forEach(el => {
            if (el !== dropdown) {
                el.classList.remove('show');
            }
        });
        
        // 切换当前下拉菜单
        dropdown.classList.toggle('show', !isShown);
        
        // 移动端特殊处理
        if (window.innerWidth <= 768) {
            if (!isShown) {
                // 显示时添加遮罩
                addMobileOverlay();
                // 禁止背景滚动
                document.body.style.overflow = 'hidden';
            } else {
                // 隐藏时移除遮罩
                removeMobileOverlay();
                // 恢复背景滚动
                document.body.style.overflow = '';
            }
        }
    });
    
    // Bootstrap的data-bs-auto-close="outside"已经处理了下拉菜单关闭逻辑
    // 这里只需要处理移动端特殊情况
    
    // 窗口大小改变时的处理
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // 桌面端时移除移动端样式
            removeMobileOverlay();
            document.body.style.overflow = '';
        }
    });
    
    // ESC键关闭下拉菜单
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            dropdown.classList.remove('show');
            removeMobileOverlay();
            document.body.style.overflow = '';
        }
    });
}

// 添加移动端遮罩
function addMobileOverlay() {
    if (document.querySelector('.mobile-overlay')) return;
    
    const overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1040;
        backdrop-filter: blur(2px);
    `;
    
    overlay.addEventListener('click', function() {
        document.querySelector('.version-dropdown').classList.remove('show');
        removeMobileOverlay();
        document.body.style.overflow = '';
    });
    
    document.body.appendChild(overlay);
}

// 移除移动端遮罩
function removeMobileOverlay() {
    const overlay = document.querySelector('.mobile-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// 版本信息缓存
let versionInfoCache = {
    data: null,
    timestamp: 0,
    isLoading: false
};

// 加载版本信息
async function loadVersionInfo(forceRefresh = false) {
    const content = document.getElementById('system-menu-content');
    const CACHE_DURATION = 2 * 60 * 1000; // 2分钟缓存
    const now = Date.now();
    
    // 如果正在加载，避免重复请求
    if (versionInfoCache.isLoading && !forceRefresh) {
        return;
    }
    
    // 检查缓存是否有效
    if (!forceRefresh && versionInfoCache.data && 
        (now - versionInfoCache.timestamp) < CACHE_DURATION) {
        // 使用缓存数据
        const cachedData = versionInfoCache.data;
        displayVersionInfo(
            cachedData.version_info, 
            cachedData.app_info, 
            cachedData.software_update
        );
        updateVersionStatus(cachedData.summary.updates_available);
        return;
    }
    
    // 显示加载状态（仅在没有缓存数据时）
    if (!versionInfoCache.data && content) {
        content.innerHTML = `
            <div class="d-flex align-items-center justify-content-center py-3">
                <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                <small class="text-muted">加载系统信息...</small>
            </div>
        `;
    }
    
    versionInfoCache.isLoading = true;
    
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.success && data.data.version_info) {
            // 更新缓存
            versionInfoCache.data = data.data;
            versionInfoCache.timestamp = now;
            
            displayVersionInfo(
                data.data.version_info, 
                data.data.app_info, 
                data.data.software_update
            );
            updateVersionStatus(data.data.summary.updates_available);
        } else {
            // 如果有缓存数据，继续使用；否则显示错误
            if (versionInfoCache.data) {
                const cachedData = versionInfoCache.data;
                displayVersionInfo(
                    cachedData.version_info, 
                    cachedData.app_info, 
                    cachedData.software_update
                );
            } else {
                displayVersionError();
            }
        }
    } catch (error) {
        console.error('获取版本信息失败:', error);
        // 如果有缓存数据，继续使用；否则显示错误
        if (versionInfoCache.data) {
            const cachedData = versionInfoCache.data;
            displayVersionInfo(
                cachedData.version_info, 
                cachedData.app_info, 
                cachedData.software_update
            );
        } else {
            displayVersionError();
        }
    } finally {
        versionInfoCache.isLoading = false;
    }
}

// 显示版本信息
function displayVersionInfo(versionInfo, appInfo, softwareUpdate) {
    const systemMenuContainer = document.getElementById('system-menu-content');
    if (!systemMenuContainer) return;
    
    const items = [];
    
    // 获取真实的构建时间，只显示日期部分
    const fullBuildTime = appInfo?.build_time || versionInfo?.build_time || '2024-12-25 14:30:00';
    const buildDate = fullBuildTime.split(' ')[0]; // 只取日期部分
    
    // 检查是否有软件更新
    const hasAppUpdate = softwareUpdate?.update_available || false;
    
    // 添加刷新按钮和构建时间信息
    items.push(`
        <div class="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
            <h6 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>系统信息
            </h6>
            <button class="btn btn-outline-primary btn-sm refresh-btn" id="refreshBtn" title="刷新系统状态" data-bs-toggle="false">
                <i class="bi bi-arrow-clockwise refresh-icon"></i>
            </button>
        </div>
        <div class="px-3 py-1 text-muted small">
            <div class="d-flex justify-content-between">
                <span>构建日期:</span>
                <span>${buildDate}</span>
            </div>
        </div>
        <div class="dropdown-divider"></div>
    `);
    
    // 组件版本信息
    items.push(`
        <h6 class="dropdown-header">
            <i class="bi bi-cpu me-2"></i>组件版本
        </h6>
    `);
    
    // 定义实际使用的核心组件（基于真实API数据）
    const keyComponents = {
        'fastapi': {
            name: 'FastAPI',
            version: versionInfo.fastapi?.version || '0.104.0',
            available: versionInfo.fastapi?.available !== false,
            update_available: versionInfo.fastapi?.update_available || false,
            description: 'Web框架核心'
        },
        'uvicorn': {
            name: 'Uvicorn',
            version: versionInfo.uvicorn?.version || '0.24.0',
            available: versionInfo.uvicorn?.available !== false,
            update_available: versionInfo.uvicorn?.update_available || false,
            description: 'ASGI服务器'
        },
        'pymatgen': {
            name: 'Pymatgen',
            version: versionInfo.pymatgen?.version || '2024.11.13',
            available: versionInfo.pymatgen?.available !== false,
            update_available: versionInfo.pymatgen?.update_available || false,
            description: '材料科学计算'
        },
        'ase': {
            name: 'ASE 原子模拟',
            version: versionInfo.ase?.version || '3.26.0',
            available: versionInfo.ase?.available !== false,
            update_available: versionInfo.ase?.update_available || false,
            description: '原子结构处理'
        },
        'usd-core': {
            name: 'Pixar USD',
            version: versionInfo.usd_version || '24.11',
            available: versionInfo.usd?.available !== false,
            update_available: versionInfo.usd?.update_available || false,
            description: '3D场景描述'
        },
        'plotly': {
            name: 'Plotly.js',
            version: versionInfo.plotly?.version || '2.27.0',
            available: versionInfo.plotly?.available !== false,
            update_available: versionInfo.plotly?.update_available || false,
            description: '3D可视化'
        },
        'pillow': {
            name: 'Pillow',
            version: versionInfo.pillow?.version || '10.1.0',
            available: versionInfo.pillow?.available !== false,
            update_available: versionInfo.pillow?.update_available || false,
            description: '图像处理'
        },
        'loguru': {
            name: 'Loguru',
            version: versionInfo.loguru?.version || '0.7.2',
            available: versionInfo.loguru?.available !== false,
            update_available: versionInfo.loguru?.update_available || false,
            description: '日志系统'
        }
    };
    
    Object.entries(keyComponents).forEach(([key, info]) => {
        // 判断组件健康状态
        const isHealthy = info.available !== false;
        const hasUpdate = info.update_available;
        
        // 状态图标和颜色逻辑 - 简洁清晰的设计
        let statusIcon, statusColor, statusTitle;
        if (isHealthy) {
            if (hasUpdate) {
                statusIcon = '<i class="bi bi-arrow-up-circle-fill"></i>'; // 有更新可用
                statusColor = 'text-warning';
                statusTitle = '有更新可用';
            } else {
                statusIcon = '<i class="bi bi-check-circle-fill"></i>'; // 运行正常
                statusColor = 'text-success';
                statusTitle = '运行正常';
            }
        } else {
            statusIcon = '<i class="bi bi-exclamation-triangle-fill"></i>'; // 异常状态
            statusColor = 'text-danger';
            statusTitle = '状态异常';
        }
        
        items.push(`
            <div class="d-flex justify-content-between align-items-center py-2 px-3 component-item" data-component="${key}">
                <div class="d-flex align-items-center flex-grow-1">
                    <div class="me-3">
                        <div class="d-flex align-items-center gap-2">
                            <span class="fw-medium text-dark">${info.name}</span>
                            <span class="version-tag">v${info.version}</span>
                        </div>
                        <div class="text-muted small mt-1">${info.description}</div>
                    </div>
                </div>
                <div class="status-check ${statusColor}" title="${statusTitle}">
                    ${statusIcon}
                </div>
            </div>
        `);
    });
    

    
    systemMenuContainer.innerHTML = items.join('');
}

// 显示版本信息错误
function displayVersionError(errorMessage = '获取失败') {
    const systemMenuContainer = document.getElementById('system-menu-content');
    if (!systemMenuContainer) return;
    
    systemMenuContainer.innerHTML = `
        <div class="d-flex align-items-center justify-content-center py-3">
            <i class="bi bi-exclamation-triangle text-warning me-2"></i>
            <small class="text-muted">${errorMessage}</small>
        </div>
        <div class="text-center py-2">
            <button class="btn btn-outline-primary btn-sm" onclick="checkForUpdates(true)">
                <i class="bi bi-arrow-clockwise me-1"></i>重试
            </button>
        </div>
    `;
}

// 创建进度显示模态框
function createProgressModal(packages) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'updateProgressModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'updateProgressModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    const packageList = packages.map(pkg => `
        <div class="d-flex align-items-center mb-2" id="progress-${pkg}">
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status" style="width: 1rem; height: 1rem;"></div>
            <span class="flex-grow-1">${pkg}</span>
            <span class="badge bg-secondary">等待中</span>
        </div>
    `).join('');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="updateProgressModalLabel">
                        <i class="bi bi-download me-2"></i>组件更新进度
                    </h5>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" style="width: 0%" id="overall-progress">
                                0%
                            </div>
                        </div>
                        <small class="text-muted mt-1 d-block" id="progress-text">准备更新...</small>
                    </div>
                    <div class="border rounded p-3" style="max-height: 300px; overflow-y: auto;">
                        ${packageList}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

// 更新进度模态框状态
function updateProgressModal(packageName, current, total, status) {
    const progressElement = document.getElementById(`progress-${packageName}`);
    const overallProgress = document.getElementById('overall-progress');
    const progressText = document.getElementById('progress-text');
    
    if (progressElement) {
        const spinner = progressElement.querySelector('.spinner-border');
        const badge = progressElement.querySelector('.badge');
        
        switch (status) {
            case 'updating':
                spinner.className = 'spinner-border spinner-border-sm text-warning me-2';
                badge.className = 'badge bg-warning';
                badge.textContent = '更新中';
                break;
            case 'success':
                spinner.className = 'bi bi-check-circle text-success me-2';
                badge.className = 'badge bg-success';
                badge.textContent = '成功';
                break;
            case 'failed':
                spinner.className = 'bi bi-x-circle text-danger me-2';
                badge.className = 'badge bg-danger';
                badge.textContent = '失败';
                break;
        }
    }
    
    // 更新整体进度
    if (overallProgress && progressText) {
        const percentage = Math.round((current / total) * 100);
        overallProgress.style.width = `${percentage}%`;
        overallProgress.textContent = `${percentage}%`;
        
        if (status === 'updating') {
            progressText.textContent = `正在更新 ${packageName} (${current}/${total})`;
        } else if (current === total) {
            progressText.textContent = '更新完成！';
        }
    }
}

// 更新版本状态
function updateVersionStatus(updatesAvailable) {
    const updateAllBtn = document.getElementById('update-all-btn');
    
    // 显示或隐藏一键升级按钮
    if (updateAllBtn) {
        updateAllBtn.style.display = updatesAvailable > 0 ? 'block' : 'none';
        
        // 更新按钮文本
        if (updatesAvailable > 0) {
            updateAllBtn.innerHTML = `<i class="bi bi-rocket me-1"></i>一键升级 (${updatesAvailable})`;
        } else {
            updateAllBtn.innerHTML = '<i class="bi bi-rocket me-1"></i>一键升级';
        }
    }
}

// 缓存机制配置
const versionCache = {
    data: null,
    timestamp: 0,
    ttl: 5 * 60 * 1000, // 5分钟缓存时间
    isLoading: false,
    retryCount: 0,
    maxRetries: 3
};

// 网络状态检测
const networkStatus = {
    isOnline: navigator.onLine,
    lastOnlineTime: Date.now()
};

// 监听网络状态变化
window.addEventListener('online', () => {
    networkStatus.isOnline = true;
    networkStatus.lastOnlineTime = Date.now();
    // 网络恢复时刷新数据
    checkForUpdates(true);
});

window.addEventListener('offline', () => {
    networkStatus.isOnline = false;
});

// 带缓存的版本检查
// 检查运行状态（快速检查，不检查版本更新）
async function checkRuntimeStatus() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.log('运行状态检查超时，正在取消请求...');
            controller.abort();
        }, 5000); // 5秒超时，比版本检查更快
        
        const response = await fetch('/api/runtime-status', {
            signal: controller.signal,
            headers: {
                'Cache-Control': 'no-cache',
                'Accept': 'application/json'
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // 更新运行状态显示
            updateRuntimeStatusDisplay(data.data);
            console.log('✅ 系统运行状态检查完成');
        } else {
            throw new Error('服务器返回无效数据');
        }
    } catch (error) {
        console.error('检查运行状态失败:', error);
        
        // 显示错误状态
        let errorMessage = '运行状态检查失败';
        if (error.name === 'AbortError') {
            errorMessage = '检查超时';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = '网络连接失败';
        }
        
        showRuntimeStatusError(errorMessage);
    }
}

// 更新运行状态显示（直接显示详细版本信息）
function updateRuntimeStatusDisplay(statusData) {
    // 如果有缓存的版本数据，直接显示
    if (versionCache.data) {
        displayVersionInfo(
            versionCache.data.version_info,
            versionCache.data.app_info,
            versionCache.data.software_update
        );
        updateVersionStatus(versionCache.data.summary.updates_available);
    } else {
        // 没有缓存数据时，调用完整的版本检查
        checkForUpdates(false); // 使用缓存，不强制刷新
    }
}

// 显示运行状态错误
function showRuntimeStatusError(errorMessage) {
    const statusIndicator = document.querySelector('.status-indicator');
    if (statusIndicator) {
        statusIndicator.className = 'status-indicator text-danger';
        statusIndicator.innerHTML = `<i class="bi bi-exclamation-triangle"></i> ${errorMessage}`;
    }
}

async function checkForUpdates(forceRefresh = false) {
    const now = Date.now();
    
    // 检查缓存是否有效
    if (!forceRefresh && versionCache.data && (now - versionCache.timestamp) < versionCache.ttl) {
        displayCachedVersionInfo();
        return;
    }
    
    // 防止重复请求
    if (versionCache.isLoading) {
        return;
    }
    
    // 离线时使用缓存
    if (!networkStatus.isOnline && versionCache.data) {
        displayCachedVersionInfo();
        showOfflineIndicator();
        return;
    }
    
    versionCache.isLoading = true;
    
    try {
        // 只在没有缓存数据时显示加载状态
        if (!versionCache.data) {
            showVersionLoading();
        }
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.log('API请求超时，正在取消请求...');
            controller.abort();
        }, 15000); // 增加到15秒超时
        
        const response = await fetch('/api/status', {
            signal: controller.signal,
            headers: {
                'Cache-Control': 'no-cache',
                'Accept': 'application/json'
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.data.version_info) {
            // 更新缓存
            versionCache.data = data.data;
            versionCache.timestamp = now;
            versionCache.retryCount = 0; // 重置重试计数
            
            displayVersionInfo(
                data.data.version_info, 
                data.data.app_info, 
                data.data.software_update
            );
            updateVersionStatus(data.data.summary.updates_available);
            hideOfflineIndicator();
        } else {
            throw new Error('服务器返回无效数据');
        }
    } catch (error) {
        console.error('检查更新失败:', error);
        
        // 区分不同类型的错误
        let errorMessage = '检查更新失败';
        if (error.name === 'AbortError') {
            errorMessage = '请求超时，请检查网络连接';
            console.log('请求被中止 - 可能是超时或网络问题');
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = '网络连接失败';
        } else if (error.message.includes('HTTP')) {
            errorMessage = `服务器错误: ${error.message}`;
        }
        
        // 重试机制 - 但不对AbortError进行重试
        if (versionCache.retryCount < versionCache.maxRetries && 
            networkStatus.isOnline && 
            error.name !== 'AbortError') {
            versionCache.retryCount++;
            console.log(`第${versionCache.retryCount}次重试...`);
            setTimeout(() => {
                versionCache.isLoading = false;
                checkForUpdates(forceRefresh);
            }, 2000 * versionCache.retryCount); // 递增延迟重试
            return;
        }
        
        // 如果有缓存数据，使用缓存；否则显示错误
        if (versionCache.data) {
            displayCachedVersionInfo();
            showOfflineIndicator();
        } else {
            displayVersionError(errorMessage);
        }
    } finally {
        versionCache.isLoading = false;
    }
}

// 显示缓存的版本信息
function displayCachedVersionInfo() {
    if (versionCache.data) {
        displayVersionInfo(
            versionCache.data.version_info, 
            versionCache.data.app_info, 
            versionCache.data.software_update
        );
        updateVersionStatus(versionCache.data.summary.updates_available);
    }
}

// 显示加载状态
function showVersionLoading() {
    const versionContainer = document.getElementById('version-dropdown-content');
    if (!versionContainer) return;
    
    versionContainer.innerHTML = `
        <div class="d-flex align-items-center justify-content-center py-3">
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
            <small class="text-muted">加载中...</small>
        </div>
    `;
}

// 显示离线指示器
function showOfflineIndicator() {
    const versionContainer = document.getElementById('version-dropdown-content');
    if (!versionContainer) return;
    
    // 在现有内容顶部添加离线提示
    const offlineIndicator = versionContainer.querySelector('.offline-indicator');
    if (!offlineIndicator) {
        const indicator = document.createElement('div');
        indicator.className = 'offline-indicator alert alert-warning alert-sm mb-2 py-1';
        indicator.innerHTML = `
            <i class="bi bi-wifi-off me-1"></i>
            <small>离线模式 - 显示缓存数据</small>
        `;
        versionContainer.insertBefore(indicator, versionContainer.firstChild);
    }
}

// 隐藏离线指示器
function hideOfflineIndicator() {
    const offlineIndicator = document.querySelector('.offline-indicator');
    if (offlineIndicator) {
        offlineIndicator.remove();
    }
}

// 升级单个组件（使用真实API）
async function updateComponent(componentName) {
    const componentItem = document.querySelector(`[data-component="${componentName}"]`);
    const updateBtn = componentItem?.querySelector('button[onclick*="updateComponent"]');
    const statusBadge = componentItem?.querySelector('.badge');
    
    if (!updateBtn) return;
    
    // Bootstrap的data-bs-auto-close="outside"已经处理了下拉菜单关闭逻辑
    
    // 显示升级中状态
    updateBtn.disabled = true;
    updateBtn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i>';
    if (statusBadge) {
        statusBadge.className = 'badge bg-warning badge-sm';
        statusBadge.textContent = '升级中';
    }
    
    try {
        // 调用真实的包更新API
        const response = await fetch('/api/packages/update-single', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                package: componentName,
                force: false
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示成功状态
            updateBtn.innerHTML = '<i class="bi bi-check-circle text-success"></i>';
            if (statusBadge) {
                statusBadge.className = 'badge bg-success badge-sm';
                statusBadge.textContent = '已升级';
            }
            
            // 使用增强的成功提示
            showUpgradeSuccessAlert(componentName, {
                oldVersion: info?.version,
                newVersion: result.new_version || '最新版本'
            });
            
            // 3秒后刷新版本信息
            setTimeout(async () => {
                await loadVersionInfo();
            }, 3000);
        } else {
            throw new Error(result.error || '升级失败');
        }
    } catch (error) {
        console.error(`升级${componentName}时出错:`, error);
        
        // 显示失败状态
        updateBtn.innerHTML = '<i class="bi bi-exclamation-circle text-danger"></i>';
        if (statusBadge) {
            statusBadge.className = 'badge bg-danger badge-sm';
            statusBadge.textContent = '失败';
        }
        
        showAlert(`${componentName} 更新失败: ${error.message}`, 'danger');
        
        // 5秒后恢复原状态
        setTimeout(() => {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
            if (statusBadge) {
                statusBadge.className = 'badge bg-warning badge-sm';
                statusBadge.textContent = '可更新';
            }
        }, 5000);
    }
}

// 检查软件更新
async function checkSoftwareUpdate() {
    try {
        const response = await fetch('/api/software/check-update');
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            console.error('检查软件更新失败:', data.error);
            return null;
        }
    } catch (error) {
        console.error('检查软件更新失败:', error);
        return null;
    }
}

// 执行软件更新
async function updateSoftware() {
    const updateBtn = event?.target || document.querySelector('button[onclick*="updateSoftware"]');
    
    if (updateBtn) {
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i>';
    }
    
    try {
        const response = await fetch('/api/software/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message || '软件更新成功', 'success');
            
            // 刷新版本信息
            setTimeout(() => {
                checkForUpdates();
            }, 2000);
            
            return true;
        } else {
            showAlert(`软件更新失败: ${data.error}`, 'danger');
            return false;
        }
    } catch (error) {
        console.error('软件更新失败:', error);
        showAlert('软件更新失败，请检查网络连接', 'danger');
        return false;
    } finally {
        if (updateBtn) {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        }
    }
}

// 一键升级所有组件（智能检测）
async function upgradeAllComponents() {
    const btn = document.getElementById('upgrade-all-btn');
    const originalText = btn?.textContent || '一键升级';
    
    try {
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> 检测中...';
        }
        
        // 1. 首先检查软件更新
        const softwareUpdate = await checkSoftwareUpdate();
        let hasSoftwareUpdate = softwareUpdate && softwareUpdate.has_update;
        
        // 2. 检查组件更新
        if (btn) {
            btn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> 检查组件更新...';
        }
        
        const statusResponse = await fetch('/api/status');
        const statusData = await statusResponse.json();
        
        let hasComponentUpdates = false;
        if (statusData.success && statusData.data.summary) {
            hasComponentUpdates = statusData.data.summary.updates_available > 0;
        }
        
        // 3. 根据检测结果执行相应操作
        if (!hasSoftwareUpdate && !hasComponentUpdates) {
            showAlert('所有软件和组件都是最新版本！', 'info');
            return;
        }
        
        let upgradeSteps = [];
        if (hasSoftwareUpdate) {
            upgradeSteps.push('软件更新');
        }
        if (hasComponentUpdates) {
            upgradeSteps.push('组件升级');
        }
        
        // 4. 执行升级
        if (btn) {
            btn.innerHTML = `<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> 升级中 (${upgradeSteps.join('、')})...`;
        }
        
        let allSuccess = true;
        let results = [];
        
        // 先升级软件（如果需要）
        if (hasSoftwareUpdate) {
            if (btn) {
                btn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> 正在更新软件...';
            }
            const softwareResult = await updateSoftware();
            results.push(`软件更新: ${softwareResult ? '成功' : '失败'}`);
            if (!softwareResult) allSuccess = false;
        }
        
        // 再升级组件（如果需要）
        if (hasComponentUpdates) {
            if (btn) {
                btn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> 正在升级组件...';
            }
            
            const response = await fetch('/api/components/upgrade-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            const componentResult = data.success;
            results.push(`组件升级: ${componentResult ? '成功' : '失败'}`);
            if (!componentResult) allSuccess = false;
        }
        
        // 5. 显示结果
        const upgradeResults = {
            total: upgradeSteps.length,
            successful: results.filter(r => r.includes('成功')).length,
            failed: results.filter(r => r.includes('失败')).length
        };
        
        showBatchUpgradeResult(upgradeResults);
        
        // 重新加载版本信息
        await loadVersionInfo();
        
    } catch (error) {
        console.error('升级失败:', error);
        showAlert('升级过程中发生错误，请检查网络连接', 'danger');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-rocket me-1"></i>' + originalText;
        }
    }
}

// 批量升级所有组件（使用真实API，带进度显示）
async function upgradeAllComponents() {
    const upgradeBtn = document.getElementById('upgrade-all-btn');
    if (!upgradeBtn) return;
    
    try {
        // 获取当前状态以确定需要更新的包
        const statusResponse = await fetch('/api/status');
        const statusData = await statusResponse.json();
        
        if (!statusData.success) {
            throw new Error('无法获取当前状态');
        }
        
        const packagesToUpdate = [];
        
        // 收集需要更新的包
        if (statusData.data.version_info && statusData.data.version_info.components) {
            for (const component of statusData.data.version_info.components) {
                if (component.update_available) {
                    packagesToUpdate.push(component.name);
                }
            }
        }
        
        if (packagesToUpdate.length === 0) {
            showAlert('没有可更新的组件', 'info');
            return;
        }
        
        // 创建进度显示模态框
        const progressModal = createProgressModal(packagesToUpdate);
        document.body.appendChild(progressModal);
        
        // 显示模态框
        const modal = new bootstrap.Modal(progressModal);
        modal.show();
        
        // 禁用更新按钮
        upgradeBtn.disabled = true;
        upgradeBtn.innerHTML = '<i class="bi bi-arrow-clockwise" style="animation: spin 1s linear infinite;"></i> 更新中...';
        
        let successCount = 0;
        let failedPackages = [];
        
        // 逐个更新包并显示进度
        for (let i = 0; i < packagesToUpdate.length; i++) {
            const packageName = packagesToUpdate[i];
            
            // 更新进度显示
            updateProgressModal(packageName, i + 1, packagesToUpdate.length, 'updating');
            
            try {
                const response = await fetch('/api/packages/update-single', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        package: packageName,
                        force: false
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    updateProgressModal(packageName, i + 1, packagesToUpdate.length, 'success');
                    successCount++;
                } else {
                    updateProgressModal(packageName, i + 1, packagesToUpdate.length, 'failed');
                    failedPackages.push(packageName);
                }
            } catch (error) {
                updateProgressModal(packageName, i + 1, packagesToUpdate.length, 'failed');
                failedPackages.push(packageName);
            }
            
            // 添加延迟避免过快更新
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // 显示最终结果
        const batchResults = {
            total: packagesToUpdate.length,
            successful: successCount,
            failed: failedPackages.length
        };
        
        showBatchUpgradeResult(batchResults);
        
        // 3秒后关闭模态框并刷新
        setTimeout(async () => {
            modal.hide();
            document.body.removeChild(progressModal);
            await loadVersionInfo();
        }, 3000);
        
    } catch (error) {
        console.error('批量更新失败:', error);
        showAlert(`批量更新失败: ${error.message}`, 'danger');
    } finally {
        // 恢复按钮状态
        upgradeBtn.disabled = false;
        upgradeBtn.innerHTML = '<i class="bi bi-rocket me-1"></i>一键更新';
    }
}

// 设置多面体控制事件监听器
function setupPolyhedraControls() {
    console.log('🔧 设置多面体控制事件监听器...');
    
    // 多面体显示复选框
    const showPolyhedra = document.getElementById('showPolyhedra');
    if (showPolyhedra) {
        showPolyhedra.addEventListener('change', function(e) {
            const isChecked = e.target.checked;
            console.log('🔷 多面体显示状态:', isChecked);
            
            // 显示/隐藏透明度控制
            const opacityControl = document.getElementById('polyhedronOpacityControl');
            if (opacityControl) {
                opacityControl.style.display = isChecked ? 'block' : 'none';
            }
            
            // 如果有CrystalPreview实例，调用相应方法
            if (window.crystalPreviewInstance) {
                window.crystalPreviewInstance.togglePolyhedra(isChecked);
            }
            
            // 如果有Crystal Toolkit渲染器，更新渲染参数
            if (crystalPreview && crystalPreview.renderParams) {
                crystalPreview.renderParams.showPolyhedra = isChecked;
                crystalPreview.updateRender(true);
            }
        });
    }
    
    // 多面体透明度滑块
    const polyhedronOpacity = document.getElementById('polyhedronOpacity');
    const polyhedronOpacityValue = document.getElementById('polyhedronOpacityValue');
    if (polyhedronOpacity && polyhedronOpacityValue) {
        polyhedronOpacity.addEventListener('input', function(e) {
            const opacity = parseFloat(e.target.value);
            polyhedronOpacityValue.textContent = opacity.toFixed(1);
            console.log('🔷 多面体透明度:', opacity);
            
            // 如果有CrystalPreview实例，调用相应方法
            if (window.crystalPreviewInstance) {
                window.crystalPreviewInstance.setPolyhedronOpacity(opacity);
            }
            
            // 如果有Crystal Toolkit渲染器，更新渲染参数
            if (crystalPreview && crystalPreview.renderParams) {
                crystalPreview.renderParams.polyhedronOpacity = opacity;
                crystalPreview.updateRender(true);
            }
        });
    }
    
    console.log('✅ 多面体控制事件监听器设置完成');
}

// 初始化多面体控制状态
function initPolyhedraControls() {
    const showPolyhedra = document.getElementById('showPolyhedra');
    const opacityControl = document.getElementById('polyhedronOpacityControl');
    
    // 初始状态下隐藏透明度控制
    if (opacityControl) {
        opacityControl.style.display = 'none';
    }
    
    // 如果复选框被选中，显示透明度控制
    if (showPolyhedra && showPolyhedra.checked && opacityControl) {
        opacityControl.style.display = 'block';
    }
}