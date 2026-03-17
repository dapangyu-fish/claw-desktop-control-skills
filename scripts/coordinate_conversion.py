import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import os
import sys

def get_project_root():
    """Returns the absolute path to the project root directory."""
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
    project_root = get_project_root()
    font_path = os.path.join(project_root, "NotoSansSC-VariableFont_wght.ttf")
    
    font_candidates = [
        font_path,
        "./NotoSansSC-VariableFont_wght.ttf",
    ]
    for path in font_candidates:
        try:
            if path.endswith(".ttc"):
                return ImageFont.truetype(path, size, index=0)
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def convert_to_absolute(json_path: str, source_image_path: str, output_json_path: str):
    # 加载原始图片获取真实尺寸
    img = Image.open(source_image_path)
    orig_width, orig_height = img.size
    print(f"📏 原图尺寸: {orig_width}×{orig_height}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    objects = data.get("objects", [])
    absolute_objects = []
    for obj in objects:
        norm_bbox = obj.get("bbox", [0, 0, 0, 0])
        x1, y1, x2, y2 = norm_bbox

        abs_x1 = round(x1 / 1000 * orig_width)
        abs_y1 = round(y1 / 1000 * orig_height)
        abs_x2 = round(x2 / 1000 * orig_width)
        abs_y2 = round(y2 / 1000 * orig_height)

        center_x = round((abs_x1 + abs_x2) / 2)
        center_y = round((abs_y1 + abs_y2) / 2)

        absolute_objects.append({
            "text": obj.get("text", "未命名元素"),
            "bbox": [abs_x1, abs_y1, abs_x2, abs_y2],
            "center": [center_x, center_y]
        })

    result = {"objects": absolute_objects}
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 绝对坐标 JSON 已保存: {output_json_path}（已新增 center 字段）")
    return img, absolute_objects


# ====================== 标注函数（已支持自定义输出路径） ======================
def draw_annotations(img: Image.Image, absolute_objects: list, source_image_path: str, annotated_path: str = None):
    draw = ImageDraw.Draw(img, "RGBA")
    font = get_chinese_font(24)
    print("✅ 已加载中文字体")

    for i, obj in enumerate(absolute_objects):
        x1, y1, x2, y2 = obj["bbox"]
        text_content = obj.get("text", "文字")
        cx, cy = obj.get("center", [0, 0])

        draw.rectangle([x1, y1, x2, y2],
                       outline=(255, 0, 0, 255), width=6, fill=(255, 0, 0, 50))

        label = f"Det-{i+1}: {text_content} | 中心:({cx},{cy})"
        draw.text((x1 + 5, y1 - 30), label, fill=(255, 0, 0, 255), font=font)

        print(f"✅ 标注: {text_content} → 框[{x1},{y1},{x2},{y2}] 中心({cx},{cy})")

    # ==================== 自定义保存路径 ====================
    if annotated_path is None:
        p = Path(source_image_path)
        annotated_path = p.with_name(f"{p.stem}_annotated{p.suffix}")

    img.save(annotated_path)
    print(f"🎉 标注图片已保存到你指定的位置: {annotated_path}")
    img.show()  # 可选：本地预览


# ====================== 命令行 ======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="坐标转换 + 图片标注工具（--source_image 为原始图片）")
    parser.add_argument("--input", required=True, help="输入 JSON 文件（归一化 bbox）")
    parser.add_argument("--output", required=True, help="输出绝对坐标 JSON 文件路径")
    parser.add_argument("--source_image", required=True, help="原始图片路径（必须真实存在，用于读取尺寸和作为标注底图）")
    parser.add_argument("--annotated", default=None, help="标注图片保存路径（可选，不填则自动加 _annotated）")
    args = parser.parse_args()

    # 执行转换
    img, abs_objects = convert_to_absolute(args.input, args.source_image, args.output)
    
    # 执行标注
    draw_annotations(img, abs_objects, args.source_image, args.annotated)