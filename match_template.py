#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模糊匹配模板生成工具
功能：读取模板文件和输入数据，通过模糊匹配将输入数据填充到模板中，输出到指定目录
"""

import copy
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


def load_json_file(file_path: str) -> Dict:
    """
    加载JSON文件

    Args:
        file_path: JSON文件路径

    Returns:
        解析后的JSON数据
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(file_path: str, data: Dict) -> None:
    """
    保存JSON文件

    Args:
        file_path: 保存路径
        data: 要保存的数据
    """
    with open(file_path, "w", encoding="utf-8") as f:
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

    # 处理特殊前缀映射 - 支持多种格式的Android属性key
    key_mappings = {
        # 标准 build.* 前缀
        "build.": "ro.build.",
        # hardware.* 前缀
        "hardware.": "ro.hardware.",
        # product.* 前缀
        "product.": "ro.product.",
        # phone.* 前缀
        "phone.": "gsm.",
        # 已经是 ro.* 格式的保持不变
    }

    for prefix, replacement in key_mappings.items():
        if key.startswith(prefix):
            key = replacement + key[len(prefix) :]
            break

    # 移除末尾的下划线和大写字母的转换
    # build.BOARD -> ro.build.board (已经是小写)
    return key


def get_key_variants(key: str) -> List[str]:
    """
    获取一个key的所有可能变体，用于匹配

    Args:
        key: 原始key

    Returns:
        key变体列表
    """
    variants = set()
    key_lower = key.lower()

    # 添加原始key
    variants.add(key_lower)

    # 添加标准化后的key
    normalized = normalize_key(key)
    variants.add(normalized)

    # 如果是 build.XXX 格式，添加 ro.build.XXX 变体
    if key_lower.startswith("build."):
        variants.add("ro." + key_lower)
    # 如果是 hardware.XXX 格式，添加 ro.hardware.XXX 变体
    elif key_lower.startswith("hardware."):
        variants.add("ro." + key_lower)

    return list(variants)


def exact_match(description: str, input_data: Dict) -> Optional[str]:
    """
    方法1: 精确匹配 - description与标准化后的key完全匹配

    Args:
        description: 模板中的description字段
        input_data: 输入数据字典

    Returns:
        匹配到的值，如果没有匹配返回None
    """
    if not description:
        return None

    desc_lower = str(description).lower()

    # 直接精确匹配
    for key in input_data.keys():
        key_normalized = normalize_key(key)
        if key_normalized == desc_lower:
            return str(input_data[key])

    return None


def suffix_match(description: str, input_data: Dict) -> Optional[str]:
    """
    方法2: 后缀匹配 - 匹配description的最后部分与key的后缀

    例如: ro.build.version.release -> 尝试匹配 version.release 或 build.version.release

    Args:
        description: 模板中的description字段
        input_data: 输入数据字典

    Returns:
        匹配到的值，如果没有匹配返回None
    """
    if not description:
        return None

    desc_lower = str(description).lower()
    parts = desc_lower.split(".")

    # 从最长的后缀开始尝试匹配
    for i in range(len(parts), 0, -1):
        partial_key = ".".join(parts[-i:])

        for key in input_data.keys():
            key_normalized = normalize_key(key)

            # 精确后缀匹配：key以partial_key结尾
            if key_normalized.endswith(partial_key):
                return str(input_data[key])

    return None


