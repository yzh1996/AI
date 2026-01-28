# Phase 1: 配置管理功能 - 手动集成说明

## 已完成的工作

1. ✅ 创建了 `utils/encryption.py` - 密码加密工具
2. ✅ 创建了 `utils/cache.py` - 缓存工具
3. ✅ 创建了 `config_manager.py` - 配置管理器
4. ✅ 更新了 `requirements.txt` - 添加依赖
5. ✅ 更新了 `.env` - 添加环境变量

## 需要手动修改 web_view_analyzer.py

### 步骤 1: 修改导入部分（文件开头）

将：
```python
from flask import Flask, render_template, jsonify, request
import pymysql
import re
import json
import os
from typing import Set, Dict, List
from datetime import datetime

app = Flask(__name__)

# 注释数据文件路径
COMMENTS_FILE = 'table_comments.json'

# 数据库配置
DB_CONFIG = {
    'host': '192.168.8.33',
    'port': 2030,
    'database': 'donggua',
    'user': 'root',
    'password': 'quxing2021'
}
```

替换为：
```python
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
```

### 步骤 2: 删除全局 analyzer 实例

删除这一行（约第275行）：
```python
analyzer = ViewDependencyAnalyzer(DB_CONFIG)
```

### 步骤 3: 在第一个 @app.route 之前添加辅助函数

在 `@app.route('/')` 之前添加：
```python
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
```

### 步骤 4: 在所有现有 API 函数开头添加 analyzer 检查

在每个 API 函数（check_view, get_dependencies, get_table_structure, save_comments）的开头添加：
```python
analyzer = get_analyzer()
if not analyzer:
    return jsonify({'error': '请先配置并激活数据库连接'}), 400
```

### 步骤 5: 添加配置管理 API 端点

在文件末尾（if __name__ == '__main__': 之前）添加新的 API 端点。

完整的配置管理 API 代码请参考 `config_api_endpoints.py` 文件（我将创建）。

## 下一步

完成上述修改后：
1. 安装新依赖：`pip install -r requirements.txt`
2. 运行应用：`python web_view_analyzer.py`
3. 访问 http://localhost:5000
4. 通过 Web 界面配置数据库连接

## 或者使用自动化脚本

运行：`python apply_phase1_changes.py`
