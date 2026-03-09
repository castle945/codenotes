
import random
from pathlib import Path
import os
from tqdm import tqdm

split_rate = 0.3 # 验证集比例

imagenet1000_data_root = "/datasets/ImageNet-1K/train"
imagenet10_data_root = "/workspace/files/datasets/ImageNet-10/"
# ls | tail
# cat -n /datasets/ImageNet-1K/ILSVRC2012_devkit_t12/data/ILSVRC2012_validation_ground_truth.txt | tail
# cat -n /datasets/ImageNet-1K/ILSVRC2012_devkit_t12/data/ILSVRC2012_validation_ground_truth.txt | grep -w "2$" | head
# 发现验证集真值标签的类别编号不是训练集子目录名的顺序

# 查找 10 类目标，要求 5 大类 2 小类
# ImageNet-1K 类名，顺序对应训练集目录下子目录名: https://gist.github.com/yrevar/942d3a0ac09ec9e5eb3a#file-imagenet1000_clsid_to_human-txt
# ls > /datasets/workspace/codevault/name.txt # 搜索 fish 
subdirnames = ['n01443537', 'n02641379', 'n01514668', 'n01819313', 'n02105641', 'n02105855'        , 'n01532829', 'n01534433', 'n01728920' , 'n01735189'] 
classnames  = ['goldfish' , 'billfish' , 'cock'     , 'cockatoo' , 'bobtail'  , 'shetland_sheepdog', 'linnet'   , 'snowbird' , 'ring_snake', 'grass_snake'] # 确保字符串小写 金鱼、长嘴鱼、鸡、鹦鹉、短尾牧羊犬、苏格兰牧羊犬、朱顶雀、雪鸟、环蛇、草蛇

def main():
    random.seed(0)

    Path(imagenet10_data_root).mkdir(exist_ok=True)
    train_root = Path(f"{imagenet10_data_root}/train")
    train_root.mkdir(exist_ok=True)
    val_root = Path(f"{imagenet10_data_root}/val")
    val_root.mkdir(exist_ok=True)

    for i, cls in enumerate(tqdm(classnames)):
        train_dir = Path(os.path.join(train_root, cls))
        train_dir.mkdir(exist_ok=True)
        val_dir = Path(os.path.join(val_root, cls))
        val_dir.mkdir(exist_ok=True)

        raw_cls_dir = os.path.join(imagenet1000_data_root, subdirnames[i])
        filenames = os.listdir(raw_cls_dir)
        eval_filenames = random.sample(filenames, k=int(len(filenames)*split_rate))
        for filename in filenames:
            filepath = os.path.join(raw_cls_dir, filename)
            if filename in eval_filenames:
                os.system(f"cp {filepath} {val_dir}")
            else:
                os.system(f"cp {filepath} {train_dir}")

if __name__ == '__main__':
    main()