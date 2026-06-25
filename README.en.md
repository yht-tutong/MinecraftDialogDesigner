[中文](README.md)

# MinecraftDialogDesigner

A GUI-based Minecraft Datapack Dialog JSON editor built with Python and PyQt5. Features multi-tab editing, CLI command-line interface, and Python API for batch processing.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-brightgreen.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

---

## Author

- **Bilibili**: [https://space.bilibili.com/630095673](https://space.bilibili.com/630095673)
- **GitHub**: [https://github.com/yht-tutong/MinecraftDialogDesigner](https://github.com/yht-tutong/MinecraftDialogDesigner)
- **QQ Group**: [https://qm.qq.com/q/ZyivYoMzmy](https://qm.qq.com/q/ZyivYoMzmy)

---

## Features

- 🎨 **Visual Editor** — GUI-based Minecraft dialog JSON editor, no hand-writing JSON required
- 📑 **Multi-Tab Editing** — Edit multiple dialogs simultaneously with drag-and-drop reordering and cross-tab copy/paste
- 📋 **7 Dialog Types** — Supports `confirmation`, `dialog_list`, `multi_action`, `notice`, `server_links`, `simple_input_form`, and `multi_action_input_form`
- 🔧 **4 Input Controls** — `boolean`, `number_range`, `single_option`, and `text` input types
- 🖼️ **Visual Preview** — Real-time rendering of how your dialog will appear in-game
- 📝 **Live JSON Preview** — Synchronized JSON output display as you edit
- 📥 **Multiple Import Methods** — File import, clipboard import, and drag-and-drop import
- 📋 **6 Built-in Templates** — Welcome notice, confirmation, option menu, text input form, number setting, quest selection
- 🔒 **Template Locking** — Lock specific fields in templates to prevent accidental modification
- ⌨️ **Keyboard Shortcuts** — `Ctrl+N` / `Ctrl+S` / `Ctrl+W` / `Ctrl+Tab` and more
- 🖥️ **CLI Interface** — Standalone command-line tool for batch generation, format conversion, and validation
- 📦 **Python API** — Pure Python API module for programmatic dialog generation (no PyQt5 required)
- ✨ **Smooth Animations** — Fade in/out and height transition animations for a polished UI experience
- 🌙 **Dark Theme** — Eye-friendly dark interface designed for long editing sessions
- 💾 **Project Files** — Save and load `.mcdialog` project files to continue your work anytime
- 🌐 **Bilingual** — Chinese tooltips on all fields for Chinese-speaking developers

---

## Installation

```bash
pip install -r requirements.txt
python main.py
```

### Requirements

- Python 3.7+
- PyQt5 (GUI mode only)
- PyQt-Fluent-Widgets (Fluent Design mode, default)
- CLI mode does not require PyQt5

### Launch Modes

```bash
python main.py              # Default Fluent Design mode
python main.py --classic    # Classic PyQt5 native dark theme
python main.py --help       # Show all options
```

### Configuration

On first run, the program automatically creates `config.json` with default settings in the project root. You can also manually copy the template:

```bash
cp config.json.example config.json
```

Then edit `config.json` to customize. Key sections:

| Section | Description |
|---------|-------------|
| `app` | App name, version, language |
| `editor` | Default dialog type, auto-save interval, default sizes |
| `export` | JSON export format, output directory, auto-validate |
| `ui` | Theme, font size, animation toggle, tooltip toggle |
| `cli` | CLI quiet mode, color output |
| `paths` | Custom template/project/export directory paths |

---

## Usage Guide

### GUI Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New tab |
| `Ctrl+S` | Save current tab |
| `Ctrl+Shift+L` | Save all tabs |
| `Ctrl+O` | Open project |
| `Ctrl+E` | Export JSON |
| `Ctrl+W` | Close current tab |
| `Ctrl+Tab` | Switch to next tab |
| `Ctrl+Shift+Tab` | Switch to previous tab |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+I` | Import JSON file |
| `Ctrl+Shift+V` | Import from clipboard |
| `Ctrl+Q` | Quit |
| `Delete` | Remove selected item |

### CLI Commands

```bash
# List all templates
python cli.py generate --list-templates

# Generate dialog from template
python cli.py generate --template welcome_notice --output dialog.json

# Convert project ↔ plain JSON
python cli.py convert --from-dialog dialog.json --to-project project.mcdialog
python cli.py convert --from-project project.mcdialog --to-dialog dialog.json

# Batch processing
python cli.py batch generate --template confirm_action --count 5 --output-dir ./output/
python cli.py batch convert --input-dir ./projects/ --output-dir ./dialogs/

# Validate JSON
python cli.py validate dialog.json
python cli.py validate --dir ./dialogs/

# Global options
python cli.py --quiet batch generate -t welcome_notice -n 10 -o ./out/
python cli.py --version
```

### Python API

```python
from src.api import list_templates, generate_from_template, validate_dialog

# List templates
for t in list_templates():
    print(f"{t['id']}: {t['name']}")

# Generate and validate
data = generate_from_template("welcome_notice")
ok, errors = validate_dialog(data)
```

### Dialog Types

| Type | Description | Use Case |
|------|-------------|----------|
| `confirmation` | Confirmation Dialog | Yes/No prompts, confirmations before actions |
| `dialog_list` | Dialog List | Multiple options presented as a list |
| `multi_action` | Multi-Action Dialog | Complex dialogs with multiple action buttons |
| `notice` | Notice Dialog | Simple informational messages |
| `server_links` | Server Links | Display server-related links |
| `simple_input_form` | Simple Input Form | Single input field dialog |
| `multi_action_input_form` | Multi-Action Input Form | Input form with multiple action buttons |

---

## Project Structure

```
MinecraftDialogDesigner/
├── main.py                     # GUI entry point
├── cli.py                      # CLI entry point (no PyQt5 dependency)
├── requirements.txt            # Python dependencies
├── config.json.example         # Configuration template
├── README.md                   # Chinese documentation
├── README.en.md                # English documentation
├── LICENSE                     # MIT License
├── src/
│   ├── model/                  # Data model layer
│   │   ├── dialog_base.py      # Dialog base class
│   │   ├── dialog_types.py     # 7 dialog types
│   │   ├── body_elements.py    # Body element models
│   │   ├── input_controls.py   # Input control models
│   │   ├── action_models.py    # Action button models
│   │   ├── submit_methods.py   # Submit method models
│   │   └── templates.py        # 6 preset templates
│   ├── view/                   # View layer (UI)
│   │   ├── main_window.py      # Main window
│   │   ├── tab_widget.py       # Multi-tab widget
│   │   ├── editor_panel.py     # Editor panel (encapsulated)
│   │   ├── dialog_editor.py    # Dialog editor panel
│   │   ├── body_editor.py      # Body element editor
│   │   ├── input_editor.py     # Input control editor
│   │   ├── action_editor.py    # Action button editor
│   │   ├── template_dialog.py  # Template selection dialog
│   │   ├── import_dialog.py    # Import preview dialog
│   │   ├── visual_preview.py   # Visual preview panel
│   │   ├── preview_panel.py    # JSON preview panel
│   │   ├── animation_utils.py  # Animation utilities
│   │   └── tooltips.py         # Chinese tooltip translations
│   ├── api/                    # Pure Python API (no PyQt5)
│   │   ├── template_api.py     # Template management API
│   │   ├── dialog_api.py       # Dialog CRUD API
│   │   └── batch_api.py        # Batch processing API
│   └── controller/             # Controller layer (logic)
│       ├── dialog_controller.py # Dialog management logic
│       ├── dialog_session.py    # Session management
│       └── json_export.py       # JSON export/import
└── _reference/                 # Reference project (Kotlin)
```

---

## Reference Projects

- [YQ-Ksim/DialogGenerator](https://github.com/YQ-Ksim/DialogGenerator)
- [DeeChael/MinecraftDialogGenerator](https://github.com/DeeChael/MinecraftDialogGenerator)
- [minecraftmaps.com/dialog-builder](https://www.minecraftmaps.com/tools/dialog-builder)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.