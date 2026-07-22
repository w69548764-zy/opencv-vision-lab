from datetime import datetime
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from image_utils import (
    canny_edge_detection,
    sobel_edge_detection,
)


WINDOW_NAME = "OpenCV Realtime Vision Lab"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "day05"
)


def create_color_display(
    image: np.ndarray
) -> np.ndarray:
    """保证传入窗口的图片为BGR三通道。"""

    if image.ndim == 2:
        return cv2.cvtColor(
            image,
            cv2.COLOR_GRAY2BGR
        )

    return image.copy()


def add_information(
    image: np.ndarray,
    mode_name: str,
    fps: float,
    mirror_enabled: bool
) -> np.ndarray:
    """在画面上添加运行信息和操作说明。"""

    result = image.copy()

    mirror_text = (
        "ON"
        if mirror_enabled
        else "OFF"
    )

    information = [
        f"Mode: {mode_name}",
        f"FPS: {fps:.1f}",
        f"Mirror: {mirror_text}",
        "1 Original | 2 Gray | 3 Canny | 4 Sobel",
        "M Mirror | S Screenshot | Q or ESC Quit",
    ]

    y_position = 30

    for text in information:
        cv2.putText(
            result,
            text,
            (15, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (0, 0, 0),
            4,
            cv2.LINE_AA
        )

        cv2.putText(
            result,
            text,
            (15, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

        y_position += 28

    return result


def save_screenshot(
    image: np.ndarray
) -> Path:
    """保存当前处理画面。"""

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        OUTPUT_DIRECTORY
        / f"camera_{timestamp}.png"
    )

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise RuntimeError("摄像头截图保存失败")

    return output_path


def main() -> None:
    """启动摄像头并逐帧进行图像处理。"""

    camera_index = 0

    capture = cv2.VideoCapture(
        camera_index
    )

    if not capture.isOpened():
        raise RuntimeError(
            "无法打开摄像头。请检查摄像头权限，"
            "或确认摄像头没有被其他程序占用。"
        )

    capture.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    capture.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    cv2.createTrackbar(
        "Canny Low",
        WINDOW_NAME,
        50,
        255,
        lambda value: None
    )

    cv2.createTrackbar(
        "Canny High",
        WINDOW_NAME,
        150,
        255,
        lambda value: None
    )

    current_mode = 1
    mirror_enabled = True

    fps = 0.0
    previous_time = perf_counter()

    mode_names = {
        1: "Original",
        2: "Grayscale",
        3: "Canny",
        4: "Sobel",
    }

    print("实时摄像头程序已启动")
    print("按1：原始画面")
    print("按2：灰度画面")
    print("按3：Canny边缘检测")
    print("按4：Sobel梯度检测")
    print("按M：切换镜像")
    print("按S：保存截图")
    print("按Q或Esc：退出")

    try:
        while True:
            success, frame = capture.read()

            if not success:
                print("无法读取摄像头画面")
                break

            if mirror_enabled:
                frame = cv2.flip(
                    frame,
                    1
                )

            if current_mode == 1:
                processed = frame.copy()

            elif current_mode == 2:
                processed = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

            elif current_mode == 3:
                low_threshold = (
                    cv2.getTrackbarPos(
                        "Canny Low",
                        WINDOW_NAME
                    )
                )

                high_threshold = (
                    cv2.getTrackbarPos(
                        "Canny High",
                        WINDOW_NAME
                    )
                )

                low_threshold = min(
                    low_threshold,
                    254
                )

                high_threshold = max(
                    high_threshold,
                    low_threshold + 1
                )

                processed = canny_edge_detection(
                    frame,
                    low_threshold=low_threshold,
                    high_threshold=high_threshold,
                    blur_kernel_size=5
                )

            else:
                processed = sobel_edge_detection(
                    frame,
                    kernel_size=3,
                    blur_kernel_size=5
                )

            screenshot_image = processed.copy()

            display_image = create_color_display(
                processed
            )

            current_time = perf_counter()

            elapsed_time = (
                current_time
                - previous_time
            )

            previous_time = current_time

            if elapsed_time > 0:
                current_fps = 1.0 / elapsed_time

                if fps == 0:
                    fps = current_fps
                else:
                    fps = (
                        0.90 * fps
                        + 0.10 * current_fps
                    )

            display_image = add_information(
                display_image,
                mode_name=mode_names[current_mode],
                fps=fps,
                mirror_enabled=mirror_enabled
            )

            cv2.imshow(
                WINDOW_NAME,
                display_image
            )

            key = cv2.waitKey(1) & 0xFF

            if key in (
                ord("q"),
                ord("Q"),
                27,
            ):
                break

            if key in (
                ord("1"),
                ord("2"),
                ord("3"),
                ord("4"),
            ):
                current_mode = int(
                    chr(key)
                )

            elif key in (
                ord("m"),
                ord("M"),
            ):
                mirror_enabled = (
                    not mirror_enabled
                )

            elif key in (
                ord("s"),
                ord("S"),
            ):
                try:
                    output_path = save_screenshot(
                        screenshot_image
                    )

                    print(
                        "截图已保存："
                        f"{output_path}"
                    )

                except RuntimeError as error:
                    print(str(error))

    finally:
        capture.release()
        cv2.destroyAllWindows()

        print("摄像头已关闭")


if __name__ == "__main__":
    main()