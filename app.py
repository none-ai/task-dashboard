"""
Task Dashboard - 项目任务管理系统
"""
from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

TASKS_FILE = '/tmp/tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>任务面板</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
        h1 { color: #00d9ff; }
        .task { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #00d9ff; }
        .task.done { border-left-color: #00ff88; opacity: 0.7; }
        .task.in-progress { border-left-color: #ffaa00; }
        .tag { background: #0f3460; padding: 3px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
        .status { float: right; font-size: 12px; }
        .time { color: #888; font-size: 12px; }
        .add-form { background: #16213e; padding: 15px; border-radius: 8px; margin: 20px 0; }
        input, select, button { padding: 8px; margin: 5px; border-radius: 4px; border: none; }
        button { background: #00d9ff; color: #000; cursor: pointer; }
        button:hover { background: #00b8d4; }
    </style>
</head>
<body>
    <h1>📋 项目任务面板</h1>
    
    <div class="add-form">
        <h3>添加新任务</h3>
        <input type="text" id="title" placeholder="任务标题" size="40">
        <input type="text" id="tag" placeholder="标签(研究/开发/部署)" size="15">
        <select id="status">
            <option value="pending">待处理</option>
            <option value="in-progress">进行中</option>
            <option value="done">已完成</option>
        </select>
        <button onclick="addTask()">添加</button>
    </div>
    
    <div id="tasks"></div>
    
    <script>
    function loadTasks() {
        fetch('/api/tasks').then(r => r.json()).then(tasks => {
            let html = '';
            tasks.forEach(t => {
                html += `<div class="task ${t.status}">
                    <span class="status">${t.status}</span>
                    <span class="tag">${t.tag}</span>
                    <strong>${t.title}</strong>
                    <div class="time">${t.created}</div>
                </div>`;
            });
            document.getElementById('tasks').innerHTML = html;
        });
    }
    
    function addTask() {
        const title = document.getElementById('title').value;
        const tag = document.getElementById('tag').value;
        const status = document.getElementById('status').value;
        if (!title) return;
        
        fetch('/api/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title, tag, status})
        }).then(() => {
            document.getElementById('title').value = '';
            loadTasks();
        });
    }
    
    loadTasks();
    setInterval(loadTasks, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/tasks')
def get_tasks():
    return jsonify(load_tasks())

@app.route('/api/tasks', methods=['POST'])
def add_task():
    tasks = load_tasks()
    data = request.json
    tasks.append({
        'title': data.get('title', ''),
        'tag': data.get('tag', '研究'),
        'status': data.get('status', 'pending'),
        'created': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    save_tasks(tasks)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
