#!/bin/bash

curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# https://www.cnblogs.com/songxi/p/12788249.html
sudo usermod -aG docker $USER
sudo systemctl restart docker # ! 服务器重新登录shell，个人PC则logout使生效

# docker-compose
# 如果镜像站 github.com 崩了换其他站，这里手动操作下
# https://github.com/docker/compose/releases
# bug https://forums.docker.com/t/unsupported-config-option-for-services-profiles/103767
# sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
# sudo chmod +x /usr/local/bin/docker-compose # 有可能 /usr/bin 中已有此文件，覆盖它


# 添加 apt-key
curl -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && distribution=$(. /etc/os-release;echo $ID$VERSION_ID) 
# 添加阿里云仓库
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
# 更新库
sudo apt-get update
# 查看当前库对应的 nvidia-docker2 可用的版本
sudo apt-cache madison nvidia-docker2
sudo apt-get install -y nvidia-docker2  && sudo pkill -SIGHUP dockerd
# 查看 nvidia-docker 版本
nvidia-docker --version