---
name: "linux-desktop-control"
description: "通过Python脚本模拟键盘鼠标并控制桌面应用程序并执行系统任务。当用户想要自动化桌面操作时调用。"
---

# Linux Desktop Control Skill

此技能允许通过 Python 脚本控制桌面应用程序并执行系统操作。

## 前提条件

- **DISPLAY 环境变量**：必不可少。如果缺失，需要先询问用户。

## 核心工作流：OODA 循环 (Observe-Orient-Decide-Act)

**⚠️ Agent 行为铁律：**
1. **闭环控制 (Closed-Loop Control)**：本 Skill 必须像人类操作电脑一样，**严格遵循“观察 -> 分析 -> 决策 -> 行动 -> 验证”的单步循环**。(linux-desktop-control子任务除外，没有特指说明就是子任务)
2. **状态驱动 (State-Driven)**：**每一次行动的决策必须基于当前屏幕的真实状态**，而非预设的脚本或臆想。
3. **原子操作 (Atomic Action)**：**每次只执行一个原子动作**（如“点击搜索栏”），然后必须立即重新观察行验证的步骤。**严禁一次性生成多步操作代码！**
4. **验证即通过 (Verify or Die)**：如果上一步操作未能产生预期的屏幕变化（如窗口未打开、输入框未聚焦），**必须立即停止当前路径，进行重试或更换策略**，绝不允许假装成功继续执行。

### 阶段 0：初始化 (Initialization)
运行 setup 脚本来准备工作空间并验证环境。

**命令：**
```bash
./setup.sh
```


### 原子能力介绍 (Atomic Actions) 

## ****观察当前屏幕状态****
    ```bash
    ./scripts/ui_detect_prompt.sh ${DISPLAY}
    ```
    *(脚本会自动生成 绝对值坐标化的 以及图片描述信息的`{原始图片名称}_converted.json`)* 并在返回信息中体现
    例如运行此脚本后：
    ```bash
    🚀 正在调用 openclaw agent 进行 UI 检测...
    ✅ 执行完成！
    处理过程中的临时文件已自动保存为：/home/fish/.openclaw/workspace/linux-desktop-control/temp/desktop_screeshot_20260318_132240_temp.txt
    原始图片 文件已自动保存为：/home/fish/.openclaw/workspace/linux-desktop-control/images/desktop_screeshot_20260318_132240_annotated.png
    坐标化 JSON 文件已自动保存为：/home/fish/.openclaw/workspace/linux-desktop-control/json/desktop_screeshot_20260318_132240_converted.json
    ```

## ****规划下一步行动****
    此时需要通过“观察当前屏幕状态”生成的converted.json分析屏幕状态,结合需求,规划出下一步行动
    以下示范每一行规划均为一步的规划行动内容，需要尽可能的具体和原子：
    - 鼠标点击搜索栏
    - 键盘输入“测试搜索内容” 并按回车
    - 键盘仅输入“测试搜索内容” 不按回车
    - 将某区域拖拽至另一个区域 （最好直接给出起点终点xy坐标）
    - 按page down按键
    - 按page up按键
    - 按esc按键
    - 按ctrl + c 按键
    - 任务已经完全完成，不需要继续行动

## ****根据规划执行下一步行动****
    ```bash
    ./scripts/next_plan_prompt.sh  ~/.openclaw/workspace/linux-desktop-control/images/{图片名称}.png "规划的下一步具体行动" ${DISPLAY}
    ```

## ****验证行动是否成功执行****
    这一步仍然是回到****观察当前屏幕状态**** 进行下一轮观察-验证-规划-执行的循环

**工具参考：**

#### 鼠标控制 (Mouse Control)
```bash
# 单击
python3 scripts/mouse_control.py click 300 400
# 双击
python3 scripts/mouse_control.py double 500 300 --duration 0.4
# 拖拽
python3 scripts/mouse_control.py drag 100 100 400 400 --duration 1.2
# 右键
python3 scripts/mouse_control.py right 600 500
# 滚动
python3 scripts/mouse_control.py scroll 200 200 -300
```

#### 键盘控制 (Keyboard Control)
```bash
# ==================== 2. 查看帮助 ====================
python3 scripts/keyboard_control.py --help
python3 scripts/keyboard_control.py press --help
python3 scripts/keyboard_control.py type --help
python3 scripts/keyboard_control.py lines --help

# ==================== 3. 完整命令示例 ====================

# 1 单键按下（press）
python3 scripts/keyboard_control.py press enter
python3 scripts/keyboard_control.py press space --presses 5
python3 scripts/keyboard_control.py press f5
python3 scripts/keyboard_control.py press esc

# 2 组合快捷键（hotkey）
python3 scripts/keyboard_control.py hotkey ctrl c
python3 scripts/keyboard_control.py hotkey ctrl v
python3 scripts/keyboard_control.py hotkey ctrl alt delete
python3 scripts/keyboard_control.py hotkey ctrl shift esc
python3 scripts/keyboard_control.py hotkey win r

# 3 输入单行文字（type）—— 最常用
python3 scripts/keyboard_control.py type "你好世界！👋 Hello 123"
python3 scripts/keyboard_control.py type "登录成功" --enter
python3 scripts/keyboard_control.py type 'https://www.google.com' --enter
python3 scripts/keyboard_control.py type "超长文本测试：ABC123 + emoji 👋 + 特殊符号 @#$%" --enter

# 4 多行文字输入（lines）—— 推荐贴代码
# 从文件贴上（最稳）
python3 scripts/keyboard_control.py lines --file code.py
python3 scripts/keyboard_control.py lines --file script.sh
python3 scripts/keyboard_control.py lines --file commands.txt

# 直接传入多行（用 \n 分隔）
python3 scripts/keyboard_control.py lines --text "第一行内容\n第二行内容\n第三行代码"
python3 scripts/keyboard_control.py lines --text "import os\nprint('hello world')\nprint('输入法已解耦！')\nexit()"

```