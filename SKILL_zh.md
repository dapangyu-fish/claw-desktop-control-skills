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
利用 `scripts/ui_detect_prompt.sh` 脚本来启动子 Agent 自动分析图片并生成 JSON。

**调用方法：**
```bash
./scripts/ui_detect_prompt.sh ~/.openclaw/workspace/linux-desktop-control/images/{图片名称}.png
```
脚本会自动在 `~/.openclaw/workspace/linux-desktop-control/json/` 路径下生成命名为 `{原始图片名称}_original.json` 的文件。

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
