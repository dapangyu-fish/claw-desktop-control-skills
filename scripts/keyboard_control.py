import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import os
import sys

def get_project_root():
    """Returns the absolute path to the project root directory."""
    # Assuming this file is in scripts/utils.py, so project root is one level up
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_script_path(script_name):
    """Returns the absolute path to a script in the scripts directory."""
    return os.path.join(get_project_root(), 'scripts', script_name)

def add_project_root_to_sys_path():
    """Adds the project root to sys.path to allow importing modules from root."""
    project_root = get_project_root()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# ====================== 智能中文字体 ======================
def get_chinese_font(size: int = 24):
    # 字体文件在项目根目录下
    project_root = get_project_root()
    font_path = os.path.join(project_root, "NotoSansSC-VariableFont_wght.ttf")
    
    font_candidates = [
        font_path,
        "./NotoSansSC-VariableFont_wght.ttf", # Fallback relative path
    ]
    for path in font_candidates:
        try:
            if path.endswith(".ttc"):
                return ImageFont.truetype(path, size, index=0)
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def convert_to_absolute(json_path: str, image_path: str, output_json_path: str):
    # 加载原图获取真实尺寸
    img = Image.open(image_path)
    orig_width, orig_height = img.size
    print(f"📏 原图尺寸: {orig_width}×{orig_height}")

    # 加载输入 JSON（归一化 0~1000）
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    objects = data.get("objects", [])
    if not objects:
        print("⚠️ JSON 中没有 objects 字段")

    # ==================== 新增：透传顶层 description 字段 ====================
    description = data.get("description")  # 直接读取（可能为 None）

    # ==================== 坐标转换：归一化 → 绝对像素 ====================
    absolute_objects = []
    for obj in objects:
        norm_bbox = obj.get("bbox", [0, 0, 0, 0])
        x1, y1, x2, y2 = norm_bbox

        abs_x1 = round(x1 / 1000 * orig_width)
        abs_y1 = round(y1 / 1000 * orig_height)
        abs_x2 = round(x2 / 1000 * orig_width)
        abs_y2 = round(y2 / 1000 * orig_height)

        # ==================== 新增：中心坐标（用于点击操作） ====================
        center_x = round((abs_x1 + abs_x2) / 2)
        center_y = round((abs_y1 + abs_y2) / 2)

        absolute_objects.append({
            "text": obj.get("text", "未命名元素"),
            "bbox": [abs_x1, abs_y1, abs_x2, abs_y2],      # 绝对像素坐标
            "center": [center_x, center_y]                 # 新增：中心坐标 (cx, cy)，方便后续点击
        })

    # 保存绝对坐标 JSON（透传 description + 新增 center）
    result = {"objects": absolute_objects}
    if description is not None:  # 只在存在时写入，避免多余的 null
        result["description"] = description

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 绝对坐标 JSON 已保存: {output_json_path}（已新增 center 字段 + 透传 description）")
    return img, absolute_objects


def draw_annotations(img: Image.Image, absolute_objects: list, tag_image_path: str):
    draw = ImageDraw.Draw(img, "RGBA")
    font = get_chinese_font(24)
    print("✅ 已加载中文字体")

    for i, obj in enumerate(absolute_objects):
        x1, y1, x2, y2 = obj["bbox"]
        text_content = obj.get("text", "文字")
        cx, cy = obj.get("center", [0, 0])  # 读取中心坐标（仅用于日志）

        # 红色半透明框 + 边框
        draw.rectangle([x1, y1, x2, y2],
                       outline=(255, 0, 0, 255), width=6, fill=(255, 0, 0, 50))

        # 标签文字（上方）
        label = f"Det-{i+1}: {text_content} | 中心:({cx},{cy})"
        draw.text((x1 + 5, y1 - 30), label, fill=(255, 0, 0, 255), font=font)

        print(f"✅ 标注: {text_content} → 框[{x1},{y1},{x2},{y2}] 中心({cx},{cy})")

    # 自动保存标注图片（原文件名 + _annotated）
    p = Path(tag_image_path)
    annotated_path = p.with_name(f"{p.stem}_annotated{p.suffix}")
    img.save(annotated_path)
    print(f"🎉 标注图片已保存: {annotated_path}")
    img.show()  # 可选：本地预览


# ====================== 命令行 ======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="坐标转换 + 图片标注工具（新增 center + 透传 description）")
    parser.add_argument("--input", required=True, help="输入 JSON 文件（归一化 bbox）")
    parser.add_argument("--output", required=True, help="输出绝对坐标 JSON 文件路径")
    parser.add_argument("--tag_image", required=True, help="原图路径（用于获取尺寸和绘制标注）")
    args = parser.parse_args()

    # 执行转换（现在每个对象都会包含 center，且 description 自动透传）
    img, abs_objects = convert_to_absolute(args.input, args.tag_image, args.output)

    # 执行标注并保存
    draw_annotations(img, abs_objects, args.tag_image)