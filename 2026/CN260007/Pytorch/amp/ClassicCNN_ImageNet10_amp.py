# 经典 CNN 网络 ImageNet-10 训练脚本
# 参考资料: https://cloud.tencent.com/developer/article/2317761
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from torchvision import datasets, transforms
from tu4c.models import AlexNet, VGG16, ResNet50
from tu4c.utils import create_logger

import argparse, tqdm, datetime, os

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
    parser.add_argument('--use_amp', action='store_true', help='use mix precision training')
    
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

def main():
    args = parse_args()
    logger = create_logger(log_file=f"{os.path.basename(__file__)[:-3]}_{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.log")

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

    model = eval(args.modelname)(num_classes=10).to(device)
    optim = Adam(model.parameters(), lr=args.lr)
    scaler = torch.cuda.amp.GradScaler(enabled=args.use_amp)
    loss_fn = CrossEntropyLoss()

    logger.info(args.__dict__)
    all_eval_results = []
    for epoch in range(args.epochs):
        train_loss_sum, train_acc_sum, n = 0.0, 0.0, 0
        model.train()
        for input, label in tqdm.tqdm(train_loader):
            input, label = input.to(device), label.to(device)
            # (B, 3, 224, 224)->(B, 10)
            with torch.cuda.amp.autocast(enabled=args.use_amp):
                pred = model(input)
            loss = loss_fn(pred, label)
            optim.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optim)
            scaler.update()

            train_loss_sum += loss.cpu().item()
            train_acc_sum += (pred.argmax(dim=1) == label).sum().cpu().item()
            n += label.shape[0]
        
        train_acc = train_acc_sum / n
        test_acc = evaluate(val_loader, model)
        logger.info(f'epoch {epoch+1}, loss sum {train_loss_sum:.3f}, train acc {train_acc:.3f}, val acc {test_acc:.3f}')
        all_eval_results.append({'epoch': epoch+1, 'train_acc': train_acc, 'val_acc': test_acc})

    sorted_results = sorted(all_eval_results, key=lambda x: x['val_acc'], reverse=True)
    logger.info(f'best: val acc: {sorted_results[0]["val_acc"]:.3f} epoch {sorted_results[0]["epoch"]}')
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
        logger.info(f"gt:   {' '.join(list(classnames[label[:num_show].cpu().numpy()]))}")
        logger.info(f"pred: {' '.join(list(classnames[pred_label[:num_show]]))}")

if __name__ == '__main__':
    main()
