# Docker 私有部署 registry 服务

### docker-registry-ui.yaml - 部署带界面的 registry 服务 [ [W](https://github.com/Joxit/docker-registry-ui) ]

- 关于删除：界面上点删除之后并没有在磁盘上删除镜像，需要再进 registry 容器内执行垃圾回收彻底删除，且仍有空文件夹残留，每次清理完都需要重启容器，否则重新 push 的话之前的镜像不会实际上传

```bash
export registry_path="$(pwd)/registry" && docker compose -f docker-registry-ui.yml up -d

# 客户端还需如下配置，并重启服务
write to /etc/docker/daemon.json
{
    "insecure-registries": [
	      "njust.docker.com" or "ip:port"
    ]
}
sudo systemctl restart docker

# 界面上删除，再进 registry 容器实际删除并重启容器
registry garbage-collect /etc/docker/registry/config.yml
# 如果全删除则更省事的办法是删除 $registry_path 目录并重新创建 registry 容器
```
