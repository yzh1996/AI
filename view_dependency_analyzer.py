#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StarRocks 视图依赖关系分析工具
"""

import pymysql
import re
from typing import Set, List, Tuple


class ViewDependencyAnalyzer:
    """视图依赖关系分析器"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        self.database = database
        self.cursor = self.connection.cursor()
        self.visited = set()  # 避免循环依赖

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

    def is_view(self, object_name: str) -> bool:
        """判断对象是否为视图"""
        query = """
            SELECT TABLE_TYPE
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        self.cursor.execute(query, (self.database, object_name))
        result = self.cursor.fetchone()
        return result and result[0] == 'VIEW'

    def get_view_definition(self, view_name: str) -> str:
        """获取视图定义 SQL"""
        try:
            query = f"SHOW CREATE VIEW `{view_name}`"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[1] if result and len(result) >= 2 else ""
        except Exception as e:
            print(f"错误: 无法获取视图 {view_name} 的定义 - {e}")
            return ""

    def extract_dependencies(self, sql: str) -> Set[str]:
        """从 SQL 中提取依赖的表和视图"""
        # 移除注释
        sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        dependencies = set()

        # 匹配 FROM 和 JOIN 后的表名
        # 支持格式:
        # 1. `donggua`.`live_base` AS `t1`
        # 2. donggua.live_base AS t1
        # 3. `live_base` AS `t1`
        # 4. live_base AS t1
        # 5. live_base

        # 匹配带数据库名的表: `db`.`table` 或 db.table
        pattern1 = r'(?:FROM|JOIN)\s+`?(?:\w+)`?\.`?(\w+)`?\s+(?:AS\s+)?`?\w+`?'
        matches = re.finditer(pattern1, sql, re.IGNORECASE)
        for match in matches:
            table_name = match.group(1)
            if table_name.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'CASE', 'ON']:
                dependencies.add(table_name)

        # 匹配不带数据库名的表: `table` 或 table
        pattern2 = r'(?:FROM|JOIN)\s+`?(\w+)`?\s+(?:AS\s+)?`?\w+`?'
        matches = re.finditer(pattern2, sql, re.IGNORECASE)
        for match in matches:
            table_name = match.group(1)
            # 检查是否已经被 pattern1 匹配过（避免重复）
            # 通过检查前面是否有点号来判断
            match_start = match.start()
            if match_start > 0 and sql[match_start - 1] == '.':
                continue
            if table_name.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'CASE', 'ON']:
                dependencies.add(table_name)

        return dependencies

    def analyze_view(self, view_name: str, indent: int = 0) -> List[Tuple[str, int, bool]]:
        """
        递归分析视图依赖
        返回: [(对象名, 缩进层级, 是否为视图), ...]
        """
        result = []

        # 避免循环依赖
        if view_name in self.visited:
            return result

        self.visited.add(view_name)

        # 获取视图定义
        view_sql = self.get_view_definition(view_name)
        if not view_sql:
            return result

        # 提取依赖
        dependencies = self.extract_dependencies(view_sql)

        for dep in sorted(dependencies):
            is_view = self.is_view(dep)
            result.append((dep, indent, is_view))

            # 如果依赖也是视图，递归分析
            if is_view:
                sub_deps = self.analyze_view(dep, indent + 1)
                result.extend(sub_deps)

        return result

    def print_dependencies(self, view_name: str):
        """打印视图依赖关系树"""
        # 检查视图是否存在
        if not self.is_view(view_name):
            print(f"错误: '{view_name}' 不是一个视图或不存在")
            return

        print(f"{view_name}->")

        # 重置访问记录
        self.visited.clear()

        # 分析依赖
        dependencies = self.analyze_view(view_name, 0)

        if not dependencies:
            print("            (无依赖)")
            return

        # 打印依赖树
        i = 0
        while i < len(dependencies):
            dep_name, indent_level, is_view = dependencies[i]
            spaces = "            " + "    " * indent_level

            if is_view:
                # 检查下一个元素是否是这个视图的子依赖
                has_children = (i + 1 < len(dependencies) and
                               dependencies[i + 1][1] == indent_level + 1)

                if has_children:
                    # 有子依赖，打印视图名后换行
                    print(f"{spaces}{dep_name}->")
                else:
                    # 无子依赖，视图名后直接结束
                    print(f"{spaces}{dep_name}->")
            else:
                # 表直接打印
                print(f"{spaces}{dep_name}")

            i += 1


def main():
    """主函数"""
    print("=" * 60)
    print("StarRocks 视图依赖关系分析工具")
    print("=" * 60)

    # 数据库配置
    config = {
        'host': '192.168.8.33',
        'port': 2030,
        'database': 'donggua',
        'user': 'root',
        'password': 'quxing2021'
    }

    try:
        # 连接数据库
        analyzer = ViewDependencyAnalyzer(**config)
        print(f"✓ 已连接到数据库: {config['database']}\n")

        # 输入视图名称
        view_name = input("请输入视图名称: ").strip()

        if not view_name:
            print("错误: 视图名称不能为空")
            return

        print("\n依赖关系:")
        print("-" * 60)

        # 分析并打印依赖
        analyzer.print_dependencies(view_name)

        print("-" * 60)

    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
