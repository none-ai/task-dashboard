# 任务面板 v3 - Task Dashboard

现代化任务管理系统，支持长期任务和短期任务的高效管理。

## 🎯 功能特点

- **长期任务管理** - P1-P10优先级体系
- **短期任务管理** - 快速创建和处理即时任务
- **任务状态追踪** - 实时了解任务进度
- **SQLite持久化** - 数据存储稳定可靠
- **CRUD完整操作** - 支持创建、读取、更新、删除任务
- **分类管理** - 工作、学习、生活等自定义分类
- **搜索过滤** - 按类型、状态、分类搜索任务
- **截止日期** - 支持任务截止日期设置
- **优先级管理** - P1-P5优先级，颜色区分显示
- **现代化深色UI** - 护眼深色主题设计

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/none-ai/task-dashboard.git
cd task-dashboard

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

访问 http://localhost:8006

## 📋 路由说明

| 路由 | 说明 |
|------|------|
| `/` | 任务面板首页 |
| `/add` | 添加新任务 |
| `/edit/<id>` | 编辑任务 |
| `/delete/<id>` | 删除任务 |
| `/api/tasks` | 任务API接口 |

## 🛠️ 技术栈

- **后端**: Python 3, Flask
- **数据库**: SQLite
- **前端**: HTML, CSS, JavaScript
- **UI框架**: Bootstrap (可选)

## 📊 任务优先级

| 优先级 | 颜色 | 说明 |
|--------|------|------|
| P1 | 🔴 红色 | 最高优先级 |
| P2 | 🟠 橙色 | 高优先级 |
| P3 | 🟡 黄色 | 中等优先级 |
| P4 | 🟢 绿色 | 低优先级 |
| P5 | 🔵 蓝色 | 最低优先级 |

## 📄 许可证

MIT License

---

作者: stlin256's openclaw
