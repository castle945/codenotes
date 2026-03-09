"""
LeNet FashionMNIST dist train (pytorch > 1.10)
Usage: 
    python LeNet_FashionMNIST_ddp.py
    torchrun --nproc_per_node=2 LeNet_FashionMNIST_ddp.py --dist
    torchrun --nproc_per_node=2 --rdzv_endpoint=localhost:29501 LeNet_FashionMNIST_ddp.py --dist
"""
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from torchvision import datasets, transforms
from tu4c.models import LeNet
from tu4c.utils import create_logger

import argparse, tqdm, datetime, os
import torch.distributed as dist

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--epochs',     default=20,   type=int,   help='number of epoch in training')
    parser.add_argument('--batch_size', default=256,  type=int,   help='batch size in training')
    parser.add_argument('--lr',         default=0.01, type=float, help='learning rate')
    parser.add_argument("--dist", action="store_true", help="DDP")
    
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
    # 初始化
    if args.dist:
        torch.distributed.init_process_group(backend="nccl")
        torch.cuda.set_device(dist.get_rank() % torch.cuda.device_count())
    args.rank = dist.get_rank() if args.dist else 0
    logger = create_logger(log_file=f"{os.path.basename(__file__)[:-3]}_{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.log")

    train_dataset = datasets.FashionMNIST(root='/workspace/files/datasets/FashionMNIST/train', train=True, transform=transforms.ToTensor(), download=False)
    val_dataset = datasets.FashionMNIST(root='/workspace/files/datasets/FashionMNIST/test', train=False, transform=transforms.ToTensor(), download=False)
    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset) if args.dist else None
    val_sampler = torch.utils.data.distributed.DistributedSampler(val_dataset) if args.dist else None
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, sampler=train_sampler)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, sampler=val_sampler)

    model = LeNet().to(device)
    if args.dist:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[dist.get_rank()])
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
        # DDP 会开多个进程，多次运行 train.py，确保只有一次打印 
        if args.rank == 0:
            logger.info(f'epoch {epoch+1}, loss sum {train_loss_sum:.3f}, train acc {train_acc:.3f}, val acc {test_acc:.3f}')
        all_eval_results.append({'epoch': epoch+1, 'train_acc': train_acc, 'val_acc': test_acc})

    sorted_results = sorted(all_eval_results, key=lambda x: x['val_acc'], reverse=True)
    logger.info(f'best: val acc: {sorted_results[0]["val_acc"]:.3f} epoch {sorted_results[0]["epoch"]}')
if __name__ == '__main__':
    main()
