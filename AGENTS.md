# 项目开发规范

**Generated:** 2026-03-05
**Project:** 微霸转魔云腾格式转换工具

## 项目概述

| 属性 | 值 |
|------|-----|
| 类型 | Python CLI + Web 工具 |
| 入口 | `match_template.py` (CLI), `web_app.py` (Web) |
| 依赖 | Flask (Web) |

## 目录结构

```
./
├── match_template.py   # 主程序入口（模糊匹配核心逻辑）
├── web_app.py         # Flask Web 服务入口
├── template/           # 魔云腾模板 JSON
├── input/             # 输入数据目录
├── myoutput/          # 输出结果目录
├── templates/          # Flask HTML 模板
├── start.sh/stop.sh   # 启动/停止脚本
└── AGENTS.md          # 本文件
```

## 代码地图

| 符号 | 类型 | 位置 | 作用 |
|------|------|------|------|
| `fuzzy_match_description` | 函数 | match_template.py:259 | 多策略模糊匹配主入口 |
| `exact_match` | 函数 | match_template.py:109 | 精确匹配策略 |
| `suffix_match` | 函数 | match_template.py:134 | 后缀匹配策略 |
| `special_mapping_match` | 函数 | match_template.py:167 | 特殊字段映射 |
| `normalize_key` | 函数 | match_template.py:42 | key 标准化 |
| `match_template_with_input` | 函数 | match_template.py:306 | 模板填充核心 |
| Flask app | 应用 | web_app.py | REST API |

## 匹配策略优先级

1. 精确匹配 → 2. 后缀匹配 → 3. 特殊映射 → 4. 智能模糊匹配

## 约定（偏离标准处）

- **无包结构**：代码在根目录，无 `src/` 包
- **硬编码路径**：`match_template.py:360-363` 定义路径
- **无 `__main__.py`**：`python -m match_template` 不工作

---

## 1. 项目概述

本项目是一个 Python 工具，用于模糊匹配模板数据与输入数据，并将结果输出到指定目录。

**技术栈**：
- Python 3.x
- 标准库（json, os, re, datetime, typing）

---

## 2. 运行与测试命令

### 2.1 运行主程序

```bash
# 直接运行主脚本（Windows）
python match_template.py

# 或使用 Python 模块方式
python -m match_template
```

### 2.2 测试命令

本项目使用 **pytest** 作为测试框架。

```bash
# 运行所有测试
pytest

# 运行所有测试（详细输出）
pytest -v

# 运行单个测试文件
pytest tests/test_match_template.py

# 运行单个测试函数
pytest tests/test_match_template.py::test_fuzzy_match_description

# 运行单个测试函数（使用完整路径）
pytest tests/test_match_template.py -k "test_function_name"

# 显示测试覆盖率
pytest --cov=. --cov-report=term-missing
```

### 2.3 代码检查与格式化

```bash
# 运行所有检查（flake8 + black）
flake8 .
black --check .

# 自动格式化代码
black .

# 类型检查
mypy .

# 运行完整的质量检查
pylint match_template.py
```

### 2.4 虚拟环境

```bash
# 创建虚拟环境（Windows）
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install pytest black flake8 pylint mypy
```

---

## 3. 代码风格规范

### 3.1 总体原则

- **语言一致性**：所有代码注释、文档、Git 提交信息必须使用简体中文
- **代码注释**：必须包含详尽的中文逻辑注释，严禁无注释或纯英文注释
- **DRY 原则**：避免重复代码，追求高内聚低耦合
- **错误处理**：提供健壮的异常处理机制

### 3.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | 小写字母 + 下划线 | `match_template.py`, `my_utils.py` |
| 函数名 | 蛇形命名法 + 动词 | `load_json_file()`, `fuzzy_match_description()` |
| 变量名 | 蛇形命名法 + 名词 | `input_data`, `matched_count` |
| 类名 | 帕斯卡命名法 | `DataProcessor`, `TemplateMatcher` |
| 常量 | 全大写 + 下划线 | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 私有成员 | 单下划线前缀 | `_internal_method()`, `_private_var` |

### 3.3 导入规范

```python
# 标准库放在最前面
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

# 第三方库放在中间（如果有）
# import requests
# import pandas as pd

# 本地模块放在最后（如果有）
# from . import utils
# from .models import UserModel
```

**规则**：
- 每类库之间用空行分隔
- 导入语句按字母排序
- 避免使用 `from xxx import *`
- 使用绝对导入而非相对导入

