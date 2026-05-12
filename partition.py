from typing import List, Set, Dict
from dataclasses import dataclass
import networkx as nx


"""
Estruturas de dados básicas 
    @dataclass Point: representa um vértice
    @dataclass Rectangle: representa um retângulo
"""

@dataclass
class Point:
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x},{self.y})"


@dataclass
class Rectangle:

    id: int
    vertices: List[Point]
    
    def __repr__(self):
        return f"R{self.id}"


"""Estrutura de dados para a partição retangular"""

class RectangularPartition:
    
    def __init__(self, rectangles: List[Rectangle]):
        self.rectangles = rectangles
        self.vertices: Set[Point] = set()
        
        self.vertex_to_rectangles: Dict[Point, Set[int]] = {}
        self.rectangle_to_vertices: Dict[int, Set[Point]] = {}
        
        self.graph = None
        self._build_structures()
    
    #construçao de mapas e grafos 
    def _build_structures(self):
        
        for rect in self.rectangles:
            self.rectangle_to_vertices[rect.id] = set(rect.vertices)
            for vertex in rect.vertices:
                self.vertices.add(vertex)
                if vertex not in self.vertex_to_rectangles:
                    self.vertex_to_rectangles[vertex] = set()
                self.vertex_to_rectangles[vertex].add(rect.id)
        
        self._build_incidence_graph()
    
    def _build_incidence_graph(self):

        self.graph = nx.Graph()
        
        # Adicionar nós de vértices
        for vertex in self.vertices:
            self.graph.add_node(('V', vertex), type='vertex')
        
        # Adicionar nós de retângulos
        for rect in self.rectangles:
            self.graph.add_node(('R', rect.id), type='rectangle')
        
        # Adicionar arestas
        for vertex, rect_ids in self.vertex_to_rectangles.items():
            for rect_id in rect_ids:
                self.graph.add_edge(('V', vertex), ('R', rect_id))


    """Funções de consulta:"""
    
    def get_rectangles_covered_by_vertex(self, vertex: Point) -> Set[int]:
        return self.vertex_to_rectangles.get(vertex, set())
    
    def get_vertices_of_rectangle(self, rect_id: int) -> Set[Point]:
        return self.rectangle_to_vertices.get(rect_id, set())
    
    def get_rectangles_at_distance(self, vertex: Point, distance: int) -> Set[int]:
        if distance == 0:
            return self.get_rectangles_covered_by_vertex(vertex)
        
        # aplicar BFS no grafo para encontrar vértices alcançáveis
        reachable = {vertex}
        current_level = {vertex}
        
        for _ in range(distance):
            next_level = set()
            for v in current_level:
                neighbors = self.get_vertex_neighbors(v, distance=1)
                next_level.update(neighbors)
            reachable.update(next_level)
            current_level = next_level
        
        covered = set()
        for v in reachable:
            covered.update(self.get_rectangles_covered_by_vertex(v))
        
        return covered
    
    def get_vertex_neighbors(self, vertex: Point, distance: int = 1) -> Set[Point]:
        """Vértices adjacentes no grafo"""
        neighbors = set()
        vertex_node = ('V', vertex)
        
        if vertex_node in self.graph:
            # Pegar retângulos incidentes
            incident_rects = [n for n in self.graph.neighbors(vertex_node) 
                            if n[0] == 'R']
            
            # Pegar outros vértices desses retângulos
            for rect_node in incident_rects:
                for neighbor in self.graph.neighbors(rect_node):
                    if neighbor[0] == 'V' and neighbor[1] != vertex:
                        neighbors.add(neighbor[1])
        
        return neighbors


"""Parser para ficheiros de partição
    Lê ficheiro com formato:
    num_instances
    num_rectangles
    rect_id num_vertices x1 y1 x2 y2 ...
    ..."""

def parse_partition_file(filename: str) -> List[RectangularPartition]:
    partitions = []
    
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    idx = 0
    num_instances = int(lines[idx])
    idx += 1
    
    for _ in range(num_instances):
        num_rectangles = int(lines[idx])
        idx += 1
        
        rectangles = []
        for _ in range(num_rectangles):
            parts = list(map(int, lines[idx].split()))
            
            rect_id = parts[0]
            num_vertices = parts[1]
            
            vertices = []
            for i in range(num_vertices):
                x = parts[2 + 2*i]
                y = parts[2 + 2*i + 1]
                vertices.append(Point(x, y))
            
            rectangles.append(Rectangle(rect_id, vertices))
            idx += 1
        
        partitions.append(RectangularPartition(rectangles))
    
    return partitions

#CUBANO E E DAVID VEJAM O QUE ACHAM
#ACHO QUE NÃO VOU METER NADA DE AQUI PARA O FICHEIRO DE TESTES, VOU DEIXAR SÓ AS ESTRUTURAS DE DADOS E O PARSER, PARA O TESTE FICAR MAIS SIMPLES.