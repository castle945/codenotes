# @# 数据集
batch_size = 32
norm_cfg = dict(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
train_dataloader = dict(
    batch_size=batch_size,
    num_workers=4,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True, round_up=True), # 此参数与 Dataloader 的 shuffle 参数冲突，指定 shuffle=True 则会执行 RandomSampler，round_up 默认值为 True 等价于 Dataloader 的 drop_last=False
    collate_fn=dict(type='default_collate'), # 一般要加，否则默认值是 pseudo_collate 会和 Pytorch 中的默认值(default_collate)行为不同
    # num_batch_per_epoch=20, # @! 每个 epoch 只迭代 20 个批量，要求是继承数据集基类的，可用于调试
    dataset=dict(
        type='ImageNet10Dataset',
        data_root='./data/imagenet10',
        ann_file='imagenet10_infos_train.json',
        data_prefix=dict(img_path='train/'),
        # indices=640,            # 每个 epoch 只迭代 640 个样本，效果同 num_batch_per_epoch 参数
        pipeline=[
            dict(type='LoadImage'),
            dict(type='MyRandomResizedCrop', size=224),
            dict(type='MyRandomHorizontalFlip'),
            dict(type='MyToTensor'),
            dict(type='MyNormalize', **norm_cfg)
        ],
    ),
)
val_dataloader = dict(
    batch_size=batch_size,
    num_workers=4,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    collate_fn=dict(type='default_collate'),
    dataset=dict(
        type='ImageNet10Dataset',
        data_root='./data/imagenet10',
        ann_file='imagenet10_infos_val.json',
        data_prefix=dict(img_path='val/'),
        test_mode=True,
        pipeline=[
            dict(type='LoadImage'),
            dict(type='MyResize', size=(224, 224)),
            dict(type='MyToTensor'),
            dict(type='MyNormalize', **norm_cfg)
        ],
    ),
)

# @# 模型
model = dict(type='MMResNet')

# @# 优化器封装
lr = 0.001
optim_wrapper = dict(optimizer=dict(type='Adam', lr=lr))

# @# 参数调度器
# param_scheduler = dict(type='MultiStepLR', by_epoch=True, milestones=[4, 8], gamma=0.1) # 支持传入 [{}] 对同一个超参数的多个阶段或多个超参数精细调整

# @# 运行时
work_dir = 'work_dirs'
train_cfg = dict(by_epoch=True, max_epochs=35, val_interval=1)
val_cfg = dict()
val_evaluator = dict(type='Accuracy') # 支持传入 [{}] 同时评测多个指标

# 依次解注释查看运行效果
# 恢复训练
# resume = True                         # 会在当前实验目录下新建一个时间戳命名的新目录存放日志数据，日志数据被截断、检查点模型正常
# load_from = './work_dirs/epoch_2.pth' # 指定从哪个检查点模型恢复，默认从最后一个

# 分布式训练 没有定制 MMDistributedDataParallel 的需要
# CUDA_VISIBLE_DEVICES=0,1 torchrun --nproc_per_node=2 --rdzv_endpoint=localhost:43210 ResNet50_Cifar10.py --launcher pytorch

# 混精度训练 2936M->2760M
# optim_wrapper = dict(type='AmpOptimWrapper', optimizer=dict(type='Adam', lr=lr)) # 可以并存覆盖之前的同名配置

# 梯度累加 2936M->2566M 同时要求 batch_size/4=64
# optim_wrapper = dict(type='OptimWrapper', accumulative_counts=4, optimizer=dict(type='Adam', lr=lr))

# 模型编译，torch>=2.0 传入编译参数，略
# 性能更优的第三方优化器，需额外安装包，略，用法如 optim_wrapper = dict(optimizer=dict(type='DAdaptAdaGrad', lr=0.001, momentum=0.9))

# 可视化日志
# tensorboard --logdir 20250524_152435/vis_data --port 6007
# visualizer = dict(type='Visualizer', vis_backends=[dict(type='TensorboardVisBackend')])
# pip install wandb && wandb login
visualizer = dict(type='Visualizer', vis_backends=[dict(type='WandbVisBackend', init_kwargs=dict(project="WandbTest", name="250526", tags=["tag1", "tag2"]))])

# 设置随机种子
# randomness = dict(seed=0, deterministic=True)

# 设置模型验证、权重保存、日志打印的频率
# train_cfg = dict(by_epoch=True, max_epochs=20, val_begin=10, val_interval=2)     # 从第 10 轮开始验证，每 2 轮验证一次
# default_hooks = dict(
#     checkpoint=dict(type='CheckpointHook', interval=2),
#     logger=dict(type='LoggerHook', interval=50),        # 默认值为间隔 10 iter
# )

# 设置 find_unused_parameters=True 和 detect_anomalous_params=True 来实现打印未使用的模型参数和未参与 loss 计算的模型参数，略

# 内置钩子用法
# default_hooks = dict(
    # checkpoint=dict(type='CheckpointHook', max_keep_ckpts=5),                     # 最多保存最新的 5 个权重
    # checkpoint=dict(type='CheckpointHook', save_best='accuracy', rule='greater'), # 评测器返回的评价指标为有序字典，值为 auto 则根据评价指标的第一个指标判断最优权重
    # checkpoint=dict(type='CheckpointHook', save_last=True, published_keys=['meta', 'state_dict']), # 指定发布权重包含的值，可删除优化器状态等不需要的值，同样可用于 save_best
    # checkpoint=dict(type='CheckpointHook', interval=2, save_begin=10),            # 从第 10 轮开始保存，每 2 轮保存一次
    # 默认钩子的逻辑: 默认 6 个内置钩子都有都用默认参数，如果传入某个钩子的配置参数，参数非空则更新该钩子的参数，参数为 None 则禁用该钩子(钩子数才会下降)
    # logger=None, # 禁用某个默认钩子，当关闭日志钩子即使开启 Tensorboard 后端，不会记录数据
# )

# 调试模式
# work_dir = 'work_dirs/debug'
# randomness = dict(seed=0)
# train_dataloader.batch_size = 1
# train_dataloader.num_workers = 0
# train_dataloader.persistent_workers = False
# train_dataloader.num_batch_per_epoch = 4
# train_cfg = dict(by_epoch=True, max_epochs=2, val_interval=1)