### 3.4 类型注解

必须为所有函数参数和返回值添加类型注解：

```python
# 正确示例
def load_json_file(file_path: str) -> Dict:
    """加载 JSON 文件"""
    ...

def process_data(data: Dict[str, Any], options: Optional[Dict] = None) -> List[Dict]:
    """处理数据并返回结果列表"""
    ...

# 避免
def process_data(data):  # 缺少类型注解
    ...
```

### 3.5 函数与类规范

每个函数和类必须包含中文文档字符串（docstring）：

```python
def function_name(param1: str, param2: int) -> bool:
    """
    函数功能的简要描述
    
    详细说明函数的工作原理、参数含义、返回值以及可能的异常。
    
    Args:
        param1: 参数1的用途和说明
        param2: 参数2的用途和说明
        
    Returns:
        返回值的说明
        
    Raises:
        ValueError: 当参数无效时抛出
        FileNotFoundError: 当文件不存在时抛出
    """
    # 函数实现...
    pass
```

### 3.6 缩进与格式化

- **缩进**：使用 4 个空格缩进（不使用 Tab）
- **行长度**：每行不超过 120 个字符
- **空格**：
  - 逗号后加空格：`[1, 2, 3]`
  - 运算符两侧加空格：`a + b = c`
  - 关键字参数不加空格：`function(arg1=value1, arg2=value2)`
- **空行**：
  - 顶级定义之间空两行
  - 方法定义之间空一行
  - 逻辑相关的代码块之间空一行

### 3.7 错误处理规范

```python
# 优先使用具体的异常类型
try:
    result = load_json_file(file_path)
except FileNotFoundError:
    # 处理文件不存在的情况
    logging.error(f"配置文件不存在: {file_path}")
    raise
except json.JSONDecodeError as e:
    # 处理 JSON 解析错误
    logging.error(f"JSON 格式错误: {e}")
    raise
except Exception as e:
    # 捕获所有其他异常
    logging.exception(f"未知错误: {e}")
    raise
```

**规则**：
- 避免裸 `except:`，始终指定具体异常类型
- 优先在异常发生处处理，否则向上抛出
- 使用 logging 而非 print 进行错误输出

### 3.8 常量与配置

- 将硬编码的值抽取为常量或配置文件
- 使用枚举类定义相关常量集合
- 敏感信息（如密码、API 密钥）不得硬编码

```python
# 推荐
class AppConfig:
    """应用配置类"""
    MAX_RETRY = 3
    TIMEOUT_SECONDS = 30
    DEFAULT_ENCODING = "utf-8"

# 避免
def some_function():
    retry = 3  # 硬编码
    timeout = 30
```

---

## 4. Git 提交规范

### 4.1 提交信息格式

```
<类型>(<范围>): <简短描述>

[可选的详细描述]

[可选的脚注]
```

**类型**：
- `feat`: 新功能
- `fix`: 错误修复
- `refactor`: 代码重构
- `docs`: 文档更新
- `style`: 代码格式调整
- `test`: 测试相关
- `chore`: 构建或辅助工具变动

### 4.2 示例

```
feat(模板匹配): 添加模糊匹配算法支持

实现了基于多策略的模糊匹配算法：
- 精确匹配
- 部分路径匹配
- 包含关系匹配
- 特殊字段映射

解决了 issue #123 中描述的问题

Closes #123
```

---

## 5. 目录结构规范

```
项目根目录/
├── .venv/              # 虚拟环境（不提交）
├── input/              # 输入数据目录
├── myoutput/          # 输出结果目录
├── template/          # 模板文件目录
├── tests/              # 测试文件目录
│   └── test_*.py       # 测试文件
├── match_template.py   # 主程序入口
├── AGENTS.md           # 本文件
└── README.md           # 项目说明
```

---

## 6. 注意事项

1. **不提交的文件**：`.venv/`、`__pycache__/`、`*.pyc`、`.idea/`、`*.log`
2. **路径处理**：使用 `os.path.join()` 拼接路径，避免硬编码路径分隔符
3. **字符编码**：文件读写统一使用 `utf-8` 编码
4. **日志输出**：使用 `logging` 模块而非 `print`

---

## 7. 常用开发工具

- **IDE**: PyCharm / VS Code
- **Python 版本**: 3.8+
- **推荐插件**:
  - Python (VS Code)
  - Pylance (VS Code)
  - Black Formatter (VS Code)
  - Flake8 (VS Code)
