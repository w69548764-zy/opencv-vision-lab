# OpenCV Vision Lab

一个使用 Python、OpenCV 和 Streamlit 开发的图像处理学习项目。

项目从基础图像读写开始，逐步实现几何变换、颜色空间转换、二值化、形态学操作和轮廓检测，并将这些功能整合到可交互的网页界面中。用户可以上传图片、调整处理参数、对比处理结果，并下载生成的 PNG 图片。

## 项目功能

### 基础图像处理

- 读取、显示和保存图片
- 获取图片宽度、高度和颜色通道数
- 对输入路径和图片读取结果进行检查

### 几何变换

- 按比例缩放图片
- 中心区域裁剪
- 保持完整画面的任意角度旋转
- 水平、垂直及双向翻转

### 颜色空间转换

- BGR 转灰度图
- BGR 转 HSV
- 分离并查看 H、S、V 三个通道

### 阈值与二值化

- 固定阈值二值化
- Otsu 自动阈值二值化
- 自适应高斯阈值二值化
- 普通和反向二值化

### 形态学处理

- 腐蚀
- 膨胀
- 开运算
- 闭运算
- 自定义形态学卷积核尺寸

### 轮廓检测

- 检测图片中的外部轮廓
- 按轮廓面积过滤小目标和噪点
- 绘制轮廓、外接矩形和面积信息
- 统计有效轮廓数量

### Streamlit 可视化界面

- 支持上传 JPG、JPEG、PNG 和 BMP 图片
- 在侧边栏选择处理功能并实时调整参数
- 并排显示原图和处理结果
- 显示图片尺寸、通道数和处理说明
- 将处理结果下载为 PNG 图片

## 技术栈

- Python
- OpenCV
- NumPy
- Streamlit
- Git 和 GitHub

## 项目结构

```text
opencv-vision-lab/
├── assets/
│   └── input/
│       └── test.jpg
├── outputs/
│   ├── day01/
│   ├── day02/
│   └── day03/
├── src/
│   ├── app.py
│   ├── day01_image_test.py
│   ├── day02_transformations.py
│   ├── day03_threshold_morphology.py
│   └── image_utils.py
├── .gitignore
├── README.md
└── requirements.txt
```

说明：

- `assets/input/` 用于存放实验输入图片。
- `outputs/` 用于保存前三天脚本生成的处理结果；如果该目录已被 `.gitignore` 忽略，它可能不会显示在 GitHub 仓库中。
- `src/image_utils.py` 保存项目复用的图像处理函数。
- `src/day01_image_test.py` 用于测试基础图像读写。
- `src/day02_transformations.py` 用于测试几何变换和颜色空间转换。
- `src/day03_threshold_morphology.py` 用于测试二值化、形态学操作和轮廓检测。
- `src/app.py` 是 Streamlit 可视化应用入口。

## 环境要求

- Python 3.10 或更高版本
- Windows、macOS 或 Linux

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/w69548764-zy/opencv-vision-lab.git
cd opencv-vision-lab
```

### 2. 创建虚拟环境

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS 或 Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 启动可视化应用

在项目根目录执行：

```bash
python -m streamlit run src/app.py
```

启动成功后，浏览器通常会自动打开：

```text
http://localhost:8501
```

如果浏览器没有自动打开，可以复制终端中显示的 `Local URL` 并在浏览器中访问。

停止应用时，在终端按 `Ctrl + C`。

## 运行分阶段实验脚本

运行脚本前，请确保以下测试图片存在：

```text
assets/input/test.jpg
```

### 第一天：基础图像读写

```bash
python src/day01_image_test.py
```

### 第二天：几何变换与颜色空间

```bash
python src/day02_transformations.py
```

### 第三天：阈值、形态学与轮廓检测

```bash
python src/day03_threshold_morphology.py
```

脚本运行后，处理结果分别保存在：

```text
outputs/day01/
outputs/day02/
outputs/day03/
```

部分实验脚本会打开 OpenCV 图片窗口。请先点击任意图片窗口，再按任意键关闭窗口并结束程序。

## 第三天输出结果

`outputs/day03/` 中会生成以下 11 张图片：

```text
01_gray.jpg
02_blurred_gray.jpg
03_fixed_threshold.jpg
04_otsu_threshold.jpg
05_otsu_inverse.jpg
06_adaptive_threshold.jpg
07_eroded.jpg
08_dilated.jpg
09_opened.jpg
10_closed.jpg
11_contours.jpg
```

## 核心处理流程

```text
输入图片
  ↓
读取与格式检查
  ↓
几何变换或颜色空间转换
  ↓
灰度化与高斯滤波
  ↓
阈值二值化
  ↓
形态学处理
  ↓
轮廓检测与面积过滤
  ↓
显示、保存或下载结果
```

## 常见问题

### 1. 提示找不到输入图片

请确认测试图片位于：

```text
assets/input/test.jpg
```

并确保在项目根目录运行脚本。

### 2. 执行 `python src/app.py` 后出现 Streamlit 警告

Streamlit 应用不能按普通 Python 脚本启动，请使用：

```bash
python -m streamlit run src/app.py
```

### 3. 网页中的图片颜色异常

OpenCV 默认使用 BGR 通道顺序，网页显示时需要进行正确的通道处理。项目中的显示函数已经针对 OpenCV 彩色图片设置 `channels="BGR"`。

### 4. 轮廓数量过多

可以在网页侧边栏提高最小轮廓面积占比，或在第三天脚本中增大 `min_contour_area`，以过滤面积较小的噪点。

### 5. 整张图片被识别为一个轮廓

这通常说明前景和背景的黑白方向不合适。可以切换反向二值化选项，再观察检测结果。

### 6. GitHub 推送失败并提示无法连接 443 端口

这通常是当前网络无法连接 GitHub，不代表本地提交丢失。可以先使用以下命令确认提交仍在本地：

```bash
git log -1 --oneline
```

网络恢复后重新执行：

```bash
git push origin main
```

不需要重复执行 `git add` 和 `git commit`。

## 开发进度

- [x] 完成基础图像读写
- [x] 完成几何变换
- [x] 完成颜色空间转换
- [x] 完成固定阈值、Otsu 阈值和自适应阈值处理
- [x] 完成腐蚀、膨胀、开运算和闭运算
- [x] 完成轮廓检测、面积过滤和边界框绘制
- [x] 完成 Streamlit 可视化界面
- [x] 支持上传图片、实时调整参数和下载结果
- [ ] 增加 Canny 边缘检测
- [ ] 增加实时摄像头处理
- [ ] 增加图片处理前后效果展示截图
- [ ] 完善在线部署和项目说明

## 学习目标

本项目主要用于巩固以下知识：

- Python 项目目录与模块化开发
- NumPy 数组和图片数据的关系
- OpenCV 图像读写及 BGR 通道顺序
- 几何变换和颜色空间转换
- 阈值分割及形态学处理
- 轮廓提取、面积计算和目标定位
- Streamlit 交互式应用开发
- Git 版本管理与 GitHub 项目维护

## 后续计划

下一阶段计划加入边缘检测、实时摄像头处理、更多参数控制和项目展示截图，并进一步完善应用部署，使项目能够通过公开网页直接体验。