def special_mapping_match(description: str, input_data: Dict) -> Optional[str]:
    """
    方法3: 特殊字段映射 - 使用预定义的映射表

    Args:
        description: 模板中的description字段
        input_data: 输入数据字典

    Returns:
        匹配到的值，如果没有匹配返回None
    """
    if not description:
        return None

    desc_lower = str(description).lower()

    # 特殊字段映射表 - 解决description与输入key不一致的问题
    special_mappings = {
        # version 相关
        "ro.build.version.release": "build.VERSION.RELEASE",
        "ro.build.version.sdk": "build.VERSION.SDK",
        "ro.build.version.codename": "build.VERSION.CODENAME",
        "ro.build.version.incremental": "build.VERSION.INCREMENTAL",
        "ro.build.version.security_patch": "build.VERSION.SECURITY_PATCH",
        # build 相关
        "ro.build.id": "build.ID",
        "ro.build.display": "build.DISPLAY",
        "ro.build.fingerprint": "build.FINGERPRINT",
        "ro.build.device": "build.DEVICE",
        "ro.build.product": "build.PRODUCT",
        "ro.build.manufacturer": "build.MANUFACTURER",
        "ro.build.model": "build.MODEL",
        "ro.build.brand": "build.BRAND",
        "ro.build.hardware": "build.HARDWARE",
        "ro.build.board": "build.BOARD",
        "ro.build.type": "build.TYPE",
        "ro.build.tags": "build.TAGS",
        # radio 相关
        "gsm.version.baseband": "build.RADIO",
        # sim/network 相关
        "gsm.sim.operator": "phone.SimOperatorName",
        "gsm.network.operator": "phone.NetworkOperatorName",
        # hardware 相关
        "ro.hardware": "build.HARDWARE",
        # 产品相关
        "ro.product.device": "build.DEVICE",
        "ro.product.model": "build.MODEL",
        "ro.product.name": "build.PRODUCT",
        "ro.product.brand": "build.BRAND",
        # 主板相关
        "ro.product.board": "build.BOARD",
        "ro.board.platform": "build.HARDWARE",
    }

    if desc_lower in special_mappings:
        mapped_key = special_mappings[desc_lower]
        if mapped_key in input_data:
            return str(input_data[mapped_key])

    return None


def smart_fuzzy_match(description: str, input_data: Dict) -> Optional[str]:
    """
    方法4: 智能模糊匹配 - 只用于简单字段名的精确部分匹配

    例如: "LCDX" -> "LCDX", "density" -> "density"
    避免匹配像 "ro.display.brightness.brightness.mode" 这种复杂字段

    Args:
        description: 模板中的description字段
        input_data: 输入数据字典

    Returns:
        匹配到的值，如果没有匹配返回None
    """
    if not description:
        return None

    desc_lower = str(description).lower()

    # 只有当description不包含"."时才使用这种模糊匹配
    # 这样可以避免匹配到复杂的ro.*字段
    if "." not in desc_lower:
        for key in input_data.keys():
            key_normalized = normalize_key(key)
            if key_normalized == desc_lower:
                return str(input_data[key])

    return None


def fuzzy_match_description(description: str, input_data: Dict) -> Optional[str]:
    """
    模糊匹配description与输入数据 - 使用多策略优先级匹配

    匹配优先级：
    1. 精确匹配 (exact_match)
    2. 后缀匹配 (suffix_match)
    3. 特殊映射 (special_mapping_match)
    4. 智能模糊匹配 (smart_fuzzy_match)

    Args:
        description: 模板中的description字段
        input_data: 输入数据字典

    Returns:
        匹配到的值，如果没有匹配返回None
    """
    # 跳过数字类型的description
    if isinstance(description, (int, float)):
        return None

    if not description:
        return None

    # 方法1: 精确匹配
    result = exact_match(description, input_data)
    if result is not None:
        return result

    # 方法2: 后缀匹配
    result = suffix_match(description, input_data)
    if result is not None:
        return result

    # 方法3: 特殊映射
    result = special_mapping_match(description, input_data)
    if result is not None:
        return result

    # 方法4: 智能模糊匹配
    result = smart_fuzzy_match(description, input_data)
    if result is not None:
        return result

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
    # 深度复制模板（保持原始键值对顺序）
    result = copy.deepcopy(template)

    # 统计匹配信息
    matched_count = 0
    total_count = 0

    if "env" in result and isinstance(result["env"], list):
        for item in result["env"]:
            total_count += 1
            description = item.get("description", "")

            # 跳过数字类型的description
            if isinstance(description, (int, float)):
                continue

            # 尝试匹配值
            matched_value = fuzzy_match_description(description, input_data)

            if matched_value is not None:
                item["value"] = matched_value
                matched_count += 1
                # 如果有与description同名的额外字段，也更新它
                if str(description) in item:
                    item[str(description)] = matched_value

    return result


def generate_output_filename() -> str:
    """
    生成输出文件名，使用 yyyy-mm-dd hh:ss:mm 格式

    Returns:
        文件名（不含扩展名）
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H-%M-%S").replace(":", "-")


def main():
    """主函数"""
    # 定义路径 - 支持跨平台
    base_dir = os.path.dirname(os.path.abspath(__file__))
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
    if "env" in template:
        print(f"    - env数组长度: {len(template['env'])}")

    # 加载输入文件
    print(f"\n[2] 加载输入文件: {input_path}")
    input_raw = load_json_file(input_path)
    # 输入数据的实际数据在 data 字段中
    input_data = input_raw.get("data", {})
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
