# dataset settings
dataset_type = 'ImageNet10Dataset'
data_root = 'data/imagenet10/'
batch_size = 32
norm_cfg = dict(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])

train_pipeline = [
    dict(type='LoadImage'),
    dict(type='MyRandomResizedCrop', size=224),
    dict(type='MyRandomHorizontalFlip'),
    dict(type='MyToTensor'),
    dict(type='MyNormalize', **norm_cfg)
]
test_pipeline = [
    dict(type='LoadImage'),
    dict(type='MyResize', size=(224, 224)),
    dict(type='MyToTensor'),
    dict(type='MyNormalize', **norm_cfg)
]

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
        pipeline=train_pipeline,
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
        pipeline=test_pipeline,
    ),
)

val_evaluator = dict(type='Accuracy') # 支持传入 [{}] 同时评测多个指标

# tensorboard --logdir 20250524_152435/vis_data --port 6007
# vis_backends = [dict(type='TensorboardVisBackend')]
# pip install wandb && wandb login
# vis_backends = [dict(type='WandbVisBackend', init_kwargs=dict(project="WandbTest", name="250526", tags=["tag1", "tag2"]))]
# visualizer = dict(type='Visualizer', vis_backends=vis_backends)
