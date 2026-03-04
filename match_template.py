#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模糊匹配模板生成工具
功能：读取模板文件和输入数据，通过模糊匹配将输入数据填充到模板中，输出到指定目录
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def load_json_file(file_path: str) -> Dict:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的JSON数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(file_path: str, data: Dict) -> None:
    """
    保存JSON文件
    
    Args:
        file_path: 保存路径
        data: 要保存的数据
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def normalize_key(key: str) -> str:
    """
    标准化输入数据的key，转换为与模板description匹配的格式
    例如: build.BOARD -> ro.build.board
    
    Args:
        key: 原始key
        
    Returns:
        标准化后的key
    """
    # 转换为小写
    key = key.lower()
    
    # 处理特殊前缀映射
    key_mappings = {
        'build.': 'ro.build.',
        'phone.': 'gsm.',
        'hardware.': 'hw.',
    }
    
    for prefix, replacement in key_mappings.items():
        if key.startswith(prefix):
            key = replacement + key[len(prefix):]
            break
    
    return key


def fuzzy_match_description(description: str, input_data: Dict) -> Optional[str]:
    """
    模糊匹配description与输入数据
    
    Args:
        description: 模板中的description字段
        input_data: 输入数据字典
        
    Returns:
        匹配到的值，如果没有匹配返回None
    """
    if not description:
        return None
    
    # 将description转换为小写进行匹配
    desc_lower = str(description).lower()
    
    # 方法1: 直接精确匹配输入数据的key
    for key in input_data.keys():
        key_normalized = normalize_key(key)
        if key_normalized == desc_lower:
            return str(input_data[key])
    
    # 方法2: 匹配description中的最后一部分
    # 例如: ro.build.version.release -> 尝试匹配 build.version.release 或 version.release
    parts = desc_lower.split('.')
    for i in range(len(parts), 0, -1):
        partial_key = '.'.join(parts[-i:])
        for key in input_data.keys():
            key_normalized = normalize_key(key)
            if key_normalized.endswith(partial_key) or partial_key in key_normalized:
                return str(input_data[key])
    
    # 方法3: 检查description是否包含在输入key中
    for key in input_data.keys():
        key_normalized = normalize_key(key)
        if desc_lower in key_normalized or key_normalized in desc_lower:
            return str(input_data[key])
    
    # 方法4: 处理特殊字段映射
    special_mappings = {
        'ro.build.version.release': 'build.VERSION.RELEASE',
        'ro.build.version.sdk': 'build.VERSION.SDK',
        'ro.build.version.codename': 'build.VERSION.CODENAME',
        'ro.build.version.incremental': 'build.VERSION.INCREMENTAL',
        'ro.build.version.security_patch': 'build.VERSION.SECURITY_PATCH',
        'ro.build.id': 'build.ID',
        'ro.build.display': 'build.DISPLAY',
        'ro.build.fingerprint': 'build.FINGERPRINT',
        'ro.build.device': 'build.DEVICE',
        'ro.build.product': 'build.PRODUCT',
        'ro.build.manufacturer': 'build.MANUFACTURER',
        'ro.build.model': 'build.MODEL',
        'ro.build.brand': 'build.BRAND',
        'ro.build.hardware': 'build.HARDWARE',
        'ro.build.board': 'build.BOARD',
        'ro.build.type': 'build.TYPE',
        'ro.build.tags': 'build.TAGS',
        'gsm.version.baseband': 'build.RADIO',
        'gsm.sim.operator': 'phone.SimOperatorName',
        'gsm.network.operator': 'phone.NetworkOperatorName',
        'ro.hardware': 'build.HARDWARE',
    }
    
    if desc_lower in special_mappings:
        mapped_key = special_mappings[desc_lower]
        if mapped_key in input_data:
            return str(input_data[mapped_key])
    
    return None


def match_template_with_input(template: Dict, input_data: Dict) -> Dict:
    """
    将输入数据模糊匹配到模板
    
    Args:
        template: 模板数据
        input_data: 输入数据（取data字段）
        
    Returns:
        填充后的模板数据
    """
    # 深度复制模板
    result = json.loads(json.dumps(template))
    
    # 统计匹配信息
    matched_count = 0
    total_count = 0
    
    if 'env' in result and isinstance(result['env'], list):
        for item in result['env']:
            total_count += 1
            description = item.get('description', '')
            
            # 尝试匹配值
            matched_value = fuzzy_match_description(description, input_data)
            
            if matched_value is not None:
                item['value'] = matched_value
                matched_count += 1
                # 如果有与description同名的额外字段，也更新它
                if str(description) in item:
                    item[str(description)] = matched_value
    
    print(f"匹配统计: {matched_count}/{total_count} 项匹配成功")
    
    return result


def generate_output_filename() -> str:
    """
    生成输出文件名，使用 yyyy-mm-dd hh:ss:mm 格式
    
    Returns:
        文件名（不含扩展名）
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S").replace(":", "-")


def main():
    """主函数"""
    # 定义路径
    base_dir = r"C:\Users\Administrator\PyCharmMiscProject"
    template_path = os.path.join(base_dir, "template", "myt-origin.json")
    input_path = os.path.join(base_dir, "input", "res_1.json")
    output_dir = os.path.join(base_dir, "myoutput")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 50)
    print("模糊匹配模板生成工具")
    print("=" * 50)
    
    # 加载模板文件
    print(f"\n[1] 加载模板文件: {template_path}")
    template = load_json_file(template_path)
    print(f"    - 模板结构: {list(template.keys())}")
    if 'env' in template:
        print(f"    - env数组长度: {len(template['env'])}")
    
    # 加载输入文件
    print(f"\n[2] 加载输入文件: {input_path}")
    input_raw = load_json_file(input_path)
    # 输入数据的实际数据在 data 字段中
    input_data = input_raw.get('data', {})
    print(f"    - 输入数据键数量: {len(input_data)}")
    print(f"    - 部分输入键: {list(input_data.keys())[:5]}...")
    
    # 执行模糊匹配
    print(f"\n[3] 执行模糊匹配...")
    result = match_template_with_input(template, input_data)
    
    # 生成输出文件名
    output_filename = generate_output_filename()
    output_path = os.path.join(output_dir, f"{output_filename}.json")
    
    # 保存结果
    print(f"\n[4] 保存结果到: {output_path}")
    save_json_file(output_path, result)
    
    print(f"\n完成！输出文件: {output_path}")
    print("=" * 50)
    
    return output_path


if __name__ == "__main__":
    main()
