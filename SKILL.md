---
name: "linux-desktop-control"
description: "Control desktop applications and perform system tasks via Python scripts. Invoke when user wants to automate desktop actions."
---

# Linux Desktop Control Skill

This skill allows controlling desktop applications and performing system operations using Python scripts.

## Prerequisites

- **DISPLAY Environment Variable**: This variable is essential. If missing, ask the user to provide it.

## Core Workflow: OODA Loop (Observe-Orient-Decide-Act)

**⚠️ CRITICAL RULE for Agent:**
This Skill is a **Closed-Loop Control System**, not a linear script.
**You MUST strictly follow the "Screenshot -> Analyze -> Decide -> Act -> Verify" loop** until the final goal is achieved.
**DO NOT generate code for all steps at once! You MUST "take one step, look once".**

### Phase 0: Initialization
Run the setup script to prepare the workspace and verify the environment.

**Command:**
```bash
./setup.sh
```

### Phase 1: Observe & Verify
**This step MUST be executed before EVERY action!**
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

4. **Self-Correction & Verification**:
   - **If this is the first step**: Skip verification and proceed to Phase 2.
   - **If an action was just performed**: Compare the **before** and **after** screenshots/UI data.
     - *Ask yourself: "Did the last action work? Is the window open? Is there text in the input box?"*
     - **If failed**: Stop the current plan, analyze the cause, and try an alternative (e.g., keyboard shortcut instead of click, or re-target coordinates).
     - **If successful**: Proceed to the next step.

### Phase 2: Plan & Decide
1. **Assess Current State**: Based on Phase 1 results, determine how far you are from the final goal.
2. **Formulate Next Step**: **Plan ONLY the NEXT 1 atomic action** (e.g., "Click Search Bar").
   - **DO NOT** plan subsequent "Type text" or "Press Enter" because you don't know if "Click Search Bar" succeeded yet.
3. **Get Target Coordinates**: Find the target element's `bbox` center `(x, y)` from `_converted.json`.

### Phase 3: Act
1. **Execute Action**: Use `mouse_control.py` or `keyboard_control.py` to execute a **SINGLE** action.
2. **Wait for Response**: Allow system reaction time after an action (e.g., wait 1-2 seconds), usually implied in scripts or requires explicit `sleep`.

**Tools Reference:**

#### Mouse Control
```bash
# Click
python3 scripts/mouse_control.py click 300 400
# Double Click
python3 scripts/mouse_control.py double 500 300 --duration 0.4
# Drag
python3 scripts/mouse_control.py drag 100 100 400 400 --duration 1.2
# Right Click
python3 scripts/mouse_control.py right 600 500
# Scroll
python3 scripts/mouse_control.py scroll 200 200 -300
```

#### Keyboard Control
```bash
# Press Key
python3 scripts/keyboard_control.py press enter
# Hotkey
python3 scripts/keyboard_control.py hotkey ctrl c
# Type Text
python3 scripts/keyboard_control.py type "Hello World!" --interval 0.05
```

### Phase 4: Loop
- **Return to Phase 1** until the task is completed.

