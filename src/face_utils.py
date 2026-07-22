from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np


@lru_cache(maxsize=1)
def load_face_classifier() -> cv2.CascadeClassifier:
    """加载OpenCV自带的正脸检测模型。"""

    model_path = (
        Path(cv2.data.haarcascades)
        / "haarcascade_frontalface_default.xml"
    )

    classifier = cv2.CascadeClassifier(
        str(model_path)
    )

    if classifier.empty():
        raise RuntimeError(
            f"无法加载人脸检测模型：{model_path}"
        )

    return classifier


@lru_cache(maxsize=1)
def load_eye_classifier() -> cv2.CascadeClassifier:
    """加载OpenCV自带的眼睛检测模型。"""

    model_path = (
        Path(cv2.data.haarcascades)
        / "haarcascade_eye_tree_eyeglasses.xml"
    )

    classifier = cv2.CascadeClassifier(
        str(model_path)
    )

    if classifier.empty():
        raise RuntimeError(
            f"无法加载眼睛检测模型：{model_path}"
        )

    return classifier


def convert_to_detection_gray(
    image: np.ndarray
) -> np.ndarray:
    """转换为适合目标检测的灰度图。"""

    if image is None or image.size == 0:
        raise ValueError("输入图像不能为空")

    if image.ndim == 2:
        gray = image.copy()

    elif image.ndim == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    elif image.ndim == 3 and image.shape[2] == 4:
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2GRAY
        )

    else:
        raise ValueError("不支持当前图像格式")

    return cv2.equalizeHist(gray)


def ensure_bgr(image: np.ndarray) -> np.ndarray:
    """保证输出图像为BGR三通道。"""

    if image.ndim == 2:
        return cv2.cvtColor(
            image,
            cv2.COLOR_GRAY2BGR
        )

    if image.ndim == 3 and image.shape[2] == 4:
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2BGR
        )

    if image.ndim == 3 and image.shape[2] == 3:
        return image.copy()

    raise ValueError("不支持当前图像格式")


def detect_faces(
    image: np.ndarray,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
    min_face_size: int = 40
) -> list[tuple[int, int, int, int]]:
    """检测图像中的正脸并返回目标框。"""

    if scale_factor <= 1.0:
        raise ValueError("缩放系数必须大于1.0")

    if min_neighbors < 0:
        raise ValueError("相邻候选框数量不能小于0")

    if min_face_size <= 0:
        raise ValueError("最小人脸尺寸必须大于0")

    gray = convert_to_detection_gray(image)
    classifier = load_face_classifier()

    detected_faces = classifier.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(
            min_face_size,
            min_face_size
        ),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    return [
        tuple(int(value) for value in face)
        for face in detected_faces
    ]


def annotate_faces(
    image: np.ndarray,
    faces: list[tuple[int, int, int, int]],
    detect_eyes_enabled: bool = False
) -> np.ndarray:
    """绘制人脸目标框、编号以及可选的眼睛框。"""

    result = ensure_bgr(image)
    gray = convert_to_detection_gray(result)

    eye_classifier = (
        load_eye_classifier()
        if detect_eyes_enabled
        else None
    )

    for index, (x, y, width, height) in enumerate(
        faces,
        start=1
    ):
        cv2.rectangle(
            result,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            2
        )

        label = f"Face {index}"

        cv2.putText(
            result,
            label,
            (x, max(y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        if eye_classifier is None:
            continue

        face_gray = gray[
            y:y + height,
            x:x + width
        ]

        minimum_eye_size = max(
            10,
            width // 10
        )

        eyes = eye_classifier.detectMultiScale(
            face_gray,
            scaleFactor=1.1,
            minNeighbors=8,
            minSize=(
                minimum_eye_size,
                minimum_eye_size
            )
        )

        valid_eyes = [
            eye
            for eye in eyes
            if eye[1] < int(height * 0.65)
        ]

        valid_eyes = sorted(
            valid_eyes,
            key=lambda eye: eye[2] * eye[3],
            reverse=True
        )[:2]

        for eye_x, eye_y, eye_width, eye_height in valid_eyes:
            cv2.rectangle(
                result,
                (x + eye_x, y + eye_y),
                (
                    x + eye_x + eye_width,
                    y + eye_y + eye_height
                ),
                (0, 255, 255),
                2
            )

    return result


def blur_faces(
    image: np.ndarray,
    faces: list[tuple[int, int, int, int]],
    blur_kernel_size: int = 51
) -> np.ndarray:
    """模糊检测到的人脸区域。"""

    if (
        blur_kernel_size <= 0
        or blur_kernel_size % 2 == 0
    ):
        raise ValueError("模糊卷积核必须是正奇数")

    result = ensure_bgr(image)

    for x, y, width, height in faces:
        face_region = result[
            y:y + height,
            x:x + width
        ]

        if face_region.size == 0:
            continue

        blurred_region = cv2.GaussianBlur(
            face_region,
            (
                blur_kernel_size,
                blur_kernel_size
            ),
            0
        )

        result[
            y:y + height,
            x:x + width
        ] = blurred_region

    return result