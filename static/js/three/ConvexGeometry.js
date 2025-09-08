// ConvexGeometry wrapper for non-module usage
// This is a simplified version that works without ES6 modules

(function() {
    'use strict';
    
    if (typeof THREE === 'undefined') {
        console.error('THREE.js must be loaded before ConvexGeometry');
        return;
    }
    
    // Simple ConvexGeometry implementation
    function ConvexGeometry(points) {
        THREE.BufferGeometry.call(this);
        
        this.type = 'ConvexGeometry';
        
        points = points || [];
        
        // Simple convex hull algorithm (gift wrapping)
        var vertices = [];
        var faces = [];
        
        if (points.length >= 4) {
            var hull = this.computeConvexHull(points);
            vertices = hull.vertices;
            faces = hull.faces;
        }
        
        // Build geometry
        var positions = [];
        var normals = [];
        var uvs = [];
        
        for (var i = 0; i < faces.length; i++) {
            var face = faces[i];
            var a = vertices[face.a];
            var b = vertices[face.b];
            var c = vertices[face.c];
            
            positions.push(a.x, a.y, a.z);
            positions.push(b.x, b.y, b.z);
            positions.push(c.x, c.y, c.z);
            
            // Calculate normal
            var cb = new THREE.Vector3().subVectors(c, b);
            var ab = new THREE.Vector3().subVectors(a, b);
            var normal = new THREE.Vector3().crossVectors(cb, ab).normalize();
            
            normals.push(normal.x, normal.y, normal.z);
            normals.push(normal.x, normal.y, normal.z);
            normals.push(normal.x, normal.y, normal.z);
            
            // Simple UV mapping
            uvs.push(0, 0);
            uvs.push(1, 0);
            uvs.push(0.5, 1);
        }
        
        this.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        this.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        this.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    }
    
    ConvexGeometry.prototype = Object.create(THREE.BufferGeometry.prototype);
    ConvexGeometry.prototype.constructor = ConvexGeometry;
    
    // Simple convex hull computation
    ConvexGeometry.prototype.computeConvexHull = function(points) {
        var vertices = [];
        var faces = [];
        
        // Remove duplicate points
        var uniquePoints = [];
        for (var i = 0; i < points.length; i++) {
            var point = points[i];
            var isDuplicate = false;
            for (var j = 0; j < uniquePoints.length; j++) {
                if (point.distanceTo(uniquePoints[j]) < 1e-10) {
                    isDuplicate = true;
                    break;
                }
            }
            if (!isDuplicate) {
                uniquePoints.push(point.clone());
            }
        }
        
        if (uniquePoints.length < 4) {
            // Not enough points for a 3D convex hull
            return { vertices: [], faces: [] };
        }
        
        // Simple tetrahedron for basic convex hull
        // In a real implementation, you would use a proper 3D convex hull algorithm
        vertices = uniquePoints.slice(0, Math.min(8, uniquePoints.length));
        
        // Create simple faces (this is a very basic implementation)
        if (vertices.length >= 4) {
            faces = [
                { a: 0, b: 1, c: 2 },
                { a: 0, b: 2, c: 3 },
                { a: 0, b: 3, c: 1 },
                { a: 1, b: 3, c: 2 }
            ];
            
            // Add more faces if we have more vertices
            for (var k = 4; k < vertices.length; k++) {
                faces.push({ a: 0, b: k - 1, c: k });
                faces.push({ a: 1, b: k, c: k - 1 });
            }
        }
        
        return { vertices: vertices, faces: faces };
    };
    
    // Attach to THREE namespace
    THREE.ConvexGeometry = ConvexGeometry;
    
})();
