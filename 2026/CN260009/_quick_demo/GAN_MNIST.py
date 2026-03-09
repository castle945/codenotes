# GAN MNIST MMEngine 训练脚本，MMengine 风格，不使用配置文件
# 参考: https://mmengine.readthedocs.io/zh_CN/latest/examples/train_a_gan.html

from torch.optim import Adam
import torch
from mmengine.runner import Runner
from mmengine.optim import OptimWrapper, OptimWrapperDict

# @# 数据集
from mmengine.dataset import BaseDataset
from torchvision.datasets import MNIST
from mmcv.transforms import to_tensor
import numpy as np
class MNISTDataset(BaseDataset):
    def __init__(self, data_root, pipeline, test_mode=False):
        # 不管训练测试都拿测试集中的 10000 个样本来做，反正不需要图片的类别标签
        self.mnist_dataset = MNIST(data_root, train=False, download=False)
        super().__init__(data_root=data_root, pipeline=pipeline, test_mode=test_mode)

    @staticmethod
    def totensor(img):
        # (28, 28) -> (28, 28, 1) -> (1, 28, 28)
        if len(img.shape) < 3:
            img = np.expand_dims(img, -1)
        img = np.ascontiguousarray(img.transpose(2, 0, 1))
        return to_tensor(img)

    def load_data_list(self):
        return [
            # (PIL.Image, label) 的元组，取 x[0] 得到 (28, 28) 的图片
            dict(inputs=self.totensor(np.array(x[0]))) for x in self.mnist_dataset
        ]

# @# 模型
# @## 生成器模型: 堆叠的多个全连接层，输出 shape(B, 1*28*28)，最后展平为 (B, 1, 28, 28) 作为生成的图片
import torch.nn as nn
class Generator(nn.Module):
    def __init__(self, noise_size, img_shape):
        """
        Args:
            noise_size: 第一层的输入通道
        """
        super().__init__()
        self.img_shape = img_shape
        self.noise_size = noise_size

        def block(in_feat, out_feat, normalize=True):
            layers = [nn.Linear(in_feat, out_feat)]
            if normalize:
                layers.append(nn.BatchNorm1d(out_feat, 0.8))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *block(noise_size, 128, normalize=False),
            *block(128, 256),
            *block(256, 512),
            *block(512, 1024),
            # np.prod 计算所有元素的乘积，即 1 * 28 * 28
            nn.Linear(1024, int(np.prod(img_shape))),
            nn.Tanh(),
        )

    def forward(self, z):
        """
        每给定一个 noise_size 长度的向量，model 生成 1 * 28 * 28 的图片
        Args:
            z: shape(B, noise_size)
        """
        img = self.model(z)
        img = img.view(img.size(0), *self.img_shape)
        return img

# @## 判别器模型: 一堆堆叠的全连接层，输入图片 shape(B, 1, 28, 28)，输出 shape(B, 1)，即二分类结果
class Discriminator(nn.Module):
    def __init__(self, img_shape):
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(int(np.prod(img_shape)), 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )

    def forward(self, img):
        img_flat = img.view(img.size(0), -1)
        validity = self.model(img_flat)

        return validity

# @## GAN 模型
import torch.nn.functional as F
from mmengine.model import BaseModel
from mmengine.model import ImgDataPreprocessor
# 设置 requires_grad 以冻结或解冻模型参数，用于训练生成器时冻结判别器的参数
def set_requires_grad(nets, requires_grad=False):
    if not isinstance(nets, list):
        nets = [nets]
    for net in nets:
        if net is not None:
            for param in net.parameters():
                param.requires_grad = requires_grad
