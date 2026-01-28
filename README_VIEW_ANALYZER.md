# StarRocks 视图依赖关系分析工具

一个用于分析 StarRocks 数据库视图依赖关系的工具，提供命令行和 Web 两种使用方式。

## 📋 项目简介

本工具可以帮助你快速分析 StarRocks 数据库中视图的依赖关系，递归查找视图所依赖的所有表和视图，直到最底层。支持可视化的树形结构展示，方便理解复杂的依赖关系。

## ✨ 功能特点

### 命令行版本 (`view_dependency_analyzer.py`)
- ✅ 递归分析视图依赖关系
- ✅ 自动识别表和视图
- ✅ 树形结构输出
- ✅ 循环依赖保护
- ✅ 支持带数据库名的表名格式（如 `donggua`.`live_base`）

### Web 版本 (`web_view_analyzer.py`)
- ✅ 美观的 Web 界面
- ✅ 可折叠的树形结构
- ✅ 按需加载依赖（点击展开）
- ✅ 智能区分表和视图
- ✅ 实时错误提示
- ✅ 响应式设计

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- StarRocks 数据库访问权限

### 2. 安装依赖

```bash
pip install pymysql flask
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

默认配置（可在代码中修改）：

```python
DB_CONFIG = {
    'host': '192.168.8.33',
    'port': 2030,
    'database': 'donggua',
    'user': 'root',
    'password': 'quxing2021'
}
```

## 📖 使用方法

### 方式一：命令行版本

```bash
python view_dependency_analyzer.py
```

运行后输入视图名称，例如：

```
请输入视图名称: live_base_view
```

输出示例：

```
live_base_view->
            jl_user
            jl_user_shop_type_view->
                user_shop_mapping
            live_base
            live_info_traffic
            live_sales_view->
                sales_detail
                product_info
```

### 方式二：Web 版本

1. 启动 Web 服务：

```bash
python web_view_analyzer.py
```

2. 打开浏览器访问：

```
http://localhost:5000
```

3. 在输入框中输入视图名称，点击"分析"按钮

4. 点击视图节点（📊 图标）可展开查看其依赖关系

## 📁 文件结构

```
langgraph_test/
├── view_dependency_analyzer.py    # 命令行版本
├── web_view_analyzer.py           # Web 服务后端
├── templates/
│   └── index.html                 # Web 前端页面
├── requirements.txt               # Python 依赖
└── README_VIEW_ANALYZER.md        # 本文档
```

## 🎯 使用场景

### 场景 1：理解视图依赖关系

当你需要了解一个视图依赖了哪些表和视图时：

```
输入: live_base_view
输出: 显示所有直接和间接依赖的表和视图
```

### 场景 2：影响分析

当你需要修改某个表结构，想知道会影响哪些视图时：

1. 分析所有可能相关的视图
2. 查看依赖树中是否包含该表
3. 评估修改影响范围

### 场景 3：数据血缘分析

追踪数据从源表到最终视图的流转路径：

```
live_base_view -> live_sales_view -> sales_detail (源表)
```

## 🔧 技术实现

### 核心功能

#### 1. SQL 解析

支持多种表名格式：
- `` `donggua`.`live_base` AS `t1` ``
- `donggua.live_base AS t1`
- `` `live_base` AS `t1` ``
- `live_base`

使用正则表达式提取 FROM 和 JOIN 子句中的表名：

```python
# 匹配带数据库名的表
pattern1 = r'(?:FROM|JOIN)\s+`?(?:\w+)`?\.`?(\w+)`?\s+(?:AS\s+)?`?\w+`?'

# 匹配不带数据库名的表
pattern2 = r'(?:FROM|JOIN)\s+`?(\w+)`?\s+(?:AS\s+)?`?\w+`?'
```

#### 2. 递归分析

```python
def analyze_view(self, view_name: str, indent: int = 0):
    # 获取视图定义
    view_sql = self.get_view_definition(view_name)

    # 提取依赖
    dependencies = self.extract_dependencies(view_sql)

    # 递归分析视图依赖
    for dep in dependencies:
        if self.is_view(dep):
            self.analyze_view(dep, indent + 1)
