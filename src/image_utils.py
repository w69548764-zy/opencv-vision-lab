from pathlib import Path

import cv2
import numpy as np


def load_image(image_path: Path) -> np.ndarray:
    """读取图片，读取失败时抛出异常。"""

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"图片读取失败，请检查路径：{image_path}"
        )

    return image


def save_image(output_path: Path, image: np.ndarray) -> None:
    """保存图片，并自动创建输出目录。"""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = cv2.imwrite(str(output_path), image)

    if not success:
        raise RuntimeError(f"图片保存失败：{output_path}")


def resize_by_scale(
    image: np.ndarray,
    scale: float
) -> np.ndarray:
    """按照比例缩放图片。"""

    if scale <= 0:
        raise ValueError("缩放比例必须大于0")

    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA
        if scale < 1
        else cv2.INTER_CUBIC
    )


def center_crop(
    image: np.ndarray,
    crop_width: int,
    crop_height: int
) -> np.ndarray:
    """从图片中心裁剪指定大小的区域。"""

    height, width = image.shape[:2]

    crop_width = min(crop_width, width)
    crop_height = min(crop_height, height)

    start_x = (width - crop_width) // 2
    start_y = (height - crop_height) // 2

    end_x = start_x + crop_width
    end_y = start_y + crop_height

    return image[start_y:end_y, start_x:end_x]


def rotate_bound(
    image: np.ndarray,
    angle: float
) -> np.ndarray:
    """旋转图片，并扩大画布，避免内容被截断。"""

    height, width = image.shape[:2]

    center_x = width / 2
    center_y = height / 2

    matrix = cv2.getRotationMatrix2D(
        (center_x, center_y),
        angle,
        1.0
    )

    cosine = abs(matrix[0, 0])
    sine = abs(matrix[0, 1])

    new_width = int(height * sine + width * cosine)
    new_height = int(height * cosine + width * sine)

    matrix[0, 2] += new_width / 2 - center_x
    matrix[1, 2] += new_height / 2 - center_y

    border_value = (
        (255, 255, 255)
        if image.ndim == 3
        else 255
    )

    return cv2.warpAffine(
        image,
        matrix,
        (new_width, new_height),
        borderValue=border_value
    )


def flip_image(
    image: np.ndarray,
    flip_code: int
) -> np.ndarray:
    """
    翻转图片。

    flip_code = 1：水平翻转
    flip_code = 0：垂直翻转
    flip_code = -1：水平和垂直同时翻转
    """

    if flip_code not in (-1, 0, 1):
        raise ValueError("flip_code只能是-1、0或1")

    return cv2.flip(image, flip_code)


def convert_to_gray(image: np.ndarray) -> np.ndarray:
    """将彩色图片转换为灰度图，灰度图则直接复制。"""

    if image.ndim == 2:
        return image.copy()

    if image.ndim == 3 and image.shape[2] == 3:
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    raise ValueError("暂不支持该图片格式")


def fixed_threshold(
    gray_image: np.ndarray,
    threshold_value: int = 127
) -> np.ndarray:
    """使用固定阈值进行二值化。"""

    if not 0 <= threshold_value <= 255:
        raise ValueError("阈值必须在0到255之间")

    _, binary = cv2.threshold(
        gray_image,
        threshold_value,
        255,
        cv2.THRESH_BINARY
    )

    return binary


def otsu_threshold(
    gray_image: np.ndarray,
    inverse: bool = False
) -> tuple[float, np.ndarray]:
    """使用Otsu算法自动选择阈值。"""

    threshold_type = (
        cv2.THRESH_BINARY_INV
        if inverse
        else cv2.THRESH_BINARY
    )

    threshold_value, binary = cv2.threshold(
        gray_image,
        0,
        255,
        threshold_type + cv2.THRESH_OTSU
    )

    return threshold_value, binary


def adaptive_threshold_image(
    gray_image: np.ndarray,
    block_size: int = 11,
    constant: int = 2
) -> np.ndarray:
    """根据像素周围区域计算自适应阈值。"""

    if block_size < 3 or block_size % 2 == 0:
        raise ValueError("block_size必须是大于等于3的奇数")

    return cv2.adaptiveThreshold(
        gray_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        constant
    )


def create_kernel(
    kernel_size: int = 5,
    shape: int = cv2.MORPH_RECT
) -> np.ndarray:
    """创建形态学操作使用的结构元素。"""

    if kernel_size <= 0:
        raise ValueError("卷积核尺寸必须大于0")

    return cv2.getStructuringElement(
        shape,
        (kernel_size, kernel_size)
    )


def erode_image(
    binary_image: np.ndarray,
    kernel_size: int = 5,
    iterations: int = 1
) -> np.ndarray:
    """腐蚀白色区域。"""

    kernel = create_kernel(kernel_size)

    return cv2.erode(
        binary_image,
        kernel,
        iterations=iterations
    )


def dilate_image(
    binary_image: np.ndarray,
    kernel_size: int = 5,
    iterations: int = 1
) -> np.ndarray:
    """膨胀白色区域。"""

    kernel = create_kernel(kernel_size)

    return cv2.dilate(
        binary_image,
        kernel,
        iterations=iterations
    )


def opening_operation(
    binary_image: np.ndarray,
    kernel_size: int = 5
) -> np.ndarray:
    """开运算：先腐蚀后膨胀，去除白色小噪点。"""

    kernel = create_kernel(kernel_size)

    return cv2.morphologyEx(
        binary_image,
        cv2.MORPH_OPEN,
        kernel
    )


def closing_operation(
    binary_image: np.ndarray,
    kernel_size: int = 5
) -> np.ndarray:
    """闭运算：先膨胀后腐蚀，填补白色区域中的小孔。"""

    kernel = create_kernel(kernel_size)

    return cv2.morphologyEx(
        binary_image,
        cv2.MORPH_CLOSE,
        kernel
    )


def detect_and_draw_contours(
    original_image: np.ndarray,
    binary_image: np.ndarray,
    min_area: float = 100.0
) -> tuple[np.ndarray, int]:
    """检测轮廓，过滤小轮廓并绘制边界框。"""

    contours, _ = cv2.findContours(
        binary_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    result = original_image.copy()
    valid_contour_count = 0

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < min_area:
            continue

        valid_contour_count += 1

        # 获取轮廓的外接矩形
        x, y, width, height = cv2.boundingRect(contour)

        # 绘制绿色轮廓
        cv2.drawContours(
            result,
            [contour],
            -1,
            (0, 255, 0),
            2
        )

        # 绘制蓝色矩形框
        cv2.rectangle(
            result,
            (x, y),
            (x + width, y + height),
            (255, 0, 0),
            2
        )

        # 显示轮廓面积
        cv2.putText(
            result,
            f"Area: {int(area)}",
            (x, max(y - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA
        )

    return result, valid_contour_count