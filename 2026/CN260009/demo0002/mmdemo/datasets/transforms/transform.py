from torchvision import transforms
from mmdemo.registry import TRANSFORMS
from PIL import Image

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
