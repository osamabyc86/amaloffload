# task_splitter.py
from typing import Dict, Any, List
import networkx as nx
import hashlib

class TaskSplitter:
    def __init__(self):
        self._dependency_graph = nx.DiGraph()
    
    def add_task(self, task_id: str, task: Dict[str, Any], deps: List[str] = []):
        """إضافة مهمة مع تبعياتها"""
        self._dependency_graph.add_node(task_id, task=task)
        for dep in deps:
            self._dependency_graph.add_edge(dep, task_id)
    
    def split_tasks(self) -> Dict[str, List[Dict]]:
        """تقسيم المهام إلى مجموعات متوازية"""
        clusters = {}
        for component in nx.weakly_connected_components(self._dependency_graph):
            subgraph = self._dependency_graph.subgraph(component)
            for level, nodes in enumerate(nx.topological_generations(subgraph)):
                for node in nodes:
                    cluster_id = self._generate_cluster_id(node, level)
                    if cluster_id not in clusters:
                        clusters[cluster_id] = []
                    clusters[cluster_id].append({
                        'task_id': node,
                        'task': self._dependency_graph.nodes[node]['task']
                    })
        return clusters
    
    def _generate_cluster_id(self, node: str, level: int) -> str:
        """إنشاء معرف فريد لكل مجموعة مهام"""
        deps = list(self._dependency_graph.predecessors(node))
        deps_hash = hashlib.md5(','.join(sorted(deps)).encode()).hexdigest()[:8]
        return f"L{level}-{deps_hash}"
