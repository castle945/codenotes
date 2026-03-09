# LeNet MNIST 训练脚本
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from torchvision import datasets, transforms
from tu4c.models import LeNet
from tu4c.utils import create_logger

import argparse, tqdm, datetime, os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--epochs',     default=20,   type=int,   help='number of epoch in training')
    parser.add_argument('--batch_size', default=256,  type=int,   help='batch size in training')
    parser.add_argument('--lr',         default=0.01, type=float, help='learning rate')
    
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

    train_dataset = datasets.mnist.MNIST(root='/workspace/files/datasets', train=True, transform=transforms.ToTensor(), download=False)
    val_dataset = datasets.mnist.MNIST(root='/workspace/files/datasets', train=False, transform=transforms.ToTensor(), download=False)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    model = LeNet().to(device)
    optim = Adam(model.parameters(), lr=args.lr)
    loss_fn = CrossEntropyLoss()

    logger.info(args.__dict__)
    all_eval_results = []
    for epoch in range(args.epochs):
        train_loss_sum, train_acc_sum, n = 0.0, 0.0, 0
        model.train()
        for input, label in tqdm.tqdm(train_loader):
            input, label = input.to(device), label.to(device)
            # (B, 28, 28)->(B, 10)
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
if __name__ == '__main__':
    main()
