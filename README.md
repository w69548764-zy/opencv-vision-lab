# OpenCV Vision Lab

一个基于 Python、OpenCV 和 Streamlit 开发的图像处理与分析项目。

## 项目介绍

本项目用于学习计算机视觉的基础图像处理方法。目前已经实现图片读取、灰度化、高斯滤波和 Canny 边缘检测。

后续将增加阈值处理、形态学操作、参数调节和交互式可视化界面。

## 当前功能

- 读取本地图片
- 输出图片尺寸和通道信息
- 彩色图片灰度化
- 高斯滤波降噪
- Canny 边缘检测
- 保存并显示处理结果
- 图片读取失败检测

## 项目结构

```text
opencv-vision-lab/
├── assets/
│   └── input/                 # 测试图片
├── outputs/                   # 程序输出结果
├── src/
│   └── day01_image_test.py    # 第一天图像处理程序
├── .gitignore
├── README.md
└── requirements.txt
```

## 环境要求

- Python 3.12
- OpenCV
- NumPy
- Pillow
- Matplotlib
- Streamlit

## 安装依赖

首先创建并激活虚拟环境：

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
```

然后安装依赖：

```bash
pip install -r requirements.txt
```

## 运行程序

在项目根目录执行：

```bash
python src/day01_image_test.py
```

运行成功后，程序会显示：

- 原始图片
- 灰度图片
- 高斯模糊图片
- 边缘检测图片

处理结果会保存在 `outputs` 文件夹中。

## 开发计划

- [x] 完成基础开发环境配置
- [x] 完成图片读取和显示
- [x] 完成灰度化、滤波和边缘检测
- [ ] 增加图片缩放、裁剪和旋转
- [ ] 增加阈值与形态学处理
- [ ] 制作 Streamlit 可视化界面
- [ ] 完善异常处理和项目文档