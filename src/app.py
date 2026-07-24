import cv2
import numpy as np
import streamlit as st

from image_utils import (
    adaptive_threshold_image,
    canny_edge_detection,
    center_crop,
    closing_operation,
    convert_to_gray,
    detect_and_draw_contours,
    dilate_image,
    erode_image,
    fixed_threshold,
    flip_image,
    opening_operation,
    otsu_threshold,
    resize_by_scale,
    rotate_bound,
    sobel_edge_detection,
)

from face_utils import (
    annotate_faces,
    blur_faces,
    detect_faces,
)


APP_TITLE = "OpenCV Vision Lab"

DOWNLOAD_FILENAMES = {
    "查看原图": "original_image.png",
    "图片缩放": "resized_image.png",
    "中心裁剪": "cropped_image.png",
    "图片旋转": "rotated_image.png",
    "图片翻转": "flipped_image.png",
    "灰度转换": "grayscale_image.png",
    "HSV通道": "hsv_channel.png",
    "二值化": "binary_image.png",
    "边缘检测": "edge_detection.png",
    "形态学操作": "morphology_result.png",
    "轮廓检测": "contour_detection.png",
    "人脸检测": "face_detection.png",
}

OPERATION_GUIDES = {
    "查看原图": "保持原始像素不变，适合用于处理前后的基准对比。",
    "图片缩放": "按照比例同时改变宽度和高度，用于观察插值缩放效果。",
    "中心裁剪": "从图像中心保留指定比例的区域，不改变保留区域的像素。",
    "图片旋转": "旋转后自动扩展画布，尽量避免原图边缘被裁掉。",
    "图片翻转": "支持水平、垂直以及双方向翻转。",
    "灰度转换": "将 BGR 三通道图像转换为单通道灰度图。",
    "HSV通道": "分别查看色相、饱和度和亮度信息，便于颜色分析。",
    "二值化": "将灰度图分成黑白两类，支持固定、Otsu 和自适应阈值。",
    "边缘检测": "Canny 适合提取清晰轮廓，Sobel 用于观察水平与垂直梯度。",
    "形态学操作": "腐蚀、膨胀、开运算和闭运算可用于去噪、连接或填补区域。",
    "轮廓检测": "先生成二值图，再通过面积阈值过滤过小的轮廓。",
    "人脸检测": "使用 Haar Cascade 定位正脸，可绘制目标框或进行隐私模糊。",
}


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_styles() -> None:
    """增加少量页面样式，保持桌面端和移动端都可读。"""

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 0.8rem;
            padding: 0.8rem 1rem;
            background: rgba(128, 128, 128, 0.05);
        }
        [data-testid="stImage"] img {
            border-radius: 0.7rem;
        }
        .app-kicker {
            color: #00bfa6;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 0.2rem;
        }
        .app-subtitle {
            color: rgba(128, 128, 128, 0.95);
            font-size: 1.05rem;
            margin-top: -0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def decode_uploaded_image(file_bytes: bytes) -> np.ndarray:
    """把网页上传的字节数据解码为OpenCV图片。"""

    if not file_bytes:
        raise ValueError("图片内容为空，请重新选择图片")

    image_array = np.frombuffer(
        file_bytes,
        dtype=np.uint8,
    )

    try:
        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )
    except cv2.error as error:
        raise ValueError(
            "图片格式无法识别，请更换图片后重试"
        ) from error

    if image is None:
        raise ValueError("图片解码失败，请更换图片后重试")

    if image.size == 0:
        raise ValueError("图片尺寸无效，请更换图片后重试")

    return image


def encode_png(image: np.ndarray) -> bytes:
    """把OpenCV图片编码为可下载的PNG数据。"""

    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("当前没有可供下载的有效处理结果")

    if image.ndim not in (2, 3):
        raise ValueError("处理结果的图像维度无效")

    image = np.ascontiguousarray(image)

    try:
        success, encoded_image = cv2.imencode(
            ".png",
            image,
        )
    except cv2.error as error:
        raise RuntimeError("处理结果编码失败") from error

    if not success:
        raise RuntimeError("处理结果编码失败")

    return encoded_image.tobytes()


