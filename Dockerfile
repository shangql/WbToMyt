# 微霸转魔云腾格式转换工具 - Docker 镜像

# 使用官方 Python 轻量级镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 防止 Python 输出缓冲，确保日志实时显示
ENV PYTHONUNBUFFERED=1
# 设置默认端口
ENV FLASK_RUN_PORT=8080

# 安装系统依赖（用于构建 Python 扩展）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p input myoutput template

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "web_app.py"]
