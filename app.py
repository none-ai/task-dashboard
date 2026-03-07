"""
Task Dashboard - 太子任务管理系统 v3
增强版：SQLite持久化、CRUD操作、分类管理、搜索过滤
"""
import sqlite3
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string, g

app = Flask(__name__)
DATABASE = '/tmp/tasks.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """初始化数据库表"""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'P5',
                type TEXT DEFAULT 'long',
                status TEXT DEFAULT 'pending',
                category TEXT DEFAULT '默认',
                due_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#00d9ff'
            )
        ''')
        # 添加默认分类
        db.execute("INSERT OR IGNORE INTO categories (name, color) VALUES ('默认', '#00d9ff')")
        db.execute("INSERT OR IGNORE INTO categories (name, color) VALUES ('工作', '#ff6b6b')")
        db.execute("INSERT OR IGNORE INTO categories (name, color) VALUES ('学习', '#4ecdc4')")
        db.execute("INSERT OR IGNORE INTO categories (name, color) VALUES ('生活', '#ffe66d')")
        db.commit()

# 迁移旧数据（如果存在JSON文件）
def migrate_from_json():
    json_file = '/tmp/tasks.json'
    if os.path.exists(json_file):
        try:
            import json
            with open(json_file, 'r') as f:
                tasks = json.load(f)
            db = get_db()
            for t in tasks:
                db.execute('''
                    INSERT INTO tasks (title, description, priority, type, status, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (t.get('title', ''), t.get('description', ''),
                      t.get('priority', 'P5'), t.get('type', 'long'),
                      t.get('status', 'pending'), t.get('tag', '默认')))
            db.commit()
            os.rename(json_file, json_file + '.bak')
            print("已迁移旧数据到数据库")
        except Exception as e:
            print(f"迁移失败: {e}")

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>任务面板 v3</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }

        h1 {
            color: #00d9ff;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .subtitle { color: #666; margin-bottom: 20px; font-size: 14px; }

        /* 统计卡片 */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #16213e;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #2a2a5e;
        }
        .stat-card .num { font-size: 32px; font-weight: bold; }
        .stat-card .label { color: #888; font-size: 14px; margin-top: 5px; }
        .stat-card.total .num { color: #00d9ff; }
        .stat-card.long .num { color: #ff6b6b; }
        .stat-card.short .num { color: #4ecdc4; }
        .stat-card.done .num { color: #4ade80; }

        /* 搜索和过滤 */
        .toolbar {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .toolbar input, .toolbar select {
            background: #16213e;
            border: 1px solid #2a2a5e;
            color: #eee;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
        }
        .toolbar input:focus, .toolbar select:focus {
            outline: none;
            border-color: #00d9ff;
        }
        .btn {
            background: #00d9ff;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,217,255,0.3); }
        .btn.danger { background: #ff6b6b; }
        .btn.success { background: #4ade80; }
        .btn.small { padding: 5px 12px; font-size: 12px; }

        /* 任务卡片 */
        .task-section { margin-top: 30px; }
        .task-section h2 {
            color: #ff6b6b;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .task-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }
        .task {
            background: #16213e;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2a2a5e;
            transition: all 0.3s;
        }
        .task:hover {
            border-color: #00d9ff;
            transform: translateY(-3px);
        }
        .task.done { opacity: 0.6; }
        .task.done .title { text-decoration: line-through; }

        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .priority {
            color: #ffd700;
            font-weight: bold;
            font-size: 14px;
        }
        .priority.p1 { color: #ff4757; }
        .priority.p2 { color: #ff6b6b; }
        .priority.p3 { color: #ffa502; }
        .priority.p4 { color: #ffd700; }
        .priority.p5 { color: #7bed9f; }

        .title { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
        .description { color: #888; font-size: 14px; margin-bottom: 12px; }

        .meta {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            font-size: 12px;
        }
        .tag {
            background: #333;
            padding: 4px 12px;
            border-radius: 15px;
        }
        .tag.long { background: #ff6b6b; color: #000; }
        .tag.short { background: #00d9ff; color: #000; }
        .category {
            padding: 4px 12px;
            border-radius: 15px;
            color: #000;
        }
        .due-date {
            color: #888;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .due-date.overdue { color: #ff4757; }

        .task-actions {
            display: flex;
            gap: 8px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #2a2a5e;
        }

        /* 模态框 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.show { display: flex; }
        .modal-content {
            background: #1a1a3e;
            padding: 30px;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            border: 1px solid #2a2a5e;
        }
        .modal h2 { color: #00d9ff; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #888; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            background: #16213e;
            border: 1px solid #2a2a5e;
            color: #eee;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
        }
        .form-group textarea { min-height: 80px; resize: vertical; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #00d9ff;
        }
        .form-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }

        .empty { text-align: center; padding: 40px; color: #666; }

        /* 分类管理 */
        .category-manager {
            background: #16213e;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }
        .category-manager h3 { color: #00d9ff; margin-bottom: 15px; }
        .category-list {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .category-item {
            padding: 8px 16px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .category-item:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 太子任务面板 v3</h1>
        <p class="subtitle">增强版：SQLite持久化 | CRUD操作 | 分类管理 | 搜索过滤</p>

        <div class="stats" id="stats"></div>

        <div class="toolbar">
            <input type="text" id="search" placeholder="🔍 搜索任务..." oninput="filterTasks()">
            <select id="filterType" onchange="filterTasks()">
                <option value="">全部类型</option>
                <option value="long">长期任务</option>
                <option value="short">短期任务</option>
            </select>
            <select id="filterStatus" onchange="filterTasks()">
                <option value="">全部状态</option>
                <option value="pending">待处理</option>
                <option value="done">已完成</option>
            </select>
            <select id="filterCategory" onchange="filterTasks()">
                <option value="">全部分类</option>
            </select>
            <button class="btn" onclick="openModal()">➕ 新增任务</button>
        </div>

        <div class="task-section">
            <h2>🔥 长期任务</h2>
            <div class="task-grid" id="long-tasks"></div>
        </div>

        <div class="task-section">
            <h2>⚡ 短期任务</h2>
            <div class="task-grid" id="short-tasks"></div>
        </div>
    </div>

    <!-- 新增/编辑任务模态框 -->
    <div class="modal" id="taskModal">
        <div class="modal-content">
            <h2 id="modalTitle">➕ 新增任务</h2>
            <form id="taskForm">
                <input type="hidden" id="taskId">
                <div class="form-group">
                    <label>任务标题 *</label>
                    <input type="text" id="title" required placeholder="输入任务标题">
                </div>
                <div class="form-group">
                    <label>任务描述</label>
                    <textarea id="description" placeholder="输入任务描述（可选）"></textarea>
                </div>
                <div class="form-group">
                    <label>任务类型</label>
                    <select id="type">
                        <option value="long">长期任务</option>
                        <option value="short">短期任务</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>优先级</label>
                    <select id="priority">
                        <option value="P1">P1 - 紧急</option>
                        <option value="P2">P2 - 高</option>
                        <option value="P3">P3 - 中高</option>
                        <option value="P4">P4 - 中</option>
                        <option value="P5" selected>P5 - 低</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>分类</label>
                    <select id="category"></select>
                </div>
                <div class="form-group">
                    <label>截止日期</label>
                    <input type="date" id="dueDate">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn danger" onclick="closeModal()">取消</button>
                    <button type="submit" class="btn success">保存</button>
                </div>
            </form>
        </div>
    </div>

    <script>
    let allTasks = [];
    let categories = [];

    function loadData() {
        Promise.all([
            fetch('/api/tasks').then(r => r.json()),
            fetch('/api/categories').then(r => r.json())
        ]).then(([tasks, cats]) => {
            allTasks = tasks;
            categories = cats;
            updateCategoryFilters();
            filterTasks();
        });
    }

    function updateCategoryFilters() {
        const filterCat = document.getElementById('filterCategory');
        const formCat = document.getElementById('category');
        const opts = '<option value="">全部分类</option>' +
            categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
        filterCat.innerHTML = opts;
        formCat.innerHTML = categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
    }

    function filterTasks() {
        const search = document.getElementById('search').value.toLowerCase();
        const type = document.getElementById('filterType').value;
        const status = document.getElementById('filterStatus').value;
        const cat = document.getElementById('filterCategory').value;

        let filtered = allTasks.filter(t => {
            const matchSearch = !search ||
                t.title.toLowerCase().includes(search) ||
                (t.description && t.description.toLowerCase().includes(search));
            const matchType = !type || t.type === type;
            const matchStatus = !status || t.status === status;
            const matchCat = !cat || t.category === cat;
            return matchSearch && matchType && matchStatus && matchCat;
        });

        const long = filtered.filter(t => t.type === 'long');
        const short = filtered.filter(t => t.type === 'short');

        // 更新统计
        const doneCount = allTasks.filter(t => t.status === 'done').length;
        document.getElementById('stats').innerHTML = `
            <div class="stat-card total"><div class="num">${allTasks.length}</div><div class="label">总任务</div></div>
            <div class="stat-card long"><div class="num">${long.length}</div><div class="label">长期任务</div></div>
            <div class="stat-card short"><div class="num">${short.length}</div><div class="label">短期任务</div></div>
            <div class="stat-card done"><div class="num">${doneCount}</div><div class="label">已完成</div></div>
        `;

        renderTasks(long, 'long-tasks');
        renderTasks(short, 'short-tasks');
    }

    function renderTasks(tasks, elId) {
        if (!tasks.length) {
            document.getElementById(elId).innerHTML = '<div class="empty">暂无任务</div>';
            return;
        }

        let html = '';
        tasks.forEach(t => {
            const pClass = 'p' + t.priority.replace('P', '');
            const today = new Date().toISOString().split('T')[0];
            const overdueClass = t.due_date && t.due_date < today && t.status !== 'done' ? 'overdue' : '';

            const catColor = categories.find(c => c.name === t.category)?.color || '#00d9ff';

            html += `<div class="task ${t.status}">
                <div class="task-header">
                    <span class="priority ${pClass}">${t.priority}</span>
                    <span class="tag ${t.type}">${t.type === 'long' ? '长期' : '短期'}</span>
                </div>
                <div class="title">${t.title}</div>
                ${t.description ? `<div class="description">${t.description}</div>` : ''}
                <div class="meta">
                    <span class="category" style="background:${catColor}">${t.category}</span>
                    ${t.due_date ? `<span class="due-date ${overdueClass}">📅 ${t.due_date}</span>` : ''}
                </div>
                <div class="task-actions">
                    <button class="btn small ${t.status === 'done' ? '' : 'success'}" onclick="toggleStatus(${t.id}, '${t.status}')">
                        ${t.status === 'done' ? '↩️ 恢复' : '✅ 完成'}
                    </button>
                    <button class="btn small" onclick="editTask(${t.id})">✏️ 编辑</button>
                    <button class="btn small danger" onclick="deleteTask(${t.id})">🗑️ 删除</button>
                </div>
            </div>`;
        });
        document.getElementById(elId).innerHTML = html;
    }

    function openModal(task = null) {
        const modal = document.getElementById('taskModal');
        const form = document.getElementById('taskForm');

        if (task) {
            document.getElementById('modalTitle').textContent = '✏️ 编辑任务';
            document.getElementById('taskId').value = task.id;
            document.getElementById('title').value = task.title;
            document.getElementById('description').value = task.description || '';
            document.getElementById('type').value = task.type;
            document.getElementById('priority').value = task.priority;
            document.getElementById('category').value = task.category;
            document.getElementById('dueDate').value = task.due_date || '';
        } else {
            document.getElementById('modalTitle').textContent = '➕ 新增任务';
            form.reset();
            document.getElementById('taskId').value = '';
        }

        modal.classList.add('show');
    }

    function closeModal() {
        document.getElementById('taskModal').classList.remove('show');
    }

    function editTask(id) {
        const task = allTasks.find(t => t.id === id);
        if (task) openModal(task);
    }

    document.getElementById('taskForm').onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('taskId').value;
        const data = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            type: document.getElementById('type').value,
            priority: document.getElementById('priority').value,
            category: document.getElementById('category').value,
            due_date: document.getElementById('dueDate').value || null
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/tasks/${id}` : '/api/tasks';

        await fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        closeModal();
        loadData();
    };

    async function toggleStatus(id, status) {
        const newStatus = status === 'done' ? 'pending' : 'done';
        await fetch(`/api/tasks/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status: newStatus})
        });
        loadData();
    }

    async function deleteTask(id) {
        if (!confirm('确定要删除这个任务吗？')) return;
        await fetch(`/api/tasks/${id}`, {method: 'DELETE'});
        loadData();
    }

    // 关闭模态框点击背景
    document.getElementById('taskModal').onclick = (e) => {
        if (e.target.id === 'taskModal') closeModal();
    };

    loadData();
    setInterval(loadData, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

# ========== API 路由 ==========

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    db = get_db()
    tasks = db.execute('SELECT * FROM tasks ORDER BY CASE status WHEN "pending" THEN 0 ELSE 1 END, priority, created_at DESC').fetchall()
    return jsonify([dict(row) for row in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    db = get_db()
    db.execute('''
        INSERT INTO tasks (title, description, type, priority, category, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['title'], data.get('description'), data.get('type', 'long'),
          data.get('priority', 'P5'), data.get('category', '默认'), data.get('due_date')))
    db.commit()
    return jsonify({'success': True, 'message': '任务创建成功'})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    db = get_db()
    db.execute('''
        UPDATE tasks SET
            title = COALESCE(?, title),
            description = COALESCE(?, description),
            type = COALESCE(?, type),
            priority = COALESCE(?, priority),
            status = COALESCE(?, status),
            category = COALESCE(?, category),
            due_date = COALESCE(?, due_date),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (data.get('title'), data.get('description'), data.get('type'),
          data.get('priority'), data.get('status'), data.get('category'),
          data.get('due_date'), task_id))
    db.commit()
    return jsonify({'success': True, 'message': '任务更新成功'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    return jsonify({'success': True, 'message': '任务删除成功'})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    db = get_db()
    cats = db.execute('SELECT * FROM categories').fetchall()
    return jsonify([dict(row) for row in cats])

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    db = get_db()
    try:
        db.execute('INSERT INTO categories (name, color) VALUES (?, ?)',
                  (data['name'], data.get('color', '#00d9ff')))
        db.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False, 'message': '分类已存在'}), 400

if __name__ == '__main__':
    init_db()
    migrate_from_json()
    app.run(host='0.0.0.0', port=8006, debug=True)
