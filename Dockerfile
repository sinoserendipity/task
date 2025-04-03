# 使用官方 Python 3.9 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 初始化数据库
RUN python -c "from app import init_db; init_db()"

# 暴露端口（默认 5000，可根据需要调整）
EXPOSE 5000

# 使用 Gunicorn 运行 Flask 应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
