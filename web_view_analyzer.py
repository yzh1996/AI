#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StarRocks 视图依赖关系 Web 分析工具
"""

from flask import Flask, render_template, jsonify, request, session
from flask_session import Session
import pymysql
import re
import json
import os
from typing import Set, Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from config_manager import get_config_manager
from metadata_manager import MetadataManager
from export_manager import ExportManager
from flask import send_file
import io

from utils.cache import get_cache


# 加载环境变量
load_dotenv()

app = Flask(__name__)

# Flask 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE', 'filesystem')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# 初始化 Session
Session(app)

# 注释数据文件路径
COMMENTS_FILE = 'table_comments.json'


class ViewDependencyAnalyzer:
    """视图依赖关系分析器"""

    def __init__(self, config: Dict):
        self.config = config
        self.database = config['database']
        self.comments = self.load_comments()

    def load_comments(self) -> Dict:
        """加载注释数据"""
        if os.path.exists(COMMENTS_FILE):
            try:
                with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载注释文件失败: {e}")
                return {}
        return {}

    def save_comments(self):
        """保存注释数据"""
        try:
            with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.comments, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存注释文件失败: {e}")

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

    def object_exists(self, object_name: str) -> bool:
        """判断对象（表或视图）是否存在"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT TABLE_NAME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            cursor.execute(query, (self.database, object_name))
            result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()

    def get_object_type(self, object_name: str) -> str:
        """获取对象类型：'table', 'view', 或 None"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT TABLE_TYPE
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            cursor.execute(query, (self.database, object_name))
            result = cursor.fetchone()
            if not result:
                return None
            return 'view' if result[0] == 'VIEW' else 'table'
        finally:
            conn.close()

    def is_view(self, object_name: str) -> bool:
        """判断对象是否为视图"""
        return self.get_object_type(object_name) == 'view'

    def get_view_definition(self, view_name: str) -> str:
        """获取视图定义 SQL"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = f"SHOW CREATE VIEW `{view_name}`"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[1] if result and len(result) >= 2 else ""
        except Exception as e:
            print(f"错误: 无法获取视图 {view_name} 的定义 - {e}")
            return ""
        finally:
            conn.close()

    def extract_dependencies(self, sql: str) -> Set[str]:
        """从 SQL 中提取依赖的表和视图"""
        # 移除注释
        sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        dependencies = set()

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
            # 检查是否已经被 pattern1 匹配过
            match_start = match.start()
            if match_start > 0 and sql[match_start - 1] == '.':
                continue
            if table_name.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'CASE', 'ON']:
                dependencies.add(table_name)

        return dependencies

    def get_direct_dependencies(self, object_name: str) -> List[Dict]:
        """获取对象的直接依赖（不递归）"""
        obj_type = self.get_object_type(object_name)

        # 如果对象不存在，返回空
        if not obj_type:
            return []

        # 如果是表，没有依赖，返回空
        if obj_type == 'table':
            return []

        # 如果是视图，获取其依赖
        view_sql = self.get_view_definition(object_name)
        if not view_sql:
            return []

        dependencies = self.extract_dependencies(view_sql)
        result = []

        for dep in sorted(dependencies):
            # 验证依赖的对象是否存在
            dep_type = self.get_object_type(dep)
            if dep_type:  # 只添加存在的对象
                result.append({
                    'name': dep,
                    'type': dep_type,
                    'has_children': dep_type == 'view'
                })

        return result


    def get_table_structure(self, table_name: str) -> Dict:
        """获取表结构信息"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # 获取表类型
            type_query = """
                SELECT TABLE_TYPE, TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            cursor.execute(type_query, (self.database, table_name))
            type_result = cursor.fetchone()

            if not type_result:
                return {'error': '表或视图不存在'}

            table_type = 'view' if type_result[0] == 'VIEW' else 'table'
            db_comment = type_result[1] or ''

            # 获取字段信息
            columns_query = """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_COMMENT
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            cursor.execute(columns_query, (self.database, table_name))
            columns = cursor.fetchall()

            # 获取保存的注释
            table_key = f"{self.database}.{table_name}"
            saved_comments = self.comments.get(table_key, {})
            table_comment = saved_comments.get('table_comment', db_comment)
            column_comments = saved_comments.get('column_comments', {})

            # 构建字段列表
            column_list = []
            for col in columns:
                column_name = col[0]
                column_list.append({
                    'name': column_name,
                    'data_type': col[1],
                    'column_type': col[2],
                    'nullable': col[3] == 'YES',
                    'default': col[4],
                    'db_comment': col[5] or '',
                    'custom_comment': column_comments.get(column_name, col[5] or '')
                })

            return {
                'table_name': table_name,
                'table_type': table_type,
                'table_comment': table_comment,
                'columns': column_list
            }

        except Exception as e:
            return {'error': str(e)}
        finally:
            conn.close()

    def save_table_comments(self, table_name: str, table_comment: str, column_comments: Dict) -> bool:
        """保存表和字段注释"""
        try:
            table_key = f"{self.database}.{table_name}"
            self.comments[table_key] = {
                'table_comment': table_comment,
                'column_comments': column_comments,
                'updated_at': datetime.now().isoformat()
            }
            self.save_comments()
            return True
        except Exception as e:
            print(f"保存注释失败: {e}")
            return False

    def get_all_tables_and_views(self) -> List[Dict]:
        """获取所有表和视图列表"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT TABLE_NAME, TABLE_TYPE, TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """
            cursor.execute(query, (self.database,))
            results = cursor.fetchall()

            tables_and_views = []
            for row in results:
                table_name = row[0]
                table_type = 'view' if row[1] == 'VIEW' else 'table'
                table_comment = row[2] or ''

                tables_and_views.append({
                    'name': table_name,
                    'type': table_type,
                    'comment': table_comment
                })

            return tables_and_views
        except Exception as e:
            print(f"获取表和视图列表失败: {e}")
            return []
        finally:
            conn.close()


