from torchvision.models import resnet50
from mmdemo.registry import MODELS
from mmengine.model import BaseModel
import torch.nn.functional as F

@MODELS.register_module('MMResNet')
class MMResNet(BaseModel):
    def __init__(self):
        super().__init__()
        self.resnet = resnet50()

    # @! 形参由批量数据字典解包而来，必须带 kwargs 来装不用的参数
    def forward(self, img, img_label, mode, **kwargs):
        x = self.resnet(img)
        if mode == 'loss':
            return {'loss': F.cross_entropy(x, img_label)}
        elif mode == 'predict':
            return x, img_label
