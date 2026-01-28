# StarRocks 视图依赖关系分析工具 - 完整功能说明

## 📦 项目概述

这是一个功能强大的 StarRocks 数据库视图依赖关系分析工具，提供 Web 界面和命令行两种使用方式。

**核心功能**：
- 🔍 递归分析视图依赖关系
- 📊 可视化依赖关系树
- 📋 查看表结构详情
- ✏️ 编辑表和字段注释
- 💾 持久化保存注释数据

## 🎯 主要特性

### 1. 依赖关系分析
- ✅ 输入视图名称，自动分析所有依赖
- ✅ 递归查找到最底层（直到所有依赖都是表）
- ✅ 自动识别表和视图
- ✅ 循环依赖保护
- ✅ 可折叠的树形结构展示

### 2. 表结构查看
- ✅ 点击任意表/视图节点查看详情
- ✅ 显示完整字段信息：
  - 字段名称
  - 数据类型（完整类型）
  - 是否可空（YES/NO）
  - 默认值
  - 字段注释
- ✅ 美观的表格展示

### 3. 注释管理
- ✅ 为表添加整体注释说明
- ✅ 为每个字段添加业务含义注释
- ✅ 实时编辑，一键保存
- ✅ 注释数据持久化存储
- ✅ 支持中文注释

### 4. 界面设计
- ✅ 左右分栏布局
- ✅ 紫色渐变主题
- ✅ 响应式设计
- ✅ 流畅的动画效果
- ✅ 友好的交互提示

## 📁 项目文件结构

```
langgraph_test/
├── web_view_analyzer.py           # Web 服务后端（主程序）
├── view_dependency_analyzer.py    # 命令行版本
├── templates/
│   ├── index.html                 # Web 前端页面（新版）
│   └── index_old.html             # 旧版页面（备份）
├── table_comments.json            # 注释数据存储（自动生成）
├── requirements.txt               # Python 依赖
├── README_VIEW_ANALYZER.md        # 完整使用文档
├── QUICKSTART.md                  # 快速开始指南
├── UPDATE_LOG.md                  # 功能更新说明
├── TEST_GUIDE.md                  # 测试指南
└── SUMMARY.md                     # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pymysql flask
```

### 2. 配置数据库

编辑 `web_view_analyzer.py`，修改数据库配置：

```python
DB_CONFIG = {
    'host': '192.168.8.33',      # 数据库地址
    'port': 2030,                # 端口
    'database': 'donggua',       # 数据库名
    'user': 'root',              # 用户名
    'password': 'quxing2021'     # 密码
}
```

### 3. 启动服务

```bash
python web_view_analyzer.py
```

### 4. 访问页面

打开浏览器访问：http://localhost:5000

## 💡 使用场景

### 场景 1：理解数据流转
**问题**：不清楚某个视图的数据来源

**解决方案**：
1. 输入视图名称分析依赖
2. 查看依赖树，了解数据来源
3. 点击每个表查看字段详情
4. 理解数据流转路径

### 场景 2：维护数据字典
**问题**：团队缺少完整的数据字典文档

**解决方案**：
1. 分析所有核心视图
2. 为每个表添加注释说明
3. 为每个字段添加业务含义
4. 导出 `table_comments.json` 作为数据字典

### 场景 3：影响分析
**问题**：需要修改某个表，不确定影响范围

**解决方案**：
1. 查找依赖该表的所有视图
2. 评估修改影响的视图数量
3. 查看字段使用情况
4. 制定安全的修改方案

### 场景 4：新人培训
**问题**：新人不熟悉数据库结构

**解决方案**：
1. 展示核心视图的依赖关系
2. 逐个表查看字段说明
3. 通过注释理解业务含义
4. 快速掌握数据库结构

## 🎨 界面说明

### 左侧面板 - 依赖关系树

```
┌─────────────────────────┐
│ [输入视图名称]  [分析]   │
├─────────────────────────┤
│ 📊 live_base_view       │
│ ├─ 📋 jl_user           │
│ ├─ 📊 live_sales_view   │ ← 点击展开
│ │  ├─ 📋 sales_detail   │
│ │  └─ 📋 product_info   │
│ └─ 📋 live_base ✓       │ ← 选中状态
└─────────────────────────┘
```

**图标说明**：
- 📊 = 视图（可点击展开）
- 📋 = 表（不可展开）
- ✓ = 当前选中

**颜色说明**：
- 🔵 蓝色边框 = 视图
- 🟢 绿色边框 = 表
- 🟣 紫色背景 = 选中状态

### 右侧面板 - 表结构详情

```
┌──────────────────────────────────┐
│ 表名: live_base                  │
│ 类型: 表                         │
│                                  │
│ 表注释: [直播基础信息表_______]  │ ← 可编辑
│                                  │
│ 字段列表:                        │
│ ┌────────────────────────────┐  │
│ │字段名│类型    │可空│注释    │  │
│ ├────────────────────────────┤  │
│ │id    │INT(11) │NO  │[主键]  │  │ ← 可编辑
│ │name  │VARCHAR │YES │[名称]  │  │
│ └────────────────────────────┘  │
│                                  │
│         [💾 保存注释]            │
└──────────────────────────────────┘
```

## 🔧 API 接口说明

### 1. 检查视图是否存在
```
POST /api/check_view
Request:  {"view_name": "live_base_view"}
Response: {"success": true}
```

### 2. 获取视图依赖
```
POST /api/dependencies
Request:  {"view_name": "live_base_view"}
Response: {
  "dependencies": [
    {"name": "table1", "type": "table", "has_children": false},
    {"name": "view1", "type": "view", "has_children": true}
  ]
}
```