def show_image(
    image: np.ndarray,
    caption: str,
) -> None:
    """按照OpenCV图片格式显示图片。"""

    if image.ndim == 3:
        st.image(
            image,
            caption=caption,
            channels="BGR",
            width="stretch",
        )
    else:
        st.image(
            image,
            caption=caption,
            clamp=True,
            width="stretch",
        )


def create_binary_image(
    image: np.ndarray,
    method: str,
    threshold_value: int,
    inverse: bool,
) -> tuple[np.ndarray, str]:
    """根据界面参数生成二值图。"""

    gray = convert_to_gray(image)

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0,
    )

    if method == "固定阈值":
        binary = fixed_threshold(
            blurred,
            threshold_value=threshold_value,
        )

        if inverse:
            binary = cv2.bitwise_not(binary)

        description = f"固定阈值：{threshold_value}"

    elif method == "Otsu自动阈值":
        otsu_value, binary = otsu_threshold(
            blurred,
            inverse=inverse,
        )

        description = (
            f"Otsu自动阈值：{otsu_value:.2f}"
        )

    else:
        binary = adaptive_threshold_image(
            blurred,
            block_size=11,
            constant=2,
        )

        if inverse:
            binary = cv2.bitwise_not(binary)

        description = "自适应高斯阈值"

    if inverse:
        description += "，反向二值化"

    return binary, description


def format_file_size(byte_count: int) -> str:
    """把字节数转换为适合页面展示的文件大小。"""

    if byte_count < 1024:
        return f"{byte_count} B"

    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"

    return f"{byte_count / (1024 * 1024):.1f} MB"


inject_custom_styles()

st.markdown(
    '<div class="app-kicker">INTERACTIVE COMPUTER VISION</div>',
    unsafe_allow_html=True,
)

st.title("🔬 OpenCV Vision Lab")

st.caption(
    "基于 OpenCV 与 Streamlit 的交互式计算机视觉实验平台"
)

st.markdown(
    """
    本平台集成了图像基础处理、几何变换、颜色空间转换、
    阈值分割、形态学操作、轮廓检测、边缘检测和人脸检测等功能。

    你可以上传本地图片，也可以使用浏览器摄像头拍照，
    并通过侧边栏实时调整算法参数、观察处理结果。
    """,
)

st.divider()

st.sidebar.header("🎛️ 图像处理控制台")

st.sidebar.info(
    "选择图片来源和处理功能，"
    "然后调整参数观察图像变化。",
)

input_method = st.radio(
    "选择图片来源",
    [
        "上传本地图片",
        "摄像头拍照",
    ],
    horizontal=True,
)

image_source = None

if input_method == "上传本地图片":
    image_source = st.file_uploader(
        "上传图片",
        type=["jpg", "jpeg", "png", "bmp"],
        help="支持 JPG、JPEG、PNG 和 BMP，建议文件不超过 20 MB。",
    )

    empty_message = (
        "请先上传一张 JPG、PNG 或 BMP 图片。"
    )

else:
    image_source = st.camera_input(
        "使用摄像头拍摄一张图片",
        resolution="720p",
        help="浏览器会请求摄像头权限；云端部署时也可以使用。",
    )

    empty_message = "请先允许摄像头权限并拍摄图片。"

if image_source is None:
    st.info(empty_message)
    st.stop()

try:
    source_bytes = image_source.getvalue()
    image = decode_uploaded_image(source_bytes)
except ValueError as error:
    st.error(str(error))
    st.stop()

height, width = image.shape[:2]

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

