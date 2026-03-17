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
1. **闭环控制 (Closed-Loop Control)**：本 Skill 必须像人类操作电脑一样，**严格遵循“截图 -> 分析 -> 决策 -> 行动 -> 验证”的单步循环**。
2. **状态驱动 (State-Driven)**：**每一次行动的决策必须基于当前屏幕的真实状态**，而非预设的脚本或臆想。
3. **原子操作 (Atomic Action)**：**每次只执行一个原子动作**（如“点击搜索栏”），然后必须立即重新截图验证。**严禁一次性生成多步操作代码！**
4. **验证即通过 (Verify or Die)**：如果上一步操作未能产生预期的屏幕变化（如窗口未打开、输入框未聚焦），**必须立即停止当前路径，进行重试或更换策略**，绝不允许假装成功继续执行。

### 阶段 0：初始化 (Initialization)
运行 setup 脚本来准备工作空间并验证环境。

**命令：**
```bash
./setup.sh
```

### 阶段 1：观察 (Observe) & 验证 (Verify)
**每一次行动前必须执行此步骤！这是整个循环的起点。**

1. **截图**：获取当前屏幕状态。
   ```bash
   xfce4-screenshooter -f -s ~/.openclaw/workspace/linux-desktop-control/images/desktop_screeshot_$(date +%Y%m%d_%H%M%S).png
   ```

2. **分析**：利用 `ui_detect_prompt.sh` 分析 UI 元素。
   ```bash
   ./scripts/ui_detect_prompt.sh ~/.openclaw/workspace/linux-desktop-control/images/{图片名称}.png
   ```
   *(脚本会自动生成 绝对值坐标化的 `{原始图片名称（不带后缀）}_converted.json`)*

3. **根据截图状态转换的converted.json 断言 (State Assertion) & 自我修正**：
   - **如果是任务开始**：确认起始状态（如桌面是否显示）。
   - **如果刚执行了操作**：**必须对比操作前后的截图/UI数据**。
     - *示例：上一步是“打开浏览器”。现在屏幕上有浏览器窗口吗？如果没有，操作失败。*
     - *示例：上一步是“点击搜索框”。现在输入法激活了吗？有光标吗？如果没有，操作失败。*
     - **失败处理**：如果断言失败，**不要继续下一步**！必须分析原因（如点击没反应、加载慢），尝试重试、增加等待时间或改用快捷键。

### 阶段 2：规划 (Plan) & 决策 (Decide)
**⚠️ 必须使用 `TodoWrite` 工具来显式输出你的思考过程和下一步计划！**

1. **当前状态评估**：根据阶段 1 的真实状态，判断距离最终目标还有多远。
2. **更新 Todo 列表**：
   - 将已完成的步骤标记为 `completed`。
   - **新增**接下来的 1 个原子动作作为 `in_progress` 的任务。
   - 保持 Todo 列表清晰，让用户能看到你正在做什么。
3. **制定下一步**：**只规划接下来的 1 个原子动作**。
   - *错误示范*：“点击搜索栏 -> 等待 -> 输入‘飞书’ -> 回车”。（这是脚本思维，禁止！）
   - *正确示范*：“当前未聚焦搜索栏 -> 计划点击搜索栏坐标 (x,y)”。（执行后回到阶段 1 验证是否聚焦成功，然后再规划输入）
4. **获取目标坐标**：从 `_converted.json` 中找到目标元素的 `bbox` 中心点 `(x, y)`。

### 阶段 3：行动 (Act)
1. **执行操作**：使用 `mouse_control.py` 或 `keyboard_control.py` 执行**单个**动作。
2. **等待响应**：操作后必须给予系统反应时间（例如等待 2-5 秒，取决于应用响应速度），这通常隐含在脚本中或需要显式 `sleep`。

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

# ==================== 4. 进阶小技巧 ====================
# 想更快：修改脚本里的 pyautogui.PAUSE = 0.05
# 想更稳：改成 0.15
# 紧急停止：把鼠标快速移到屏幕左上角（pyautogui FAILSAFE）
# macOS 自动用 command+v，Windows/Linux 自动用 ctrl+v

# ==================== 5. 一键测试所有功能（复制粘贴运行） ====================
echo "=== 测试开始 ==="
python3 scripts/keyboard_control.py press enter
python3 scripts/keyboard_control.py hotkey ctrl v
python3 scripts/keyboard_control.py type "测试成功！👋" --enter
python3 scripts/keyboard_control.py lines --text "多行测试\n第2行\n第3行"
echo "=== 测试结束 ==="

# ================================================
# 使用完后直接把这个文件保存为 README.md 或 help.md 即可
# 以后每次用终端复制上面的命令就行！
# 有问题直接改脚本里的 pyautogui.PAUSE 数值调节速度
# ================================================
```

### 阶段 4：循环 (Loop)
- **回到 阶段 1**，直到满足“完成定义 (Definition of Done)”。

## 完成定义 (Definition of Done)
Agent 只有在满足以下条件时才能宣布任务完成：
1. **最终目标达成**：屏幕上出现了明确的成功标志（如“安装完成”提示、目标应用已打开并显示主页）。
2. **验证通过**：最后一次截图必须包含证明任务成功的视觉证据。
3. **无遗留问题**：所有中间产生的临时窗口（如安装包管理器）已正确关闭（如果需要）。

## 错误处理与重试策略
1. **元素未找到**：如果 JSON 中没有目标元素，尝试滚动屏幕或检查是否在其他标签页/窗口。
2. **操作无响应**：如果点击后屏幕无变化，尝试：
   - 检查是否需要双击。
   - 检查是否需要右键菜单。
   - 尝试使用键盘快捷键（如 `Ctrl+L` 定位地址栏，`Super` 键打开菜单）。
3. **应用未启动**：如果点击图标后应用未出现，尝试通过命令行启动（`RunCommand`）作为备选方案。
```

### 6. 验证 (Verification)
执行完操作（鼠标点击或键盘输入）后，**必须验证结果**。

**步骤：**
1. 再次截图（参考步骤 1）。
2. 分析新截图以确认预期变化是否发生（例如：窗口是否打开、文字是否输入、按钮是否点击）。
3. 如果操作失败或结果不符合预期，请重试或调整策略。
