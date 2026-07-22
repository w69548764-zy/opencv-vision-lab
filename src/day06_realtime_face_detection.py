from datetime import datetime
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from face_utils import (
    annotate_faces,
    blur_faces,
    detect_faces,
)


WINDOW_NAME = "OpenCV Realtime Face Detection"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "day06"
)


def open_camera(
    camera_index: int = 0
) -> cv2.VideoCapture:
    """打开Windows摄像头，失败时使用通用方式重试。"""

    capture = cv2.VideoCapture(
        camera_index,
        cv2.CAP_DSHOW
    )

    if capture.isOpened():
        return capture

    capture.release()

    return cv2.VideoCapture(
        camera_index
    )


def save_screenshot(
    image: np.ndarray
) -> Path:
    """保存当前人脸处理结果。"""

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )[:-3]

    output_path = (
        OUTPUT_DIRECTORY
        / f"face_{timestamp}.png"
    )

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise RuntimeError("截图保存失败")

    return output_path


def add_information(
    image: np.ndarray,
    mode_name: str,
    face_count: int,
    fps: float,
    mirror_enabled: bool,
    eye_detection_enabled: bool
) -> np.ndarray:
    """添加运行信息和快捷键提示。"""

    result = image.copy()

    cv2.rectangle(
        result,
        (0, 0),
        (result.shape[1], 165),
        (20, 20, 20),
        -1
    )

    information = [
        f"Mode: {mode_name}",
        f"Faces: {face_count} | FPS: {fps:.1f}",
        (
            f"Mirror: {'ON' if mirror_enabled else 'OFF'}"
            f" | Eyes: "
            f"{'ON' if eye_detection_enabled else 'OFF'}"
        ),
        "1 Boxes | 2 Privacy Blur | E Eyes | M Mirror",
        "S Screenshot | Q or ESC Quit",
    ]

    y_position = 28

    for text in information:
        cv2.putText(
            result,
            text,
            (15, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

        y_position += 30

    return result


def main() -> None:
    """启动实时人脸检测。"""

    capture = open_camera(
        camera_index=0
    )

    if not capture.isOpened():
        raise RuntimeError(
            "无法打开摄像头。请检查权限，"
            "并关闭正在占用摄像头的软件。"
        )

    capture.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    capture.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    mode = 1
    mirror_enabled = True
    eye_detection_enabled = False

    fps = 0.0
    previous_time = perf_counter()

    print("第六天实时人脸检测已启动")
    print("1：目标框标注")
    print("2：隐私模糊")
    print("E：开关眼睛检测")
    print("M：开关镜像")
    print("S：保存截图")
    print("Q或Esc：退出")

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

            faces = detect_faces(
                frame,
                scale_factor=1.1,
                min_neighbors=5,
                min_face_size=50
            )

            if mode == 1:
                processed = annotate_faces(
                    frame,
                    faces,
                    detect_eyes_enabled=(
                        eye_detection_enabled
                    )
                )

                mode_name = "Face Boxes"

            else:
                processed = blur_faces(
                    frame,
                    faces,
                    blur_kernel_size=51
                )

                mode_name = "Privacy Blur"

            screenshot_image = processed.copy()

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
                processed,
                mode_name=mode_name,
                face_count=len(faces),
                fps=fps,
                mirror_enabled=mirror_enabled,
                eye_detection_enabled=(
                    eye_detection_enabled
                )
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

            if key == ord("1"):
                mode = 1

            elif key == ord("2"):
                mode = 2

            elif key in (
                ord("e"),
                ord("E"),
            ):
                eye_detection_enabled = (
                    not eye_detection_enabled
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
                        f"截图已保存：{output_path}"
                    )

                except RuntimeError as error:
                    print(str(error))

            if cv2.getWindowProperty(
                WINDOW_NAME,
                cv2.WND_PROP_VISIBLE
            ) < 1:
                break

    finally:
        capture.release()
        cv2.destroyAllWindows()

        print("摄像头已关闭")


if __name__ == "__main__":
    main()