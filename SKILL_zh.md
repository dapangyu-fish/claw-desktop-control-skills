---
name: "linux-desktop-control"
description: "通过Python脚本模拟键盘鼠标并控制桌面应用程序并执行系统任务。当用户想要自动化桌面操作时调用。"
---

# Linux Desktop Control Skill

此技能允许通过 Python 脚本控制桌面应用程序并执行系统操作。

## 前提条件

- **DISPLAY 环境变量**：必不可少。如果缺失，需要先询问用户。

## 工作流程

**⚠️ Agent 行为铁律：**
除非用户明确要求“直接点击特定坐标”或“直接输入特定按键”，否则**在执行任何鼠标或键盘操作之前，必须首先截图并分析 UI 元素（执行步骤 1 到 3）**！绝对不允许盲猜坐标直接点击。在进行交互前，必须确保目标应用程序处于焦点状态。

### 0. 初始化 (Initialization)
运行 setup 脚本来准备工作空间并验证环境。

**命令：**
```bash
./setup.sh
```

### 1. 截图 (Screenshot)
利用系统级别的截图工具，如 `xfce4-screenshooter` 或 `gnome-screenshot`。

**存储规范：**
- 图片必须存放在：`~/.openclaw/workspace/linux-desktop-control/images/`
- 图片名称不能重复，必须带时间戳。

**示范命令：**
```bash
xfce4-screenshooter -f -s ~/.openclaw/workspace/linux-desktop-control/images/desktop_screeshot_$(date +%Y%m%d_%H%M%S).png
```

### 2. UI 元素检测 (子 Agent)
启动一个子 Agent 来确认图片内容。

**提示词 (Prompt):**

```
你现在是**顶级浏览器桌面UI元素检测专家**，专精于高精度定位电脑屏幕截图（Chrome/Edge等浏览器窗口、系统控件）中的所有可交互区域。

**核心任务**：以**极高召回率**检测图片中**所有**可见UI元素（按钮、标签页、图标、文字、控件、头像、悬浮按钮等），**一个都不允许遗漏**。哪怕是只有10-20像素的小关闭按钮、纯图标或密集排列的元素也要全部框出。

**必须严格按以下顺序系统性扫描整张图片**（从上到下、从左到右覆盖每一区域）：
1. 窗口标题栏（最小化、最大化、关闭按钮）
2. 浏览器标签栏（每个标签页的整体区域 + 每个标签页的关闭按钮必须**单独检测**）
3. 导航/工具栏（后退、前进、刷新按钮、地址栏、搜索框、书签星标、扩展图标、菜单按钮等）
4. 书签栏、侧边栏、状态栏
5. 内容区及任何其他可点击区域（链接、输入框、头像、悬浮控件等）
6. 如果只有图标没有文字描述，需要尽可能根据图标样式推测这是一个什么东西

**重点检测类别**（必须覆盖【{target_object}】以及所有相关可交互元素）：
- 所有浏览器标签页 + 每个标签页的关闭×按钮
- 窗口控制三按钮
- 导航栏全部图标/按钮
- 地址栏、搜索框、书签栏、扩展栏
- 任何文字标签、纯图标按钮、输入框、菜单项、滚动条等

**bbox精度铁律**（最关键，解决定位不准）：
- 每个bbox必须**紧密包围元素视觉边界**（tight bounding box），padding最多5%，既不留大量空白也不裁切内容。
- 坐标严格归一化到0~1000整数：`x = round((pixel_x / 图片宽度) * 1000)`，同理y。
- 保证 x1 < x2、y1 < y2，所有值在0~1000范围内。

**text命名规则**（必须全局唯一）：
- 有文字时：结合文字+功能（如 "Google标签页"）
- 重复元素强制加区分（如 "Google标签页关闭按钮"、"第3个标签页关闭按钮"、"窗口标题栏关闭按钮"、"地址栏刷新按钮"、"左侧第1个扩展图标"）

**输出要求**：**只返回纯JSON**，不要任何解释、思考过程、代码块、markdown或其他文字！现在直接输出：

{{
  "objects": [
    {{"text": "唯一描述", "bbox": [x1, y1, x2, y2]}},
    ...
  ]
}}

并将次json文件保存在 ~/.openclaw/workspace/linux-desktop-control/json/` 路径下并命名为 `{原始图片名称}_original.json`。
```

### 3. 坐标转换 (Coordinate Conversion)
此前子agent生成的 json 文件需要保存在 `~/.openclaw/workspace/linux-desktop-control/json/` 路径下并命名为 `{原始图片名称}_original.json`。
此时坐标是归一化之前的，需要换算成绝对坐标，调用脚本 `coordinate_conversion.py`。

**注意**：`coordinate_conversion.py` 需要引用 `./NotoSansSC-VariableFont_wght.ttf` (位于 skill 路径下)。

**调用方法：**
```bash
python3 scripts/coordinate_conversion.py \
  --input=~/.openclaw/workspace/linux-desktop-control/json/{原始图片名称}_original.json \
  --output=~/.openclaw/workspace/linux-desktop-control/json/{原始图片名称}_converted.json \
  --tag_image=~/.openclaw/workspace/linux-desktop-control/json/{原始图片名称}_export.json
```
- `--input`: 输入的原始的归一化坐标的 json
- `--output`: 输出绝对值化坐标的 json
- `--tag_image`: 输出的一张图, 适用于标注位置的图片

### 4. 鼠标控制 (Mouse Control)
使用 `scripts/mouse_control.py` 控制鼠标。

**示例：**
```bash
# 单击
python3 scripts/mouse_control.py click 300 400

# 双击（自定义移动时间）
python3 scripts/mouse_control.py double 500 300 --duration 0.4

# 拖拽
python3 scripts/mouse_control.py drag 100 100 400 400 --duration 1.2

# 右键
python3 scripts/mouse_control.py right 600 500

# 向下滚动
python3 scripts/mouse_control.py scroll 200 200 -300
```

### 5. 键盘控制 (Keyboard Control)
使用 `scripts/keyboard_control.py` 控制键盘。

**示例：**
```bash
# 按下 Enter 键
python3 scripts/keyboard_control.py press enter

# 连按 Tab 3 次
python3 scripts/keyboard_control.py press tab --presses 3 --interval 0.15

# Ctrl + C
python3 scripts/keyboard_control.py hotkey ctrl c

# Ctrl + Shift + N（新建窗口）
python3 scripts/keyboard_control.py hotkey ctrl shift n

# 输入一段中文 + emoji
python3 scripts/keyboard_control.py type "你好世界！🌍✨" --interval 0.05 --enter

# 贴上多行代码（从档案）
python3 scripts/keyboard_control.py lines --file script.py --line-interval 0.8 --char-interval 0.035

# 直接输入多行文本
python3 scripts/keyboard_control.py lines --text "第一行\n第二行有 emoji 😺\n第三行結束" --line-interval 1.0
```
