# Web View Analyzer 增强功能 - 完整实现文档

## 🎉 项目完成总结

所有三个 Phase 的功能已全部实现完成！

### ✅ Phase 1: 动态数据库配置管理 (100%)
### ✅ Phase 2: 实时表/视图检测 (100%)
### ✅ Phase 3: 依赖关系导出 (100%)

---

## 📦 新增文件清单

### 核心模块
1. **utils/encryption.py** - 密码加密/解密工具
2. **utils/cache.py** - 内存缓存工具
3. **config_manager.py** - 数据库配置管理器
4. **metadata_manager.py** - 元数据管理器
5. **export_manager.py** - 导出管理器

### 修改的文件
1. **web_view_analyzer.py** - 主应用（添加所有新 API）
2. **templates/index.html** - 前端界面（添加所有新 UI）
3. **requirements.txt** - 依赖列表（已更新）
4. **.env** - 环境变量配置（已更新）

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
 
```

### 3. 访问界面
打开浏览器访问：**http://localhost:5000**

---

## 🎯 功能使用指南

### 功能 1: 数据库配置管理

#### 创建配置
1. 点击右上角 **"⚙️ 数据库配置"** 按钮
2. 点击 **"+ 新建配置"**
3. 填写配置信息：
   - **配置名称**: 例如 "生产环境"
   - **数据库类型**: MySQL / StarRocks / PostgreSQL
   - **主机地址**: 192.168.8.33
   - **端口**: 2030
   - **数据库名**: donggua
   - **Catalog**: (可选) 用于 Trino/Presto
   - **用户名**: root
   - **密码**: 你的密码
4. 点击 **"创建并激活"**

#### 管理配置
- **测试连接**: 验证数据库连接是否正常
- **保存**: 保存配置修改
- **激活**: 切换到该配置
- **删除**: 删除配置

#### 安全特性
- ✅ 密码使用 Fernet 对称加密存储
- ✅ 加密密钥存储在环境变量中
- ✅ Session 加密保护
- ✅ 前端永不显示明文密码

---

### 功能 2: 实时表/视图检测

#### 手动刷新
1. 点击右上角 **"🔄 刷新"** 按钮
2. 系统会检测数据库中的变化
3. 如果有变化，会显示 Toast 通知

#### 自动刷新
1. 勾选 **"自动刷新"** 开关
2. 系统每 30 秒自动检测一次
3. 检测到变化时自动通知

#### 变化通知
系统会检测并通知以下变化：
- ✅ 新增的表
- ✅ 删除的表
- ✅ 新增的视图
- ✅ 删除的视图

---

### 功能 3: 依赖关系导出

#### 导出步骤
1. 在依赖树中选择要导出的对象（或手动输入）
2. 点击右上角 **"⬇️ 导出"** 按钮
3. 选择导出格式：
   - **Mermaid 图表代码**: 可在 Markdown 中渲染
   - **PNG 图片**: 位图格式
   - **SVG 矢量图**: 矢量格式，可缩放
   - **JSON 数据**: 结构化数据
4. (可选) 勾选 **"限制深度"** 并设置最大层数
5. 点击 **"导出"**

#### 导出格式说明

**Mermaid 代码**
- 适合嵌入文档
- 可在 GitHub、GitLab 等平台直接渲染
- 支持在线编辑器预览

**PNG/SVG 图片**
- 视图用蓝色方框表示
- 表用绿色椭圆表示
- 箭头表示依赖关系
- SVG 格式支持无损缩放

**JSON 数据**
- 包含完整的依赖树结构
- 包含导出元数据（时间、数据库等）
- 适合程序化处理

---

## 🔧 API 文档

### 配置管理 API

#### 获取所有配置
```
GET /api/configs
```

#### 创建配置
```
POST /api/configs
Content-Type: application/json

{
  "name": "配置名称",
  "driver": "mysql|starrocks|postgresql",
  "host": "主机地址",
  "port": 端口号,
  "database": "数据库名",
  "catalog": "目录名(可选)",
  "user": "用户名",
  "password": "密码"
}
```

#### 更新配置
```
PUT /api/configs/<config_id>
Content-Type: application/json

{
  "name": "新名称",
  ...
}
```

#### 删除配置
```
DELETE /api/configs/<config_id>
```

#### 激活配置
```
POST /api/configs/<config_id>/activate
```

#### 测试连接
```
POST /api/configs/test
Content-Type: application/json

{
  "config_id": "配置ID"
}
```

#### 获取当前激活的配置
```
GET /api/configs/active
```

---

### 元数据管理 API

#### 获取元数据快照
```
GET /api/metadata/snapshot
```

#### 检测元数据变化
```
POST /api/metadata/changes
```

#### 强制刷新元数据
```
POST /api/metadata/refresh
```

#### 获取所有对象列表
```
GET /api/metadata/objects
```

---

### 导出功能 API

#### 导出 Mermaid 代码
```
POST /api/export/mermaid
Content-Type: application/json

{
  "root_object": "对象名称",
  "max_depth": 5  // 可选
}
```

#### 导出图片
```
POST /api/export/image
Content-Type: application/json

{
  "root_object": "对象名称",
  "format": "png|svg",
  "max_depth": 5  // 可选
}
```

#### 导出 JSON
```
POST /api/export/json
Content-Type: application/json

