import os
import math
from PIL import Image

def create_photo_layout(
    image_path,
    output_path=None,
    photo_type="1寸",
    spacing_mm=2,
    custom_layout=None,
    dpi=300,
    paper_size_mm=None
):
    # 1. 毫米转像素辅助函数
    def mm_to_px(mm):
        return int(math.floor((mm / 25.4) * dpi))

    # 2. 常见尺寸映射 (单位: mm)
    SIZE_MAP = {
        # 中国常用尺寸
        "1寸 (25x35 mm)": (25, 35),
        "小2寸 (33x48 mm)": (33, 48),
        "2寸 (35x49 mm)": (35, 49),
        "大2寸 (35x53 mm)": (35, 53),
        "3寸 (55x84 mm)": (55, 84),
        # 常见证件照（也用于国际）
        "35x45 mm": (35, 45),
        "35x50 mm": (35, 50),
        "51x51 mm": (51, 51),
        # 标签友好的键
        "US Visa (51x51 mm)": (51, 51),
        "Japan (35x45 mm)": (35, 45),
        "Schengen (35x45 mm)": (35, 45),
        "UK (35x45 mm)": (35, 45),
        "Canada (35x50 mm)": (35, 50),
        "Thailand (35x45 mm)": (35, 45),
    }

    PAPER_SIZES = {
        "6寸相纸 102x152 mm": (102, 152),
        "4x6 in 102x152 mm": (102, 152),
        "A4 210x297 mm": (210, 297),
    }

    # 允许传入自定义纸张尺寸覆盖默认
    if paper_size_mm:
        PAPER_W, PAPER_H = paper_size_mm
    else:
        PAPER_W, PAPER_H = PAPER_SIZES.get("6寸相纸 102x152 mm")

    # 解析照片尺寸支持字符串键或直接传入(mm_w, mm_h)
    if isinstance(photo_type, (tuple, list)) and len(photo_type) == 2:
        TARGET_W, TARGET_H = photo_type
    elif isinstance(photo_type, str):
        if photo_type in SIZE_MAP:
            TARGET_W, TARGET_H = SIZE_MAP[photo_type]
        else:
            # 兼容原先简单值
            if photo_type == "1寸":
                TARGET_W, TARGET_H = 25, 35
            elif photo_type == "2寸":
                TARGET_W, TARGET_H = 35, 53
            else:
                raise ValueError("不支持的照片类型，请选择常见尺寸或传入(mm_w, mm_h)")

    # 自动生成输出文件名（如果未提供）: 源文件名 + _{尺寸标签}.{ext}
    if output_path is None:
        src_dir, src_name = os.path.split(image_path)
        stem, ext = os.path.splitext(src_name)
        # 创建简短尺寸标签
        size_tag = None
        if isinstance(photo_type, str):
            if "1寸" in photo_type or "1inch" in photo_type:
                size_tag = "1inch"
            elif "2寸" in photo_type or "2inch" in photo_type:
                size_tag = "2inch"
            elif "35x45" in photo_type or "35x45 mm" in photo_type:
                size_tag = "35x45"
            elif "51x51" in photo_type or "Passport" in photo_type:
                size_tag = "51x51"
        if not size_tag:
            try:
                size_tag = f"{int(TARGET_W)}x{int(TARGET_H)}mm"
            except Exception:
                size_tag = f"{TARGET_W}x{TARGET_H}"

        output_path = os.path.join(src_dir, f"{stem}_{size_tag}{ext}")

    # 转换为像素尺寸
    paper_pixel_w = mm_to_px(PAPER_W)
    paper_pixel_h = mm_to_px(PAPER_H)
    target_pixel_w = mm_to_px(TARGET_W)
    target_pixel_h = mm_to_px(TARGET_H)
    spacing_pixel = mm_to_px(spacing_mm)

    if not os.path.exists(image_path):
        print(f"错误: 找不到输入照片 {image_path}")
        return

    # 3. 【核心修改】中央自动裁剪与缩放逻辑
    src_img = Image.open(image_path)
    src_w, src_h = src_img.size
    
    # 计算目标比例 (如1寸为 25/35 = 0.714)
    target_ratio = target_pixel_w / target_pixel_h
    src_ratio = src_w / src_h

    print(f"--- 照片裁剪处理 ---")
    print(f"原图尺寸: {src_w} x {src_h} (比例: {src_ratio:.3f})")
    print(f"目标比例: {target_ratio:.3f}")

    if src_ratio > target_ratio:
        # 原图太宽了（如 16:9 或 1:1 正方形），需要裁掉左右两边
        crop_h = src_h
        crop_w = int(src_h * target_ratio)
        offset_x = (src_w - crop_w) // 2
        offset_y = 0
        print(f"裁剪策略: 左右裁剪，裁掉宽度 {src_w - crop_w} 像素")
    else:
        # 原图太长了，需要裁掉上下两边
        crop_w = src_w
        crop_h = int(src_w / target_ratio)
        offset_x = 0
        offset_y = (src_h - crop_h) // 2
        print(f"裁剪策略: 上下裁剪，裁掉高度 {src_h - crop_h} 像素")

    # 执行中央裁剪
    cropped_img = src_img.crop((offset_x, offset_y, offset_x + crop_w, offset_y + crop_h))
    
    # 高质量缩放到标准1寸/2寸像素大小（不拉伸、无白边，完美填满）
    photo_cell = cropped_img.resize((target_pixel_w, target_pixel_h), Image.Resampling.LANCZOS)

    # 4. 计算布局 (行列数)
    if custom_layout and len(custom_layout) == 2:
        cols, rows = custom_layout
    else:
        cols = int((paper_pixel_w + spacing_pixel) / (target_pixel_w + spacing_pixel))
        rows = int((paper_pixel_h + spacing_pixel) / (target_pixel_h + spacing_pixel))
        cols, rows = max(1, cols), max(1, rows)

    print(f"\n--- 排版布局 (DPI: {dpi}) ---")
    print(f"最终采用布局: {cols} 列 x {rows} 行 (共 {cols * rows} 张)")

    # 5. 创建画布并计算整体居中偏移量
    canvas = Image.new("RGB", (paper_pixel_w, paper_pixel_h), "white")
    
    total_grid_w = cols * target_pixel_w + (cols - 1) * spacing_pixel
    total_grid_h = rows * target_pixel_h + (rows - 1) * spacing_pixel

    start_x = (paper_pixel_w - total_grid_w) // 2
    start_y = (paper_pixel_h - total_grid_h) // 2

    # 6. 循环拼图
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * (target_pixel_w + spacing_pixel)
            y = start_y + r * (target_pixel_h + spacing_pixel)
            if x + target_pixel_w <= paper_pixel_w and y + target_pixel_h <= paper_pixel_h:
                canvas.paste(photo_cell, (x, y))

    # 7. 高质量输出保存
    canvas.save(output_path, "JPEG", quality=95, dpi=(dpi, dpi))
    print(f"成功生成打印排版图: {output_path}\n")

# --- 测试运行 ---
if __name__ == "__main__":
    test_image = "C:\\Users\\fire_\\Downloads\\vivo办公套件\\IMG_20260621_0930352.jpg" 
    
    # 模拟生成一张 2048*2048 的正方形测试图
    if not os.path.exists(test_image):
        print("生成 2048x2048 测试图片中...")
        # 模拟一个人像区域，中间画个圆圈
        from PIL import ImageDraw
        img = Image.new("RGB", (2048, 2048), "#3498db")
        draw = ImageDraw.Draw(img)
        draw.ellipse([524, 524, 1524, 1524], fill="#e74c3c") # 模拟人脸位置
        img.save(test_image)

    # 运行排版
    create_photo_layout(test_image, "1inch_cropped_layout.jpg", photo_type="1寸", spacing_mm=2)