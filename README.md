# 微霸2026 转 魔云腾数字孪生 格式转换工具

本项目用于将微霸2026机型采集的数据格式转换为魔云腾数字孪生平台所需的格式。

---

## 1. 项目概述

### 1.1 功能说明

该工具实现了两类数据格式之间的自动转换：

- **源格式（微霸2026）**：从设备采集的原始机型数据，包含 `build.*`、`phone.*`、`hardware.*` 等字段
- **目标格式（魔云腾数字孪生）**：数字孪生平台定义的模板格式，包含 `env` 数组，每个元素包含 `id`、`name`、`description`、`value` 字段

### 1.2 技术栈

- Python 3.x
- 标准库：json, os, re, datetime, typing

---

## 2. 数据格式示例

### 2.1 输入格式（微霸2026）

```json
{
  "code": 1,
  "data": {
    "build.BOARD": "NIC-LX2",
    "build.BRAND": "HONOR",
    "build.VERSION.SDK": "28",
    "build.VERSION.RELEASE": "9",
    "phone.NetworkOperatorName": "中国电信",
    "hardware.GPURender": "Mali-G78",
    "hardware.dpi": 480
  }
}
```

### 2.2 输出格式（魔云腾数字孪生）

```json
{
  "env": [
    {
      "id": 0,
      "name": "PropRw",
      "description": "ro.build.version.sdk",
      "value": "28"
    },
    {
      "id": 0,
      "name": "PropRw", 
      "description": "ro.build.version.release",
      "value": "9"
    }
  ]
}
```

---

## 3. 目录结构

```
项目根目录/
├── input/                  # 输入数据目录（微霸采集的原始数据）
│   └── res_1.json         # 示例输入文件
├── template/              # 模板文件目录（魔云腾标准模板）
│   └── myt-origin.json    # 目标格式模板
├── myoutput/              # 输出结果目录
│   └── *.json             # 转换后的结果文件
├── match_template.py      # 主程序入口
├── AGENTS.md              # 开发规范
└── README.md              # 本文件
```

---

## 4. 快速开始

### 4.1 运行转换

```bash
# 直接运行
python match_template.py
```

### 4.2 运行效果

程序执行后会输出：

```
==================================================
模糊匹配模板生成工具
==================================================

[1] 加载模板文件: template/myt-origin.json
    - 模板结构: ['env']
    - env数组长度: 1200+

[2] 加载输入文件: input/res_1.json
    - 输入数据键数量: 80+
    - 部分输入键: ['build.BOARD', 'build.BRAND', 'build.DATE.UTC']...

[3] 执行模糊匹配...
匹配统计: 800+/1200+ 项匹配成功

[4] 保存结果到: myoutput/2026-03-04 22-16-00.json

完成！输出文件: myoutput/2026-03-04 22-16-00.json
==================================================
```

---

## 5. 匹配算法说明

### 5.1 匹配策略

工具采用多策略模糊匹配，依次尝试：

1. **精确匹配**：将输入key标准化后直接匹配模板description
2. **部分路径匹配**：尝试匹配description的最后几级路径
3. **包含关系匹配**：检查description是否包含在输入key中，或反之
4. **特殊字段映射**：针对已知字段建立映射表（如 `build.VERSION.SDK` → `ro.build.version.sdk`）

### 5.2 Key标准化规则

输入数据的key会被标准化处理：

| 原始前缀 | 转换后前缀 | 示例 |
|---------|-----------|------|
| `build.` | `ro.build.` | `build.BOARD` → `ro.build.board` |
| `phone.` | `gsm.` | `phone.SimOperator` → `gsm.sim.operator` |
| `hardware.` | `hw.` | `hardware.GPURender` → `hw.gpurender` |

### 5.3 特殊映射表

对于无法通过规则自动匹配的字段，使用预定义的特殊映射表：

```python
special_mappings = {
    'ro.build.version.release': 'build.VERSION.RELEASE',
    'ro.build.version.sdk': 'build.VERSION.SDK',
    'gsm.version.baseband': 'build.RADIO',
    'gsm.sim.operator': 'phone.SimOperatorName',
    'ro.hardware': 'build.HARDWARE',
}
```

---

## 6. 模板配置

### 6.1 模板结构

魔云腾数字孪生模板由 `env` 数组组成，每个元素包含：

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | int | 标识符（通常为0） |
| name | string | 字段名称（如 PropRw, GL_RENDERER） |
| description | string | 匹配依据的key |
| value | string | 填充的值 |

### 6.2 自定义模板

如需使用自定义模板：

1. 将模板文件放入 `template/` 目录
2. 修改 `match_template.py` 中的路径配置：

```python
template_path = os.path.join(base_dir, "template", "your-template.json")
```

---

## 7. 开发指南

### 7.1 代码规范

遵循项目根目录下的 `AGENTS.md` 文件中的规范：

- 使用简体中文注释和文档
- 函数必须包含类型注解
- 使用 docstring 描述函数功能

### 7.2 测试

```bash
# 运行所有测试
pytest -v

# 运行单个测试
pytest tests/test_match_template.py::test_fuzzy_match_description
```

### 7.3 代码检查

```bash
# 格式化
black .

# 类型检查
mypy .

# 质量检查
pylint match_template.py
```

---

## 8. 常见问题

### 8.1 匹配率低怎么办

- 检查输入数据是否包含足够的字段
- 可在 `fuzzy_match_description` 函数中添加更多特殊映射
- 确认模板 `description` 字段与输入 `key` 格式兼容

### 8.2 如何添加新字段映射

在 `match_template.py` 的 `special_mappings` 字典中添加映射关系：

```python
special_mappings = {
    'ro.new.field': 'build.NEW_FIELD',  # description -> input key
}
```

---

## 9. 许可证

MIT License
