#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元数据管理模块
用于检测数据库中表和视图的变化
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Set, Tuple
import pymysql


class MetadataManager:
    """元数据管理器"""

    def __init__(self, config: Dict):
        """
        初始化元数据管理器

        Args:
            config: 数据库配置
        """
        self.config = config
        self.database = config['database']

    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            charset='utf8mb4'
        )

    def get_metadata_snapshot(self) -> Dict:
        """
        获取当前数据库的元数据快照

        Returns:
            元数据快照字典
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # 查询所有表和视图
            query = """
                SELECT TABLE_NAME, TABLE_TYPE
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """
            cursor.execute(query, (self.database,))
            results = cursor.fetchall()

            tables = []
            views = []

            for row in results:
                table_name = row[0]
                table_type = row[1]

                if table_type == 'VIEW':
                    views.append(table_name)
                else:
                    tables.append(table_name)

            # 生成校验和
            all_objects = sorted(tables + views)
            checksum = hashlib.md5(json.dumps(all_objects).encode()).hexdigest()

            return {
                'database': self.database,
                'timestamp': datetime.now().isoformat(),
                'tables': tables,
                'views': views,
                'checksum': checksum,
                'total_count': len(all_objects)
            }

        finally:
            conn.close()

    def compare_snapshots(self, old_snapshot: Dict, new_snapshot: Dict) -> Dict:
        """
        比较两个快照，检测变化

        Args:
            old_snapshot: 旧快照
            new_snapshot: 新快照

        Returns:
            变化详情
        """
        if not old_snapshot:
            return {
                'has_changes': True,
                'added_tables': new_snapshot['tables'],
                'removed_tables': [],
                'added_views': new_snapshot['views'],
                'removed_views': [],
                'timestamp': new_snapshot['timestamp']
            }

        old_tables = set(old_snapshot.get('tables', []))
        new_tables = set(new_snapshot.get('tables', []))
        old_views = set(old_snapshot.get('views', []))
        new_views = set(new_snapshot.get('views', []))

        added_tables = list(new_tables - old_tables)
        removed_tables = list(old_tables - new_tables)
        added_views = list(new_views - old_views)
        removed_views = list(old_views - new_views)

        has_changes = bool(added_tables or removed_tables or added_views or removed_views)

        return {
            'has_changes': has_changes,
            'added_tables': sorted(added_tables),
            'removed_tables': sorted(removed_tables),
            'added_views': sorted(added_views),
            'removed_views': sorted(removed_views),
            'timestamp': new_snapshot['timestamp']
        }

    def get_all_objects(self) -> List[Dict]:
        """
        获取所有表和视图的列表

        Returns:
            对象列表
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            query = """
                SELECT TABLE_NAME, TABLE_TYPE, TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_TYPE DESC, TABLE_NAME
            """
            cursor.execute(query, (self.database,))
            results = cursor.fetchall()

            objects = []
            for row in results:
                objects.append({
                    'name': row[0],
                    'type': 'view' if row[1] == 'VIEW' else 'table',
                    'comment': row[2] or ''
                })

            return objects

        finally:
            conn.close()
