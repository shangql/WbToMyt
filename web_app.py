#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web服务模块
提供HTTP接口用于格式转换
"""

import json
import os
from flask import Flask, render_template, request, jsonify
from match_template import (
    load_json_file,
    normalize_key,
    fuzzy_match_description,
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
    
    接收JSON数据，转换为魔云腾数字孪生格式
    
    请求体格式：
    {
        "input_data": {...},
        "template": {...}  // 可选，默认使用内置模板
    }
    
    返回格式：
    {
        "success": true/false,
        "data": {...},
        "message": "...",
        "stats": {
            "matched": 10,
            "total": 100
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "请求数据为空"
            }), 400
        
        # 获取输入数据
        input_raw = data.get('input_data')
        if not input_raw:
            return jsonify({
                "success": False,
                "message": "缺少 input_data 字段"
            }), 400
        
        # 从 data 字段提取实际数据
        input_data = input_raw.get('data', input_raw)
        
        # 获取模板（可选）
        template = data.get('template')
        if not template:
            # 使用内置默认模板（绝对路径）
            template_path = os.path.join(BASE_DIR, 'template', 'myt-origin.json')
            template = load_json_file(template_path)
        
        # 执行转换
        result = match_template_with_input(template, input_data)
        
        # 统计匹配信息
        matched_count = 0
        total_count = 0
        if 'env' in result:
            total_count = len(result['env'])
            for item in result['env']:
                if item.get('value') and item.get('description'):
                    matched_count += 1
        
        return jsonify({
            "success": True,
            "data": result,
            "message": "转换成功",
            "stats": {
                "matched": matched_count,
                "total": total_count,
                "rate": f"{matched_count}/{total_count}"
            }
        })
    
    except FileNotFoundError as e:
        return jsonify({
            "success": False,
            "message": f"模板文件不存在: {e}"
        }), 404
    except json.JSONDecodeError as e:
        return jsonify({
            "success": False,
            "message": f"JSON解析错误: {e}"
        }), 400
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "message": f"转换失败: {str(e)}",
            "detail": traceback.format_exc()
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "service": "微霸2026 转 魔云腾数字孪生 格式转换服务"
    })


if __name__ == '__main__':
    print("=" * 50)
    print("启动 Web 服务...")
    print("访问地址: http://localhost:8080")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=8080)
