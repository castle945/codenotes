# LeNet Cifar10 训练脚本
# 参考精度: 62.8% see https://github.com/j-holub/Cifar-10-Image-Classifcation-using-LeNet5
# wandb sweep --project WandbTest LeNet_Cifar10_grid_search.yaml
# CUDA_VISIBLE_DEVICES=0 wandb agent city945/WandbTest/glvrh9oz --count 36 # 3*3*2*2 种配置，也可以小于 36 则不跑完所有遍历
# wandb sweep --project WandbTest LeNet_Cifar10_bayes_search.yaml
# CUDA_VISIBLE_DEVICES=0 wandb agent city945/WandbTest/hsn0rzws --count 36
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from torchvision import datasets, transforms
from tu4c.models import LeNet

import argparse, tqdm, datetime, os
import wandb

import numpy as np
classnames = np.array(['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck'])
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--epochs',     default=20,   type=int,   help='number of epoch in training')
    parser.add_argument('--batch_size', default=256,  type=int,   help='batch size in training')
    parser.add_argument('--lr',         default=0.01, type=float, help='learning rate')
    parser.add_argument('--use_sigmoid',default=True, help='sigmoid or relu')
    parser.add_argument('--show_preds', action='store_true', help='show preds images')
    parser.add_argument('--use_wandb', action='store_true', default=True, help='') # 修改为默认 True
    parser.add_argument('--logger_iter_interval', type=int, default=50, help='')
    
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

    if args.use_wandb:
        wandb.init(project='WandbTest', config=vars(args), dir='/tmp')
        wandb.run.name = f"{os.path.basename(__file__)[:-3]}_{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"
        # wandb.run.tags = ['tag1', 'tag2']
        args = wandb.config # for wandb.sweep

    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    train_dataset = datasets.CIFAR10(root='/workspace/files/datasets/CIFAR10', train=True, transform=transform, download=False) 
    val_dataset = datasets.CIFAR10(root='/workspace/files/datasets/CIFAR10', train=False, transform=transform, download=False)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    model = LeNet(use_sigmoid=args.use_sigmoid, in_channels=3).to(device)
    optim = Adam(model.parameters(), lr=args.lr)
    loss_fn = CrossEntropyLoss()

    print(args.__dict__)
    all_eval_results = []
    accumulated_iter = 0
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
        plt.imsave('cifar10_pred.png', np.transpose(image.numpy(), (1, 2, 0)))
        print(f"gt:   {' '.join(list(classnames[label[:num_show].cpu().numpy()]))}")
        print(f"pred: {' '.join(list(classnames[pred_label[:num_show]]))}")

if __name__ == '__main__':
    main()
