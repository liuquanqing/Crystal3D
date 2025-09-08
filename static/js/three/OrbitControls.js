// OrbitControls wrapper for non-module usage
// This is a simplified version that works without ES6 modules

(function() {
    'use strict';
    
    if (typeof THREE === 'undefined') {
        console.error('THREE.js must be loaded before OrbitControls');
        return;
    }
    
    // Simple OrbitControls implementation
    function OrbitControls(object, domElement) {
        this.object = object;
        this.domElement = domElement || document;
        
        // Basic properties
        this.enabled = true;
        this.target = new THREE.Vector3();
        this.minDistance = 0;
        this.maxDistance = Infinity;
        this.minZoom = 0;
        this.maxZoom = Infinity;
        this.minPolarAngle = 0;
        this.maxPolarAngle = Math.PI;
        this.minAzimuthAngle = -Infinity;
        this.maxAzimuthAngle = Infinity;
        this.enableDamping = false;
        this.dampingFactor = 0.05;
        this.enableZoom = true;
        this.zoomSpeed = 1.0;
        this.enableRotate = true;
        this.rotateSpeed = 1.0;
        this.enablePan = true;
        this.panSpeed = 1.0;
        this.screenSpacePanning = true;
        this.keyPanSpeed = 7.0;
        this.autoRotate = false;
        this.autoRotateSpeed = 2.0;
        
        // Mouse buttons
        this.mouseButtons = {
            LEFT: THREE.MOUSE.ROTATE,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.PAN
        };
        
        // Internal state
        var scope = this;
        var state = { NONE: -1, ROTATE: 0, DOLLY: 1, PAN: 2, TOUCH_ROTATE: 3, TOUCH_PAN: 4, TOUCH_DOLLY_PAN: 5, TOUCH_DOLLY_ROTATE: 6 };
        var currentState = state.NONE;
        
        var EPS = 0.000001;
        var spherical = new THREE.Spherical();
        var sphericalDelta = new THREE.Spherical();
        var scale = 1;
        var panOffset = new THREE.Vector3();
        var zoomChanged = false;
        
        var rotateStart = new THREE.Vector2();
        var rotateEnd = new THREE.Vector2();
        var rotateDelta = new THREE.Vector2();
        
        var panStart = new THREE.Vector2();
        var panEnd = new THREE.Vector2();
        var panDelta = new THREE.Vector2();
        
        var dollyStart = new THREE.Vector2();
        var dollyEnd = new THREE.Vector2();
        var dollyDelta = new THREE.Vector2();
        
        // Basic update function
        this.update = function() {
            var offset = new THREE.Vector3();
            var quat = new THREE.Quaternion().setFromUnitVectors(object.up, new THREE.Vector3(0, 1, 0));
            var quatInverse = quat.clone().invert();
            var lastPosition = new THREE.Vector3();
            var lastQuaternion = new THREE.Quaternion();
            
            return function update() {
                var position = scope.object.position;
                offset.copy(position).sub(scope.target);
                offset.applyQuaternion(quat);
                spherical.setFromVector3(offset);
                
                if (scope.autoRotate && currentState === state.NONE) {
                    rotateLeft(getAutoRotationAngle());
                }
                
                spherical.theta += sphericalDelta.theta;
                spherical.phi += sphericalDelta.phi;
                spherical.theta = Math.max(scope.minAzimuthAngle, Math.min(scope.maxAzimuthAngle, spherical.theta));
                spherical.phi = Math.max(scope.minPolarAngle, Math.min(scope.maxPolarAngle, spherical.phi));
                spherical.makeSafe();
                spherical.radius *= scale;
                spherical.radius = Math.max(scope.minDistance, Math.min(scope.maxDistance, spherical.radius));
                
                scope.target.add(panOffset);
                offset.setFromSpherical(spherical);
                offset.applyQuaternion(quatInverse);
                position.copy(scope.target).add(offset);
                scope.object.lookAt(scope.target);
                
                if (scope.enableDamping === true) {
                    sphericalDelta.theta *= (1 - scope.dampingFactor);
                    sphericalDelta.phi *= (1 - scope.dampingFactor);
                    panOffset.multiplyScalar(1 - scope.dampingFactor);
                } else {
                    sphericalDelta.set(0, 0, 0);
                    panOffset.set(0, 0, 0);
                }
                
                scale = 1;
                
                if (zoomChanged || lastPosition.distanceToSquared(scope.object.position) > EPS || 8 * (1 - lastQuaternion.dot(scope.object.quaternion)) > EPS) {
                    lastPosition.copy(scope.object.position);
                    lastQuaternion.copy(scope.object.quaternion);
                    zoomChanged = false;
                    return true;
                }
                
                return false;
            };
        }();
        
        function getAutoRotationAngle() {
            return 2 * Math.PI / 60 / 60 * scope.autoRotateSpeed;
        }
        
        function rotateLeft(angle) {
            sphericalDelta.theta -= angle;
        }
        
        function rotateUp(angle) {
            sphericalDelta.phi -= angle;
        }
        
        // Event handlers
        function onMouseDown(event) {
            if (scope.enabled === false) return;
            
            event.preventDefault();
            
            switch (event.button) {
                case 0: // left
                    if (event.ctrlKey || event.metaKey || event.shiftKey) {
                        if (scope.enablePan === false) return;
                        handleMouseDownPan(event);
                        currentState = state.PAN;
                    } else {
                        if (scope.enableRotate === false) return;
                        handleMouseDownRotate(event);
                        currentState = state.ROTATE;
                    }
                    break;
                case 1: // middle
                    if (scope.enableZoom === false) return;
                    handleMouseDownDolly(event);
                    currentState = state.DOLLY;
                    break;
                case 2: // right
                    if (scope.enablePan === false) return;
                    handleMouseDownPan(event);
                    currentState = state.PAN;
                    break;
            }
            
            if (currentState !== state.NONE) {
                document.addEventListener('mousemove', onMouseMove, false);
                document.addEventListener('mouseup', onMouseUp, false);
            }
        }
        
        function onMouseMove(event) {
            if (scope.enabled === false) return;
            
            event.preventDefault();
            
            switch (currentState) {
                case state.ROTATE:
                    if (scope.enableRotate === false) return;
                    handleMouseMoveRotate(event);
                    break;
                case state.DOLLY:
                    if (scope.enableZoom === false) return;
                    handleMouseMoveDolly(event);
                    break;
                case state.PAN:
                    if (scope.enablePan === false) return;
                    handleMouseMovePan(event);
                    break;
            }
        }
        
        function onMouseUp(event) {
            if (scope.enabled === false) return;
            
            document.removeEventListener('mousemove', onMouseMove, false);
            document.removeEventListener('mouseup', onMouseUp, false);
            
            currentState = state.NONE;
        }
        
        function onMouseWheel(event) {
            if (scope.enabled === false || scope.enableZoom === false || (currentState !== state.NONE && currentState !== state.ROTATE)) return;
            
            event.preventDefault();
            event.stopPropagation();
            
            handleMouseWheel(event);
        }
        
        function handleMouseDownRotate(event) {
            rotateStart.set(event.clientX, event.clientY);
        }
        
        function handleMouseDownDolly(event) {
            dollyStart.set(event.clientX, event.clientY);
        }
        
        function handleMouseDownPan(event) {
            panStart.set(event.clientX, event.clientY);
        }
        
        function handleMouseMoveRotate(event) {
            rotateEnd.set(event.clientX, event.clientY);
            rotateDelta.subVectors(rotateEnd, rotateStart).multiplyScalar(scope.rotateSpeed);
            var element = scope.domElement === document ? scope.domElement.body : scope.domElement;
            rotateLeft(2 * Math.PI * rotateDelta.x / element.clientHeight);
            rotateUp(2 * Math.PI * rotateDelta.y / element.clientHeight);
            rotateStart.copy(rotateEnd);
            scope.update();
        }
        
        function handleMouseMoveDolly(event) {
            dollyEnd.set(event.clientX, event.clientY);
            dollyDelta.subVectors(dollyEnd, dollyStart);
            if (dollyDelta.y > 0) {
                dollyIn(getZoomScale());
            } else if (dollyDelta.y < 0) {
                dollyOut(getZoomScale());
            }
            dollyStart.copy(dollyEnd);
            scope.update();
        }
        
        function handleMouseMovePan(event) {
            panEnd.set(event.clientX, event.clientY);
            panDelta.subVectors(panEnd, panStart).multiplyScalar(scope.panSpeed);
            pan(panDelta.x, panDelta.y);
            panStart.copy(panEnd);
            scope.update();
        }
        
        function handleMouseWheel(event) {
            if (event.deltaY < 0) {
                dollyOut(getZoomScale());
            } else if (event.deltaY > 0) {
                dollyIn(getZoomScale());
            }
            scope.update();
        }
        
        function dollyIn(dollyScale) {
            if (scope.object.isPerspectiveCamera) {
                scale /= dollyScale;
            } else if (scope.object.isOrthographicCamera) {
                scope.object.zoom = Math.max(scope.minZoom, Math.min(scope.maxZoom, scope.object.zoom * dollyScale));
                scope.object.updateProjectionMatrix();
                zoomChanged = true;
            }
        }
        
        function dollyOut(dollyScale) {
            if (scope.object.isPerspectiveCamera) {
                scale *= dollyScale;
            } else if (scope.object.isOrthographicCamera) {
                scope.object.zoom = Math.max(scope.minZoom, Math.min(scope.maxZoom, scope.object.zoom / dollyScale));
                scope.object.updateProjectionMatrix();
                zoomChanged = true;
            }
        }
        
        function getZoomScale() {
            return Math.pow(0.95, scope.zoomSpeed);
        }
        
        function pan(deltaX, deltaY) {
            var element = scope.domElement === document ? scope.domElement.body : scope.domElement;
            
            if (scope.object.isPerspectiveCamera) {
                var position = scope.object.position;
                var offset = position.clone().sub(scope.target);
                var targetDistance = offset.length();
                targetDistance *= Math.tan((scope.object.fov / 2) * Math.PI / 180.0);
                panLeft(2 * deltaX * targetDistance / element.clientHeight, scope.object.matrix);
                panUp(2 * deltaY * targetDistance / element.clientHeight, scope.object.matrix);
            } else if (scope.object.isOrthographicCamera) {
                panLeft(deltaX * (scope.object.right - scope.object.left) / scope.object.zoom / element.clientWidth, scope.object.matrix);
                panUp(deltaY * (scope.object.top - scope.object.bottom) / scope.object.zoom / element.clientHeight, scope.object.matrix);
            }
        }
        
        function panLeft(distance, objectMatrix) {
            var v = new THREE.Vector3();
            v.setFromMatrixColumn(objectMatrix, 0);
            v.multiplyScalar(-distance);
            panOffset.add(v);
        }
        
        function panUp(distance, objectMatrix) {
            var v = new THREE.Vector3();
            if (scope.screenSpacePanning === true) {
                v.setFromMatrixColumn(objectMatrix, 1);
            } else {
                v.setFromMatrixColumn(objectMatrix, 0);
                v.crossVectors(scope.object.up, v);
            }
            v.multiplyScalar(distance);
            panOffset.add(v);
        }
        
        // Initialize event listeners
        this.domElement.addEventListener('mousedown', onMouseDown, false);
        this.domElement.addEventListener('wheel', onMouseWheel, false);
        
        // Dispose method
        this.dispose = function() {
            scope.domElement.removeEventListener('mousedown', onMouseDown, false);
            scope.domElement.removeEventListener('wheel', onMouseWheel, false);
            document.removeEventListener('mousemove', onMouseMove, false);
            document.removeEventListener('mouseup', onMouseUp, false);
        };
        
        // Initial update
        this.update();
    }
    
    // Attach to THREE namespace
    THREE.OrbitControls = OrbitControls;
    
})();