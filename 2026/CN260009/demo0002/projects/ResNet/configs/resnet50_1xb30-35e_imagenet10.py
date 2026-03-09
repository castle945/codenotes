_base_ = ['../../../configs/_base_/datasets/imagenet10.py', '../../../configs/_base_/default_runtime.py']
custom_imports = dict(
    imports=['projects.ResNet.resnet'], allow_failed_imports=False)

lr = 0.001
optim_wrapper = dict(optimizer=dict(type='Adam', lr=lr))

train_cfg = dict(by_epoch=True, max_epochs=35, val_interval=1)
val_cfg = dict()

model = dict(type='MMResNet')

