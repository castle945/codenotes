# ResNet50 Cifar10 MMEngine 训练脚本，Pytorch 风格，对比 LeNet_Cifar10.py
# 参考: https://mmengine.readthedocs.io/zh_CN/latest/get_started/15_minutes.html
from torch.utils.data import DataLoader
from torch.optim import Adam
import torch.nn.functional as F

from torchvision import datasets, transforms
from torchvision.models import resnet50

import argparse
from mmengine.runner import Runner


def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--epochs',     default=20,   type=int,   help='number of epoch in training')
    parser.add_argument('--batch_size', default=256,  type=int,   help='batch size in training')
    parser.add_argument('--lr',         default=0.01, type=float, help='learning rate')
    
    return parser.parse_args()

from mmengine.model import BaseModel
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

from mmengine.evaluator import BaseMetric
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
    args = parse_args()

    norm_cfg = dict(mean=[0.491, 0.482, 0.447], std=[0.202, 0.199, 0.201])
    data_transform = {
        "train": transforms.Compose([
            transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip(),
            transforms.ToTensor(), transforms.Normalize(**norm_cfg)
        ]),
        "val": transforms.Compose([ 
            transforms.ToTensor(), transforms.Normalize(**norm_cfg)
        ])
    }

    train_dataset = datasets.CIFAR10(root='/workspace/files/datasets/CIFAR10', train=True, transform=data_transform['train'], download=False)
    val_dataset = datasets.CIFAR10(root='/workspace/files/datasets/CIFAR10', train=False, transform=data_transform['val'], download=False)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    runner = Runner(
        model=MMResNet(),
        work_dir='work_dirs',
        train_dataloader=train_loader,
        optim_wrapper=dict(optimizer=dict(type=Adam, lr=args.lr)),
        # 训练配置，用于指定训练周期、验证间隔等信息
        train_cfg=dict(by_epoch=True, max_epochs=args.epochs, val_interval=1),
        val_dataloader=val_loader,
        # 验证配置，用于指定验证所需要的额外参数
        val_cfg=dict(),
        # 用于验证的评测器，这里使用默认评测器，并评测指标
        val_evaluator=dict(type=Accuracy),
    )
    runner.train()

if __name__ == '__main__':
    main()