### 3. 获取表结构
```
POST /api/table_structure
Request:  {"table_name": "live_base"}
Response: {
  "table_name": "live_base",
  "table_type": "table",
  "table_comment": "直播基础信息表",
  "columns": [
    {
      "name": "id",
      "data_type": "int",
      "column_type": "int(11)",
      "nullable": false,
      "default": null,
      "db_comment": "",
      "custom_comment": "主键ID"
    }
  ]
}
```

### 4. 保存注释
```
POST /api/save_comments
Request: {
  "table_name": "live_base",
  "table_comment": "直播基础信息表",
  "column_comments": {
    "id": "主键ID",
    "name": "名称"
  }
}
Response: {"success": true, "message": "保存成功"}
```

## 📊 数据存储格式

### table_comments.json

```json
{
  "donggua.live_base": {
    "table_comment": "直播基础信息表，存储直播间的基本信息",
    "column_comments": {
      "id": "主键ID，自增",
      "anchor_id": "主播ID，关联 jl_user 表",
      "room_name": "直播间名称",
      "start_time": "开播时间",
      "end_time": "下播时间"
    },
    "updated_at": "2026-01-27T17:30:00.123456"
  },
  "donggua.jl_user": {
    "table_comment": "用户信息表",
    "column_comments": {
      "anchor_id": "用户ID，主键",
      "nickname": "用户昵称"
    },
    "updated_at": "2026-01-27T17:35:00.123456"
  }
}
```

## ⚙️ 配置说明

### 数据库配置

在 `web_view_analyzer.py` 中修改：

```python
DB_CONFIG = {
    'host': '192.168.8.33',      # 数据库主机地址
    'port': 2030,                # 数据库端口（StarRocks 默认 9030）
    'database': 'donggua',       # 数据库名称
    'user': 'root',              # 数据库用户名
    'password': 'quxing2021'     # 数据库密码
}
```

### 服务配置

在 `web_view_analyzer.py` 最后一行修改：

```python
app.run(
    debug=True,           # 调试模式（生产环境改为 False）
    host='0.0.0.0',       # 监听地址（0.0.0.0 表示所有网卡）
    port=5000             # 监听端口
)
```

### 注释文件路径

在 `web_view_analyzer.py` 开头修改：

```python
COMMENTS_FILE = 'table_comments.json'  # 注释文件路径
```

## 🔒 安全注意事项

### 1. 数据库权限
- 只需要 SELECT 权限
- 需要查询 `information_schema` 的权限
- 不需要修改表结构的权限

### 2. 注释数据安全
- 注释保存在本地文件，不写入数据库
- 建议定期备份 `table_comments.json`
- 可以将注释文件纳入版本控制

### 3. 网络安全
- 默认监听 0.0.0.0，可从任何 IP 访问
- 生产环境建议配置防火墙
- 建议添加身份认证机制

## 📚 相关文档

- **README_VIEW_ANALYZER.md** - 完整使用文档
- **QUICKSTART.md** - 5 分钟快速开始
- **UPDATE_LOG.md** - 功能更新说明
- **TEST_GUIDE.md** - 测试指南
- **SUMMARY.md** - 本文档（功能总结）

## 🐛 故障排查

### 问题 1：无法连接数据库
```
错误: Can't connect to MySQL server
```
**解决方案**：
1. 检查数据库地址和端口
2. 确认网络连接正常
3. 验证用户名和密码
4. 检查防火墙设置

### 问题 2：视图不存在
```
错误: 'xxx' 不是一个视图或不存在
```
**解决方案**：
1. 确认视图名称拼写正确
2. 检查是否在正确的数据库中
3. 验证用户是否有查询权限

### 问题 3：注释保存失败
```
错误: 保存失败
```
**解决方案**：
1. 检查文件写入权限
2. 确认磁盘空间充足
3. 查看后端日志获取详细错误

### 问题 4：页面加载慢
**解决方案**：
1. 检查数据库连接速度
2. 减少一次性展开的节点数量
3. 考虑优化数据库查询

## 🎓 最佳实践

### 1. 注释编写规范
- **表注释**：简要说明表的用途和业务含义
- **字段注释**：说明字段的业务含义、取值范围、关联关系
- **使用中文**：便于团队理解
- **保持更新**：表结构变更时及时更新注释

### 2. 依赖分析技巧
- **从核心视图开始**：先分析最重要的业务视图
- **逐层展开**：不要一次性展开所有节点
- **记录依赖关系**：将重要的依赖关系截图保存

### 3. 团队协作
- **版本控制**：将 `table_comments.json` 纳入 Git
- **定期同步**：团队成员定期拉取最新注释
- **统一规范**：制定注释编写规范

## 📈 性能优化建议

### 1. 数据库优化
- 确保 `information_schema` 查询性能良好
- 考虑为常用视图创建物化视图

### 2. 前端优化
- 使用虚拟滚动处理大量字段
- 实现注释的本地缓存
- 添加加载进度提示

### 3. 后端优化
- 实现查询结果缓存
- 使用连接池管理数据库连接
- 异步处理耗时操作

## 🔮 未来规划

- [ ] 支持导出注释为 Markdown/PDF 文档
- [ ] 添加注释搜索功能
- [ ] 支持批量导入注释（Excel/CSV）
- [ ] 添加字段关系图可视化
- [ ] 支持多数据库切换
- [ ] 添加用户权限管理
- [ ] 支持注释历史版本
- [ ] 添加反向依赖查询（查询哪些视图依赖某个表）

## 📞 技术支持

如有问题或建议，请：
1. 查看相关文档
2. 检查故障排查章节
3. 提交 GitHub Issue
4. 联系项目维护者

---

**项目版本**: v2.0
**最后更新**: 2026-01-27
**作者**: Claude Code
**许可证**: MIT License
