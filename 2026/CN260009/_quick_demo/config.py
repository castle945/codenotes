# @# 数据集
batch_size = 256
norm_cfg = dict(mean=[0.491, 0.482, 0.447], std=[0.202, 0.199, 0.201])
train_dataloader = dict(
    batch_size=batch_size,
    sampler=dict(type='DefaultSampler', shuffle=True),
    collate_fn=dict(type='default_collate'),
    dataset=dict(
        type='Cifar10',
        root='/workspace/files/datasets/CIFAR10',
        train=True,
        transform=[
            dict(type='RandomCrop', size=32, padding=4),
            dict(type='RandomHorizontalFlip'),
            dict(type='MyToTensor'),
            dict(type='MyNormalize', **norm_cfg)
        ],
        download=True
    ),
)
val_dataloader = dict(
    batch_size=batch_size,
    sampler=dict(type='DefaultSampler', shuffle=False),
    collate_fn=dict(type='default_collate'),
    dataset=dict(
        type='Cifar10',
        root='/workspace/files/datasets/CIFAR10',
        train=False,
        transform=[
            dict(type='MyToTensor'),
            dict(type='MyNormalize', **norm_cfg)
        ],
        download=True
    ),
)

# @# 模型
model = dict(type='MMResNet')

# @# 优化器封装
lr = 0.01
optim_wrapper = dict(optimizer=dict(type='Adam', lr=lr))

# @# 运行时
work_dir = 'work_dirs'
train_cfg = dict(by_epoch=True, max_epochs=20, val_interval=1)
val_cfg = dict()
val_evaluator = dict(type='Accuracy')
