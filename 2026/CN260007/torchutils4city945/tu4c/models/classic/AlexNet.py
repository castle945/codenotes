# modified from https://github.com/shanglianlm0525/PyTorch-Networks/blob/master/ClassicNetwork/AlexNet.py
import torch.nn as nn

class AlexNet(nn.Module):
    def __init__(self, num_classes=1000, init_weights=False, use_bias=True):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=64, kernel_size=11, stride=4, padding=2, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(64, 192, 5, stride=1, padding=2, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, 2),
            nn.Conv2d(192, 384, 3, stride=1, padding=1, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, 3, stride=1, padding=1, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, stride=1, padding=1, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, 2),
        )
        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(6, 6))
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(in_features=256*6*6, out_features=4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(in_features=4096, out_features=4096),
            nn.ReLU(inplace=True),
            nn.Linear(in_features=4096, out_features=num_classes),
        )
        if init_weights:
            self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = self.classifier(x.view(x.shape[0], -1))
        return x

if __name__ == '__main__':
    import torch, torchvision
    import numpy as np
    from tu4c.utils import set_random_seed

    model = AlexNet()
    model_tv = torchvision.models.alexnet()
    model.load_state_dict(model_tv.state_dict())
    input = torch.randn(1, 3, 224, 224)
    print(model)
    assert (str(model) == str(model_tv))
    set_random_seed(666)
    output1 = model(input).detach().numpy()
    set_random_seed(666)
    output2 = model_tv(input).detach().numpy()
    assert np.array_equal(output1, output2)
