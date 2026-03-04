#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web服务模块
提供HTTP接口用于格式转换
输入输出格式与 match_template.py 命令行一致
"""

import json
import os
from flask import Flask, render_template, request, Response
from match_template import (
    load_json_file,
    match_template_with_input
)


# 获取应用根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 创建Flask应用
app = Flask(__name__)


@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """
    转换接口
    
    请求体格式（与 res_1.json 一致）：
    {
        "code": 1,
        "data": {
            "build.BOARD": "NIC-LX2",
            "build.BRAND": "HONOR",
            ...
        }
    }
    
    返回格式（与 match_template.py 命令行一致）：
    直接返回转换后的模板数据
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return Response(
                json.dumps({"error": "请求数据为空"}),
                status=400,
                mimetype='application/json'
            )
        
        # 获取输入数据（与 match_template.py 命令行处理一致：从 data 字段提取）
        input_data = data.get('data', {})
        if not input_data:
            return Response(
                json.dumps({"error": "缺少 data 字段"}),
                status=400,
                mimetype='application/json'
            )
        
        # 加载模板（与 match_template.py 命令行一致）
        template_path = os.path.join(BASE_DIR, 'template', 'myt-origin.json')
        template = load_json_file(template_path)
        
        # 执行转换（与 match_template.py 命令行一致）
        result = match_template_with_input(template, input_data)
        
        # 直接返回转换结果，保持字典顺序
        return Response(
            json.dumps(result, ensure_ascii=False),
            mimetype='application/json'
        )
    
    except FileNotFoundError as e:
        return Response(
            json.dumps({"error": f"模板文件不存在: {e}"}),
            status=404,
            mimetype='application/json'
        )
    except json.JSONDecodeError as e:
        return Response(
            json.dumps({"error": f"JSON解析错误: {e}"}),
            status=400,
            mimetype='application/json'
        )
    except Exception as e:
        import traceback
        return Response(
            json.dumps({"error": f"转换失败: {str(e)}", "detail": traceback.format_exc()}),
            status=500,
            mimetype='application/json'
        )


@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return json.dumps({"status": "ok", "service": "微霸2026 转 魔云腾格式转换服务"})


if __name__ == '__main__':
    print("=" * 50)
    print("启动 Web 服务...")
    print("访问地址: http://localhost:8080")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=8080)
