# MinecraftDialogDesigner

一个使用 Python + PyQt5 开发的 Minecraft 数据包 Dialog JSON 可视化编辑器，支持图形化编辑、实时预览、多标签页并行编辑、CLI 命令行和 Python API 调用。

[English](README.en.md)

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![UI](https://img.shields.io/badge/UI-PyQt5-brightgreen.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

---

## 👤 作者信息

| 平台 | 链接 |
|------|------|
| B站主页 | [https://space.bilibili.com/630095673](https://space.bilibili.com/630095673) |
| GitHub 项目主页 | [https://github.com/yht-tutong/MinecraftDialogDesigner](https://github.com/yht-tutong/MinecraftDialogDesigner) |
| QQ 交流群 | [https://qm.qq.com/q/ZyivYoMzmy](https://qm.qq.com/q/ZyivYoMzmy) |

---

## ✨ 功能特性

- 🎨 **可视化编辑器** — 图形化界面编辑 Minecraft 对话框 JSON
- 📑 **多标签页编辑** — 同时编辑多个对话框，支持拖拽排序、跨标签页复制粘贴
- 📋 **7 种对话框类型** — 支持 `confirmation` / `dialog_list` / `multi_action` / `notice` / `server_links` / `simple_input_form` / `multi_action_input_form`
- 🔧 **4 种输入控件** — 支持 `boolean` / `number_range` / `single_option` / `text` 四种输入类型
- 🖼️ **可视化预览** — 实时渲染对话框在游戏中的外观
- 📝 **JSON 实时预览** — 同步显示导出的 JSON 格式
- 📥 **多种导入方式** — 文件导入、剪贴板导入、拖拽导入
- 📋 **6 个预设模板** — 欢迎通知、确认对话框、选项菜单、文本输入表单、数值设置、任务选择
- 🔒 **模板锁定** — 模板可锁定指定字段，防止误修改
- ⌨️ **键盘快捷键** — 支持 `Ctrl+N` / `Ctrl+S` / `Ctrl+W` / `Ctrl+Tab` 等快捷键
- 🖥️ **CLI 命令行** — 独立命令行入口，支持批量生成、格式转换、验证
- 📦 **Python API** — 纯 Python API 模块，可被其他脚本导入调用
- ✨ **流畅动画** — 淡入淡出和高度变化动画效果
- 🌙 **深色主题** — 护眼的深色界面设计
- 💾 **项目文件** — 支持保存/加载 `.mcdialog` 项目文件
- 🌐 **中英双语** — 所有字段含中文悬停提示

---

## 🚀 安装说明

```bash
pip install -r requirements.txt
python main.py
```

### 环境要求

- Python 3.7 或更高版本
- PyQt5（GUI 模式需要）
- PyQt-Fluent-Widgets（Fluent Design 模式需要，默认模式）
- CLI 模式无需 PyQt5

### 启动模式

```bash
python main.py              # 默认 Fluent Design 模式
python main.py --classic    # 经典 PyQt5 原生深色主题
python main.py --help       # 查看所有参数
```

### 配置文件

首次运行程序时会自动在项目根目录创建 `config.json` 并填入默认配置。你也可以手动复制模板：

```bash
cp config.json.example config.json
```

然后编辑 `config.json` 自定义设置。主要配置项：

| 配置组 | 说明 |
|--------|------|
| `app` | 应用名称、版本、语言 |
| `editor` | 默认对话框类型、自动保存间隔、默认尺寸 |
| `export` | JSON 导出格式、输出目录、自动验证 |
| `ui` | 主题、字体大小、动画开关、提示开关 |
| `cli` | CLI 静默模式、彩色输出 |
| `paths` | 自定义模板/项目/导出目录路径 |

---

## 📖 使用指南

### GUI 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+N` | 新建标签页 |
| `Ctrl+S` | 保存当前标签页 |
| `Ctrl+Shift+L` | 全部保存 |
| `Ctrl+O` | 打开项目 |
| `Ctrl+E` | 导出 JSON |
| `Ctrl+W` | 关闭当前标签页 |
| `Ctrl+Tab` | 切换下一个标签页 |
| `Ctrl+Shift+Tab` | 切换上一个标签页 |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+I` | 导入 JSON 文件 |
| `Ctrl+Shift+V` | 从剪贴板导入 |
| `Ctrl+Q` | 退出程序 |
| `Delete` | 删除选中项 |

### CLI 命令行

```bash
# 列出所有模板
python cli.py generate --list-templates

# 从模板生成对话框
python cli.py generate --template welcome_notice --output dialog.json

# 项目文件 ↔ 纯 JSON 转换
python cli.py convert --from-dialog dialog.json --to-project project.mcdialog
python cli.py convert --from-project project.mcdialog --to-dialog dialog.json

# 批量处理
python cli.py batch generate --template confirm_action --count 5 --output-dir ./output/
python cli.py batch convert --input-dir ./projects/ --output-dir ./dialogs/

# 验证 JSON
python cli.py validate dialog.json
python cli.py validate --dir ./dialogs/

# 全局选项
python cli.py --quiet batch generate -t welcome_notice -n 10 -o ./out/
python cli.py --version
```

### Python API

```python
from src.api import list_templates, generate_from_template, validate_dialog

# 列出模板
for t in list_templates():
    print(f"{t['id']}: {t['name']}")

# 生成并验证
data = generate_from_template("welcome_notice")
ok, errors = validate_dialog(data)
```

### 对话框类型

| 类型 | 说明 | 典型用途 |
|------|------|----------|
| `confirmation` | 确认对话框 | 向玩家确认操作（是/否） |
| `dialog_list` | 对话框列表 | 展示多个选项供玩家选择 |
| `multi_action` | 多操作对话框 | 提供多个操作按钮 |
| `notice` | 公告对话框 | 向玩家显示公告或提示信息 |
| `server_links` | 服务器链接 | 展示服务器相关链接 |
| `simple_input_form` | 简单输入表单 | 收集玩家输入数据 |
| `multi_action_input_form` | 多操作输入表单 | 结合操作按钮与输入表单 |

---

## 📁 项目结构

```
MinecraftDialogDesigner/
├── main.py                     # GUI 程序入口
├── cli.py                      # CLI 命令行入口（无 PyQt5 依赖）
├── requirements.txt            # Python 依赖
├── config.json.example         # 配置文件模板
├── README.md                   # 中文文档
├── README.en.md                # 英文文档
├── LICENSE                     # MIT 许可证
├── src/
│   ├── model/                  # 数据模型层
│   │   ├── dialog_base.py      # 对话框基类
│   │   ├── dialog_types.py     # 7种对话框类型
│   │   ├── body_elements.py    # 主体元素模型
│   │   ├── input_controls.py   # 输入控件模型
│   │   ├── action_models.py    # 操作按钮模型
│   │   ├── submit_methods.py   # 提交方法模型
│   │   └── templates.py        # 6个预设模板
│   ├── view/                   # 视图层 (UI)
│   │   ├── main_window.py      # 主窗口
│   │   ├── tab_widget.py       # 多标签页组件
│   │   ├── editor_panel.py     # 编辑器面板（封装）
│   │   ├── dialog_editor.py    # 对话框编辑面板
│   │   ├── body_editor.py      # 主体元素编辑器
│   │   ├── input_editor.py     # 输入控件编辑器
│   │   ├── action_editor.py    # 操作按钮编辑器
│   │   ├── template_dialog.py  # 模板选择对话框
│   │   ├── import_dialog.py    # 导入预览对话框
│   │   ├── visual_preview.py   # 可视化预览面板
│   │   ├── preview_panel.py    # JSON 预览面板
│   │   ├── animation_utils.py  # 动画工具
│   │   └── tooltips.py         # 中文提示翻译
│   ├── api/                    # 纯 Python API 模块（无 PyQt5）
│   │   ├── template_api.py     # 模板管理 API
│   │   ├── dialog_api.py       # 对话框 CRUD API
│   │   └── batch_api.py        # 批量处理 API
│   └── controller/             # 控制层 (逻辑)
│       ├── dialog_controller.py # 对话框管理逻辑
│       ├── dialog_session.py    # 会话管理
│       └── json_export.py       # JSON 导出与导入
└── _reference/                 # 参考项目 (Kotlin)
```

---

## 📚 参考项目

- [YQ-Ksim/DialogGenerator](https://github.com/YQ-Ksim/DialogGenerator)
- [DeeChael/MinecraftDialogGenerator](https://github.com/DeeChael/MinecraftDialogGenerator)
- [minecraftmaps.com/dialog-builder](https://www.minecraftmaps.com/tools/dialog-builder)

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源，详情请查看 [LICENSE](LICENSE) 文件。