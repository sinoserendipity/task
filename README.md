### Python + Flask + SQLite 任务统计记录
执行 python app.py
浏览器地址 http://127.0.0.1:5000

项目目录结构
确保你的项目目录结构如下：

```text
your_project/
├── app.py
├── templates/
│   └── index.html
├── requirements.txt
└── Dockerfile
```

构建和运行 Docker 容器
构建镜像： 在项目根目录下运行以下命令：

```bash
docker build -t task-recorder .
```
运行容器： 构建完成后，运行以下命令启动容器：

```bash
docker run -d -p 5000:5000 --name task-recorder-container task-recorder
```

-d：后台运行容器。
-p 5000:5000：将主机的 5000 端口映射到容器的 5000 端口。
--name：为容器命名。
访问应用： 打开浏览器，访问 http://localhost:5000，你应该能看到任务记录程序的界面。
数据持久化
当前配置中，SQLite 数据库文件 tasks.db 会在容器内创建。如果容器停止或删除，数据会丢失。为了持久化数据，可以使用 Docker 卷或绑定挂载：

使用卷
修改运行命令：
```bash
docker run -d -p 5000:5000 -v task_data:/app --name task-recorder-container task-recorder
```

这里 task_data 是一个 Docker 卷，数据会存储在 Docker 的卷管理系统中。

使用绑定挂载
如果你想将数据存储在主机上的特定目录（例如 ./data），可以这样运行：

```
docker run -d -p 5000:5000 -v ./data:/app --name task-recorder-container task-recorder
```

确保 ./data 目录已存在，否则需要先创建。

注意事项
数据库路径： 代码中 SQLite 数据库文件是 tasks.db，默认存储在 /app 目录下。如果使用卷或挂载，确保路径一致，或者修改 app.py 中的数据库路径。
调试模式： 当前 Dockerfile 使用 FLASK_ENV=development 启用了调试模式。在生产环境中，建议移除此环境变量或设置为 production。
安全性： Flask 的开发服务器不适合生产环境。生产中应使用 Gunicorn 或 uWSGI，并搭配 Nginx 作为反向代理。你可以修改 CMD 为：

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

并在 requirements.txt 中添加 gunicorn。
