# python tools/create_data.py imagenet10 --root-path ./data/imagenet10 --extra-tag imagenet10
import argparse
import os, json

def imagenet10_data_prep(root_path, info_prefix):
    metainfo = {'classes': ['goldfish', 'billfish', 'cock', 'cockatoo', 'bobtail', 'shetland_sheepdog', 'linnet', 'snowbird', 'ring_snake', 'grass_snake']} # 确保字符串小写 金鱼、长嘴鱼、鸡、鹦鹉、短尾牧羊犬、苏格兰牧羊犬、朱顶雀、雪鸟、环蛇、草蛇
    classname2id = { classname:id for id, classname in enumerate(metainfo['classes'])}
    for split in ['train', 'val']:
        # @% 虽然可以直接存相对路径，但遵循 MMEngine 设计规范用配置参数 data_prefix 传入相对路径
        data_list = [{'img_path': filename, 'img_label': classname2id[classname]}
                    for classname in metainfo['classes']
                    for filename in os.listdir(os.path.join(root_path, split, classname))
        ]
        with open(f'{root_path}/{info_prefix}_infos_{split}.json', 'w') as f:
            json.dump({'metainfo': metainfo, 'data_list': data_list}, f, indent=4)
    print("Create data done!")


parser = argparse.ArgumentParser(description='Data converter arg parser')
parser.add_argument('dataset', metavar='imagenet10', help='name of the dataset')
parser.add_argument(
    '--root-path',
    type=str,
    default='./data/imagenet10',
    help='specify the root path of dataset')
parser.add_argument('--extra-tag', type=str, default='imagenet10')
args = parser.parse_args()

if __name__ == "__main__":
    if args.dataset == 'imagenet10':
        imagenet10_data_prep(
            root_path=args.root_path,
            info_prefix=args.extra_tag)
    else:
        raise NotImplementedError(f'Don\'t support {args.dataset} dataset.')
