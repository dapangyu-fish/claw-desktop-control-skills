#!/bin/bash

# ================================================
# OpenClaw Linux桌面UI检测脚本 - 单参数自动命名版（带重试机制）
# 用法: ./ui_detect.sh <图片完整路径>
# 示例:
#   ./ui_detect.sh desktop_screenshot_20260316_203530.png
# ================================================

if [ "$#" -ne 1 ]; then
    echo "用法错误！只需一个参数（图片路径）。"
    echo "正确用法: $0 <图片路径>"
    echo ""
    echo "示例:"
    echo "  $0 desktop_screenshot_20260316_203530.png"
    exit 1
fi

# 参数
IMAGE_PATH="$1"                    # 使用用户传入的路径（原脚本此处逻辑不一致，已修正）
DISPLAY="$1"

# 截图流程
set -euo pipefail

screenshot_success=0

# 1. grim (Wayland 主流)
if command -v grim >/dev/null 2>&1; then
    grim "${IMAGE_PATH}" && screenshot_success=1
fi

# 2. spectacle (KDE)
if [ $screenshot_success -eq 0 ] && command -v spectacle >/dev/null 2>&1; then
    spectacle -f -b -o "${IMAGE_PATH}" && screenshot_success=1
fi

# 3. scrot (X11 经典轻量工具)
if [ $screenshot_success -eq 0 ] && command -v scrot >/dev/null 2>&1; then
    scrot "${IMAGE_PATH}" && screenshot_success=1
fi

# 4. import (ImageMagick 兜底)
if [ $screenshot_success -eq 0 ] && command -v import >/dev/null 2>&1; then
    import -window root "${IMAGE_PATH}" && screenshot_success=1
fi

# 5. gnome-screenshot
if [ $screenshot_success -eq 0 ] && command -v gnome-screenshot >/dev/null 2>&1; then
    gnome-screenshot -f "${IMAGE_PATH}" && screenshot_success=1
fi

# 6. xfce4-screenshooter
if [ $screenshot_success -eq 0 ] && command -v xfce4-screenshooter >/dev/null 2>&1; then
    xfce4-screenshooter -f -s "${IMAGE_PATH}" && screenshot_success=1
fi

# 7. maim (现代 scrot 替代)
if [ $screenshot_success -eq 0 ] && command -v maim >/dev/null 2>&1; then
    maim --format png "${IMAGE_PATH}" && screenshot_success=1
fi

# ──────────────── 结果判断 ────────────────

if [ $screenshot_success -eq 1 ]; then
    sleep 1
    # 可选：尝试复制到剪贴板
    if command -v wl-copy >/dev/null 2>&1; then
        wl-copy < "${IMAGE_PATH}"
    elif command -v xclip >/dev/null 2>&1; then
        xclip -selection clipboard -t image/png -i "${IMAGE_PATH}"
    fi
else
    echo "错误：没有找到任何可用的截图工具" >&2
    echo "请安装以下任一工具：" >&2
    echo "  • grim          (Wayland)" >&2
    echo "  • spectacle     (KDE)" >&2
    echo "  • scrot         (X11 通用)" >&2
    echo "  • ImageMagick   (import 命令)" >&2
    echo "  • gnome-screenshot" >&2
    echo "  • xfce4-screenshooter" >&2
    echo "  • maim" >&2
    exit 1
fi

# 检查图片是否存在
if [ ! -f "$IMAGE_PATH" ]; then
    echo "错误：图片文件不存在: $IMAGE_PATH"
    exit 1
fi

# ==================== 自动生成 JSON 文件名 ====================
IMAGE_BASENAME=$(basename "$IMAGE_PATH")
EXPORT_IMAGE_NAME="${IMAGE_BASENAME%.*}_annotated.png" 
ORIGINAL_JSON_NAME="${IMAGE_BASENAME%.*}_original.json" 
CONVERTED_JSON_NAME="${IMAGE_BASENAME%.*}_converted.json" 
TEMP_TXT_NAME="${IMAGE_BASENAME%.*}_temp.txt" 

