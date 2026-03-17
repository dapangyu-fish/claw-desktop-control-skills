#!/bin/bash

# ================================================
# OpenClaw Linux桌面UI检测脚本 - 单参数自动命名版
# 用法: ./get_next_plan_prompt.sh <图片完整路径> <请求提示>
# 示例:
#   ./get_next_plan_prompt.sh /home/fish/.openclaw/workspace/linux-desktop-control/images/desktop_screenshot_20260316_203530.png "我需要点击搜索框"
# ================================================

if [ "$#" -ne 2 ]; then
    echo "正确用法: $0 <screenshot_path> <request_prompt>"
    echo ""
    echo "示例:"
    echo "  $0 /home/fish/.openclaw/workspace/linux-desktop-control/images/desktop_screenshot_20260316_203530.png \"Please find the search bar\""
    exit 1
fi

# 参数
IMAGE_PATH="$1"
REQUEST_PROMPT="$2"

# 检查图片是否存在
if [ ! -f "$IMAGE_PATH" ]; then
    echo "错误：图片文件不存在: $IMAGE_PATH"
    exit 1
fi

# ==================== 自动生成 JSON 文件名 ====================
IMAGE_BASENAME=$(basename "$IMAGE_PATH")
CONVERTED_JSON_NAME="${IMAGE_BASENAME%.*}_converted.json" 
CONVERTED_JSON_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/json/${CONVERTED_JSON_NAME}"

# 创建输出目录
mkdir -p "$HOME/.openclaw/workspace/linux-desktop-control/json"

echo "🚀 分析下一步动作..."

# 完整 Prompt（零临时文件，直接 heredoc）
openclaw agent --agent linux-desktop-control-ui-detect --message "$(cat << EOF
/new 请分析下这张图${IMAGE_PATH}，你可以参考一份JSON文件：${CONVERTED_JSON_PATH}，内含图片中一些可见的UI元素，我现在需要根据请求提示：${REQUEST_PROMPT}，分析下一步动作。
EOF
)" 
