import json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse


# ====================== 智能中文字体 ======================
def get_chinese_font(size: int = 24):
    font_candidates = [
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


# ====================== 坐标转换 + 添加 center ======================
def convert_to_absolute(result: dict, orig_width: int, orig_height: int):
    """将归一化bbox转为绝对坐标，并为每个object添加center字段"""
    # 深拷贝，避免修改原始数据
    new_result = json.loads(json.dumps(result))
    for obj in new_result.get("objects", []):
        if "bbox" not in obj:
            continue
        x1, y1, x2, y2 = obj["bbox"]

        # 转为真实像素坐标
        real_x1 = int(x1 / 1000 * orig_width)
        real_y1 = int(y1 / 1000 * orig_height)
        real_x2 = int(x2 / 1000 * orig_width)
        real_y2 = int(y2 / 1000 * orig_height)

        obj["bbox"] = [real_x1, real_y1, real_x2, real_y2]

        # 添加中心坐标
        center_x = (real_x1 + real_x2) // 2
        center_y = (real_y1 + real_y2) // 2
        obj["center"] = [center_x, center_y]

    return new_result


# ====================== 画图标注（已完全移除 gt_bboxes） ======================
def draw_annotations(image_path: str, result: dict, output_path: str = None):
    img = Image.open(image_path)
    orig_width, orig_height = img.size
    print(f"📏 原图尺寸: {orig_width}×{orig_height}")

    # 确保图片模式为 RGBA 以便绘制半透明效果
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    draw = ImageDraw.Draw(img, "RGBA")
    font = get_chinese_font(24)
    print("✅ 已加载中文字体")

    for i, obj in enumerate(result.get("objects", [])):
        x1, y1, x2, y2 = obj["bbox"]
        text_content = obj.get("text", "文字")

        # 绘制红色框（豆包结果）
        draw.rectangle([x1, y1, x2, y2],
                       outline=(255, 0, 0, 255), width=6, fill=(255, 0, 0, 50))

        label = f"豆包-{i + 1}: {text_content}"
        draw.text((x1 + 5, y1 - 32), label, fill=(255, 0, 0, 255), font=font)

        print(f"✅ 检测到: {text_content} → 绝对坐标: [{x1},{y1},{x2},{y2}] 中心: {obj.get('center')}")

    if output_path is None:
        output_path = str(Path(image_path).with_name(f"{Path(image_path).stem}_annotated.jpg"))

    # 根据输出文件格式进行适当的模式转换
    save_path = Path(output_path)
    suffix = save_path.suffix.lower()

    if suffix in [".jpg", ".jpeg"]:
        # JPG 不支持透明度，转换为 RGB
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
    else:
        # 其他格式（如 PNG）保持 RGBA
        if img.mode != "RGBA":
            img = img.convert("RGBA")

    img.save(output_path)
    print(f"🎉 标注图片已保存: {output_path}")
    # img.show()  # 需要预览时取消注释


# ====================== 主程序 ======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="豆包 OCR 文字定位 - 绝对坐标转换 + 标注（已移除GT）")
    parser.add_argument("--input", required=True, help="输入 JSON 文件（归一化 bbox）")
    parser.add_argument("--output", required=True, help="输出绝对坐标 JSON 文件路径（含 center）")
    parser.add_argument("--source_image", required=True, help="原始图片路径（必须存在）")
    parser.add_argument("--annotated", default=None, help="标注图片保存路径（可选）")
    args = parser.parse_args()

    # 加载输入JSON
    with open(args.input, "r", encoding="utf-8") as f:
        json_file = json.load(f)

    # 打开图片获取真实尺寸
    img = Image.open(args.source_image)
    orig_width, orig_height = img.size

    # 转换坐标并添加 center
    converted_result = convert_to_absolute(json_file, orig_width, orig_height)

    # 保存转换后的JSON到 --output
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(converted_result, f, ensure_ascii=False, indent=2)
    print(f"✅ 绝对坐标JSON已保存: {args.output}")

    # 生成并保存标注图片到 --annotated
    draw_annotations(
        image_path=args.source_image,
        result=converted_result,
        output_path=args.annotated
    )