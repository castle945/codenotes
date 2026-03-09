# 经典 CNN 网络 ImageNet-10 训练脚本
# wandb sweep --project WandbTest ClassicCNN_ImageNet10_finetune.yaml
# CUDA_VISIBLE_DEVICES=0 wandb agent city945/WandbTest/7xjkpdkc --count 24
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from torchvision import datasets, transforms
from tu4c.models import AlexNet, VGG16, ResNet50

import argparse, tqdm, datetime, os
import wandb

import numpy as np
classnames  = np.array(['billfish', 'bobtail', 'cock', 'cockatoo', 'goldfish', 'grass_snake', 'linnet', 'ring_snake', 'shetland_sheepdog', 'snowbird'])
data_root = "/workspace/files/datasets/ImageNet-10/"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--modelname',  default='AlexNet', choices=['AlexNet', 'VGG16', 'ResNet50'], type=str, help='')
    parser.add_argument('--epochs',     default=30,     type=int,   help='number of epoch in training')
    parser.add_argument('--batch_size', default=64,     type=int,   help='batch size in training')
    parser.add_argument('--lr',         default=0.0002, type=float, help='learning rate')
    parser.add_argument('--show_preds', action='store_true',        help='show preds images')
    parser.add_argument('--finetune',   default=None, choices=['all', 'classifier'], type=str, help='')
    parser.add_argument('--use_wandb', action='store_true', default=True, help='') # 修改为默认 True
    parser.add_argument('--logger_iter_interval', type=int, default=15, help='')
    
    return parser.parse_args()

@torch.no_grad()
def evaluate(val_loader, model):
    model.eval()
    acc_sum, n = 0.0, 0
    for input, label in val_loader:
        input, label = input.to(device), label.to(device)
        pred = model(input)
        acc_sum += (pred.argmax(dim=1) == label).sum().cpu().item()
        n += label.shape[0]

    return acc_sum / n

def load_checkpoint(model, modelname):
    import torchvision
    if modelname == "AlexNet":
        ckpt = os.path.join(os.path.expanduser("~"), '.cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth')
        if not os.path.exists(ckpt):
            model_torch = torchvision.models.alexnet(pretrained=True)
    elif modelname == "VGG16": 
        ckpt = os.path.join(os.path.expanduser("~"), '.cache/torch/hub/checkpoints/vgg16_bn-6c64b313.pth')
        if not os.path.exists(ckpt):
            model_torch = torchvision.models.vgg16_bn(pretrained=True)
    # ResNet 分类器的属性名不同，不参与该实验
    # elif modelname == "ResNet50":
    #     ckpt = os.path.join(os.path.expanduser("~"), '.cache/torch/hub/checkpoints/resnet50-0676ba61.pth')
    #     if not os.path.exists(ckpt):
    #         model_torch = torchvision.models.resnet50(pretrained=True)
    else:
        raise ValueError("Invalid model name")
    
    model.load_state_dict(torch.load(ckpt))

def main():
    args = parse_args()
    if args.use_wandb:
        wandb.init(project='WandbTest', config=vars(args), dir='/tmp')
        wandb.run.name = f"{os.path.basename(__file__)[:-3]}_{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"
        args = wandb.config # for wandb.sweep

    data_transform = {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]),
        "val": transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    }
    train_dataset = datasets.ImageFolder(root=os.path.join(data_root, "train"), transform=data_transform['train'])
    val_dataset = datasets.ImageFolder(root=os.path.join(data_root, "val"), transform=data_transform['val'])
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=8)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, num_workers=8)

    model = eval(args.modelname)(num_classes=1000).to(device) # 为加载预训练模型，需与模型参数保持一致
    optim = Adam(model.parameters(), lr=args.lr)
    if args.finetune:
        load_checkpoint(model, args.modelname)
        model.classifier[-1] = torch.nn.Linear(model.classifier[-1].in_features, 10).to(device) # 此处再替换分类器
        if args.finetune == "all":
            # 模型骨干网络和分类器一起微调
            optim = Adam(model.parameters(), lr=args.lr)
        elif args.finetune == "classifier":
            # 只微调分类器
            optim = Adam(model.classifier[-1].parameters(), lr=args.lr)
    loss_fn = CrossEntropyLoss()

    print(args.__dict__)
    all_eval_results = []
    accumulated_iter = 0
    for epoch in range(args.epochs):
        train_loss_sum, train_acc_sum, n = 0.0, 0.0, 0
        model.train()
        for input, label in tqdm.tqdm(train_loader):
            input, label = input.to(device), label.to(device)
            # (B, 3, 224, 224)->(B, 10)
            pred = model(input)
            loss = loss_fn(pred, label)
            optim.zero_grad()
            loss.backward()
            optim.step()

            train_loss_sum += loss.cpu().item()
            train_acc_sum += (pred.argmax(dim=1) == label).sum().cpu().item()
            n += label.shape[0]
        
            if args.use_wandb and (accumulated_iter % args.logger_iter_interval == 0):
                # 此数据集太小故在每轮结束额外计算每轮的损失和准确率，一般是每个 iter 记录 iter 的 loss，这里折中，间隔 N 个 iter 记录当前 iter 的 loss
                train_metrics = {
                    "train/train_loss": loss, 
                }
                wandb.log(train_metrics)

            accumulated_iter += 1
        
        train_acc = train_acc_sum / n
        test_acc = evaluate(val_loader, model)
        print(f'epoch {epoch+1}, loss sum {train_loss_sum:.3f}, train acc {train_acc:.3f}, val acc {test_acc:.3f}')
        all_eval_results.append({'epoch': epoch+1, 'train_acc': train_acc, 'val_acc': test_acc})

        if args.use_wandb:
            val_metrics = {
                "eval/epoch": epoch,
                "eval/val_acc_epoch": test_acc,
                "eval/train_acc_epoch": train_acc,
                "eval/train_loss_epoch": train_loss_sum / n,
            }
            wandb.log(val_metrics)

    sorted_results = sorted(all_eval_results, key=lambda x: x['val_acc'], reverse=True)
    print(f'best: val acc: {sorted_results[0]["val_acc"]:.3f} epoch {sorted_results[0]["epoch"]}')
    if args.use_wandb:
        wandb.log({"eval/best_val_acc": sorted_results[0]["val_acc"], "eval/epoch": sorted_results[0]["epoch"]})
        wandb.finish()
    if args.show_preds:
        import matplotlib.pyplot as plt
        import torchvision
        num_show = 4
        image, label = next(iter(train_loader))
        input, _ = image.to(device)[:num_show], label.to(device)[:num_show]
        pred = model(input)
        pred_label = pred.argmax(dim=1).cpu().numpy()

        image = torchvision.utils.make_grid(image[:num_show]) / 2 + 0.5     # unnormalize
        plt.imsave('imagenet10_pred.png', np.transpose(image.numpy(), (1, 2, 0)))
        print(f"gt:   {' '.join(list(classnames[label[:num_show].cpu().numpy()]))}")
        print(f"pred: {' '.join(list(classnames[pred_label[:num_show]]))}")

if __name__ == '__main__':
    main()
