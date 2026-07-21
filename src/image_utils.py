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