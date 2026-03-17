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
本 Skill 是一个**闭环控制系统**，而非单次执行脚本。
**必须严格遵循“截图 -> 分析 -> 决策 -> 行动 -> 验证”的循环**，直到最终目标完成。
**严禁一次性生成所有步骤的代码！必须“走一步，看一步”。**

### 阶段 0：初始化 (Initialization)
运行 setup 脚本来准备工作空间并验证环境。

**命令：**
```bash
./setup.sh
```

### 阶段 1：观察 (Observe) & 验证 (Verify)
**每一次行动前必须执行此步骤！**
1. **截图**：获取当前屏幕状态。
   ```bash
   xfce4-screenshooter -f -s ~/.openclaw/workspace/linux-desktop-control/images/desktop_screeshot_$(date +%Y%m%d_%H%M%S).png
   ```
2. **分析**：利用 `ui_detect_prompt.sh` 分析 UI 元素。
   ```bash
   ./scripts/ui_detect_prompt.sh ~/.openclaw/workspace/linux-desktop-control/images/{图片名称}.png
   ```
   *(脚本会自动生成 `{原始图片名称（不带后缀）}_original.json`)*

3. **坐标转换**：将归一化坐标转换为绝对坐标。
   ```bash
   python3 scripts/coordinate_conversion.py \
     --input=~/.openclaw/workspace/linux-desktop-control/json/{原始图片名称（不带后缀）}_original.json \
     --output=~/.openclaw/workspace/linux-desktop-control/json/{原始图片名称（不带后缀）}_converted.json \
     --tag_image=~/.openclaw/workspace/linux-desktop-control/json/{原始图片名称（不带后缀）}_export.json
   ```

4. **自我修正与验证**：
   - **如果是第一步**：跳过验证，直接进入阶段 2。
   - **如果刚执行了操作**：对比**操作前**和**操作后**的截图/UI数据。
     - *问自己：“上一步操作生效了吗？窗口打开了吗？输入框有字了吗？”*
     - **如果失败**：停止当前计划，分析原因，尝试替代方案（如快捷键代替点击，或重新定位坐标）。
     - **如果成功**：继续下一步。

### 阶段 2：规划 (Plan) & 决策 (Decide)
1. **当前状态评估**：根据阶段 1 的结果，判断距离最终目标还有多远。
2. **制定下一步**：**只规划接下来的 1 个原子动作**（例如：“点击搜索栏”）。
   - **不要**规划后续的“输入内容”或“按回车”，因为你还不知道“点击搜索栏”是否成功。
3. **获取目标坐标**：从 `_converted.json` 中找到目标元素的 `bbox` 中心点 `(x, y)`。

### 阶段 3：行动 (Act)
1. **执行操作**：使用 `mouse_control.py` 或 `keyboard_control.py` 执行**单个**动作。
2. **等待响应**：操作后必须给予系统反应时间（例如等待 1-2 秒），这通常隐含在脚本中或需要显式 `sleep`。

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
# 按键
python3 scripts/keyboard_control.py press enter
# 组合键
python3 scripts/keyboard_control.py hotkey ctrl c
# 输入文本
python3 scripts/keyboard_control.py type "你好世界！" --interval 0.05
```

### 阶段 4：循环 (Loop)
- **回到 阶段 1**，直到任务完成。
python3 scripts/keyboard_control.py hotkey ctrl shift n

# 输入一段中文 + emoji
python3 scripts/keyboard_control.py type "你好世界！🌍✨" --interval 0.05 --enter

# 贴上多行代码（从档案）
python3 scripts/keyboard_control.py lines --file script.py --line-interval 0.8 --char-interval 0.035

# 直接输入多行文本
python3 scripts/keyboard_control.py lines --text "第一行\n第二行有 emoji 😺\n第三行結束" --line-interval 1.0
```

### 6. 验证 (Verification)
执行完操作（鼠标点击或键盘输入）后，**必须验证结果**。

**步骤：**
1. 再次截图（参考步骤 1）。
2. 分析新截图以确认预期变化是否发生（例如：窗口是否打开、文字是否输入、按钮是否点击）。
3. 如果操作失败或结果不符合预期，请重试或调整策略。
