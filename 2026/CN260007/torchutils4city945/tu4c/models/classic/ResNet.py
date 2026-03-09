# modified from https://github.com/shanglianlm0525/PyTorch-Networks/blob/master/ClassicNetwork/ResNet.py
import torch.nn as nn

__all__ = ['ResNet50', 'ResNet101', 'ResNet152']

class Bottleneck(nn.Module):
    def __init__(self, in_places, places, stride=1,downsampling=False, expansion = 4):
        super(Bottleneck,self).__init__()
        self.expansion = expansion
        self.downsampling = downsampling

        # bottleneck
        self.conv1 = nn.Conv2d(in_channels=in_places, out_channels=places, kernel_size=1, stride=1, bias=False)
        self.bn1 = nn.BatchNorm2d(places)
        self.conv2 = nn.Conv2d(in_channels=places, out_channels=places, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(places)
        self.conv3 = nn.Conv2d(in_channels=places, out_channels=places*self.expansion, kernel_size=1, stride=1, bias=False)
        self.bn3 = nn.BatchNorm2d(places*self.expansion)
        self.relu = nn.ReLU(inplace=True)

        if self.downsampling:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels=in_places, out_channels=places*self.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(places*self.expansion)
            )

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsampling:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out) # 打印模型结构时，ReLU 的处理不知道咋回事，可能打印出来的结构跟实际结构不一定一致，只差异在 ReLU 层的排布
        return out

class ResNet(nn.Module):
    def __init__(self, blocks, num_classes=1000, init_weights=True,expansion=4):
        super(ResNet,self).__init__()
        self.expansion = expansion

        # conv1
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self.make_layer(in_places = 64, places= 64, block=blocks[0], stride=1)
        self.layer2 = self.make_layer(in_places = 256,places=128, block=blocks[1], stride=2)
        self.layer3 = self.make_layer(in_places=512,places=256, block=blocks[2], stride=2)
        self.layer4 = self.make_layer(in_places=1024,places=512, block=blocks[3], stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(1, 1))
        self.fc = nn.Linear(2048, num_classes)
        if init_weights:
            self._initialize_weights()

    def make_layer(self, in_places, places, block, stride):
        layers = []
        layers.append(Bottleneck(in_places, places,stride, downsampling =True))
        for i in range(1, block):
            layers.append(Bottleneck(places*self.expansion, places))

        return nn.Sequential(*layers)
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = self.fc(x.view(x.shape[0], -1))
        return x

def ResNet50(num_classes=1000, init_weights=True, **kwargs):
    return ResNet([3, 4, 6, 3], num_classes, init_weights)
def ResNet101(num_classes=1000, init_weights=True, **kwargs):
    return ResNet([3, 4, 23, 3], num_classes, init_weights)
def ResNet152(num_classes=1000, init_weights=True, **kwargs):
    return ResNet([3, 8, 36, 3], num_classes, init_weights)

if __name__ == '__main__':
    import torch, torchvision
    import numpy as np

    model = ResNet50().eval()
    model_tv = torchvision.models.resnet50().eval()
    model.load_state_dict(model_tv.state_dict())
    input = torch.randn(1, 3, 224, 224)
    print(model)
    assert (str(model) == str(model_tv))
    assert (str(ResNet101()) == str(torchvision.models.resnet101()))
    assert (str(ResNet152()) == str(torchvision.models.resnet152()))
    assert np.array_equal(model(input).detach().numpy(), model_tv(input).detach().numpy())
