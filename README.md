# 微霸转魔云腾格式转换工具

一个用于模糊匹配模板数据与输入数据，并将结果输出到指定目录的工具。主要用于将微霸（WeBang）采集的 Android 设备信息转换为魔云腾（MoYunTeng）格式。

## 功能特性

- **多策略模糊匹配**：支持精确匹配、部分路径匹配、包含关系匹配和特殊字段映射
- **命令行模式**：通过 Python 脚本直接运行转换
- **Web 服务模式**：提供 RESTful API 接口，支持 HTTP 请求调用
- **中文支持**：完整支持中文数据处理

## 目录结构

```
项目根目录/
├── .venv/              # 虚拟环境（不提交）
├── input/              # 输入数据目录
│   └── res_1.json      # 输入数据示例
├── myoutput/          # 输出结果目录
├── template/          # 模板文件目录
│   └── myt-origin.json # 魔云腾模板
├── tests/              # 测试文件目录（预留）
├── web_app.py         # Web 服务入口
├── match_template.py  # 命令行主程序
├── requirements.txt   # 依赖清单
├── start.cmd          # Windows 启动脚本
├── stop.cmd           # Windows 停止脚本
└── README.md          # 本文件
```

## 环境要求

- Python 3.8 或更高版本
- Windows / macOS / Linux

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <项目地址>
cd WbToMyt
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法一：命令行模式

#### 1. 准备输入数据

将待转换的数据放入 `input` 目录，文件名可自定义，格式如下：

```json
{
  "code": 1,
  "data": {
    "build.BOARD": "NIC-LX2",
    "build.BRAND": "HONOR",
    "build.DEVICE": "NIC-LX2",
    "build.MODEL": "NIC-LX2",
    ...
  }
}
```

#### 2. 修改配置文件

编辑 `match_template.py` 中的路径配置：

```python
# 第 195-198 行
base_dir = r"C:\Users\Administrator\PycharmProjects\WbToMyt"  # 修改为你的项目路径
template_path = os.path.join(base_dir, "template", "myt-origin.json")
input_path = os.path.join(base_dir, "input", "res_1.json")  # 修改为你的输入文件名
output_dir = os.path.join(base_dir, "myoutput")
```

#### 3. 运行转换

```bash
# Windows
python match_template.py

# 或使用 Python 模块方式
python -m match_template
```

#### 4. 查看结果

转换结果将保存在 `myoutput` 目录中，文件名格式为 `yyyy-mm-dd hh-mm-ss.json`。

---

### 方法二：Web 服务模式

#### 1. 启动服务

```bash
# Windows（使用提供的脚本）
start.cmd

# 或手动运行
python web_app.py
```

服务启动后将显示：

```
==================================================
启动 Web 服务...
访问地址: http://localhost:8080
==================================================
```

#### 2. 访问 Web 界面

打开浏览器访问 `http://localhost:8080` 可以看到转换界面。

#### 3. 调用转换接口

使用 POST 请求调用转换接口：

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "code": 1,
    "data": {
      "build.BOARD": "NIC-LX2",
      "build.BRAND": "HONOR",
      "build.DEVICE": "NIC-LX2",
      "build.MODEL": "NIC-LX2"
    }
  }'
```

#### 4. 停止服务

```bash
# Windows（使用提供的脚本）
stop.cmd
```

## 转换示例

### 输入数据（微霸格式）

```json
{
  "code": 1,
  "data": {
    "build.BOARD": "NIC-LX2",
    "build.BRAND": "HONOR",
    "build.DEVICE": "NIC-LX2",
    "build.MODEL": "NIC-LX2",
    "build.MANUFACTURER": "HONOR",
    "build.VERSION.RELEASE": "9",
    "build.VERSION.SDK": "28"
  }
}
```

### 输出数据（魔云腾格式）

```json
{
  "env": [
    {
      "id": 0,
      "name": "DEVICE",
      "description": "ro.build.device",
      "value": "NIC-LX2"
    },
    {
      "id": 0,
      "name": "MODEL",
      "description": "ro.build.model",
      "value": "NIC-LX2"
    },
    ...
  ]
}
```

## 模糊匹配策略

工具采用多策略匹配算法，依次尝试以下方法：

1. **精确匹配**：将输入 key 标准化后与模板 description 精确匹配
2. **部分路径匹配**：匹配 description 的后缀部分
3. **包含关系匹配**：检查 description 是否包含在输入 key 中
4. **特殊字段映射**：处理 Android 系统特殊字段的映射关系

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 界面首页 |
| `/convert` | POST | 转换接口 |
| `/sample/<filename>` | GET | 下载示例文件 |
| `/health` | GET | 健康检查 |

## 开发相关

### 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
pytest -v

# 运行单个测试文件
pytest tests/test_match_template.py
```

### 代码检查

```bash
# 安装检查工具
pip install black flake8 pylint mypy

# 格式化代码
black .

# 代码检查
flake8 .
pylint match_template.py
```

## 常见问题

### Q: 转换后部分字段为空怎么办？

A: 检查输入数据中的 key 是否与模板的 description 字段匹配。工具支持多种匹配策略，如果仍无法匹配，可手动添加映射关系。

### Q: 如何添加新的字段映射？

A: 在 `match_template.py` 的 `special_mappings` 字典中添加新的映射关系。

### Q: Web 服务无法启动？

A: 确保 8080 端口未被占用，或修改 `web_app.py` 中的端口配置。

## 许可证

本项目仅供学习和内部使用，具体许可证请查看 LICENSE 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request。

---

如有问题，请联系维护者。
