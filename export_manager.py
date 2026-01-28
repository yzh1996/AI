#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出管理模块
支持多种格式导出依赖关系
"""

from typing import Dict, List, Set, Optional
from graphviz import Digraph
import io


class ExportManager:
    """导出管理器"""

    def __init__(self, analyzer):
        """
        初始化导出管理器

        Args:
            analyzer: ViewDependencyAnalyzer 实例
        """
        self.analyzer = analyzer

    def build_dependency_tree(self, root_object: str, max_depth: Optional[int] = None) -> Dict:
        """
        构建依赖树

        Args:
            root_object: 根对象名称
            max_depth: 最大递归深度，None 表示无限制

        Returns:
            依赖树字典
        """
        visited = set()

        def traverse(obj_name: str, current_depth: int = 0) -> Dict:
            if max_depth is not None and current_depth >= max_depth:
                return None

            if obj_name in visited:
                return None

            visited.add(obj_name)

            obj_type = self.analyzer.get_object_type(obj_name)
            if not obj_type:
                return None

            node = {
                'name': obj_name,
                'type': obj_type,
                'dependencies': []
            }

            if obj_type == 'view':
                deps = self.analyzer.get_direct_dependencies(obj_name)
                for dep in deps:
                    child = traverse(dep['name'], current_depth + 1)
                    if child:
                        node['dependencies'].append(child)

            return node

        return traverse(root_object)

    def export_mermaid(self, root_object: str, max_depth: Optional[int] = None) -> str:
        """
        导出为 Mermaid 图表代码

        Args:
            root_object: 根对象名称
            max_depth: 最大递归深度

        Returns:
            Mermaid 代码字符串
        """
        tree = self.build_dependency_tree(root_object, max_depth)
        if not tree:
            return "graph TD\n    Error[对象不存在]"

        lines = ["graph TD"]
        node_id_map = {}
        node_counter = [0]

        def get_node_id(name: str) -> str:
            if name not in node_id_map:
                node_counter[0] += 1
                node_id_map[name] = f"N{node_counter[0]}"
            return node_id_map[name]

        def traverse(node: Dict):
            node_id = get_node_id(node['name'])
            node_type = node['type'].upper()

            # 视图用方框，表用圆角矩形
            if node['type'] == 'view':
                lines.append(f"    {node_id}[\"{node['name']} - {node_type}\"]")
            else:
                lines.append(f"    {node_id}(\"{node['name']} - {node_type}\")")

            for dep in node['dependencies']:
                dep_id = get_node_id(dep['name'])
                lines.append(f"    {node_id} --> {dep_id}")
                traverse(dep)

        traverse(tree)

        return "\n".join(lines)

    def export_dot(self, root_object: str, max_depth: Optional[int] = None) -> str:
        """
        导出为 Graphviz DOT 格式

        Args:
            root_object: 根对象名称
            max_depth: 最大递归深度

        Returns:
            DOT 格式字符串
        """
        tree = self.build_dependency_tree(root_object, max_depth)
        if not tree:
            return "digraph { Error [label=\"对象不存在\"]; }"

        dot = Digraph(comment='Dependency Graph')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box', style='filled')

        visited_edges = set()

        def traverse(node: Dict):
            node_name = node['name']

            # 视图用蓝色方框，表用绿色椭圆
            if node['type'] == 'view':
                dot.node(node_name, f"{node_name}\n(VIEW)",
                        fillcolor='lightblue', shape='box')
            else:
                dot.node(node_name, f"{node_name}\n(TABLE)",
                        fillcolor='lightgreen', shape='ellipse')

            for dep in node['dependencies']:
                edge = (node_name, dep['name'])
                if edge not in visited_edges:
                    visited_edges.add(edge)
                    dot.edge(node_name, dep['name'])
                    traverse(dep)

        traverse(tree)

        return dot.source

    def export_image(self, root_object: str, format: str = 'png',
                    max_depth: Optional[int] = None) -> bytes:
        """
        导出为图片格式

        Args:
            root_object: 根对象名称
            format: 图片格式 ('png' 或 'svg')
            max_depth: 最大递归深度

        Returns:
            图片二进制数据
        """
        tree = self.build_dependency_tree(root_object, max_depth)
        if not tree:
            # 返回错误图片
            dot = Digraph()
            dot.node('Error', '对象不存在')
            return dot.pipe(format=format)

        dot = Digraph(comment='Dependency Graph')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box', style='filled', fontname='Arial')

        visited_edges = set()

        def traverse(node: Dict):
            node_name = node['name']

            # 视图用蓝色方框，表用绿色椭圆
            if node['type'] == 'view':
                dot.node(node_name, f"{node_name}\\n(VIEW)",
                        fillcolor='lightblue', shape='box')
            else:
                dot.node(node_name, f"{node_name}\\n(TABLE)",
                        fillcolor='lightgreen', shape='ellipse')

            for dep in node['dependencies']:
                edge = (node_name, dep['name'])
                if edge not in visited_edges:
                    visited_edges.add(edge)
                    dot.edge(node_name, dep['name'])
                    traverse(dep)

        traverse(tree)

        return dot.pipe(format=format)

    def export_json(self, root_object: str, max_depth: Optional[int] = None) -> Dict:
        """
        导出为 JSON 格式

        Args:
            root_object: 根对象名称
            max_depth: 最大递归深度

        Returns:
            JSON 字典
        """
        tree = self.build_dependency_tree(root_object, max_depth)

        return {
            'export_metadata': {
                'database': self.analyzer.database,
                'root_object': root_object,
                'export_date': __import__('datetime').datetime.now().isoformat(),
                'format_version': '1.0',
                'max_depth': max_depth
            },
            'dependency_tree': tree
        }
