# OpenCV Vision Lab

基于 Python、OpenCV 和 Streamlit 开发的交互式计算机视觉实验平台，支持图片上传、浏览器摄像头拍照、本地实时摄像头处理和多种经典计算机视觉算法。

## 项目简介

本项目用于学习和实践 OpenCV 图像处理技术。用户可以通过网页选择处理功能并实时调整参数，对比原图与处理结果。

除网页功能外，项目还提供本地实时摄像头程序，支持边缘检测、人脸检测、眼睛检测、人脸隐私模糊、FPS显示和截图保存。

## 在线体验

部署完成后在这里填写在线地址。

> 在线版支持浏览器摄像头拍照，但不能直接访问用户电脑上的 `VideoCapture(0)`。

## 项目展示

### 交互式处理页面

![项目首页](docs/images/home.png)

### 边缘检测

![边缘检测](docs/images/edge-detection.png)

### 人脸检测

![人脸检测](docs/images/face-detection.png)

### 实时摄像头处理

![实时人脸检测](docs/images/realtime-face.png)

## 核心功能

- 图像上传和浏览器摄像头拍照
- 图片尺寸、通道等基本信息展示
- 图像缩放、裁剪、旋转和翻转
- 灰度、RGB和HSV颜色空间转换
- 全局阈值、自适应阈值和Otsu二值化
- 腐蚀、膨胀、开运算和闭运算
- 轮廓提取、面积过滤和目标框绘制
- Canny边缘检测和参数调节
- Sobel水平与垂直梯度计算
- 本地摄像头实时边缘检测
- Haar Cascade人脸与眼睛检测
- 人脸目标框、编号和数量统计
- 人脸隐私模糊
- 实时FPS显示、模式切换和截图保存
- PNG处理结果下载
- Pytest核心功能测试

## 技术栈

- Python
- OpenCV
- NumPy
- Streamlit
- Pytest
- Git
- GitHub

## 项目结构

```text
opencv-vision-lab/
├── .streamlit/
│   └── config.toml
├── docs/
│   └── images/
├── outputs/
├── src/
│   ├── app.py
│   ├── face_utils.py
│   ├── day05_realtime_camera.py
│   └── day06_realtime_face_detection.py
├── tests/
│   └── test_face_utils.py
├── .gitignore
├── packages.txt
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## 快速开始

### 1. 克隆项目

```bash
git clone 你的GitHub仓库地址
cd opencv-vision-lab
```

### 2. 创建虚拟环境

Windows：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS或Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. 启动网页

```bash
python -m streamlit run src/app.py
```

### 5. 启动本地实时人脸检测

```bash
python src/day06_realtime_face_detection.py
```

## 实时人脸检测快捷键

| 按键 | 功能 |
|---|---|
| `1` | 显示人脸目标框 |
| `2` | 开启人脸隐私模糊 |
| `E` | 开关眼睛检测 |
| `M` | 开关镜像 |
| `S` | 保存当前截图 |
| `Q`或`Esc` | 退出程序 |

## 自动测试

安装开发依赖：

```bash
python -m pip install -r requirements-dev.txt
```

运行测试：

```bash
python -m pytest -v
```

## 技术说明

### 人脸检测

项目使用OpenCV Haar Cascade分类器进行人脸检测。检测结果格式为：

```text
(x, y, width, height)
```

其中 `(x, y)` 表示目标框左上角坐标。

### 主要参数

- `scaleFactor`：控制图像金字塔每层的缩放比例。
- `minNeighbors`：控制候选目标框需要满足的邻居数量。
- `minSize`：忽略尺寸过小的目标区域。

### 人脸检测与人脸识别

本项目实现的是人脸检测，即判断图像中的人脸位置，没有判断具体人物身份，因此不能称为人脸识别系统。

## 使用限制

- Haar Cascade更适合正脸、光线充足、遮挡较少的场景。
- 侧脸、低光照和大角度人脸可能出现漏检。
- 浏览器摄像头拍照功能可以在线使用。
- `VideoCapture(0)`实时程序只能在本地电脑运行。
- 请勿将包含他人隐私的截图提交到公开仓库。

## 后续改进方向

- 使用深度学习模型提升人脸检测准确率
- 增加视频文件上传和逐帧处理
- 增加处理参数预设与历史记录
- 增加图像直方图和统计分析
- 使用GitHub Actions执行自动测试

## 作者

宇

本项目为计算机视觉学习与实践项目。