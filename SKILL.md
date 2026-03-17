---
name: "linux-desktop-control"
description: "Control desktop applications and perform system tasks via Python scripts. Invoke when user wants to automate desktop actions."
---

# Linux Desktop Control Skill

This skill allows controlling desktop applications and performing system operations using Python scripts.

## Prerequisites

- **DISPLAY Environment Variable**: This variable is essential. If missing, ask the user to provide it.

## Core Workflow: OODA Loop (Observe-Orient-Decide-Act)

**⚠️ CRITICAL RULES for Agent:**
1. **Closed-Loop Control**: This Skill MUST function like a human using a computer, **strictly following the "Screenshot -> Analyze -> Decide -> Act -> Verify" single-step loop**.
2. **State-Driven**: **Every decision MUST be based on the current REAL screen state**, not on pre-conceived scripts or assumptions.
3. **Atomic Action**: **Execute ONLY ONE atomic action at a time** (e.g., "Click Search Bar"), then IMMEDIATELY re-verify. **Generating multi-step code at once is STRICTLY FORBIDDEN!**
4. **Verify or Die**: If the previous action failed to produce the expected screen change (e.g., window didn't open, input box didn't focus), **STOP the current path IMMEDIATELY, retry, or change strategy**. Do not pretend to succeed and continue.

### Phase 0: Initialization
Run the setup script to prepare the workspace and verify the environment.

**Command:**
```bash
./setup.sh
```

### Phase 1: Observe & Verify
**This step MUST be executed before EVERY action! This is the starting point of the loop.**

1. **Screenshot**: Capture the current screen state.
   ```bash
   xfce4-screenshooter -f -s ~/.openclaw/workspace/linux-desktop-control/images/desktop_screeshot_$(date +%Y%m%d_%H%M%S).png
   ```

2. **Analyze**: Use `ui_detect_prompt.sh` to analyze UI elements.
   ```bash
   ./scripts/ui_detect_prompt.sh ~/.openclaw/workspace/linux-desktop-control/images/{original_image_name}.png
   ```
   *(The script automatically generates `{original_image_name_without_extension}_converted.json` with absolute coordinates)*

3. **State Assertion & Self-Correction based on converted.json**:
   - **If starting a task**: Verify the initial state (e.g., is the desktop visible?).
   - **If an action was just performed**: **COMPARE screenshots/UI data before and after the action**.
     - *Example: Last step was "Open Browser". Is there a browser window on screen now? If not, action FAILED.*
     - *Example: Last step was "Click Search Box". Is the input method active? Is there a cursor? If not, action FAILED.*
     - **Handling Failure**: If assertion fails, **DO NOT proceed to the next step**! Analyze the cause (e.g., click unresponsive, slow loading), try retrying, increasing wait time, or using keyboard shortcuts.

### Phase 2: Plan & Decide
1. **Assess Current State**: Based on Phase 1's REAL state, determine the distance to the final goal.
2. **Formulate Next Step**: **Plan ONLY the NEXT 1 atomic action**.
   - *Wrong*: "Click Search Bar -> Wait -> Type 'Lark' -> Enter". (This is scripting, FORBIDDEN!)
   - *Right*: "Current state: Search Bar not focused -> Plan: Click Search Bar at (x,y)". (Execute, then return to Phase 1 to verify focus, THEN plan typing).
3. **Get Target Coordinates**: Find the target element's `bbox` center `(x, y)` from `_converted.json`.

### Phase 3: Act
1. **Execute Action**: Use `mouse_control.py` or `keyboard_control.py` to execute a **SINGLE** action.
2. **Wait for Response**: Allow system reaction time (e.g., 2-5 seconds depending on app speed), usually implied in scripts or requires explicit `sleep`.

**Tools Reference:**
*(See below for command examples)*

#### Keyboard Control
```bash
# ==================== 1. View Help ====================
python3 scripts/keyboard_control.py --help
python3 scripts/keyboard_control.py press --help
python3 scripts/keyboard_control.py type --help
python3 scripts/keyboard_control.py lines --help

# ==================== 2. Command Examples ====================

# Single Key Press
python3 scripts/keyboard_control.py press enter
python3 scripts/keyboard_control.py press space --presses 5
python3 scripts/keyboard_control.py press f5
python3 scripts/keyboard_control.py press esc

# Hotkeys (Combinations)
python3 scripts/keyboard_control.py hotkey ctrl c
python3 scripts/keyboard_control.py hotkey ctrl v
python3 scripts/keyboard_control.py hotkey ctrl alt delete
python3 scripts/keyboard_control.py hotkey ctrl shift esc
python3 scripts/keyboard_control.py hotkey win r

# Type Text (Single Line) - Recommended
python3 scripts/keyboard_control.py type "Hello World! 👋 123"
python3 scripts/keyboard_control.py type "Login Successful" --enter
python3 scripts/keyboard_control.py type 'https://www.google.com' --enter
python3 scripts/keyboard_control.py type "Long text test: ABC123 + emoji 👋 + symbols @#$%" --enter

# Type Multiple Lines (lines) - Best for Code
# From File (Most Reliable)
python3 scripts/keyboard_control.py lines --file code.py
python3 scripts/keyboard_control.py lines --file script.sh
python3 scripts/keyboard_control.py lines --file commands.txt

# Direct Multi-line Text (use \n for newline)
python3 scripts/keyboard_control.py lines --text "Line 1 content\nLine 2 content\nLine 3 code"
python3 scripts/keyboard_control.py lines --text "import os\nprint('hello world')\nprint('IME Decoupled!')\nexit()"

# ==================== 3. Pro Tips ====================
# Faster: Modify pyautogui.PAUSE = 0.05 in the script
# More Stable: Change to 0.15
# Emergency Stop: Move mouse quickly to the top-left corner (pyautogui FAILSAFE)
# macOS uses command+v automatically, Windows/Linux uses ctrl+v

# ==================== 4. One-Click Test All (Copy & Paste) ====================
echo "=== Test Start ==="
python3 scripts/keyboard_control.py press enter
python3 scripts/keyboard_control.py hotkey ctrl v
python3 scripts/keyboard_control.py type "Test Success! 👋" --enter
python3 scripts/keyboard_control.py lines --text "Multi-line Test\nLine 2\nLine 3"
echo "=== Test End ==="
```

### Phase 4: Loop
- **Return to Phase 1**, untill the "Definition of Done" is met.

## Definition of Done (DoD)
The Agent can ONLY declare the task complete when:
1. **Final Goal Achieved**: A clear success indicator appears on screen (e.g., "Installation Complete" message, target app opened and showing home page).
2. **Verification Passed**: The last screenshot MUST contain visual evidence of success.
3. **Clean State**: All intermediate temporary windows (e.g., package manager) are closed (if required).

## Error Handling & Retry Strategy
1. **Element Not Found**: If the target element is missing in JSON, try scrolling or checking other tabs/windows.
2. **Action Unresponsive**: If screen doesn't change after clicking:
   - Check if Double Click is needed.
   - Check if Right Click menu is needed.
   - Try Keyboard Shortcuts (e.g., `Ctrl+L` for address bar, `Super` key for menu).
3. **App Not Starting**: If clicking an icon fails, try launching via command line (`RunCommand`) as a fallback.