EXPORT_IMAGE_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/images/${EXPORT_IMAGE_NAME}"
ORIGINAL_JSON_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/json/${ORIGINAL_JSON_NAME}"
CONVERTED_JSON_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/json/${CONVERTED_JSON_NAME}"
TEMP_TXT_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/temp/${TEMP_TXT_NAME}"

# 创建输出目录
mkdir -p "$HOME/.openclaw/workspace/linux-desktop-control/json"
mkdir -p "$HOME/.openclaw/workspace/linux-desktop-control/temp"

echo "🚀 正在调用 openclaw agent 进行 UI 检测..."

# ==================== 重试逻辑（新增核心部分） ====================
MAX_RETRIES=3
retry_count=0
agent_success=0

while [ $retry_count -lt $MAX_RETRIES ] && [ $agent_success -eq 0 ]; do
    retry_count=$((retry_count + 1))
    echo "尝试 $retry_count/$MAX_RETRIES 调用 openclaw agent..."

    # 清理上次可能失败的文件（避免脏数据干扰）
    rm -f "$ORIGINAL_JSON_PATH"

    # 调用 openclaw agent（stderr 重定向到 temp，便于失败时排查）
    openclaw agent --agent linux-desktop-control-ui-detect --message "$(cat << EOF
/new 请分析下这张图${IMAGE_PATH}，

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
    - 坐标严格归一化到0~1000整数：\`x = round((pixel_x / 图片宽度) * 1000)\`，同理y。
    - 保证 x1 < x2、y1 < y2，所有值在0~1000范围内。

    **text命名规则**（必须全局唯一）：
    - 有文字时：结合文字+功能（如 "Google标签页"）
    - 重复元素强制加区分（如 "Google标签页关闭按钮"、"第3个标签页关闭按钮"、"窗口标题栏关闭按钮"、"地址栏刷新按钮"、"左侧第1个扩展图标"）

    **输出要求**：**只返回纯JSON**，不要任何解释、思考过程、代码块、markdown或其他文字！现在直接输出：

    {{
      "objects": [
        {{"text": "唯一描述", "bbox": [x1, y1, x2, y2]}},
        ...
      ],
      "description": "对图片整体进行详细描述"
    }}
    }}

**必须**将结果保存为文件 **$ORIGINAL_JSON_PATH**
注意 当前任务是 linux-desktop-control 的子任务
EOF
)" > "${TEMP_TXT_PATH}" 2>&1

    # 检查是否成功生成 JSON 文件（存在 + 非空）
    if [ -f "$ORIGINAL_JSON_PATH" ] && [ -s "$ORIGINAL_JSON_PATH" ]; then
        agent_success=1
        echo "✅ openclaw agent 执行成功（第 $retry_count 次尝试）"
    else
        if [ $retry_count -lt $MAX_RETRIES ]; then
            echo "⚠️ 第 $retry_count 次尝试失败（$ORIGINAL_JSON_PATH 未生成），等待 2 秒后重试..."
            sleep 2
        fi
    fi
done

# 重试全部失败后的处理
if [ $agent_success -eq 0 ]; then
    echo "❌ 错误：经过 ${MAX_RETRIES} 次尝试后，仍未能生成 $ORIGINAL_JSON_PATH" >&2
    echo "最后一次执行日志（含错误输出）：" >&2
    echo "=========================================" >&2
    cat "${TEMP_TXT_PATH}" >&2
    echo "=========================================" >&2
    echo "建议排查：" >&2
    echo "  • openclaw agent 是否正常运行" >&2
    echo "  • json 目录权限是否足够" >&2
    echo "  • 模型是否能正确解析指令并保存文件" >&2
    exit 1
fi

# ==================== 坐标转换 ====================
python3 ${HOME}/.openclaw/workspace/skills/claw-desktop-control-skills/scripts/coordinate_conversion.py \
    --input=${ORIGINAL_JSON_PATH} \
    --output=${CONVERTED_JSON_PATH} \
    --source_image=${IMAGE_PATH} \
    --annotated=${EXPORT_IMAGE_PATH} >> ${TEMP_TXT_PATH} 2>&1

echo "✅ 执行完成！"
echo "原始图片 文件已自动保存为：${IMAGE_PATH}"
echo "坐标化 JSON 文件已自动保存为：${CONVERTED_JSON_PATH}"