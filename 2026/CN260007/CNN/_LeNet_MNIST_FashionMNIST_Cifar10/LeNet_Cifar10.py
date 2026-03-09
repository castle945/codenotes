# LeNet Cifar10 训练脚本
# 参考精度: 62.8% see https://github.com/j-holub/Cifar-10-Image-Classifcation-using-LeNet5
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from torchvision import datasets, transforms
from tu4c.models import LeNet
from tu4c.utils import create_logger

import argparse, tqdm, datetime, os

import numpy as np
classnames = np.array(['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck'])
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--epochs',     default=20,   type=int,   help='number of epoch in training')
    parser.add_argument('--batch_size', default=256,  type=int,   help='batch size in training')
    parser.add_argument('--lr',         default=0.01, type=float, help='learning rate')
    parser.add_argument('--show_preds', action='store_true', help='show preds images')
    
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

    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    train_dataset = datasets.CIFAR10(root='/workspace/files/datasets/CIFAR10', train=True, transform=transform, download=False) 
    val_dataset = datasets.CIFAR10(root='/workspace/files/datasets/CIFAR10', train=False, transform=transform, download=False)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    model = LeNet(in_channels=3).to(device)
    optim = Adam(model.parameters(), lr=args.lr)
    loss_fn = CrossEntropyLoss()

    logger.info(args.__dict__)
    all_eval_results = []
    for epoch in range(args.epochs):
        train_loss_sum, train_acc_sum, n = 0.0, 0.0, 0
        model.train()
        for input, label in tqdm.tqdm(train_loader):
            input, label = input.to(device), label.to(device)
            # (B, 3, 32, 32)->(B, 10)
            pred = model(input)
            loss = loss_fn(pred, label)
            optim.zero_grad()
            loss.backward()
            optim.step()

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
        plt.imsave('cifar10_pred.png', np.transpose(image.numpy(), (1, 2, 0)))
        logger.info(f"gt:   {' '.join(list(classnames[label[:num_show].cpu().numpy()]))}")
        logger.info(f"pred: {' '.join(list(classnames[pred_label[:num_show]]))}")

if __name__ == '__main__':
    main()