metric_col1.metric("原图宽度", f"{width} px")
metric_col2.metric("原图高度", f"{height} px")
metric_col3.metric(
    "颜色通道",
    image.shape[2] if image.ndim == 3 else 1,
)
metric_col4.metric("文件大小", format_file_size(len(source_bytes)))

st.sidebar.divider()
st.sidebar.subheader("图像处理参数")

operation = st.sidebar.selectbox(
    "选择处理功能",
    [
        "查看原图",
        "图片缩放",
        "中心裁剪",
        "图片旋转",
        "图片翻转",
        "灰度转换",
        "HSV通道",
        "二值化",
        "边缘检测",
        "形态学操作",
        "轮廓检测",
        "人脸检测",
    ],
)

st.sidebar.caption(
    "所有处理均在当前会话中完成，页面不会主动保存你上传的图片。"
)

result = image.copy()
result_description = "未进行处理"
result_message_kind = "success"

if operation == "查看原图":
    result_description = "原始图片"

elif operation == "图片缩放":
    scale = st.sidebar.slider(
        "缩放比例",
        min_value=0.1,
        max_value=2.0,
        value=0.5,
        step=0.1
    )

    result = resize_by_scale(
        image,
        scale=scale
    )

    result_description = f"缩放比例：{scale:.1f}"

elif operation == "中心裁剪":
    crop_width_percent = st.sidebar.slider(
        "保留宽度",
        min_value=10,
        max_value=100,
        value=60,
        step=5,
        format="%d%%"
    )

    crop_height_percent = st.sidebar.slider(
        "保留高度",
        min_value=10,
        max_value=100,
        value=60,
        step=5,
        format="%d%%"
    )

    crop_width = int(
        width * crop_width_percent / 100
    )

    crop_height = int(
        height * crop_height_percent / 100
    )

    result = center_crop(
        image,
        crop_width=crop_width,
        crop_height=crop_height
    )

    result_description = (
        f"中心裁剪：宽度{crop_width_percent}%，"
        f"高度{crop_height_percent}%"
    )

elif operation == "图片旋转":
    angle = st.sidebar.slider(
        "旋转角度",
        min_value=-180,
        max_value=180,
        value=-45,
        step=5
    )

    result = rotate_bound(
        image,
        angle=angle
    )

    direction = (
        "顺时针"
        if angle < 0
        else "逆时针"
    )

    if angle == 0:
        direction = "不旋转"

    result_description = (
        f"{direction}旋转：{abs(angle)}°"
    )

elif operation == "人脸检测":
    face_mode = st.sidebar.radio(
        "人脸处理方式",
        [
            "目标框标注",
            "隐私模糊",
        ]
    )

    scale_factor = st.sidebar.slider(
        "多尺度缩放系数",
        min_value=1.05,
        max_value=1.50,
        value=1.10,
        step=0.05
    )

    min_neighbors = st.sidebar.slider(
        "最小相邻候选框",
        min_value=1,
        max_value=12,
        value=5
    )

    min_face_size = st.sidebar.slider(
        "最小人脸尺寸",
        min_value=20,
        max_value=200,
        value=40,
        step=10
    )

    faces = detect_faces(
        image,
        scale_factor=scale_factor,
        min_neighbors=min_neighbors,
        min_face_size=min_face_size
    )

    if face_mode == "目标框标注":
        detect_eyes_enabled = st.sidebar.checkbox(
            "同时检测眼睛",
            value=False
        )

        result = annotate_faces(
            image,
            faces,
            detect_eyes_enabled=detect_eyes_enabled
        )

        result_description = (
            f"人脸目标框标注；"
            f"检测数量：{len(faces)}；"
            f"眼睛检测："
            f"{'开启' if detect_eyes_enabled else '关闭'}"
        )

    else:
        blur_kernel_size = st.sidebar.slider(
            "人脸模糊强度",
            min_value=11,
            max_value=151,
            value=51,
            step=10
        )

        result = blur_faces(
            image,
            faces,
            blur_kernel_size=blur_kernel_size
        )

        result_description = (
            f"人脸隐私模糊；"
            f"检测数量：{len(faces)}；"
            f"模糊卷积核："
            f"{blur_kernel_size}×{blur_kernel_size}"
        )

    st.sidebar.metric(
        "检测到的人脸",
        len(faces)
    )

    if not faces:
        result_message_kind = "warning"

