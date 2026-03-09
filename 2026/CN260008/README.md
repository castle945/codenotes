# Wandb 示例代码

- LeNet_Cifar10
  - [GridSearch](https://wandb.ai/city945/WandbTest/sweeps/glvrh9oz?nw=nwusercity945)
    - 图中可以直接看到参数的重要性：学习率 > 激活函数 > 批量大小 > 轮次
    - 对于学习率，按学习率排序，发现精度高的都是学习率小的，可能说明参数空间中学习率下限还可以调低一点，X 为时间线故左右两个点的参数基本相同，可以从左右找参数相近的点组队比较
    - 对于激活函数，通过过滤条件选择一组学习率相同（由上可知学习率最小值效果最好，故选最小学习率）、批量大小相同，切换几组批量发现，相同轮次的训练结果对中，基本上 relu 精度比 sigmoid 高
    - 对于批量大小，固定学习率取最小值、ReLU 激活函数，发现批量越大精度越高，说明批量大小上限还可以调高一点
  - [BayesSearch](https://wandb.ai/city945/WandbTest/sweeps/hsn0rzws?nw=nwusercity945)：效果要优于 [RandomSearch](https://wandb.ai/city945/WandbTest/sweeps/86tpmbd4?nw=nwusercity945)，即使给定较大范围也能找到更好的参数
- [ClassicCNN_ImageNet10_finetune](https://wandb.ai/city945/WandbTest/sweeps/7xjkpdkc?nw=nwusercity945)：精度相比从头训练都能大幅度提高，只微调分类器精度高且稳定（受 lr 等参数影响小），整体微调受其他参数影响精度方差大
- [AlexNet_ImageNet10](https://wandb.ai/city945/WandbTest/sweeps/d2e13xnj?nw=nwusercity945)：init\_weight 能较小提升性能不及学习率等影响大；卷积层加不加 bias 可能能在高指标时较小提升其上限，在低指标时反而稍微拉低性能；
