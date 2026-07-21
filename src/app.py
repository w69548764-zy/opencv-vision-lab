import cv2
import numpy as np
import streamlit as st

from image_utils import (
    adaptive_threshold_image,
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
)


st.set_page_config(
    page_title="OpenCV图像处理实验室",
    page_icon="🖼️",
    layout="wide",
)


def decode_uploaded_image(file_bytes: bytes) -> np.ndarray:
    """把网页上传的字节数据解码为OpenCV图片。"""

    image_array = np.frombuffer(
        file_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError("图片解码失败，请更换图片后重试")

    return image


def encode_png(image: np.ndarray) -> bytes:
    """把OpenCV图片编码为可下载的PNG数据。"""

    success, encoded_image = cv2.imencode(
        ".png",
        image
    )

    if not success:
        raise RuntimeError("处理结果编码失败")

    return encoded_image.tobytes()


def show_image(
    image: np.ndarray,
    caption: str
) -> None:
    """按照OpenCV图片格式显示图片。"""

    if image.ndim == 3:
        st.image(
            image,
            caption=caption,
            channels="BGR",
            width="stretch"
        )
    else:
        st.image(
            image,
            caption=caption,
            clamp=True,
            width="stretch"
        )


def create_binary_image(
    image: np.ndarray,
    method: str,
    threshold_value: int,
    inverse: bool
) -> tuple[np.ndarray, str]:
    """根据界面参数生成二值图。"""

    gray = convert_to_gray(image)

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    if method == "固定阈值":
        binary = fixed_threshold(
            blurred,
            threshold_value=threshold_value
        )

        if inverse:
            binary = cv2.bitwise_not(binary)

        description = f"固定阈值：{threshold_value}"

    elif method == "Otsu自动阈值":
        otsu_value, binary = otsu_threshold(
            blurred,
            inverse=inverse
        )

        description = (
            f"Otsu自动阈值：{otsu_value:.2f}"
        )

    else:
        binary = adaptive_threshold_image(
            blurred,
            block_size=11,
            constant=2
        )

        if inverse:
            binary = cv2.bitwise_not(binary)

        description = "自适应高斯阈值"

    if inverse:
        description += "，反向二值化"

    return binary, description


st.title("OpenCV 图像处理实验室")

st.write(
    "上传一张图片，然后在左侧选择处理功能和参数。"
)

st.caption(
    "项目功能：几何变换、颜色转换、二值化、"
    "形态学操作和轮廓检测"
)

uploaded_file = st.file_uploader(
    "上传图片",
    type=["jpg", "jpeg", "png", "bmp"]
)

if uploaded_file is None:
    st.info("请先上传一张 JPG、PNG 或 BMP 图片。")
    st.stop()

try:
    image = decode_uploaded_image(
        uploaded_file.getvalue()
    )
except ValueError as error:
    st.error(str(error))
    st.stop()

height, width = image.shape[:2]

metric_col1, metric_col2, metric_col3 = st.columns(3)

metric_col1.metric("原图宽度", f"{width} px")
metric_col2.metric("原图高度", f"{height} px")
metric_col3.metric(
    "颜色通道",
    image.shape[2] if image.ndim == 3 else 1
)

st.sidebar.header("图像处理参数")

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
        "形态学操作",
        "轮廓检测",
    ]
)

result = image.copy()
result_description = "未进行处理"

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

result_height, result_width = result.shape[:2]

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

st.success(result_description)

result_col1, result_col2 = st.columns(2)

result_col1.metric(
    "结果宽度",
    f"{result_width} px"
)

result_col2.metric(
    "结果高度",
    f"{result_height} px"
)

try:
    download_data = encode_png(result)

    st.download_button(
        label="下载处理结果",
        data=download_data,
        file_name="opencv_result.png",
        mime="image/png"
    )
except RuntimeError as error:
    st.error(str(error))