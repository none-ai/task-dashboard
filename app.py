"""
Task Dashboard - 项目任务管理系统 v2 (支持长期/短期任务)
"""
from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime
from flask import request

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
    <title>任务面板 v2</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f23; color: #eee; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 5px; }
        h2 { color: #ff6b6b; margin-top: 30px; }
        .stats { color: #888; font-size: 14px; margin-bottom: 20px; }
        .task { background: #1a1a3e; padding: 12px 15px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #00d9ff; }
        .task.long { border-left-color: #ff6b6b; background: #2a1a2e; }
        .task.short { border-left-color: #4ecdc4; background: #1a2a2e; }
        .task.done { border-left-color: #00ff88; opacity: 0.6; }
        .task.pending { border-left-color: #ffd93d; }
        .tag { background: #0f3460; padding: 2px 8px; border-radius: 3px; font-size: 11px; margin-right: 8px; }
        .tag.long { background: #6b2d5c; }
        .tag.short { background: #2d5c5c; }
        .priority { color: #ff6b6b; font-weight: bold; margin-right: 10px; }
        .title { font-weight: 500; }
        .meta { color: #666; font-size: 12px; margin-top: 5px; }
        .status { float: right; font-size: 12px; }
        .section { margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>🔧 太子任务面板 v2</h1>
    <div class="stats" id="stats"></div>
    
    <div class="section">
        <h2>🔥 长期任务 (重要)</h2>
        <div id="long-tasks"></div>
    </div>
    
    <div class="section">
        <h2>⚡ 短期任务</h2>
        <div id="short-tasks"></div>
    </div>
    
    <script>
    function loadTasks() {
        fetch('/api/tasks').then(r => r.json()).then(tasks => {
            const long = tasks.filter(t => t.type === 'long');
            const short = tasks.filter(t => t.type === 'short');
            
            document.getElementById('stats').innerHTML = 
                `总: ${tasks.length} | 长期: ${long.length} | 短期: ${short.length} | 已完成: ${tasks.filter(t => t.status === 'done').length}`;
            
            renderTasks(long, 'long-tasks');
            renderTasks(short, 'short-tasks');
        });
    }
    
    function renderTasks(tasks, elId) {
        let html = '';
        tasks.forEach(t => {
            const typeClass = t.type === 'long' ? 'long' : 'short';
            const tagClass = t.type === 'long' ? 'long' : 'short';
            html += `<div class="task ${typeClass} ${t.status}">
                <span class="priority">[P${t.priority || 5}]</span>
                <span class="tag ${tagClass}">${t.tag}</span>
                <span class="title">${t.title}</span>
                <span class="status">${t.status}</span>
                <div class="meta">${t.created}</div>
            </div>`;
        });
        document.getElementById(elId).innerHTML = html || '<p style="color:#666">暂无任务</p>';
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
        'tag': data.get('tag', '🔧优化'),
        'type': data.get('type', 'short'),
        'priority': data.get('priority', 5),
        'status': data.get('status', 'pending'),
        'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'updated': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    save_tasks(tasks)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