{
  "root_object": "对象名称",
  "max_depth": 5  // 可选
}
```

---

## 📁 项目结构

```
langgraph_test/
├── utils/
│   ├── __init__.py
│   ├── encryption.py          # 加密工具
│   └── cache.py               # 缓存工具
├── config_manager.py          # 配置管理器
├── metadata_manager.py        # 元数据管理器
├── export_manager.py          # 导出管理器
├── web_view_analyzer.py       # 主应用
├── templates/
│   └── index.html             # 前端界面
├── requirements.txt           # 依赖列表
├── .env                       # 环境变量
├── db_configs.json            # 配置存储（运行时生成）
└── table_comments.json        # 注释存储
```

---

## 🔐 安全配置

### 环境变量 (.env)
```bash
# Flask 配置
SECRET_KEY=<生成的密钥>
SESSION_TYPE=filesystem

# 加密密钥
ENCRYPTION_KEY=<生成的加密密钥>

# 自动刷新间隔（秒）
AUTO_REFRESH_INTERVAL=30
```

### 密钥生成
```python
# 生成 SECRET_KEY
import secrets
print(secrets.token_hex(32))

# 生成 ENCRYPTION_KEY
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## 🎨 界面预览

### Header 区域
```
┌─────────────────────────────────────────────────────────┐
│  StarRocks 视图依赖关系分析                              │
│  可视化分析视图依赖关系，支持多数据库配置                │
│                                                          │
│  [⬇️ 导出] [🔄 刷新] [☑ 自动刷新]                       │
│  [● 生产环境] [⚙️ 数据库配置]                           │
└─────────────────────────────────────────────────────────┘
```

### 配置管理 Modal
```
┌─────────────────────────────────────────────────────────┐
│ 数据库配置管理                                    [×]    │
├──────────────┬──────────────────────────────────────────┤
│ 已保存配置   │  配置详情                                │
│              │                                          │
│ ✓ 生产环境   │  配置名称: [____________]                │
│   测试环境   │  数据库类型: [MySQL ▼]                  │
│   开发环境   │  Host: [____________]                    │
│              │  Port: [____]                            │
│ [+ 新建配置] │  Database: [____________]                │
│              │  Catalog: [____________] (可选)          │
│              │  用户名: [____________]                  │
│              │  密码: [____________] [👁]               │
│              │                                          │
│              │  [测试连接] [保存] [删除] [激活]         │
└──────────────┴──────────────────────────────────────────┘
```

### 导出 Modal
```
┌─────────────────────────────────────────────────────────┐
│ 导出依赖关系                                      [×]    │
├─────────────────────────────────────────────────────────┤
│ 导出对象: [____________]                                │
│ 提示: 留空则使用当前选中的对象                          │
│                                                          │
│ 导出格式: [Mermaid 图表代码 ▼]                         │
│                                                          │
│ ☐ 限制深度: [5] 层                                      │
│                                                          │
│ [导出]  [取消]                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 测试建议

### 1. 配置管理测试
- [ ] 创建多个数据库配置
- [ ] 测试连接功能
- [ ] 切换不同配置
- [ ] 修改配置信息
- [ ] 删除配置

### 2. 元数据检测测试
- [ ] 手动刷新功能
- [ ] 启用自动刷新
- [ ] 在数据库中创建新表/视图
- [ ] 在数据库中删除表/视图
- [ ] 验证通知显示

### 3. 导出功能测试
- [ ] 导出 Mermaid 代码
- [ ] 导出 PNG 图片
- [ ] 导出 SVG 图片
- [ ] 导出 JSON 数据
- [ ] 测试深度限制

---

## 📊 性能优化

### 缓存策略
- 元数据快照缓存：5 分钟 TTL
- 配置信息缓存：Session 级别
- 依赖树缓存：按需生成

### 连接管理
- 连接超时：5 秒
- 每次请求创建新连接
- 自动关闭连接

---

## 🐛 故障排除

### 问题 1: 无法连接数据库
**解决方案**:
1. 检查数据库配置是否正确
2. 使用"测试连接"功能验证
3. 检查网络连接
4. 确认数据库服务正在运行

### 问题 2: 密码加密失败
**解决方案**:
1. 检查 .env 文件中的 ENCRYPTION_KEY
2. 确保密钥格式正确（Base64 编码）
3. 重新生成密钥

### 问题 3: 导出图片失败
**解决方案**:
1. 确保已安装 Graphviz
2. Windows: 下载并安装 Graphviz，添加到 PATH
3. Linux: `sudo apt-get install graphviz`
4. Mac: `brew install graphviz`

### 问题 4: Session 失效
**解决方案**:
1. 检查 SECRET_KEY 是否配置
2. 清除浏览器 Cookie
3. 重新激活配置

---

## 📝 更新日志

### Version 2.0 (2026-01-28)
- ✅ 新增动态数据库配置管理
- ✅ 新增实时表/视图检测
- ✅ 新增依赖关系导出功能
- ✅ 支持多种数据库类型
- ✅ 密码加密存储
- ✅ Session 管理
- ✅ Toast 通知系统

### Version 1.0 (原始版本)
- 基础视图依赖分析
- 表结构查看
- 注释管理

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目遵循原项目的许可证。

---

## 🎓 技术栈

- **后端**: Flask, PyMySQL, SQLAlchemy, cryptography, Graphviz
- **前端**: 原生 JavaScript, HTML5, CSS3
- **存储**: JSON 文件（加密）
- **安全**: Fernet 对称加密, Flask Session
- **可视化**: Graphviz, Mermaid

---

**创建时间**: 2026-01-28
**最后更新**: 2026-01-28
**版本**: 2.0.0
