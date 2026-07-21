from pathlib import Path

import cv2

from image_utils import (
    center_crop,
    flip_image,
    load_image,
    resize_by_scale,
    rotate_bound,
    save_image,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "assets"
    / "input"
    / "test.jpg"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "day02"


def main():
    """完成第二天的图片几何变换与颜色空间转换。"""

    # 1. 读取原始图片
    image = load_image(INPUT_PATH)

    height, width = image.shape[:2]

    print("原始图片读取成功！")
    print(f"原始宽度：{width}")
    print(f"原始高度：{height}")

    # 2. 缩小为原图的50%
    resized_half = resize_by_scale(
        image,
        scale=0.5
    )

    # 3. 从图片中心裁剪60%的区域
    crop_width = int(width * 0.6)
    crop_height = int(height * 0.6)

    cropped = center_crop(
        image,
        crop_width=crop_width,
        crop_height=crop_height
    )

    # 4. 顺时针旋转45度
    # OpenCV中负数表示顺时针
    rotated = rotate_bound(
        image,
        angle=-45
    )

    # 5. 水平翻转
    flipped_horizontal = flip_image(
        image,
        flip_code=1
    )

    # 6. 垂直翻转
    flipped_vertical = flip_image(
        image,
        flip_code=0
    )

    # 7. 转换为灰度图
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # 8. 从BGR转换为HSV
    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # HSV图像依次包含色相、饱和度和亮度
    hue, saturation, value = cv2.split(hsv)

    # 9. 保存全部处理结果
    results = {
        "01_resized_half.jpg": resized_half,
        "02_center_crop.jpg": cropped,
        "03_rotated_45.jpg": rotated,
        "04_flip_horizontal.jpg": flipped_horizontal,
        "05_flip_vertical.jpg": flipped_vertical,
        "06_gray.jpg": gray,
        "07_hue.jpg": hue,
        "08_saturation.jpg": saturation,
        "09_value.jpg": value,
    }

    for filename, result_image in results.items():
        output_path = OUTPUT_DIR / filename
        save_image(output_path, result_image)
        print(f"已保存：{output_path}")

    print()
    print("第二天图像处理任务完成！")
    print("点击任意图片窗口，然后按任意键退出。")

    # 只显示部分结果，避免同时出现太多窗口
    cv2.imshow("Original", image)
    cv2.imshow("Center Crop", cropped)
    cv2.imshow("Rotated 45 Degrees", rotated)
    cv2.imshow("Horizontal Flip", flipped_horizontal)
    cv2.imshow("HSV Saturation", saturation)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()