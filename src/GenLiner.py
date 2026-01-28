import re
from collections import defaultdict
from typing import Dict, List, Set, Optional
import pymysql
from abc import ABC, abstractmethod


class DatabaseConnection(ABC):
    """数据库连接抽象基类"""

    @abstractmethod
    def get_view_definition(self, view_name: str) -> str:
        """获取视图定义SQL"""
        pass

    @abstractmethod
    def get_table_columns(self, table_name: str) -> List[str]:
        """获取表的所有列名"""
        pass

    @abstractmethod
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        pass

    @abstractmethod
    def close(self):
        """关闭连接"""
        pass


class StarRocksConnection(DatabaseConnection):
    """StarRocks数据库连接实现"""

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )

    def get_view_definition(self, view_name: str) -> str:
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"SHOW CREATE VIEW `{view_name}`")
            result = cursor.fetchone()
            cursor.close()
            return result[1] if result else ""
        except Exception:
            # 如果不是视图，尝试获取普通表的创建语句
            try:
                cursor.execute(f"SHOW CREATE TABLE `{view_name}`")
                result = cursor.fetchone()
                cursor.close()
                return result[1] if result else ""
            except Exception:
                cursor.close()
                return ""

    def get_table_columns(self, table_name: str) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute(f"DESC `{table_name}`")
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return columns

    def get_all_tables(self) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute("SHOW FULL TABLES WHERE Table_type != 'VIEW'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def close(self):
        self.connection.close()


class TableDependencyAnalyzer:
    """表依赖关系分析器"""

    def __init__(self, db_connection: StarRocksConnection):
        self.db = db_connection
        self.dependency_map: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependency: Dict[str, Set[str]] = defaultdict(set)

    def extract_dependencies_from_sql(self, sql_text: str) -> Set[str]:
        """从SQL文本中提取表依赖关系"""
        # 更精确的正则表达式，匹配数据库名.表名或表名
        patterns = [
            # 匹配 FROM/JOIN 后面的表名（可能包含数据库名）
            r'(?:FROM|JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|LEFT\s+OUTER\s+JOIN|RIGHT\s+OUTER\s+JOIN|FULL\s+OUTER\s+JOIN|CROSS\s+JOIN)\s+`?[\w_]*`?\.?`?([a-zA-Z_][a-zA-Z0-9_]*)`?(?=\s|$|\s+ON|\s+AS|\s+WHERE|\s+GROUP|\s+ORDER)',
            # 匹配在括号内的子查询中的表名
            r'\(`?[\w_]*`?\.?`?([a-zA-Z_][a-zA-Z0-9_]*)`?(?=\s+\w+|\))',
        ]

        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, sql_text, re.IGNORECASE)
            for match in matches:
                # 过滤掉常见的SQL关键字
                if match.upper() not in [
                    'ON', 'AS', 'AND', 'OR', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'LIMIT', 'BY',
                    'USING', 'SELECT', 'DISTINCT', 'ALL', 'ANY', 'SOME', 'EXISTS', 'NOT', 'IN',
                    'BETWEEN', 'LIKE', 'IS', 'NULL', 'TRUE', 'FALSE', 'CASE', 'WHEN', 'THEN',
                    'ELSE', 'END', 'UNION', 'INTERSECT', 'EXCEPT', 'MINUS', 'HAVING', 'COMPUTE',
                    'INTO', 'FOR', 'CURSOR', 'WITH', 'RECURSIVE', 'TEMPORARY', 'TEMP', 'UNLOGGED',
                    'IF', 'ENDIF', 'LOOP', 'LEAVE', 'ITERATE', 'REPEAT', 'UNTIL', 'WHILE',
                    'RETURN', 'CALL', 'DO', 'EXECUTE', 'PREPARE', 'DEALLOCATE', 'BEGIN',
                    'TABLE', 'VIEW', 'INDEX', 'COLUMN', 'CONSTRAINT', 'PRIMARY', 'FOREIGN',
                    'KEY', 'UNIQUE', 'CHECK', 'DEFAULT', 'REFERENCES', 'CASCADE', 'RESTRICT',
                    'SET', 'NO', 'ACTION', 'MATCH', 'SIMPLE', 'FULL', 'PARTIAL', 'SOURCE',
                    'TARGET', 'ROLE', 'USER', 'GRANT', 'REVOKE', 'PRIVILEGES', 'ADMIN', 'OPTION',
                    'TRIGGER', 'PROCEDURE', 'FUNCTION', 'ROUTINE', 'PACKAGE', 'TYPE', 'DOMAIN',
                    'SCHEMA', 'CATALOG', 'DATABASE', 'SERVER', 'LINK', 'CONNECTION', 'SESSION',
                    'TRANSACTION', 'ISOLATION', 'LEVEL', 'READ', 'WRITE', 'COMMIT', 'ROLLBACK',
                    'SAVEPOINT', 'LOCK', 'SHARED', 'EXCLUSIVE', 'ROW', 'PAGE', 'TABLESPACE',
                    'EXTENT', 'SEGMENT', 'CLUSTER', 'SNAPSHOT', 'CONSISTENT', 'AUTOCOMMIT',
                    'IMPLICIT', 'EXPLICIT', 'TEMP', 'VOLATILE', 'STABLE', 'IMMUTABLE', 'CALLED',
                    'ON', 'NULL', 'INPUT', 'RETURNS', 'LANGUAGE', 'EXTERNAL', 'NAME', 'PARAMETER',
                    'MODE', 'IN', 'OUT', 'INOUT', 'VARIADIC', 'SETOF', 'TABLE', 'OF', 'UNDER',
                    'SCOPE', 'SPECIFIC', 'RESULT', 'DYNAMIC', 'FUNCTION', 'METHOD', 'MAP', 'ORDER',
                    'INSTANCE', 'STATIC', 'FINAL', 'OVERRIDING', 'MEMBER', 'CONSTRUCTOR', 'SELF',
                    'NEW', 'OLD', 'ROW_COUNT', 'FOUND', 'NOT_FOUND', 'SQLSTATE', 'SQLEXCEPTION',
                    'SQLWARNING', 'CONTINUE', 'EXIT', 'UNDO', 'SIGNAL', 'RESIGNAL', 'GET',
                    'DIAGNOSTICS', 'CONDITION', 'NUMBER', 'MESSAGE_TEXT', 'CLASS_ORIGIN',
                    'SUBCLASS_ORIGIN', 'CONSTRAINT_CATALOG', 'CONSTRAINT_SCHEMA', 'CONSTRAINT_NAME',
                    'CATALOG_NAME', 'SCHEMA_NAME', 'TABLE_NAME', 'COLUMN_NAME', 'CURSOR_NAME',
                    'CONNECTION_NAME', 'SERVER_NAME', 'DBINFO', 'SYSTEM_USER', 'USER', 'CURRENT_USER',
                    'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'LOCALTIME', 'LOCALTIMESTAMP',
                    'CURRENT_ROLE', 'SESSION_USER', 'CURRENT_PATH', 'CURRENT_TRANSFORM_GROUP_ID',
                    'TRUNCATE', 'DROP', 'CREATE', 'ALTER', 'ADD', 'MODIFY', 'CHANGE', 'RENAME',
                    'DELETE', 'INSERT', 'UPDATE', 'UPSERT', 'REPLACE', 'MERGE', 'ANALYZE', 'EXPLAIN',
                    'DESCRIBE', 'DESC', 'SHOW', 'USE', 'SET', 'RESET', 'KILL', 'PURGE', 'FLUSH',
                    'CACHE', 'UNCACHE', 'REFRESH', 'LOAD', 'UNLOAD', 'EXPORT', 'IMPORT', 'COPY',
                    'MOVE', 'LINK', 'SYMLINK', 'MKDIR', 'RM', 'LS', 'CAT', 'HEAD', 'TAIL', 'STAT',
                    'CHMOD', 'CHOWN', 'CHGRP', 'MV', 'CP', 'LN', 'RM', 'RMDIR', 'MKDIRS', 'SYNC',
                    'DISTCP', 'HAR', 'ARCHIVE', 'UNARCHIVE', 'COMPACT', 'CLEANUP', 'OPTIMIZE',
                    'MAINTAIN', 'MAINTENANCE', 'REPAIR', 'RECOVER', 'RESTORE', 'BACKUP', 'SNAPSHOT',
                    'CLONE', 'FORK', 'BRANCH', 'TAG', 'CHECKOUT', 'MERGE', 'REBASE', 'CHERRY_PICK',
                    'RESET', 'REVERT', 'AMEND', 'STASH', 'POP', 'APPLY', 'DIFF', 'LOG', 'STATUS',
                    'ADD', 'REMOVE', 'COMMIT', 'PUSH', 'PULL', 'FETCH', 'CLONE', 'INIT', 'CONFIG',
                    'REMOTE', 'BRANCH', 'TAG', 'WORKTREE', 'SUBMODULE', 'SUBTREE', 'FILTER_BRANCH',
                    'FILTER_REFS', 'FILTER_OBJECTS', 'FILTER_COMMIT', 'FILTER_TREE', 'FILTER_BLOB',
                    'FILTER_TAG', 'FILTER_MERGE', 'FILTER_REBASE', 'FILTER_CHERRY_PICK', 'FILTER_RESET',
                    'FILTER_REVERT', 'FILTER_AMEND', 'FILTER_STASH', 'FILTER_POP', 'FILTER_APPLY',
                    'FILTER_DIFF', 'FILTER_LOG', 'FILTER_STATUS', 'FILTER_ADD', 'FILTER_REMOVE',
                    'FILTER_COMMIT', 'FILTER_PUSH', 'FILTER_PULL', 'FILTER_FETCH', 'FILTER_CLONE',
                    'FILTER_INIT', 'FILTER_CONFIG', 'FILTER_REMOTE', 'FILTER_WORKTREE', 'FILTER_SUBMODULE',
                    'FILTER_SUBTREE', 'FILTER_FILTER_BRANCH', 'FILTER_FILTER_REFS', 'FILTER_FILTER_OBJECTS',
                    'FILTER_FILTER_COMMIT', 'FILTER_FILTER_TREE', 'FILTER_FILTER_BLOB', 'FILTER_FILTER_TAG',
                    'FILTER_FILTER_MERGE', 'FILTER_FILTER_REBASE', 'FILTER_FILTER_CHERRY_PICK',
                    'FILTER_FILTER_RESET', 'FILTER_FILTER_REVERT', 'FILTER_FILTER_AMEND', 'FILTER_FILTER_STASH',
                    'FILTER_FILTER_POP', 'FILTER_FILTER_APPLY', 'FILTER_FILTER_DIFF', 'FILTER_FILTER_LOG',
                    'FILTER_FILTER_STATUS', 'FILTER_FILTER_ADD', 'FILTER_FILTER_REMOVE'
                ]:
                    tables.add(match)

        return tables

    def analyze_view_dependencies(self, table_name: str) -> Set[str]:
        """分析单个表或视图的依赖关系"""
        table_def = self.db.get_view_definition(table_name)
        dependencies = self.extract_dependencies_from_sql(table_def)

        # 只保留实际存在的表或视图
        all_tables = set(self.db.get_all_tables())
        valid_deps = dependencies.intersection(all_tables)

        self.dependency_map[table_name] = valid_deps

        # 更新反向依赖
        for dep in valid_deps:
            self.reverse_dependency[dep].add(table_name)

        return valid_deps

    def build_full_dependency_graph(self):
        """构建完整的依赖关系图"""
        all_tables = self.db.get_all_tables()

        for table in all_tables:
            try:
                # 尝试获取视图定义
                self.analyze_view_dependencies(table)
            except Exception:
                # 普通表没有复杂定义，跳过
                continue

    def get_dependencies_for_table(self, table_name: str) -> Set[str]:
        """获取指定表的所有依赖项"""
        if table_name in self.dependency_map:
            return self.dependency_map[table_name]

        # 如果还没有分析过，则尝试分析
        try:
            return self.analyze_view_dependencies(table_name)
        except Exception:
            # 对于普通表，返回空集
            return set()

    def get_full_dependencies_recursive(self, table_name: str, visited: Optional[Set[str]] = None) -> Dict[
        str, Set[str]]:
        """递归获取完整的依赖关系树"""
        if visited is None:
            visited = set()

        if table_name in visited:
            return {}

        visited.add(table_name)
        dependencies = self.get_dependencies_for_table(table_name)

        result = {table_name: dependencies}

        for dep in dependencies:
            sub_deps = self.get_full_dependencies_recursive(dep, visited.copy())
            result.update(sub_deps)

        return result

    def format_dependency_tree(self, root_table: str, full_analysis: bool = True) -> str:
        """格式化输出依赖关系树"""
        if full_analysis:
            # 进行完整的依赖分析
            all_deps = self.get_full_dependencies_recursive(root_table)
            return self._format_full_dependency_tree(all_deps, root_table)
        else:
            # 只显示直接依赖
            dependencies = self.get_dependencies_for_table(root_table)
            result = f"{root_table}\n"
            for dep in sorted(dependencies):
                result += f"  -> {dep}\n"
            return result

    def _format_full_dependency_tree(self, deps_dict: Dict[str, Set[str]], root_table: str) -> str:
        """格式化完整的依赖关系树"""

        def _build_tree(current_table: str, depth: int = 0, visited: Set[str] = None) -> str:
            if visited is None:
                visited = set()

            if current_table in visited:
                return f"{'  ' * depth}{current_table} (circular reference)\n"

            visited.add(current_table)
            result = f"{'  ' * depth}{current_table}\n"

            if current_table in deps_dict:
                for dep in sorted(deps_dict[current_table]):
                    result += f"{'  ' * (depth + 1)}-> {dep}\n"
                    # 递归显示下一层依赖
                    if dep in deps_dict and len(deps_dict[dep]) > 0:
                        result += _build_tree(dep, depth + 2, visited.copy())

            visited.remove(current_table)
            return result

        return _build_tree(root_table)


