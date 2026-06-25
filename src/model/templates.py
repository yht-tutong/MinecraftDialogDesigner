# templates.py
# Minecraft Dialog Designer 模板数据模块 - 预设对话框模板定义

from dataclasses import dataclass, field


@dataclass
class TemplateData:
    id: str
    name: str
    description: str
    category: str
    dialog_type: str
    preset_data: dict
    locked_fields: list = field(default_factory=list)


def get_builtin_templates() -> list:
    """返回内置的 6 个预设模板列表。"""
    return [
        # ── 欢迎通知 ──
        TemplateData(
            id="welcome_notice",
            name="欢迎通知",
            description="向玩家展示欢迎消息的 notice 通知对话框",
            category="welcome",
            dialog_type="minecraft:notice",
            locked_fields=["body", "actions"],
            preset_data={
                "type": "minecraft:notice",
                "title": {
                    "text": "欢迎来到服务器",
                    "color": "gold",
                    "bold": True
                },
                "body": [
                    {
                        "type": "plain_message",
                        "text": [
                            {"text": "欢迎来到我们的服务器！\n"},
                            {"text": "请遵守服务器规则，祝您游戏愉快！"}
                        ]
                    }
                ],
                "action": {
                    "type": "minecraft:run_command",
                    "command": "/say 我知道了"
                },
                "pause": True,
                "can_close_with_escape": True,
                "after_action": "close"
            },
        ),

        # ── 确认对话框 ──
        TemplateData(
            id="confirm_action",
            name="确认对话框",
            description="向玩家确认某项操作的 confirmation 对话框",
            category="quest",
            dialog_type="minecraft:confirmation",
            locked_fields=["actions"],
            preset_data={
                "type": "minecraft:confirmation",
                "title": {
                    "text": "确认操作",
                    "color": "red"
                },
                "body": [
                    {
                        "type": "plain_message",
                        "text": [
                            {"text": "你确定要执行此操作吗？"},
                        ]
                    }
                ],
                "yes": {
                    "type": "minecraft:run_command",
                    "command": "/say 已确认执行"
                },
                "no": {
                    "type": "minecraft:run_command",
                    "command": "/say 已取消操作"
                },
                "pause": True,
                "can_close_with_escape": True,
                "after_action": "close"
            },
        ),

        # ── 选项菜单 ──
        TemplateData(
            id="option_menu",
            name="选项菜单",
            description="提供多个操作选项的 multi_action 对话框",
            category="system",
            dialog_type="minecraft:multi_action",
            locked_fields=["actions"],
            preset_data={
                "type": "minecraft:multi_action",
                "title": {
                    "text": "请选择",
                    "color": "aqua"
                },
                "body": [
                    {
                        "type": "plain_message",
                        "text": [
                            {"text": "请选择一个操作："},
                        ]
                    }
                ],
                "actions": [
                    {
                        "type": "minecraft:run_command",
                        "command": "/say 选项一已触发"
                    },
                    {
                        "type": "minecraft:run_command",
                        "command": "/say 选项二已触发"
                    },
                    {
                        "type": "minecraft:run_command",
                        "command": "/say 选项三已触发"
                    },
                ],
                "columns": 2,
                "pause": True,
                "can_close_with_escape": True,
                "after_action": "close"
            },
        ),

        # ── 文本输入表单 ──
        TemplateData(
            id="text_input_form",
            name="文本输入表单",
            description="让玩家输入文本信息的 simple_input_form 对话框",
            category="input",
            dialog_type="minecraft:simple_input_form",
            locked_fields=["inputs"],
            preset_data={
                "type": "minecraft:simple_input_form",
                "title": {
                    "text": "输入信息",
                    "color": "green"
                },
                "body": [
                    {
                        "type": "plain_message",
                        "text": [
                            {"text": "请在下方输入您的信息："},
                        ]
                    }
                ],
                "inputs": [
                    {
                        "type": "minecraft:text",
                        "label": {
                            "text": "您的昵称"
                        },
                        "initial": "",
                        "placeholder": "请输入昵称",
                        "multiline": {
                            "enabled": False
                        }
                    }
                ],
                "action": {
                    "type": "minecraft:submit/command_template",
                    "command": "/say {input_0}"
                },
                "pause": True,
                "can_close_with_escape": True,
                "after_action": "close"
            },
        ),

        # ── 数值设置 ──
        TemplateData(
            id="number_setting",
            name="数值设置",
            description="让玩家调整数值参数的 multi_action_input_form 对话框",
            category="input",
            dialog_type="minecraft:multi_action_input_form",
            locked_fields=["inputs"],
            preset_data={
                "type": "minecraft:multi_action_input_form",
                "title": {
                    "text": "参数设置",
                    "color": "light_purple"
                },
                "body": [
                    {
                        "type": "plain_message",
                        "text": [
                            {"text": "请调整以下参数："},
                        ]
                    }
                ],
                "inputs": [
                    {
                        "type": "minecraft:number_range",
                        "label": {
                            "text": "音量大小"
                        },
                        "initial": 50.0,
                        "start": 0.0,
                        "end": 100.0,
                        "step": 1.0
                    }
                ],
                "actions": [
                    {
                        "type": "minecraft:run_command",
                        "command": "/say 参数已保存"
                    }
                ],
                "columns": 2,
                "pause": True,
                "can_close_with_escape": True,
                "after_action": "close"
            },
        ),

        # ── 任务选择 ──
        TemplateData(
            id="quest_select",
            name="任务选择",
            description="展示多个子对话框供玩家选择的 dialog_list 对话框",
            category="quest",
            dialog_type="minecraft:dialog_list",
            locked_fields=["dialogs"],
            preset_data={
                "type": "minecraft:dialog_list",
                "title": {
                    "text": "选择任务",
                    "color": "yellow"
                },
                "body": [
                    {
                        "type": "plain_message",
                        "text": [
                            {"text": "请选择一个任务："},
                        ]
                    }
                ],
                "dialogs": [
                    {
                        "type": "minecraft:notice",
                        "title": {
                            "text": "采集任务"
                        },
                        "body": [
                            {
                                "type": "plain_message",
                                "text": [
                                    {"text": "收集10个木材"},
                                ]
                            }
                        ],
                        "action": {
                            "type": "minecraft:run_command",
                            "command": "/say 接受采集任务"
                        }
                    },
                    {
                        "type": "minecraft:notice",
                        "title": {
                            "text": "战斗任务"
                        },
                        "body": [
                            {
                                "type": "plain_message",
                                "text": [
                                    {"text": "击败5只僵尸"},
                                ]
                            }
                        ],
                        "action": {
                            "type": "minecraft:run_command",
                            "command": "/say 接受战斗任务"
                        }
                    },
                    {
                        "type": "minecraft:notice",
                        "title": {
                            "text": "探索任务"
                        },
                        "body": [
                            {
                                "type": "plain_message",
                                "text": [
                                    {"text": "探索附近村庄"},
                                ]
                            }
                        ],
                        "action": {
                            "type": "minecraft:run_command",
                            "command": "/say 接受探索任务"
                        }
                    },
                ],
                "columns": 2,
                "button_width": 150,
                "pause": True,
                "can_close_with_escape": True,
                "after_action": "close"
            },
        ),
    ]