```

#### 3. 循环依赖保护

使用 `visited` 集合记录已访问的视图，避免无限递归：

```python
if view_name in self.visited:
    return result
self.visited.add(view_name)
```

### Web 版本架构

#### 后端 API

**检查视图是否存在**
```
POST /api/check_view
Body: {"view_name": "live_base_view"}
Response: {"success": true} 或 {"error": "错误信息"}
```

**获取视图依赖**
```
POST /api/dependencies
Body: {"view_name": "live_base_view"}
Response: {
  "dependencies": [
    {"name": "table1", "type": "table", "has_children": false},
    {"name": "view1", "type": "view", "has_children": true}
  ]
}
```

#### 前端交互

1. 用户输入视图名称
2. 前端调用 `/api/check_view` 验证视图存在
3. 调用 `/api/dependencies` 获取第一层依赖
4. 渲染树形结构，视图节点可点击
5. 点击视图节点时，异步加载其子依赖
6. 支持展开/折叠操作

## 🎨 界面设计

### 颜色方案

- **主色调**: 紫色渐变 (#667eea → #764ba2)
- **视图标识**: 蓝色 (#1976d2)
- **表标识**: 绿色 (#388e3c)
- **背景**: 浅灰色 (#f9f9f9)

### 图标说明

- 📊 视图（可点击展开）
- 📋 表（不可展开）
- ▶ 折叠状态
- ▼ 展开状态

## 🔍 示例

### 示例 1：简单依赖

```
视图: user_summary_view
依赖: users (表), orders (表)

输出:
user_summary_view->
            orders
            users
```

### 示例 2：多层依赖

```
视图: live_base_view
依赖:
  - live_base (表)
  - jl_user (表)
  - live_sales_view (视图)
    - sales_detail (表)
    - product_info (表)

输出:
live_base_view->
            jl_user
            live_base
            live_sales_view->
                product_info
                sales_detail
```

### 示例 3：复杂依赖树

```
live_base_view->
            jl_user
            jl_user_shop_type_view->
                user_shop_mapping
                shop_type_config
            live_base
            live_info_traffic
            live_sales_view->
                order_detail
                product_info->
                    product_category
                    product_brand
```

## ⚠️ 注意事项

1. **数据库连接**
   - 确保网络可以访问 StarRocks 数据库
   - 确认用户有查询 `information_schema` 的权限

2. **性能考虑**
   - Web 版本采用按需加载，避免一次性加载所有依赖
   - 对于依赖关系复杂的视图，建议使用 Web 版本

3. **循环依赖**
   - 工具会自动检测并避免循环依赖
   - 如果存在循环依赖，会在第一次遇到时停止递归

4. **SQL 解析限制**
   - 目前支持标准的 FROM 和 JOIN 语法
   - 不支持子查询中的表名提取
   - 不支持动态 SQL

## 🛠️ 故障排查

### 问题 1：无法连接数据库

**错误信息**: `数据库错误: Can't connect to MySQL server`

**解决方案**:
- 检查数据库地址和端口是否正确
- 确认网络连接正常
- 验证用户名和密码

### 问题 2：视图不存在

**错误信息**: `'xxx' 不是一个视图或不存在`

**解决方案**:
- 确认视图名称拼写正确
- 检查是否在正确的数据库中
- 验证用户是否有查询该视图的权限

### 问题 3：依赖关系不完整

**可能原因**:
- SQL 解析未能识别某些特殊格式
- 视图定义中使用了子查询

**解决方案**:
- 查看视图的完整 DDL
- 手动补充缺失的依赖关系

## 📝 开发计划

- [ ] 支持子查询中的表名提取
- [ ] 添加依赖关系图可视化（图形化展示）
- [ ] 支持导出依赖关系为 JSON/CSV
- [ ] 添加反向依赖查询（查询哪些视图依赖某个表）
- [ ] 支持批量分析多个视图
- [ ] 添加依赖关系缓存机制

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**最后更新**: 2026-01-27
