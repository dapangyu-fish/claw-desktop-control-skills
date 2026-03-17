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
   *(The script automatically generates `{original_image_name_without_extension}_original.json`)*

3. **Coordinate Conversion**: Convert normalized coordinates to absolute coordinates.
   ```bash
   python3 scripts/coordinate_conversion.py \
     --input=~/.openclaw/workspace/linux-desktop-control/json/{original_image_name_without_extension}_original.json \
     --output=~/.openclaw/workspace/linux-desktop-control/json/{original_image_name_without_extension}_converted.json \
     --tag_image=~/.openclaw/workspace/linux-desktop-control/json/{original_image_name_without_extension}_export.json
   ```

4. **State Assertion & Self-Correction**:
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

