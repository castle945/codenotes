# modified from https://github.com/shanglianlm0525/PyTorch-Networks/blob/master/ClassicNetwork/VGGNet.py
import torch.nn as nn

__all__ = ['VGG16', 'VGG19']

def Conv3x3BNReLU(in_channels,out_channels):
    return [
        nn.Conv2d(in_channels=in_channels,out_channels=out_channels,kernel_size=3,stride=1,padding=1),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    ]
class VGG(nn.Module):
    def __init__(self, block_nums, num_classes=1000, init_weights=True):
        super().__init__()
        feature_layers = []
        feature_layers.extend(self._make_layers(in_channels=3, out_channels=64, block_num=block_nums[0]))
        feature_layers.extend(self._make_layers(in_channels=64, out_channels=128, block_num=block_nums[1]))
        feature_layers.extend(self._make_layers(in_channels=128, out_channels=256, block_num=block_nums[2]))
        feature_layers.extend(self._make_layers(in_channels=256, out_channels=512, block_num=block_nums[3]))
        feature_layers.extend(self._make_layers(in_channels=512, out_channels=512, block_num=block_nums[4]))
        self.features = nn.Sequential(*feature_layers)
        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(7, 7))
        self.classifier = nn.Sequential(
            nn.Linear(in_features=512*7*7, out_features=4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(in_features=4096, out_features=4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(in_features=4096, out_features=num_classes)
        )
        if init_weights:
            self._initialize_weights()

    def _make_layers(self, in_channels, out_channels, block_num):
        layers = []
        layers.extend(Conv3x3BNReLU(in_channels,out_channels))
        for i in range(1,block_num):
            layers.extend(Conv3x3BNReLU(out_channels,out_channels))
        layers.append(nn.MaxPool2d(kernel_size=2,stride=2, ceil_mode=False))
        return layers

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = self.classifier(x.view(x.shape[0], -1))
        return x

def VGG16(num_classes=1000, init_weights=True, **kwargs):
    return VGG([2, 2, 3, 3, 3], num_classes, init_weights)
def VGG19(num_classes=1000, init_weights=True, **kwargs):
    return VGG([2, 2, 4, 4, 4], num_classes, init_weights)

if __name__ == '__main__':
    import torch, torchvision
    import numpy as np

    model = VGG16().eval()
    model_tv = torchvision.models.vgg16_bn().eval()
    model.load_state_dict(model_tv.state_dict())
    input = torch.randn(1, 3, 224, 224)
    print(model)
    assert (str(model) == str(model_tv))
    assert (str(VGG19()) == str(torchvision.models.vgg19_bn()))
