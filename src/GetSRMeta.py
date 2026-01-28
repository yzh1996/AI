import mysql.connector
from graphviz import Digraph
import re

# ========================
# StarRocks 连接配置（请按你的环境修改）
# ========================
STARROCKS_CONFIG = {
    'host': '192.168.8.33',
    'port': 2030,  # ←←← 关键：StarRocks 的 MySQL 协议端口
    'user': 'root',
    'password': 'quxing2021',
    'database': 'donggua',
    'charset': 'utf8mb4'
}


def get_db_connection():
    """建立 StarRocks 连接"""
    return mysql.connector.connect(**STARROCKS_CONFIG)


def get_create_statement(obj_name, obj_type='VIEW'):
    """
    获取视图或表的创建语句
    obj_type: 'VIEW' 或 'TABLE'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if obj_type == 'VIEW':
            cursor.execute(f"SHOW CREATE VIEW `{obj_name}`")
        else:
            cursor.execute(f"SHOW CREATE TABLE `{obj_name}`")
        row = cursor.fetchone()
        return row[1] if row else None
    except Exception as e:
        print(f"⚠️ 无法获取 {obj_type} `{obj_name}`: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def extract_table_names(sql_text):
    """
    从 SQL 文本中提取所有表/视图名（简化版，适用于 StarRocks）
    注意：这是一个启发式解析，复杂嵌套需更强大 parser（如 sqlglot）
    """
    if not sql_text:
        return set()

    # 移除注释和换行
    sql = re.sub(r'--.* $ ', '', sql_text, flags=re.MULTILINE)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    sql = ' '.join(sql.split())

    # 匹配 FROM / JOIN 后的表名（支持 `db`.`table` 或 `table`）
    pattern = r'(?:FROM|JOIN)\s+(`(?:[^`]+`.`[^`]+|[^`]+)`)'
    matches = re.findall(pattern, sql, re.IGNORECASE)

    tables = set()
    for match in matches:
        # 去掉反引号
        name = match.strip('`')
        # 如果包含库名（如 donggua.anchor_daily），只取表名（可选）
        if '.' in name:
            name = name.split('.')[-1]
        tables.add(name)
    return tables


def build_lineage(view_name, visited=None, graph=None, parent=None):
    """
    递归构建血缘关系
    :param view_name: 当前视图名
    :param visited: 已访问节点（防循环）
    :param graph: Graphviz 对象
    :param parent: 上游节点
    :return: 所有底层表集合
    """
    if visited is None:
        visited = set()
    if graph is None:
        graph = Digraph(comment='StarRocks View Lineage')
        graph.attr(rankdir='TB')  # 从上到下布局

    if view_name in visited:
        return visited, graph
    visited.add(view_name)

    # 添加当前节点
    graph.node(view_name, shape='box', style='filled', fillcolor='#d0e1ff')

    # 获取定义
    create_sql = get_create_statement(view_name, 'VIEW')
    if not create_sql:
        # 可能是基础表
        create_sql = get_create_statement(view_name, 'TABLE')
        if create_sql:
            graph.node(view_name, shape='ellipse', style='filled', fillcolor='#c8e6c9')
        return visited, graph

    # 提取依赖
    dependencies = extract_table_names(create_sql)
    print(f"🔍 {view_name} 依赖: {dependencies}")

    for dep in dependencies:
        # 添加边
        graph.edge(view_name, dep)
        # 递归
        build_lineage(dep, visited, graph, view_name)

    return visited, graph


def main(start_view):
    print(f"🚀 开始分析视图血缘: {start_view}")
    visited, graph = build_lineage(start_view)

    # 保存为 PDF/PNG
    # output_file = f"lineage_{start_view}"
    # graph.render(output_file, format='png', cleanup=True)
    # print(f"✅ 血缘图已生成: {output_file}.png")

    # 打印所有依赖
    print("\n📋 完整依赖链:")
    for node in sorted(visited):
        print(f"  - {node}")


if __name__ == "__main__":
    # 替换为你想分析的视图名
    START_VIEW = "live_base_view"
    main(START_VIEW)