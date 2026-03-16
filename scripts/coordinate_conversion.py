import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from scripts.utils import get_project_root

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

    # ==================== 坐标转换：归一化 → 绝对像素 ====================
    absolute_objects = []
    for obj in objects:
        norm_bbox = obj.get("bbox", [0, 0, 0, 0])
        x1, y1, x2, y2 = norm_bbox

        abs_x1 = round(x1 / 1000 * orig_width)
        abs_y1 = round(y1 / 1000 * orig_height)
        abs_x2 = round(x2 / 1000 * orig_width)
        abs_y2 = round(y2 / 1000 * orig_height)

        absolute_objects.append({
            "text": obj.get("text", "未命名元素"),
            "bbox": [abs_x1, abs_y1, abs_x2, abs_y2]   # 绝对像素坐标
        })

    # 保存绝对坐标 JSON
    result = {"objects": absolute_objects}
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 绝对坐标 JSON 已保存: {output_json_path}")
    return img, absolute_objects


def draw_annotations(img: Image.Image, absolute_objects: list, tag_image_path: str):
    draw = ImageDraw.Draw(img, "RGBA")
    font = get_chinese_font(24)
    print("✅ 已加载中文字体")

    for i, obj in enumerate(absolute_objects):
        x1, y1, x2, y2 = obj["bbox"]
        text_content = obj.get("text", "文字")

        # 红色半透明框 + 边框
        draw.rectangle([x1, y1, x2, y2],
                       outline=(255, 0, 0, 255), width=6, fill=(255, 0, 0, 50))

        # 标签文字（上方）
        label = f"Det-{i+1}: {text_content}"
        draw.text((x1 + 5, y1 - 30), label, fill=(255, 0, 0, 255), font=font)

        print(f"✅ 标注: {text_content} → [{x1},{y1},{x2},{y2}]")

    # 自动保存标注图片（原文件名 + _annotated）
    p = Path(tag_image_path)
    annotated_path = p.with_name(f"{p.stem}_annotated{p.suffix}")
    img.save(annotated_path)
    print(f"🎉 标注图片已保存: {annotated_path}")
    img.show()  # 可选：本地预览


# ====================== 命令行 ======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="坐标转换 + 图片标注工具（仅处理 JSON）")
    parser.add_argument("--input", required=True, help="输入 JSON 文件（归一化 bbox）")
    parser.add_argument("--output", required=True, help="输出绝对坐标 JSON 文件路径")
    parser.add_argument("--tag_image", required=True, help="原图路径（用于获取尺寸和绘制标注）")
    args = parser.parse_args()

    # 执行转换
    img, abs_objects = convert_to_absolute(args.input, args.tag_image, args.output)

    # 执行标注并保存
    draw_annotations(img, abs_objects, args.tag_image)