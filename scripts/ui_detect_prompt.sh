#!/bin/bash

# ================================================
# OpenClaw Linux桌面UI检测脚本 - 单参数自动命名版
# 用法: ./ui_detect.sh <图片完整路径>
# 示例:
#   ./ui_detect.sh /home/fish/.openclaw/workspace/linux-desktop-control/images/desktop_screenshot_20260316_203530.png
# ================================================

if [ "$#" -ne 1 ]; then
    echo "用法错误！只需一个参数（图片路径）。"
    echo "正确用法: $0 <screenshot_path>"
    echo ""
    echo "示例:"
    echo "  $0 /home/fish/.openclaw/workspace/linux-desktop-control/images/desktop_screenshot_20260316_203530.png"
    exit 1
fi

# 参数
IMAGE_PATH="$1"

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
EXPORT_IMAGE_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/images/${EXPORT_IMAGE_NAME}"
ORIGINAL_JSON_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/json/${ORIGINAL_JSON_NAME}"
CONVERTED_JSON_PATH="${HOME}/.openclaw/workspace/linux-desktop-control/json/${CONVERTED_JSON_NAME}"

# 创建输出目录
mkdir -p "$HOME/.openclaw/workspace/linux-desktop-control/json"

echo "🚀 正在调用 openclaw agent 进行 UI 检测..."
echo "   图片: $IMAGE_PATH"
echo "   输出: ~/.openclaw/workspace/linux-desktop-control/json/$ORIGINAL_JSON_NAME"

# 完整 Prompt（零临时文件，直接 heredoc）
openclaw agent --json --agent linux-desktop-control-ui-detect --message "$(cat << EOF
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
**重点检测类别**（必须覆盖所有浏览器相关可交互元素）：
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
{
  "objects": [
    {"text": "唯一描述", "bbox": [x1, y1, x2, y2]},
    ...
  ],
  "description": "对图片进行整体描述"
}
**必须**将结果报存为文件 **$ORIGINAL_JSON_PATH**

EOF
)" 

python3 ${HOME}/.openclaw/workspace/skills/claw-desktop-control-skills/scripts/coordinate_conversion.py \
    --input=${ORIGINAL_JSON_PATH} \
    --output=${CONVERTED_JSON_PATH} \
    --source_image=${IMAGE_PATH} \
    --annotated=${EXPORT_IMAGE_PATH}

echo "✅ 执行完成！"
echo "JSON 文件已自动保存为：~/.openclaw/workspace/linux-desktop-control/json/${CONVERTED_JSON_NAME}"