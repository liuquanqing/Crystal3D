/**
 * CIF晶体结构实时3D预览
 */
class CrystalPreview {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.animationId = null;
        this.atomGroup = null;
        this.bondGroup = null;
        this.polyhedronGroup = null;
        
        this.init();
    }
    
    init() {
        // 设置场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf8f9fa);
        
        // 设置相机
        const width = this.container.clientWidth;
        const height = this.container.clientHeight || 400;
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(10, 10, 10);
        
        // 设置渲染器
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // 清空容器并添加渲染器
        this.container.innerHTML = '';
        this.container.appendChild(this.renderer.domElement);
        
        // 设置控制器
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // 添加光源
        this.addLights();
        
        // 开始渲染循环
        this.animate();
        
        // 窗口大小变化处理
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    addLights() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // 方向光
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // 点光源
        const pointLight = new THREE.PointLight(0xffffff, 0.5);
        pointLight.position.set(-50, -50, -50);
        this.scene.add(pointLight);
    }
    
    // 从CIF数据预览晶体结构
    async previewFromCIF(file, options = {}) {
        try {
            // 清除之前的模型
            this.clearModel();
            
            // 解析CIF文件
            const cifData = await this.parseCIFFile(file);
            
            // 生成3D模型
            this.generateCrystalModel(cifData, options);
            
            // 调整相机位置
            this.fitCameraToModel();
            
            return { success: true, atomCount: cifData.atoms.length };
        } catch (error) {
            console.error('CIF预览失败:', error);
            this.showError('无法预览CIF文件: ' + error.message);
            return { success: false, error: error.message };
        }
    }
    
    // 解析CIF文件（简化版）
    async parseCIFFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const content = event.target.result;
                    const cifData = this.parseCIFContent(content);
                    resolve(cifData);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = () => reject(new Error('文件读取失败'));
            reader.readAsText(file);
        });
    }
    
    // 解析CIF内容（简化实现）
    parseCIFContent(content) {
        const atoms = [];
        const lines = content.split('\n');
        
        let inAtomLoop = false;
        let atomColumns = {};
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (line.startsWith('loop_')) {
                inAtomLoop = true;
                atomColumns = {};
                continue;
            }
            
            if (inAtomLoop && line.startsWith('_atom_site_')) {
                const column = line.split(/\s+/)[0];
                const index = Object.keys(atomColumns).length;
                atomColumns[column] = index;
                continue;
            }
            
            if (inAtomLoop && line && !line.startsWith('_') && !line.startsWith('#')) {
                const parts = line.split(/\s+/);
                
                if (parts.length >= Object.keys(atomColumns).length) {
                    const atom = {
                        element: parts[atomColumns['_atom_site_type_symbol'] || atomColumns['_atom_site_label']] || 'C',
                        x: parseFloat(parts[atomColumns['_atom_site_fract_x']] || 0),
                        y: parseFloat(parts[atomColumns['_atom_site_fract_y']] || 0),
                        z: parseFloat(parts[atomColumns['_atom_site_fract_z']] || 0)
                    };
                    
                    // 清理元素符号
                    atom.element = atom.element.replace(/[0-9]/g, '');
                    if (atom.element.length > 2) {
                        atom.element = atom.element.substring(0, 2);
                    }
                    
                    atoms.push(atom);
                }
            }
            
            if (inAtomLoop && (line.startsWith('loop_') || line.startsWith('_') && !line.startsWith('_atom_site_'))) {
                inAtomLoop = false;
            }
        }
        
        return { atoms };
    }
    
    // 生成晶体模型
    generateCrystalModel(cifData, options) {
        this.atomGroup = new THREE.Group();
        this.bondGroup = new THREE.Group();
        this.polyhedronGroup = new THREE.Group();
        
        const {
            sphereResolution = 20,
            scaleFactor = 1.0,
            includeBonds = true,
            includePolyhedra = false,
            polyhedronOpacity = 0.3,
            cellExpansion = 1
        } = options;
        
        // 元素颜色映射
        const elementColors = {
            'H': 0xffffff, 'He': 0xd9ffff, 'Li': 0xcc80ff, 'Be': 0xc2ff00,
            'B': 0xffb5b5, 'C': 0x909090, 'N': 0x3050f8, 'O': 0xff0d0d,
            'F': 0x90e050, 'Ne': 0xb3e3f5, 'Na': 0xab5cf2, 'Mg': 0x8aff00,
            'Al': 0xbfa6a6, 'Si': 0xf0c8a0, 'P': 0xff8000, 'S': 0xffff30,
            'Cl': 0x1ff01f, 'Ar': 0x80d1e3, 'K': 0x8f40d4, 'Ca': 0x3dff00,
            'default': 0x808080
        };
        
        // 元素半径映射（以埃为单位）
        const elementRadii = {
            'H': 0.31, 'He': 0.28, 'Li': 1.28, 'Be': 0.96, 'B': 0.84,
            'C': 0.70, 'N': 0.65, 'O': 0.60, 'F': 0.50, 'Ne': 0.58,
            'Na': 1.66, 'Mg': 1.41, 'Al': 1.21, 'Si': 1.11, 'P': 1.07,
            'S': 1.05, 'Cl': 1.02, 'Ar': 1.06, 'K': 2.03, 'Ca': 1.76,
            'default': 0.80
        };
        
        // 创建原子
        cifData.atoms.forEach((atom, index) => {
            const element = atom.element || 'C';
            const color = elementColors[element] || elementColors.default;
            const radius = (elementRadii[element] || elementRadii.default) * scaleFactor;
            
            // 创建球体几何体
            const geometry = new THREE.SphereGeometry(radius, sphereResolution, sphereResolution);
            const material = new THREE.MeshLambertMaterial({ color });
            const sphere = new THREE.Mesh(geometry, material);
            
            // 设置位置（简单的分数坐标到笛卡尔坐标转换）
            sphere.position.set(
                atom.x * 10 * scaleFactor,
                atom.y * 10 * scaleFactor,
                atom.z * 10 * scaleFactor
            );
            
            sphere.castShadow = true;
            sphere.receiveShadow = true;
            
            // 添加到原子组
            this.atomGroup.add(sphere);
        });
        
        // 如果需要显示化学键（简化实现）
        if (includeBonds && cifData.atoms.length > 1) {
            this.generateBonds(cifData.atoms, scaleFactor);
        }
        
        // 如果需要显示配位多面体
        if (includePolyhedra && cifData.polyhedra) {
            this.generatePolyhedra(cifData.polyhedra, scaleFactor, polyhedronOpacity);
        }
        
        // 添加到场景
        this.scene.add(this.atomGroup);
        this.scene.add(this.bondGroup);
        this.scene.add(this.polyhedronGroup);
    }
    
    // 生成化学键（简化实现）
    generateBonds(atoms, scaleFactor) {
        const bondDistance = 3.0 * scaleFactor; // 最大成键距离
        
        for (let i = 0; i < atoms.length; i++) {
            for (let j = i + 1; j < atoms.length; j++) {
                const atom1 = atoms[i];
                const atom2 = atoms[j];
                
                const pos1 = new THREE.Vector3(
                    atom1.x * 10 * scaleFactor,
                    atom1.y * 10 * scaleFactor,
                    atom1.z * 10 * scaleFactor
                );
                
                const pos2 = new THREE.Vector3(
                    atom2.x * 10 * scaleFactor,
                    atom2.y * 10 * scaleFactor,
                    atom2.z * 10 * scaleFactor
                );
                
                const distance = pos1.distanceTo(pos2);
                
                if (distance < bondDistance) {
                    this.createBond(pos1, pos2, 0.1 * scaleFactor);
                }
            }
        }
    }
    
    // 创建化学键
    createBond(pos1, pos2, radius) {
        const direction = new THREE.Vector3().subVectors(pos2, pos1);
        const length = direction.length();
        const center = new THREE.Vector3().addVectors(pos1, pos2).divideScalar(2);
        
        const geometry = new THREE.CylinderGeometry(radius, radius, length, 8);
        const material = new THREE.MeshLambertMaterial({ color: 0x666666 });
        const bond = new THREE.Mesh(geometry, material);
        
        bond.position.copy(center);
        bond.lookAt(pos2);
        bond.rotateX(Math.PI / 2);
        
        this.bondGroup.add(bond);
    }
    
    // 生成配位多面体
    generatePolyhedra(polyhedraData, scaleFactor, opacity) {
        polyhedraData.forEach((polyhedron, index) => {
            try {
                const centerCoords = polyhedron.center_coords;
                const neighborCoords = polyhedron.neighbor_coords;
                const geometryType = polyhedron.geometry_type;
                
                // 转换坐标到Three.js坐标系
                const center = new THREE.Vector3(
                    centerCoords[0] * 10 * scaleFactor,
                    centerCoords[1] * 10 * scaleFactor,
                    centerCoords[2] * 10 * scaleFactor
                );
                
                const neighbors = neighborCoords.map(coord => new THREE.Vector3(
                    coord[0] * 10 * scaleFactor,
                    coord[1] * 10 * scaleFactor,
                    coord[2] * 10 * scaleFactor
                ));
                
                // 创建多面体几何体
                const polyhedronMesh = this.createPolyhedronMesh(center, neighbors, geometryType, opacity);
                if (polyhedronMesh) {
                    this.polyhedronGroup.add(polyhedronMesh);
                }
                
            } catch (error) {
                console.warn(`生成多面体 ${index} 失败:`, error);
            }
        });
    }
    
    // 创建多面体网格
    createPolyhedronMesh(center, neighbors, geometryType, opacity) {
        try {
            // 使用ConvexGeometry创建凸包
            const points = [center, ...neighbors];
            const geometry = new THREE.ConvexGeometry(points);
            
            // 根据几何类型选择颜色
            const colorMap = {
                'octahedral': 0x4CAF50,    // 绿色
                'tetrahedral': 0x2196F3,   // 蓝色
                'square_planar': 0xFF9800, // 橙色
                'trigonal_bipyramidal': 0x9C27B0, // 紫色
                'square_pyramidal': 0xF44336,      // 红色
                'default': 0x607D8B        // 蓝灰色
            };
            
            const color = colorMap[geometryType] || colorMap.default;
            
            // 创建半透明材质
            const material = new THREE.MeshLambertMaterial({
                color: color,
                transparent: true,
                opacity: opacity,
                side: THREE.DoubleSide
            });
            
            const mesh = new THREE.Mesh(geometry, material);
            mesh.userData = {
                type: 'polyhedron',
                geometryType: geometryType,
                center: center
            };
            
            return mesh;
            
        } catch (error) {
            console.warn('创建多面体网格失败:', error);
            return null;
        }
    }
    
    // 调整相机位置以适应模型
    fitCameraToModel() {
        if (!this.atomGroup || this.atomGroup.children.length === 0) return;
        
        const box = new THREE.Box3().setFromObject(this.atomGroup);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const distance = maxDim * 2;
        
        this.camera.position.set(
            center.x + distance,
            center.y + distance,
            center.z + distance
        );
        
        this.controls.target.copy(center);
        this.controls.update();
    }
    
    // 清除模型
    clearModel() {
        if (this.atomGroup) {
            this.scene.remove(this.atomGroup);
            this.atomGroup = null;
        }
        if (this.bondGroup) {
            this.scene.remove(this.bondGroup);
            this.bondGroup = null;
        }
        if (this.polyhedronGroup) {
            this.scene.remove(this.polyhedronGroup);
            this.polyhedronGroup = null;
        }
    }
    
    // 显示错误信息
    showError(message) {
        this.container.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100">
                <div class="text-center text-muted">
                    <i class="bi bi-exclamation-triangle display-4"></i>
                    <p class="mt-2">${message}</p>
                </div>
            </div>
        `;
    }
    
    // 动画循环
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        if (this.controls) {
            this.controls.update();
        }
        
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    // 窗口大小变化处理
    onWindowResize() {
        if (!this.camera || !this.renderer) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight || 400;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    // 重置视图
    resetView() {
        this.fitCameraToModel();
    }
    
    // 切换多面体显示
    togglePolyhedra(visible) {
        if (this.polyhedronGroup) {
            this.polyhedronGroup.visible = visible;
        }
    }
    
    // 设置多面体透明度
    setPolyhedronOpacity(opacity) {
        if (this.polyhedronGroup) {
            this.polyhedronGroup.children.forEach(mesh => {
                if (mesh.material && mesh.material.transparent) {
                    mesh.material.opacity = opacity;
                }
            });
        }
    }
    
    // 获取多面体信息
    getPolyhedronInfo() {
        if (!this.polyhedronGroup) return null;
        
        const info = {
            count: this.polyhedronGroup.children.length,
            types: {}
        };
        
        this.polyhedronGroup.children.forEach(mesh => {
            const geometryType = mesh.userData.geometryType || 'unknown';
            info.types[geometryType] = (info.types[geometryType] || 0) + 1;
        });
        
        return info;
    }
    
    // 销毁预览器
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.clearModel();
        if (this.renderer) {
            this.renderer.dispose();
        }
        this.container.innerHTML = '';
    }
}