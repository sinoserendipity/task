from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY, name TEXT, time REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, task_name TEXT, task_time REAL, count INTEGER,
                  UNIQUE(date, task_name, task_time))''')
    conn.commit()
    conn.close()

# 主页面
@app.route('/')
def index():
    return render_template('index.html')

# 获取所有任务
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT name, time FROM tasks')
    tasks = [{'name': row[0], 'time': round(row[1], 1)} for row in c.fetchall()]
    conn.close()
    return jsonify(tasks)

# 添加任务
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    name = data.get('name')
    time = data.get('time')
    try:
        time = float(time)
        time = round(time, 1)
        if not name or time <= 0:
            return jsonify({'success': False, 'message': '任务名称不能为空且时间必须大于0'}), 400
        if round(time * 10) != time * 10:
            return jsonify({'success': False, 'message': '时间只能有一位小数'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '时间必须是有效的数字'}), 400

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (name, time) VALUES (?, ?)', (name, time))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 获取记录
@app.route('/api/records', methods=['GET'])
def get_records():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT task_name, task_time, count FROM records WHERE date = ?', (date,))
    records = {}
    for row in c.fetchall():
        key = f"{row[0]}_{row[1]}"
        records[key] = {'count': row[2], 'time': round(row[1], 1)}
    conn.close()
    return jsonify({'date': date, 'records': records})

# 获取月度记录
@app.route('/api/monthly_records', methods=['GET'])
def get_monthly_records():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT task_name, task_time, SUM(count) FROM records WHERE date LIKE ? GROUP BY task_name, task_time', (f'{month}%',))
    records = {}
    for row in c.fetchall():
        key = f"{row[0]}_{row[1]}"
        records[key] = {'count': row[2], 'time': round(row[1], 1)}
    conn.close()
    return jsonify(records)

# 增加任务计数
@app.route('/api/increment', methods=['POST'])
def increment_task():
    data = request.json
    task_index = data.get('task_index')
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT name, time FROM tasks LIMIT 1 OFFSET ?', (task_index,))
    task = c.fetchone()
    if task:
        date = datetime.now().strftime('%Y-%m-%d')
        c.execute('''INSERT INTO records (date, task_name, task_time, count)
                     VALUES (?, ?, ?, 1)
                     ON CONFLICT(date, task_name, task_time) DO UPDATE SET count = count + 1''',
                  (date, task[0], task[1]))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    conn.close()
    return jsonify({'success': False}), 400

# 更新任务计数
@app.route('/api/update_count', methods=['POST'])
def update_count():
    data = request.json
    task_key = data.get('task_key')
    count = max(0, int(data.get('count')))
    name, time = task_key.split('_')
    time = float(time)
    date = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    if count == 0:
        c.execute('DELETE FROM records WHERE date = ? AND task_name = ? AND task_time = ?',
                 (date, name, time))
    else:
        c.execute('INSERT OR REPLACE INTO records (date, task_name, task_time, count) VALUES (?, ?, ?, ?)',
                 (date, name, time, count))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)