elif operation == "图片翻转":
    flip_mode = st.sidebar.radio(
        "翻转方向",
        [
            "水平翻转",
            "垂直翻转",
            "水平和垂直同时翻转",
        ]
    )

    flip_code_map = {
        "水平翻转": 1,
        "垂直翻转": 0,
        "水平和垂直同时翻转": -1,
    }

    result = flip_image(
        image,
        flip_code=flip_code_map[flip_mode]
    )

    result_description = flip_mode

elif operation == "灰度转换":
    result = convert_to_gray(image)
    result_description = "BGR彩色图转换为灰度图"

elif operation == "HSV通道":
    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    hue, saturation, value = cv2.split(hsv)

    channel_name = st.sidebar.radio(
        "选择HSV通道",
        [
            "H：色相",
            "S：饱和度",
            "V：亮度",
        ]
    )

    channel_map = {
        "H：色相": hue,
        "S：饱和度": saturation,
        "V：亮度": value,
    }

    result = channel_map[channel_name]
    result_description = channel_name

elif operation == "二值化":
    threshold_method = st.sidebar.radio(
        "阈值方法",
        [
            "固定阈值",
            "Otsu自动阈值",
            "自适应阈值",
        ]
    )

    threshold_value = 127

    if threshold_method == "固定阈值":
        threshold_value = st.sidebar.slider(
            "阈值",
            min_value=0,
            max_value=255,
            value=127
        )

    inverse = st.sidebar.checkbox(
        "反向二值化",
        value=False
    )

    result, result_description = (
        create_binary_image(
            image=image,
            method=threshold_method,
            threshold_value=threshold_value,
            inverse=inverse
        )
    )


elif operation == "边缘检测":
    edge_method = st.sidebar.radio(
        "边缘检测方法",
        [
            "Canny边缘检测",
            "Sobel梯度检测",
        ]
    )

    blur_kernel_size = st.sidebar.slider(
        "高斯模糊卷积核",
        min_value=3,
        max_value=15,
        value=5,
        step=2
    )

    if edge_method == "Canny边缘检测":
        low_threshold = st.sidebar.slider(
            "低阈值",
            min_value=0,
            max_value=254,
            value=50
        )

        high_threshold = st.sidebar.slider(
            "高阈值",
            min_value=low_threshold + 1,
            max_value=255,
            value=max(150, low_threshold + 1)
        )

        result = canny_edge_detection(
            image,
            low_threshold=low_threshold,
            high_threshold=high_threshold,
            blur_kernel_size=blur_kernel_size
        )

        edge_pixel_count = int(
            np.count_nonzero(result)
        )

        result_description = (
            f"Canny边缘检测；"
            f"低阈值：{low_threshold}；"
            f"高阈值：{high_threshold}；"
            f"边缘像素：{edge_pixel_count}"
        )

    else:
        sobel_kernel_size = st.sidebar.select_slider(
            "Sobel卷积核",
            options=[1, 3, 5, 7],
            value=3
        )

        result = sobel_edge_detection(
            image,
            kernel_size=sobel_kernel_size,
            blur_kernel_size=blur_kernel_size
        )

        result_description = (
            f"Sobel梯度检测；"
            f"Sobel卷积核："
            f"{sobel_kernel_size}×"
            f"{sobel_kernel_size}；"
            f"模糊卷积核："
            f"{blur_kernel_size}×"
            f"{blur_kernel_size}"
        )

