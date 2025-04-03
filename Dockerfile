# 使用官方 Python 3.9 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt（如果有）并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 初始化数据库（确保在容器启动时创建表）
RUN python -c "from app import init_db; init_db()"

# 暴露 Flask 默认端口
EXPOSE 5000

# 设置环境变量，启用 Flask 的开发模式
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# 运行 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0"]
