# ResNet50 Cifar10 MMEngine 训练脚本，MMengine 风格
# 参考: https://mmengine.readthedocs.io/zh-cn/v0.9.1/tutorials/runner.html
import torch.nn.functional as F

from torchvision import datasets, transforms
from torchvision.models import resnet50

from mmengine.runner import Runner
from mmengine.model import BaseModel
from mmengine.dataset.base_dataset import Compose
from mmengine.config import Config
from mmengine.registry import DATASETS, TRANSFORMS, MODELS, METRICS

# 注册数据集和数据变换，复用 torchvision 中的数据集
TRANSFORMS.register_module('RandomCrop', module=transforms.RandomCrop)
TRANSFORMS.register_module('RandomHorizontalFlip', module=transforms.RandomHorizontalFlip)
TRANSFORMS.register_module('MyToTensor', module=transforms.ToTensor) # mmcv 中也有注册 ToTensor，且参数不一样，故改名
TRANSFORMS.register_module('MyNormalize', module=transforms.Normalize)
@DATASETS.register_module(name='Cifar10', force=False)
def build_torchvision_cifar10(transform=None, **kwargs):
    if isinstance(transform, dict):
        transform = [transform]
    if isinstance(transform, (list, tuple)):
        transform = Compose(transform)
    return datasets.CIFAR10(**kwargs, transform=transform)

# 注册模型
@MODELS.register_module('MMResNet')
class MMResNet(BaseModel):
    def __init__(self):
        super().__init__()
        self.resnet = resnet50()
    
    def forward(self, inputs, labels, mode):
        x = self.resnet(inputs)
        if mode == 'loss':
            return {'loss': F.cross_entropy(x, labels)}
        elif mode == 'predict':
            return x, labels

# 注册评价指标
from mmengine.evaluator import BaseMetric
@METRICS.register_module('Accuracy')
class Accuracy(BaseMetric):
    def process(self, data_batch, data_samples):
        score, gt = data_samples
        self.results.append({
            'batch_size': len(gt),
            'correct': (score.argmax(dim=1) == gt).sum().cpu()
        })

    def compute_metrics(self, results):
        total_correct = sum(item['correct'] for item in results)
        total_size = sum(item['batch_size'] for item in results)
        return dict(accuracy=100 * total_correct / total_size)


def main():
    config = Config.fromfile('config.py')
    runner = Runner.from_cfg(config)
    runner.train()

if __name__ == '__main__':
    main()