elif operation == "形态学操作":
    inverse = st.sidebar.checkbox(
        "反向二值化",
        value=True,
        key="morphology_inverse"
    )

    binary, binary_description = (
        create_binary_image(
            image=image,
            method="Otsu自动阈值",
            threshold_value=127,
            inverse=inverse
        )
    )

    morphology_method = st.sidebar.radio(
        "选择形态学操作",
        [
            "原始二值图",
            "腐蚀",
            "膨胀",
            "开运算",
            "闭运算",
        ]
    )

    kernel_size = st.sidebar.slider(
        "卷积核尺寸",
        min_value=3,
        max_value=15,
        value=5,
        step=2
    )

    if morphology_method == "原始二值图":
        result = binary

    elif morphology_method == "腐蚀":
        result = erode_image(
            binary,
            kernel_size=kernel_size
        )

    elif morphology_method == "膨胀":
        result = dilate_image(
            binary,
            kernel_size=kernel_size
        )

    elif morphology_method == "开运算":
        result = opening_operation(
            binary,
            kernel_size=kernel_size
        )

    else:
        result = closing_operation(
            binary,
            kernel_size=kernel_size
        )

    result_description = (
        f"{morphology_method}，"
        f"卷积核：{kernel_size}×{kernel_size}；"
        f"{binary_description}"
    )

elif operation == "轮廓检测":
    inverse = st.sidebar.checkbox(
        "反向二值化",
        value=True,
        key="contour_inverse"
    )

    close_kernel_size = st.sidebar.slider(
        "闭运算卷积核",
        min_value=3,
        max_value=15,
        value=5,
        step=2
    )

    min_area_percent = st.sidebar.slider(
        "最小轮廓面积占比",
        min_value=0.01,
        max_value=5.0,
        value=0.10,
        step=0.01,
        format="%.2f%%"
    )

    binary, binary_description = (
        create_binary_image(
            image=image,
            method="Otsu自动阈值",
            threshold_value=127,
            inverse=inverse
        )
    )

    closed = closing_operation(
        binary,
        kernel_size=close_kernel_size
    )

    min_area = max(
        1,
        int(
            width
            * height
            * min_area_percent
            / 100
        )
    )

    result, contour_count = (
        detect_and_draw_contours(
            original_image=image,
            binary_image=closed,
            min_area=min_area
        )
    )

    result_description = (
        f"检测到{contour_count}个有效轮廓；"
        f"最小面积：{min_area}像素；"
        f"{binary_description}"
    )

    if contour_count == 0:
        result_message_kind = "warning"

result_height, result_width = result.shape[:2]
result_channels = result.shape[2] if result.ndim == 3 else 1

st.subheader("处理结果")

left_column, right_column = st.columns(2)

with left_column:
    show_image(
        image,
        "原始图片"
    )

with right_column:
    show_image(
        result,
        operation
    )

if result_message_kind == "warning":
    st.warning(
        f"{result_description}。当前参数下未检测到目标，"
        "可以尝试降低过滤条件或更换图片。"
    )
else:
    st.success(result_description)

result_col1, result_col2, result_col3 = st.columns(3)

result_col1.metric(
    "结果宽度",
    f"{result_width} px"
)

result_col2.metric(
    "结果高度",
    f"{result_height} px"
)

result_col3.metric(
    "结果通道",
    result_channels
)

with st.expander("查看本功能说明"):
    st.write(OPERATION_GUIDES[operation])
    st.caption(f"本次处理：{result_description}")

try:
    download_data = encode_png(result)

    st.download_button(
        label="⬇️ 下载处理结果",
        data=download_data,
        file_name=DOWNLOAD_FILENAMES[operation],
        mime="image/png",
        width="stretch",
    )
except (ValueError, RuntimeError) as error:
    st.error(str(error))

st.divider()
st.caption(
    "OpenCV Vision Lab · 图像仅用于当前页面处理，请勿上传未经授权的隐私照片。"
)