from pathlib import Path
import sys

import numpy as np
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_DIRECTORY = (
    PROJECT_ROOT
    / "src"
)

sys.path.insert(
    0,
    str(SOURCE_DIRECTORY)
)


from face_utils import (  # noqa: E402
    annotate_faces,
    blur_faces,
    detect_faces,
    load_eye_classifier,
    load_face_classifier,
)


def test_face_classifier_can_be_loaded():
    """正脸检测模型应当能够正常加载。"""

    classifier = load_face_classifier()

    assert not classifier.empty()


def test_eye_classifier_can_be_loaded():
    """眼睛检测模型应当能够正常加载。"""

    classifier = load_eye_classifier()

    assert not classifier.empty()


def test_blank_image_contains_no_faces():
    """纯黑图片中不应该检测到人脸。"""

    image = np.zeros(
        (240, 320, 3),
        dtype=np.uint8
    )

    faces = detect_faces(
        image
    )

    assert faces == []


def test_face_annotation_preserves_image_shape():
    """标注目标框后不应改变图片尺寸和类型。"""

    image = np.zeros(
        (200, 300, 3),
        dtype=np.uint8
    )

    faces = [
        (50, 40, 80, 100)
    ]

    result = annotate_faces(
        image,
        faces
    )

    assert result.shape == image.shape
    assert result.dtype == image.dtype


def test_face_annotation_does_not_modify_input():
    """标注函数不应该直接破坏原始图片。"""

    image = np.zeros(
        (200, 300, 3),
        dtype=np.uint8
    )

    original_image = image.copy()

    annotate_faces(
        image,
        [(50, 40, 80, 100)]
    )

    assert np.array_equal(
        image,
        original_image
    )


def test_face_blur_changes_target_region():
    """人脸模糊应改变目标框内部的像素。"""

    random_generator = (
        np.random.default_rng(42)
    )

    image = random_generator.integers(
        0,
        256,
        size=(200, 300, 3),
        dtype=np.uint8
    )

    faces = [
        (50, 40, 80, 100)
    ]

    result = blur_faces(
        image,
        faces,
        blur_kernel_size=11
    )

    original_face = image[
        40:140,
        50:130
    ]

    blurred_face = result[
        40:140,
        50:130
    ]

    assert result.shape == image.shape

    assert not np.array_equal(
        original_face,
        blurred_face
    )


def test_face_blur_preserves_outside_region():
    """人脸框外部的像素不应该被修改。"""

    random_generator = (
        np.random.default_rng(42)
    )

    image = random_generator.integers(
        0,
        256,
        size=(200, 300, 3),
        dtype=np.uint8
    )

    result = blur_faces(
        image,
        [(50, 40, 80, 100)],
        blur_kernel_size=11
    )

    assert np.array_equal(
        image[0:30, 0:30],
        result[0:30, 0:30]
    )


def test_even_blur_kernel_is_rejected():
    """模糊卷积核不能是偶数。"""

    image = np.zeros(
        (100, 100, 3),
        dtype=np.uint8
    )

    with pytest.raises(
        ValueError,
        match="正奇数"
    ):
        blur_faces(
            image,
            [(10, 10, 40, 40)],
            blur_kernel_size=10
        )


def test_invalid_scale_factor_is_rejected():
    """人脸检测缩放系数必须大于1。"""

    image = np.zeros(
        (100, 100, 3),
        dtype=np.uint8
    )

    with pytest.raises(
        ValueError,
        match="大于1.0"
    ):
        detect_faces(
            image,
            scale_factor=1.0
        )


def test_invalid_minimum_face_size_is_rejected():
    """最小人脸尺寸必须是正数。"""

    image = np.zeros(
        (100, 100, 3),
        dtype=np.uint8
    )

    with pytest.raises(
        ValueError,
        match="大于0"
    ):
        detect_faces(
            image,
            min_face_size=0
        )