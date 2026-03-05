#!/bin/bash
# ==================================================
# 停止 Web 服务脚本
# 支持 Linux 和 macOS
# ==================================================

# 设置语言为中文
export LANG=zh_CN.UTF-8

echo "=================================================="
echo "停止 Web 服务..."
echo "=================================================="

# 方法1：查找并终止占用 8080 端口的 Python 进程
if command -v lsof &> /dev/null; then
    # macOS 和 Linux (如果安装了 lsof)
    PID=$(lsof -ti:8080)
    if [ -n "$PID" ]; then
        echo "终止进程 PID: $PID"
        kill -9 $PID 2>/dev/null
        echo "服务已停止"
    else
        echo "未发现占用 8080 端口的进程"
    fi
else
    # 方法2：使用 netstat（Linux 通用）
    PID=$(netstat -tlnp 2>/dev/null | grep :8080 | awk '{print $7}' | cut -d'/' -f1)
    if [ -n "$PID" ]; then
        echo "终止进程 PID: $PID"
        kill -9 $PID 2>/dev/null
        echo "服务已停止"
    else
        # 方法3：使用 ss（新版 Linux）
        PID=$(ss -tlnp 2>/dev/null | grep :8080 | awk '{print $6}' | cut -d'=' -f2 | cut -d',' -f1)
        if [ -n "$PID" ]; then
            echo "终止进程 PID: $PID"
            kill -9 $PID 2>/dev/null
            echo "服务已停止"
        else
            echo "未发现占用 8080 端口的进程"
        fi
    fi
fi
