"""
Task Dashboard - 太子任务管理系统
"""
from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)
TASKS_FILE = '/tmp/tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                tasks = json.load(f)
                # 标准化任务格式
                for t in tasks:
                    if 'type' not in t:
                        # 从tag判断类型
                        tag = t.get('tag', '')
                        if '长期' in tag:
                            t['type'] = 'long'
                        elif '短期' in tag or '临时' in tag:
                            t['type'] = 'short'
                        else:
                            t['type'] = 'long'  # 默认长期
                return tasks
        except:
            return []
    return []

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
        .stats { background: #1a1a3e; padding: 15px; border-radius: 10px; margin: 20px 0; color: #888; }
        .task { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; align-items: center; gap: 10px; }
        .task.done { opacity: 0.5; }
        .priority { color: #ffd700; font-weight: bold; }
        .tag { background: #333; padding: 3px 10px; border-radius: 15px; font-size: 12px; }
        .tag.long { background: #ff6b6b; }
        .tag.short { background: #00d9ff; color: #000; }
        .status { margin-left: auto; color: #888; }
    </style>
</head>
<body>
    <h1>🔧 太子任务面板 v2</h1>
    <div class="stats" id="stats"></div>
    
    <div class="section">
        <h2>🔥 长期任务</h2>
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
                `📊 总: ${tasks.length} | 🔥 长期: ${long.length} | ⚡ 短期: ${short.length} | ✅ 完成: ${tasks.filter(t => t.status === 'done').length}`;
            
            renderTasks(long, 'long-tasks');
            renderTasks(short, 'short-tasks');
        });
    }
    
    function renderTasks(tasks, elId) {
        let html = '';
        tasks.forEach(t => {
            const tagClass = t.type === 'long' ? 'long' : 'short';
            html += `<div class="task ${t.status}">
                <span class="priority">[${t.priority || 'P5'}]</span>
                <span class="tag ${tagClass}">${t.tag || t.type}</span>
                <span class="title">${t.title}</span>
                <span class="status">${t.status}</span>
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006, debug=False)
