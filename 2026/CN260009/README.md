# MMEngine 示例代码

### quick_demo

- 对应快速示例代码，可对比原生 Pytorch 实现和 MMEngine-v0.10.7 实现的区别

### demo0001

- 对应常用功能代码，可学习常用的配置参数、自定义数据集

### demo0002

- 对 demo0001 重构作为重新开发下游视觉库时的代码模版

```Bash
pip install -e .
export PYTHONPATH=`pwd`:$PYTHONPATH # 暂不清楚为什么 mmlab 实现的下游库 create_data 时不需要这个
python tools/train.py projects/ResNet/configs/resnet50_1xb30-35e_imagenet10.py
```
