# 银行卡识别系统项目介绍

## 项目概述

本项目是一个基于 Python 的银行卡卡号识别桌面应用。程序通过 PyQt5 提供图形界面，用户选择银行卡图片后，系统会自动进行图像预处理、银行卡区域定位、卡号区域提取、数字识别与结果校验，并在界面中展示识别过程和最终卡号。

项目核心目标是从普通银行卡图片中提取可信的银行卡号，适合作为图像处理、OCR 识别、数字模型训练和桌面应用开发的综合实践项目。

## 主要功能

- 图形化选择银行卡图片并启动识别。
- 展示原始图片、灰度增强图、候选区域、检测结果和卡号 ROI。
- 支持保存调试图片到 `debug` 目录，便于观察每一步处理效果。
- 使用 OpenCV 完成图像增强、轮廓检测、透视校正、候选区域筛选和数字切割。
- 支持多种识别策略：
  - PaddleOCR，可通过环境变量开启。
  - Tesseract OCR，检测到本机可用时自动使用。
  - TensorFlow CNN 数字模型，可通过环境变量开启。
  - 本地数字模板匹配，作为兜底识别方式。
- 对识别结果进行银行卡号长度、前缀、重复数字和 Luhn 校验，提高结果可信度。

## 项目结构

```text
.
├── main.py                  # PyQt5 桌面应用入口
├── card_processor.py        # 银行卡图像处理与卡号识别核心逻辑
├── digit_model.py           # CNN 数字识别模型结构定义
├── train_digit_model.py     # 使用本地 dataset 训练数字模型
├── train_ocr.py             # 使用 MNIST 训练基础数字识别模型
├── digit_recognizer.h5      # 已训练的数字识别模型文件
├── requirements.txt         # 当前环境导出的依赖列表
├── dataset/                 # 数字模板/训练样本，按 0-9 分类
├── debug/                   # 识别过程产生的调试图片
└── tp/                      # 测试图片素材
```

## 环境依赖

项目主要依赖如下：

- Python 3.x
- PyQt5
- OpenCV
- NumPy
- TensorFlow
- scikit-learn
- pytesseract，可选
- paddleocr，可选

`requirements.txt` 是从当前开发环境导出的完整依赖，里面包含较多环境路径和额外包。新环境中如果直接安装失败，建议优先安装核心依赖：

```bash
pip install pyqt5 opencv-python numpy tensorflow scikit-learn pytesseract
```

如果需要启用 PaddleOCR：

```bash
pip install paddleocr
```

如果需要启用 Tesseract OCR，需要额外安装 Tesseract 程序，并确保命令行中可以访问 `tesseract`。

## 运行方式

在项目根目录执行：

```bash
python main.py
```

运行后会打开桌面窗口，基本使用流程如下：

1. 点击“选择图片”，选择一张银行卡图片。
2. 点击“开始识别”，程序会自动处理图片并尝试识别卡号。
3. 查看右侧结果框中的识别结果。
4. 如果开启保存调试图片，可以在 `debug` 目录查看中间处理结果。

## 识别流程

整体识别流程由 `CardProcessor` 完成，主要步骤如下：

1. 读取图片并按最大宽度缩放，避免超大图片影响处理速度。
2. 构建多种处理视图，包括原图、银行卡透视校正图和小角度旋转图。
3. 对图片进行灰度化、对比度增强、二值化和形态学处理。
4. 通过轮廓和规则评分定位可能的卡号区域。
5. 对候选 ROI 进行裁剪、去斜、增强和多版本生成。
6. 依次尝试 OCR、CNN 模型或模板匹配识别数字。
7. 根据银行卡号规则、Luhn 校验和上下文评分选择最佳结果。
8. 返回格式化后的卡号，例如 `6222 1234 5678 9012`。

## 模型与数据

`dataset` 目录按数字 `0` 到 `9` 分类保存样本，每个数字目录下包含若干图片。当前项目中每个数字类别约有 80 张样本，可用于模板匹配和模型训练。

训练本地数字模型：

```bash
python train_digit_model.py
```

训练完成后会生成或覆盖：

```text
digit_recognizer.h5
```

项目默认不会加载 TensorFlow 模型，只有设置环境变量后才启用 CNN 识别：

```bash
set CARD_USE_TF=1
python main.py
```

## 可选配置

程序支持通过环境变量调整识别行为：

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `CARD_USE_PADDLEOCR` | `0` | 设置为 `1` 时尝试启用 PaddleOCR |
| `CARD_USE_TF` | `0` | 设置为 `1` 时尝试加载 `digit_recognizer.h5` |
| `CARD_MAX_OCR_ROIS` | `3` | 每张图片最多尝试的卡号候选区域数量 |
| `CARD_MAX_OCR_VARIANTS` | `3` | 每个候选区域最多尝试的图像增强版本数量 |
| `CARD_TESSERACT_TIMEOUT` | `2.0` | 单次 Tesseract OCR 超时时间 |
| `CARD_OCR_CALL_BUDGET` | `36` | 单次识别最多 OCR 调用次数 |

Windows PowerShell 示例：

```powershell
$env:CARD_USE_PADDLEOCR="1"
$env:CARD_USE_TF="1"
python main.py
```

## 调试输出

开启调试保存后，`debug` 目录会生成以下图片：

- `01_gray.png`：灰度图
- `02_enhanced.png`：增强后的图像
- `03_binary.png`：二值化图像
- `04_candidates.png`：候选区域标记图
- `05_detected.png`：最终检测框图
- `06_roi.png`：提取出的卡号区域

这些文件可以帮助判断识别失败是由图片质量、银行卡定位、卡号区域裁剪还是 OCR 阶段导致。

## 注意事项

- 图片越清晰、卡号区域越完整，识别效果越好。
- 反光、遮挡、强透视、严重倾斜和低分辨率图片会降低识别准确率。
- 如果界面中文出现乱码，通常需要检查源文件编码是否为 UTF-8。
- 银行卡号属于敏感信息，实际使用时应避免保存真实卡号图片或调试结果。
- 本项目更适合作为学习和演示用途，若用于生产环境，需要补充隐私保护、错误处理、日志脱敏和更完整的测试。

