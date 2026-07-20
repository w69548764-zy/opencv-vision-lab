from pathlib import Path

import cv2


# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 设置输入和输出路径
INPUT_PATH = PROJECT_ROOT / "assets" / "input" / "test.jpg"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# 如果输出目录不存在，就自动创建
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """读取图片并完成基础图像处理。"""

    # 读取彩色图片
    image = cv2.imread(str(INPUT_PATH))

    # 图片读取失败时，image的值为None
    if image is None:
        raise FileNotFoundError(
            f"图片读取失败，请检查图片路径：{INPUT_PATH}"
        )

    # image.shape依次表示高度、宽度、颜色通道数
    height, width, channels = image.shape

    print("图片读取成功！")
    print(f"宽度：{width} 像素")
    print(f"高度：{height} 像素")
    print(f"颜色通道：{channels}")

    # 彩色图转换为灰度图
    gray_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # 使用高斯滤波减少噪声
    blurred_image = cv2.GaussianBlur(
        gray_image,
        (5, 5),
        0
    )

    # Canny边缘检测
    edge_image = cv2.Canny(
        blurred_image,
        80,
        160
    )

    # 保存处理后的图片
    cv2.imwrite(
        str(OUTPUT_DIR / "gray.jpg"),
        gray_image
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "blur.jpg"),
        blurred_image
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "edge.jpg"),
        edge_image
    )

    print("处理完成，结果已经保存到 outputs 文件夹。")
    print("在图片窗口中按任意键退出。")

    # 显示处理结果
    cv2.imshow("Original Image", image)
    cv2.imshow("Gray Image", gray_image)
    cv2.imshow("Blurred Image", blurred_image)
    cv2.imshow("Edge Image", edge_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()