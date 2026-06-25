# tooltips.py
# Minecraft Dialog Designer 字段悬停提示翻译 - 所有字段的中文说明

# 通用设置
TOOLTIP_TITLE = "对话框标题，显示在对话框顶部"
TOOLTIP_TITLE_COLOR = "标题文字颜色，支持 Minecraft 16色"
TOOLTIP_TITLE_BOLD = "标题是否加粗"
TOOLTIP_TITLE_ITALIC = "标题是否斜体"
TOOLTIP_TITLE_UNDERLINED = "标题是否带下划线"
TOOLTIP_DIALOG_TYPE = "对话框类型：multi_action(多操作)、confirmation(确认)、dialog_list(列表)、notice(公告)、server_links(链接)、simple_input_form(简单输入表单)、multi_action_input_form(多操作输入表单)"
TOOLTIP_PAUSE = "单人模式下是否暂停游戏（默认开启）"
TOOLTIP_CAN_CLOSE_WITH_ESCAPE = "是否允许按 Esc 关闭对话框（默认开启）"
TOOLTIP_AFTER_ACTION = "操作后的行为：close(关闭)、none(无操作)、wait_for_response(等待服务器响应)"
TOOLTIP_EXTERNAL_TITLE = "在其他对话框或暂停屏幕中显示的按钮文本"

# Body 元素
TOOLTIP_BODY_WIDTH = "文本区域宽度（像素），超出自动换行"
TOOLTIP_ITEM_ID = "物品 ID，如 minecraft:diamond"
TOOLTIP_ITEM_COUNT = "物品数量"
TOOLTIP_ITEM_SHOW_DECORATIONS = "是否显示物品的耐久条、冷却、数量等装饰"
TOOLTIP_ITEM_SHOW_TOOLTIP = "鼠标悬停时是否显示物品提示框"
TOOLTIP_ITEM_WIDTH = "布局宽度（像素）"
TOOLTIP_ITEM_HEIGHT = "布局高度（像素）"

# 输入控件
TOOLTIP_INPUT_KEY = "输入控件的键名，用于提交时标识数据（仅限字母、数字、下划线）"
TOOLTIP_INPUT_LABEL = "输入控件的标签文本"
TOOLTIP_BOOLEAN_INITIAL = "是否默认选中"
TOOLTIP_BOOLEAN_ON_TRUE = "选中时提交的值"
TOOLTIP_BOOLEAN_ON_FALSE = "未选中时提交的值"
TOOLTIP_NUMBER_START = "滑条最左侧值"
TOOLTIP_NUMBER_END = "滑条最右侧值"
TOOLTIP_NUMBER_STEP = "步进值，提供后滑条只能取离散值"
TOOLTIP_NUMBER_INITIAL = "初始值"
TOOLTIP_SINGLE_OPTION_WIDTH = "按钮宽度（像素）"
TOOLTIP_SINGLE_OPTION_LABEL_VISIBLE = "是否显示标签"
TOOLTIP_TEXT_MAX_LENGTH = "输入最大长度（默认 32）"
TOOLTIP_TEXT_WIDTH = "文本框宽度（像素）"
TOOLTIP_TEXT_MULTILINE = "是否启用多行文本"
TOOLTIP_TEXT_MULTILINE_MAX_LINES = "最大行数"
TOOLTIP_TEXT_MULTILINE_HEIGHT = "文本框高度（像素）"

# 操作按钮
TOOLTIP_ACTION_LABEL = "按钮显示文本"
TOOLTIP_ACTION_COLOR = "按钮文字颜色"
TOOLTIP_ACTION_BOLD = "按钮文字是否加粗"
TOOLTIP_ACTION_TOOLTIP = "按钮悬浮提示"
TOOLTIP_ACTION_WIDTH = "按钮宽度（像素）"
TOOLTIP_ACTION_TYPE = "操作类型：open_url(打开链接)、run_command(执行命令)、suggest_command(建议命令)、change_page(翻页)、copy_to_clipboard(复制)、show_dialog(打开对话框)、custom(自定义事件)、dynamic/run_command(动态命令)、dynamic/custom(动态自定义)"
TOOLTIP_ACTION_URL = "要打开的 URL（仅支持 http/https）"
TOOLTIP_ACTION_COMMAND = "要执行的命令（无需 / 前缀）"
TOOLTIP_ACTION_DIALOG = "要打开的对话框 ID（如 minecraft:my_dialog）"
TOOLTIP_ACTION_VALUE = "要复制的文本"
TOOLTIP_ACTION_PAGE = "页码"
TOOLTIP_ACTION_CUSTOM_ID = "自定义事件 ID"
TOOLTIP_ACTION_PAYLOAD = "自定义事件载荷（JSON 对象）"
TOOLTIP_ACTION_TEMPLATE = "命令模板，使用 $(key) 引用输入控件的值"
TOOLTIP_ACTION_ADDITIONS = "附加静态数据（JSON 对象）"
TOOLTIP_ACTION_INLINE_DIALOG = "是否使用内联对话框对象（而非 ID 引用）"

# 退出动作
TOOLTIP_EXIT_ACTION_ENABLE = "是否启用退出/取消按钮"
TOOLTIP_ON_CANCEL = "用户取消/关闭对话框时的回调事件（ClickEvent 格式）"

# 对话框特有
TOOLTIP_CONFIRMATION_YES = "确认对话框的「确定」按钮"
TOOLTIP_CONFIRMATION_NO = "确认对话框的「取消」按钮"
TOOLTIP_DIALOG_LIST = "跳转目标对话框列表，支持 ID 字符串或内联对话框对象"
TOOLTIP_COLUMNS = "按钮列数"
TOOLTIP_BUTTON_WIDTH = "按钮宽度（像素）"
TOOLTIP_SUBMIT_TEMPLATE = "提交模板，使用 $(key) 引用输入控件的值"
TOOLTIP_SUBMIT_ID = "提交事件 ID（如 minecraft:form_submit）"