# ==================== 原有 API（修改为使用 get_analyzer）====================

def get_analyzer() -> Optional[ViewDependencyAnalyzer]:
    """
    获取当前会话的 analyzer 实例

    Returns:
        ViewDependencyAnalyzer 实例，如果没有激活的配置则返回 None
    """
    config_id = session.get('active_config_id')
    if not config_id:
        return None

    config_manager = get_config_manager()
    config = config_manager.get_config_with_password(config_id)
    if not config:
        return None

    # 更新最后使用时间
    config_manager.update_last_used(config_id)

    return ViewDependencyAnalyzer(config)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/check_view', methods=['POST'])
def check_view():
    """检查对象（表或视图）是否存在"""
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({'error': '请先配置并激活数据库连接'}), 400

    data = request.json
    object_name = data.get('view_name', '').strip()  # 保持参数名兼容性

    if not object_name:
        return jsonify({'error': '对象名称不能为空'}), 400

    obj_type = analyzer.get_object_type(object_name)

    if not obj_type:
        return jsonify({'error': f"'{object_name}' 不存在"}), 404

    return jsonify({
        'success': True,
        'type': obj_type,
        'name': object_name
    })


@app.route('/api/dependencies', methods=['POST'])
def get_dependencies():
    """获取对象的直接依赖"""
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({'error': '请先配置并激活数据库连接'}), 400

    data = request.json
    object_name = data.get('view_name', '').strip()  # 保持参数名兼容性

    if not object_name:
        return jsonify({'error': '对象名称不能为空'}), 400

    try:
        dependencies = analyzer.get_direct_dependencies(object_name)
        obj_type = analyzer.get_object_type(object_name)

        return jsonify({
            'dependencies': dependencies,
            'object_type': obj_type,
            'object_name': object_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/table_structure', methods=['POST'])
def get_table_structure():
    """获取表结构信息"""
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({'error': '请先配置并激活数据库连接'}), 400

    data = request.json
    table_name = data.get('table_name', '').strip()

    if not table_name:
        return jsonify({'error': '表名不能为空'}), 400

    try:
        structure = analyzer.get_table_structure(table_name)
        if 'error' in structure:
            return jsonify(structure), 404
        return jsonify(structure)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save_comments', methods=['POST'])
def save_comments():
    """保存表和字段注释"""
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({'error': '请先配置并激活数据库连接'}), 400

    data = request.json
    table_name = data.get('table_name', '').strip()
    table_comment = data.get('table_comment', '')
    column_comments = data.get('column_comments', {})

    if not table_name:
        return jsonify({'error': '表名不能为空'}), 400

    try:
        success = analyzer.save_table_comments(table_name, table_comment, column_comments)
        if success:
            return jsonify({'success': True, 'message': '保存成功'})
        else:
            return jsonify({'error': '保存失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 配置管理 API ====================

@app.route('/api/configs', methods=['GET'])
def list_configs():
    """获取所有配置列表"""
    try:
        config_manager = get_config_manager()
        configs = config_manager.list_configs()
        active_config_id = session.get('active_config_id')
        return jsonify({
            'success': True,
            'configs': configs,
            'active_config_id': active_config_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/configs', methods=['POST'])
def create_config():
    """创建新配置"""
    try:
        data = request.json
        config_manager = get_config_manager()

        # 验证必填字段
        required_fields = ['name', 'driver', 'host', 'port', 'database', 'user', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'缺少必填字段: {field}'}), 400

        # 创建配置
        config = config_manager.create_config(
            name=data['name'],
            driver=data['driver'],
            host=data['host'],
            port=int(data['port']),
            database=data['database'],
            user=data['user'],
            password=data['password'],
            catalog=data.get('catalog')
        )

        return jsonify({
            'success': True,
            'message': '配置创建成功',
            'config': config_manager.get_config(config['id'])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/configs/<config_id>', methods=['PUT'])
def update_config(config_id):
    """更新配置"""
    try:
        data = request.json
        config_manager = get_config_manager()

        # 更新配置
        config = config_manager.update_config(config_id, **data)

        if config:
            return jsonify({
                'success': True,
                'message': '配置更新成功',
                'config': config
            })
        else:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/configs/<config_id>', methods=['DELETE'])
def delete_config(config_id):
    """删除配置"""
    try:
        config_manager = get_config_manager()

        # 如果删除的是当前激活的配置，清除 session
        if session.get('active_config_id') == config_id:
            session.pop('active_config_id', None)

        success = config_manager.delete_config(config_id)

        if success:
            return jsonify({
                'success': True,
                'message': '配置删除成功'
            })
        else:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/configs/<config_id>/activate', methods=['POST'])
def activate_config(config_id):
    """激活配置"""
    try:
        config_manager = get_config_manager()
        config = config_manager.get_config(config_id)

        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404

        # 设置为当前激活的配置
        session['active_config_id'] = config_id
        config_manager.update_last_used(config_id)

        return jsonify({
            'success': True,
            'message': '配置已激活',
            'config': config
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/configs/test', methods=['POST'])
def test_config_connection():
    """测试数据库连接"""
    try:
        data = request.json
        config_id = data.get('config_id')

        if not config_id:
            return jsonify({'success': False, 'message': '缺少配置ID'}), 400

        config_manager = get_config_manager()
        success, message = config_manager.test_connection(config_id)

        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/configs/active', methods=['GET'])
def get_active_config():
    """获取当前激活的配置"""
    try:
        config_id = session.get('active_config_id')
        if not config_id:
            return jsonify({'success': False, 'error': '未激活任何配置'}), 404

        config_manager = get_config_manager()
        config = config_manager.get_config(config_id)

        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404

        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/search_tables', methods=['GET'])
def search_tables():
    """搜索表和视图 - 支持表名和注释模糊搜索"""
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({'error': '请先配置并激活数据库连接'}), 400

    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)  # 默认返回20条

    try:
        # 获取所有表和视图
        tables_and_views = analyzer.get_all_tables_and_views()

        # 加载自定义注释并合并
        custom_comments = analyzer.comments
        for item in tables_and_views:
            table_key = f"{analyzer.database}.{item['name']}"
            if table_key in custom_comments:
                # 优先使用自定义注释
                custom_comment = custom_comments[table_key].get('table_comment', '')
                if custom_comment:
                    item['comment'] = custom_comment
                    item['comment_source'] = 'custom'
                else:
                    item['comment_source'] = 'db'
            else:
                item['comment_source'] = 'db'

        # 如果有搜索关键词，进行过滤和评分
        if query:
            filtered = []
            query_lower = query.lower()

            for item in tables_and_views:
                # 搜索表名（英文）
                name_match = query_lower in item['name'].lower()

                # 搜索注释（中文或英文）
                comment_match = query in item['comment'] if item['comment'] else False

                if name_match or comment_match:
                    # 计算匹配度分数（用于排序）
                    score = 0
                    if item['name'].lower().startswith(query_lower):
                        score += 100  # 表名前缀匹配优先级最高
                    elif name_match:
                        score += 50   # 表名包含匹配

                    if comment_match:
                        if item['comment'].startswith(query):
                            score += 30  # 注释前缀匹配
                        else:
                            score += 10  # 注释包含匹配

                    item['match_score'] = score
                    filtered.append(item)

            # 按匹配度排序
            filtered.sort(key=lambda x: x['match_score'], reverse=True)

            # 限制返回数量
            filtered = filtered[:limit]
        else:
            filtered = tables_and_views[:limit]

        return jsonify({
            'success': True,
            'results': filtered,
            'total': len(filtered),
            'has_more': len(tables_and_views) > limit if not query else False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("StarRocks 视图依赖关系 Web 分析工具")
    print("=" * 60)
    print("请通过 Web 界面配置数据库连接")
    print(f"访问地址: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
