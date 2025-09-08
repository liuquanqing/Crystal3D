// ConvexHull wrapper for non-module usage
// This is a simplified version that works without ES6 modules

(function() {
    'use strict';
    
    if (typeof THREE === 'undefined') {
        console.error('THREE.js must be loaded before ConvexHull');
        return;
    }
    
    // Simple ConvexHull implementation
    function ConvexHull() {
        this.tolerance = -1;
        this.faces = [];
        this.newFaces = [];
        this.assigned = new VertexList();
        this.unassigned = new VertexList();
        this.vertices = [];
    }
    
    ConvexHull.prototype = {
        setFromPoints: function(points) {
            if (Array.isArray(points) !== true) {
                console.error('ConvexHull: Points parameter is not an array.');
                return this;
            }
            
            if (points.length < 4) {
                console.error('ConvexHull: The algorithm needs at least four points.');
                return this;
            }
            
            this.makeEmpty();
            
            for (var i = 0, l = points.length; i < l; i++) {
                this.vertices.push(new VertexNode(points[i]));
            }
            
            this.compute();
            
            return this;
        },
        
        makeEmpty: function() {
            this.faces = [];
            this.vertices = [];
            return this;
        },
        
        compute: function() {
            var vertex;
            
            this.computeInitialHull();
            
            // Add remaining vertices one by one
            while ((vertex = this.nextVertexToAdd()) !== undefined) {
                this.addVertexToHull(vertex);
            }
            
            this.reindexFaces();
            
            return this;
        },
        
        computeInitialHull: function() {
            var vertices = this.vertices;
            var min = new THREE.Vector3();
            var max = new THREE.Vector3();
            
            // Find extremes
            min.copy(vertices[0].point);
            max.copy(vertices[0].point);
            
            for (var i = 1; i < vertices.length; i++) {
                var point = vertices[i].point;
                min.min(point);
                max.max(point);
            }
            
            // Create initial tetrahedron
            var v0 = vertices[0];
            var v1 = vertices[1];
            var v2 = vertices[2];
            var v3 = vertices[3];
            
            // Create four faces
            var faces = [
                Face.create(v0, v1, v2),
                Face.create(v3, v1, v0),
                Face.create(v3, v2, v1),
                Face.create(v3, v0, v2)
            ];
            
            this.faces.push(faces[0], faces[1], faces[2], faces[3]);
            
            // Assign remaining vertices
            for (var j = 4; j < vertices.length; j++) {
                this.addVertexToFace(vertices[j], faces[0]);
            }
            
            return this;
        },
        
        addVertexToFace: function(vertex, face) {
            vertex.face = face;
            
            if (face.outside === undefined) {
                this.assigned.append(vertex);
            } else {
                this.assigned.insertBefore(face.outside, vertex);
            }
            
            face.outside = vertex;
            
            return this;
        },
        
        nextVertexToAdd: function() {
            if (this.assigned.isEmpty() === false) {
                var eyeVertex, maxDistance = 0;
                var vertex = this.assigned.first();
                
                do {
                    if (vertex.distance > maxDistance) {
                        maxDistance = vertex.distance;
                        eyeVertex = vertex;
                    }
                    vertex = vertex.next;
                } while (vertex !== undefined);
                
                return eyeVertex;
            }
        },
        
        addVertexToHull: function(eyeVertex) {
            var horizon = [];
            
            this.unassigned.clear();
            
            this.removeVertexFromFace(eyeVertex, eyeVertex.face);
            this.computeHorizon(eyeVertex.point, null, eyeVertex.face, horizon);
            
            this.newFaces = [];
            
            // Create new faces
            for (var i = 0; i < horizon.length; i += 2) {
                var edge = horizon[i];
                var face = horizon[i + 1];
                
                var newFace = this.createTriangle(eyeVertex, edge.tail(), edge.head(), face);
                this.newFaces.push(newFace);
            }
            
            // Reassign unassigned vertices
            this.resolveUnassignedPoints(this.newFaces);
            
            return this;
        },
        
        removeVertexFromFace: function(vertex, face) {
            if (vertex === face.outside) {
                if (vertex.next !== undefined && vertex.next.face === face) {
                    face.outside = vertex.next;
                } else {
                    face.outside = undefined;
                }
            }
            
            this.assigned.remove(vertex);
            
            return this;
        },
        
        computeHorizon: function(eyePoint, crossEdge, face, horizon) {
            this.deleteFaceVertices(face);
            face.mark = 'deleted';
            
            var edge;
            
            if (crossEdge === null) {
                edge = crossEdge = face.getEdge(0);
            } else {
                edge = crossEdge.next;
            }
            
            do {
                var twinEdge = edge.twin;
                var oppositeFace = twinEdge.face;
                
                if (oppositeFace.mark === 'deleted') {
                    edge = edge.next;
                    continue;
                }
                
                if (this.visible(eyePoint, oppositeFace) === true) {
                    this.computeHorizon(eyePoint, twinEdge, oppositeFace, horizon);
                } else {
                    horizon.push(edge, oppositeFace);
                }
                
                edge = edge.next;
            } while (edge !== crossEdge);
            
            return this;
        },
        
        deleteFaceVertices: function(face, absorbingFace) {
            var faceVertices = this.removeAllVerticesFromFace(face);
            
            if (faceVertices !== undefined) {
                if (absorbingFace === undefined) {
                    this.unassigned.appendChain(faceVertices);
                } else {
                    var vertex = faceVertices;
                    
                    do {
                        var nextVertex = vertex.next;
                        var distance = absorbingFace.distanceToPoint(vertex.point);
                        
                        if (distance > this.tolerance) {
                            this.addVertexToFace(vertex, absorbingFace);
                        } else {
                            this.unassigned.append(vertex);
                        }
                        
                        vertex = nextVertex;
                    } while (vertex !== undefined);
                }
            }
            
            return this;
        },
        
        removeAllVerticesFromFace: function(face) {
            if (face.outside !== undefined) {
                var start = face.outside;
                var end = face.outside;
                
                while (end.next !== undefined && end.next.face === face) {
                    end = end.next;
                }
                
                this.assigned.removeChain(start, end);
                
                start.prev = end.next = undefined;
                face.outside = undefined;
                
                return start;
            }
        },
        
        visible: function(eyePoint, face) {
            return face.distanceToPoint(eyePoint) > this.tolerance;
        },
        
        createTriangle: function(eyeVertex, a, b, face) {
            var newFace = Face.create(eyeVertex, a, b);
            this.faces.push(newFace);
            
            // Connect edges
            this.connectEdge(newFace.getEdge(0), face.getEdge(0));
            
            return newFace;
        },
        
        connectEdge: function(edge1, edge2) {
            edge1.twin = edge2;
            edge2.twin = edge1;
        },
        
        resolveUnassignedPoints: function(newFaces) {
            if (this.unassigned.isEmpty() === false) {
                var vertex = this.unassigned.first();
                
                do {
                    var nextVertex = vertex.next;
                    var maxDistance = this.tolerance;
                    var maxFace = null;
                    
                    for (var i = 0; i < newFaces.length; i++) {
                        var face = newFaces[i];
                        
                        if (face.mark === 'visible') {
                            var distance = face.distanceToPoint(vertex.point);
                            
                            if (distance > maxDistance) {
                                maxDistance = distance;
                                maxFace = face;
                            }
                            
                            if (maxDistance > 1000 * this.tolerance) break;
                        }
                    }
                    
                    if (maxFace !== null) {
                        this.addVertexToFace(vertex, maxFace);
                    }
                    
                    vertex = nextVertex;
                } while (vertex !== undefined);
            }
            
            return this;
        },
        
        reindexFaces: function() {
            var activeFaces = [];
            
            for (var i = 0; i < this.faces.length; i++) {
                var face = this.faces[i];
                
                if (face.mark !== 'deleted') {
                    activeFaces.push(face);
                }
            }
            
            this.faces = activeFaces;
            
            return this;
        }
    };
    
    // Helper classes
    function VertexNode(point) {
        this.point = point;
        this.prev = undefined;
        this.next = undefined;
        this.face = undefined;
        this.distance = 0;
    }
    
    function VertexList() {
        this.head = undefined;
        this.tail = undefined;
    }
    
    VertexList.prototype = {
        first: function() {
            return this.head;
        },
        
        last: function() {
            return this.tail;
        },
        
        clear: function() {
            this.head = this.tail = undefined;
            return this;
        },
        
        isEmpty: function() {
            return this.head === undefined;
        },
        
        append: function(vertex) {
            if (this.head === undefined) {
                this.head = vertex;
            } else {
                this.tail.next = vertex;
            }
            
            vertex.prev = this.tail;
            vertex.next = undefined;
            this.tail = vertex;
            
            return this;
        },
        
        appendChain: function(vertex) {
            if (this.head === undefined) {
                this.head = vertex;
            } else {
                this.tail.next = vertex;
            }
            
            vertex.prev = this.tail;
            
            while (vertex.next !== undefined) {
                vertex = vertex.next;
            }
            
            this.tail = vertex;
            
            return this;
        },
        
        remove: function(vertex) {
            if (vertex.prev === undefined) {
                this.head = vertex.next;
            } else {
                vertex.prev.next = vertex.next;
            }
            
            if (vertex.next === undefined) {
                this.tail = vertex.prev;
            } else {
                vertex.next.prev = vertex.prev;
            }
            
            return this;
        },
        
        removeChain: function(a, b) {
            if (a.prev === undefined) {
                this.head = b.next;
            } else {
                a.prev.next = b.next;
            }
            
            if (b.next === undefined) {
                this.tail = a.prev;
            } else {
                b.next.prev = a.prev;
            }
            
            return this;
        },
        
        insertBefore: function(target, vertex) {
            vertex.prev = target.prev;
            vertex.next = target;
            
            if (vertex.prev === undefined) {
                this.head = vertex;
            } else {
                vertex.prev.next = vertex;
            }
            
            target.prev = vertex;
            
            return this;
        }
    };
    
    function Face() {
        this.normal = new THREE.Vector3();
        this.midpoint = new THREE.Vector3();
        this.area = 0;
        this.constant = 0;
        this.outside = undefined;
        this.mark = 'visible';
        this.edge = undefined;
    }
    
    Face.create = function(a, b, c) {
        var face = new Face();
        
        var e0 = new HalfEdge(a, face);
        var e1 = new HalfEdge(b, face);
        var e2 = new HalfEdge(c, face);
        
        e0.next = e2.prev = e1;
        e1.next = e0.prev = e2;
        e2.next = e1.prev = e0;
        
        face.edge = e0;
        
        return face.compute();
    };
    
    Face.prototype = {
        getEdge: function(i) {
            var edge = this.edge;
            
            while (i > 0) {
                edge = edge.next;
                i--;
            }
            
            while (i < 0) {
                edge = edge.prev;
                i++;
            }
            
            return edge;
        },
        
        compute: function() {
            var a = this.edge.tail();
            var b = this.edge.head();
            var c = this.edge.next.head();
            
            var triangle = new THREE.Triangle(a.point, b.point, c.point);
            
            triangle.getNormal(this.normal);
            triangle.getMidpoint(this.midpoint);
            this.area = triangle.getArea();
            
            this.constant = this.normal.dot(this.midpoint);
            
            return this;
        },
        
        distanceToPoint: function(point) {
            return this.normal.dot(point) - this.constant;
        }
    };
    
    function HalfEdge(vertex, face) {
        this.vertex = vertex;
        this.prev = undefined;
        this.next = undefined;
        this.twin = undefined;
        this.face = face;
    }
    
    HalfEdge.prototype = {
        head: function() {
            return this.vertex;
        },
        
        tail: function() {
            return this.prev ? this.prev.vertex : undefined;
        },
        
        length: function() {
            var head = this.head();
            var tail = this.tail();
            
            if (tail) {
                return tail.point.distanceTo(head.point);
            }
            
            return -1;
        },
        
        lengthSquared: function() {
            var head = this.head();
            var tail = this.tail();
            
            if (tail) {
                return tail.point.distanceToSquared(head.point);
            }
            
            return -1;
        }
    };
    
    // Attach to THREE namespace
    THREE.ConvexHull = ConvexHull;
    
})();