def analyze_table_dependencies(
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        target_table: str
) -> str:
    """
    分析指定表的依赖关系

    Args:
        host: StarRocks FE节点地址
        port: StarRocks MySQL端口（通常是9030）
        user: 用户名
        password: 密码
        database: 数据库名
        target_table: 目标表名

    Returns:
        格式化的依赖关系字符串
    """
    # 创建StarRocks连接
    db_conn = StarRocksConnection(host, port, user, password, database)

    try:
        # 创建分析器
        analyzer = TableDependencyAnalyzer(db_conn)

        # 构建完整依赖图
        analyzer.build_full_dependency_graph()

        # 获取并格式化目标表的完整依赖关系
        dependency_tree = analyzer.format_dependency_tree(target_table, full_analysis=True)

        return dependency_tree
    finally:
        db_conn.close()


# 使用示例 - 针对你的StarRocks配置
if __name__ == "__main__":
    # 使用你的StarRocks连接信息
    result = analyze_table_dependencies(
        host="192.168.8.33",  # 你的StarRocks地址
        port=2030,  # StarRocks MySQL端口
        user="root",  # 用户名
        password="quxing2021",  # 密码
        database="donggua",  # 替换为你的数据库名
        target_table="live_base_view"  # 目标表名
    )

    print(result)
