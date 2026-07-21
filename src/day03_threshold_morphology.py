from pathlib import Path

import cv2

from image_utils import (
    adaptive_threshold_image,
    closing_operation,
    convert_to_gray,
    detect_and_draw_contours,
    dilate_image,
    erode_image,
    fixed_threshold,
    load_image,
    opening_operation,
    otsu_threshold,
    save_image,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "assets"
    / "input"
    / "test.jpg"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "day03"


def main():
    """完成阈值、形态学和轮廓检测实验。"""

    # 1. 读取原始图片
    image = load_image(INPUT_PATH)

    height, width = image.shape[:2]

    print("原始图片读取成功！")
    print(f"图片宽度：{width}")
    print(f"图片高度：{height}")

    # 2. 转换为灰度图片
    gray = convert_to_gray(image)

    # 3. 先进行高斯滤波，降低噪声对二值化的影响
    blurred_gray = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # 4. 固定阈值二值化
    binary_fixed = fixed_threshold(
        blurred_gray,
        threshold_value=127
    )

    # 5. Otsu自动阈值二值化
    otsu_value, binary_otsu = otsu_threshold(
        blurred_gray,
        inverse=False
    )

    print(f"Otsu自动计算的阈值：{otsu_value:.2f}")

    # 6. Otsu反向二值化
    # 普通二值化和反向二值化的黑白区域正好相反
    _, binary_inverse = otsu_threshold(
        blurred_gray,
        inverse=True
    )

    # 7. 自适应阈值
    binary_adaptive = adaptive_threshold_image(
        blurred_gray,
        block_size=11,
        constant=2
    )

    # 8. 腐蚀和膨胀
    eroded = erode_image(
        binary_inverse,
        kernel_size=5,
        iterations=1
    )

    dilated = dilate_image(
        binary_inverse,
        kernel_size=5,
        iterations=1
    )

    # 9. 开运算和闭运算
    opened = opening_operation(
        binary_inverse,
        kernel_size=5
    )

    closed = closing_operation(
        binary_inverse,
        kernel_size=5
    )

    # 10. 根据图片大小自动计算最小轮廓面积
    min_contour_area = max(
        100,
        int(width * height * 0.001)
    )

    print(f"最小轮廓面积：{min_contour_area}")

    # 11. 使用闭运算结果检测轮廓
    contour_result, contour_count = (
        detect_and_draw_contours(
            original_image=image,
            binary_image=closed,
            min_area=min_contour_area
        )
    )

    print(f"有效轮廓数量：{contour_count}")

    # 12. 保存所有结果
    results = {
        "01_gray.jpg": gray,
        "02_blurred_gray.jpg": blurred_gray,
        "03_fixed_threshold.jpg": binary_fixed,
        "04_otsu_threshold.jpg": binary_otsu,
        "05_otsu_inverse.jpg": binary_inverse,
        "06_adaptive_threshold.jpg": binary_adaptive,
        "07_eroded.jpg": eroded,
        "08_dilated.jpg": dilated,
        "09_opened.jpg": opened,
        "10_closed.jpg": closed,
        "11_contours.jpg": contour_result,
    }

    for filename, result_image in results.items():
        output_path = OUTPUT_DIR / filename
        save_image(output_path, result_image)
        print(f"已保存：{output_path}")

    print()
    print("第三天任务完成！")
    print("点击任意图片窗口，然后按任意键退出。")

    # 显示重点结果
    cv2.imshow("Original", image)
    cv2.imshow("Fixed Threshold", binary_fixed)
    cv2.imshow("Otsu Inverse", binary_inverse)
    cv2.imshow("Adaptive Threshold", binary_adaptive)
    cv2.imshow("Opening", opened)
    cv2.imshow("Closing", closed)
    cv2.imshow("Contours", contour_result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()