class GAN(BaseModel):
    def __init__(self, generator, discriminator, noise_size, data_preprocessor):
        """
        Args:
            data_preprocessor: ImgDataPreprocessor 实例，用于给定 std 和 mean 对图像进行归一化
        """
        super().__init__(data_preprocessor=data_preprocessor)
        assert generator.noise_size == noise_size
        self.generator = generator
        self.discriminator = discriminator
        self.noise_size = noise_size

    def train_step(self, data, optim_wrapper):
        """
        Args:
            data: dict_keys(['inputs', 'sample_idx'])
                inputs: [Size(1, 28, 28),..., len(batch_size)]
                sample_idx: len(batch_size)
        Locals:
            inputs_dict: dict_keys(['inputs', 'sample_idx', 'data_samples'])
                inputs: Size(B, 1, 28, 28)
                data_samples: None
        """
        inputs_dict = self.data_preprocessor(data, True)
        # 训练判别器
        disc_optimizer_wrapper = optim_wrapper['discriminator']
        with disc_optimizer_wrapper.optim_context(self.discriminator):
            log_vars = self.train_discriminator(inputs_dict, disc_optimizer_wrapper)

        # 训练生成器
        set_requires_grad(self.discriminator, False)
        gen_optimizer_wrapper = optim_wrapper['generator']
        with gen_optimizer_wrapper.optim_context(self.generator):
            log_vars_gen = self.train_generator(inputs_dict, gen_optimizer_wrapper)

        set_requires_grad(self.discriminator, True)
        log_vars.update(log_vars_gen)

        return log_vars

    def forward(self, batch_inputs, data_samples=None, mode=None):
        # 模型预测，输入
        return self.generator(batch_inputs)

    def disc_loss(self, disc_pred_fake, disc_pred_real):
        # 计算判别器的损失，判别器应该使生成图片的预测结果尽可能为 0，原始图片的预测结果尽可能为 1
        losses_dict = dict()
        # 预测值与目标值越接近，损失越小
        losses_dict['loss_disc_fake'] = F.binary_cross_entropy(
            disc_pred_fake, 0. * torch.ones_like(disc_pred_fake))
        losses_dict['loss_disc_real'] = F.binary_cross_entropy(
            disc_pred_real, 1. * torch.ones_like(disc_pred_real))

        loss, log_var = self.parse_losses(losses_dict)
        return loss, log_var

    def gen_loss(self, disc_pred_fake):
        # 计算生成器的损失，生成器应该使生成图片的预测结果尽可能为 1
        losses_dict = dict()
        losses_dict['loss_gen'] = F.binary_cross_entropy(
            disc_pred_fake, 1. * torch.ones_like(disc_pred_fake))
        loss, log_var = self.parse_losses(losses_dict)
        return loss, log_var

    def train_discriminator(self, inputs, optimizer_wrapper):
        # 训练判别器
        real_imgs = inputs['inputs'] # Size(B, 1, 28, 28)
        z = torch.randn((real_imgs.shape[0], self.noise_size)).type_as(real_imgs)
        with torch.no_grad():
            fake_imgs = self.generator(z)

        disc_pred_fake = self.discriminator(fake_imgs)
        disc_pred_real = self.discriminator(real_imgs)

        parsed_losses, log_vars = self.disc_loss(disc_pred_fake, disc_pred_real)
        optimizer_wrapper.update_params(parsed_losses)
        return log_vars

    def train_generator(self, inputs, optimizer_wrapper):
        # 训练生成器
        real_imgs = inputs['inputs'] # shape(B, 1, 28, 28)
        z = torch.randn(real_imgs.shape[0], self.noise_size).type_as(real_imgs)
        fake_imgs = self.generator(z) # 输入批量大小 B 和噪声维度 100，输出 shape(B, 1, 28, 28)

        disc_pred_fake = self.discriminator(fake_imgs)
        parsed_loss, log_vars = self.gen_loss(disc_pred_fake)

        optimizer_wrapper.update_params(parsed_loss)
        return log_vars

def main():
    train_dataloader = Runner.build_dataloader(
        dict(
            batch_size=256,
            num_workers=8,
            persistent_workers=True,
            sampler=dict(type='DefaultSampler', shuffle=True),
            dataset=MNISTDataset("/workspace/files/datasets/", [], test_mode=False)
        )
    )
    generator = Generator(noise_size=100, img_shape=(1, 28, 28))
    discriminator = Discriminator(img_shape=(1, 28, 28))
    model = GAN(generator, discriminator, 100, ImgDataPreprocessor(mean=([127.5]), std=([127.5])))

    opt_g_wrapper = OptimWrapper(optimizer=Adam(generator.parameters(), lr=0.0001, betas=(0.5, 0.999)))
    opt_d_wrapper = OptimWrapper(optimizer=Adam(discriminator.parameters(), lr=0.0001, betas=(0.5, 0.999)))

    runner = Runner(
        model=model,
        work_dir='work_dirs/',
        train_dataloader=train_dataloader,
        train_cfg=dict(by_epoch=True, max_epochs=220),
        optim_wrapper=OptimWrapperDict(generator=opt_g_wrapper, discriminator=opt_d_wrapper)
    )
    runner.train()

    from torchvision.utils import save_image
    pred_image = model(torch.randn(64, 100).cuda()) # shape(64, 100) 输入 64 个噪声向量，生成 64 张图片
    save_image(pred_image, "GAN_MNIST_preds.png", normalize=True)

if __name__ == '__main__':
    main()
