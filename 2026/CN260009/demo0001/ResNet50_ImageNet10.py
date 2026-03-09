# ResNet50 ImageNet10 MMEngine 训练脚本
import torch.nn.functional as F

from torchvision import transforms
from torchvision.models import resnet50

from mmengine.runner import Runner
from mmengine.model import BaseModel
from mmengine.dataset.base_dataset import BaseDataset
from mmengine.config import Config
from mmengine.registry import DATASETS, TRANSFORMS, MODELS, METRICS

import glob, os, json
from PIL import Image

# 注册数据集和数据变换
# 数据预处理管道之间传递的是字典，输入 data_info 管道中的每个 TRANSFORMS 模块都是新增或修改字典内容
@TRANSFORMS.register_module()
class LoadImage:
    def __call__(self, results):
        # print(results['img_path'])
        # results['img'] = Image.open('./data/imagenet10/train/billfish/n02641379_20230.JPEG') # @! ImageNet 中大部分是彩图但也存在灰度图和 RGBA，这里简单转成彩图
        results['img'] = Image.open(results['img_path']) # 后续用到的 RandomResizedCrop 中要求输入图像是 Tensor 或 PIL Image 不能是 cv2 读出来的 ndarray
        
        if results['img'].mode != "RGB":
            results['img'] = results['img'].convert("RGB")

        return results
@TRANSFORMS.register_module()
class MyRandomResizedCrop:
    def __init__(self, **kwargs):
        self.transform = transforms.RandomResizedCrop(**kwargs)
    def __call__(self, results):
        results['img'] = self.transform(results['img'])
        return results
@TRANSFORMS.register_module()
class MyRandomHorizontalFlip:
    def __init__(self, **kwargs):
        self.transform = transforms.RandomHorizontalFlip(**kwargs)
    def __call__(self, results):
        results['img'] = self.transform(results['img'])
        return results
@TRANSFORMS.register_module()
class MyResize:
    def __init__(self, **kwargs):
        self.transform = transforms.Resize(**kwargs)
    def __call__(self, results):
        results['img'] = self.transform(results['img'])
        return results
@TRANSFORMS.register_module()
class MyToTensor:
    def __init__(self, **kwargs):
        self.transform = transforms.ToTensor(**kwargs)
    def __call__(self, results):
        results['img'] = self.transform(results['img'])
        return results
@TRANSFORMS.register_module()
class MyNormalize:
    def __init__(self, **kwargs):
        self.transform = transforms.Normalize(**kwargs)
    def __call__(self, results):
        results['img'] = self.transform(results['img'])
        return results
@DATASETS.register_module()
class ImageNet10Dataset(BaseDataset):
    def parse_data_info(self, raw_data_info):
        data_info = raw_data_info
        img_prefix = self.data_prefix.get('img_path', None)
        if img_prefix is not None:
            classname = self._metainfo['classes'][data_info['img_label']]
            data_info['img_path'] = os.path.join(img_prefix, classname, data_info['img_path'])
        return data_info

# 注册模型
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

def model_analysis():
    """统计模型参数量和计算量"""
    from mmengine.analysis import get_model_complexity_info
    input_shape = (3, 224, 224)
    model = resnet50()
    analysis_results = get_model_complexity_info(model, input_shape)
    print("Model Parameters:{}".format(analysis_results['params_str']))
    print("Model Flops:{}".format(analysis_results['flops_str']))
    # print(analysis_results['out_arch']) # 以模型结构的形式显示各层参数量和计算量

# 数据集预处理
def create_data(data_root):
    metainfo = {'classes': ['goldfish', 'billfish', 'cock', 'cockatoo', 'bobtail', 'shetland_sheepdog', 'linnet', 'snowbird', 'ring_snake', 'grass_snake']} # 确保字符串小写 金鱼、长嘴鱼、鸡、鹦鹉、短尾牧羊犬、苏格兰牧羊犬、朱顶雀、雪鸟、环蛇、草蛇
    classname2id = { classname:id for id, classname in enumerate(metainfo['classes'])}
    for split in ['train', 'val']:
        # @% 虽然可以直接存相对路径，但遵循 MMEngine 设计规范用配置参数 data_prefix 传入相对路径
        data_list = [{'img_path': filename, 'img_label': classname2id[classname]}
                    for classname in metainfo['classes']
                    for filename in os.listdir(os.path.join(data_root, split, classname))
        ]
        with open(f'{data_root}/imagenet10_infos_{split}.json', 'w') as f:
            json.dump({'metainfo': metainfo, 'data_list': data_list}, f, indent=4)
    print("Create data done!")

if __name__ == '__main__':
    if len(glob.glob('./data/imagenet10/*.json')) == 0:
        create_data(data_root='./data/imagenet10')
    model_analysis()
    main()
