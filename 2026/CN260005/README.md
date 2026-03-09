# GitLab CI/CD

### demo0001 - gitlab lfs [ [1](https://docs.pingcode.com/ask/ask-ask/86612.html) ]

先添加 `.gitattributes`，然后正常推送即可，克隆仓库后得到的是文件指针，再 `git lfs pull` 下载实际文件

```Bash
# .gitattributes
# diff=lfs 等参数表示显示这些文件差异时只显示指针差异，如果是本质上是文本文件则 *.cfg filter=lfs -text 视为文本文件显示差异
*.gz filter=lfs diff=lfs merge=lfs

# apt install git-lfs
git lfs install     # 仓库初始化 lfs hooks
git lfs ls-files    # 列出 lfs 文件
git lfs pull        # 拉取 lfs 文件
```

### demo0002 - gitlab.com CI/CD [ [1]() [2](https://jihulab.com/gitlab-cn/gitlab/-/blob/master/lib/gitlab/ci/templates/Python.gitlab-ci.yml)* ]

- 持续集成 CI ：在源代码变更后（git push）后自动检测（code lint）、构建和进行单元测试，尽早发现 bug 降低解决难度
- 编写 `.gitlab-ci.yml` 即可，带此文件的提交 push 后会自动开始 CI 流水线，如果通过可以在项目主页提交 id 那里出现绿色通过标识，示例仓库参考 [pytest4gitci](https://gitlab.com/city945/pytest4gitci)
- Runner 就是运行程序的服务器，默认会使用 gitlab 提供的[小型 Runner](https://gitlab.cn/docs/jh/ci/runners/saas/linux_saas_runner.html) ，小型 Runner 性能差，对应的每分钟消耗 CI 分钟数少
- 指定 Runner 使用官方服务器，在仓库设置->CI/CD->Runner 添加 runner，设置标签即可
- 指定 Runner 使用本地计算机，添加 Runner，设置标签，会转到注册页面，遵循命令在本地计算机安装 gitlab-runner，注册，再运行即可

```bash

# 不想安装在宿主机上，可以用 gitlab/gitlab-runner:ubuntu 镜像，见 demo0003
sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
sudo chmod +x /usr/local/bin/gitlab-runner
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
sudo gitlab-runner start

sudo gitlab-runner register --url https://gitlab.com --registration-token glrt-t1_XCSsxA8YKYY7zMHB_vQg
sudo gitlab-runner run

```

### demo0003 - gitlab-runner CI/CD

#### gitlab-ce [ [安装](https://docs.gitlab.com/ee/install/docker/installation.html) [配置](https://docs.gitlab.com/ee/install/docker/configuration.html) [教程](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-gitlab-on-ubuntu)* [1](https://docs.gitlab.com/runner/install/docker.html) ]

```bash
# gitlab-ce 内部使用 nginx 作为 Web 服务器，nginx 配置文件似乎在 /var/opt/gitlab/nginx/conf 可以通过 apt update; apt install -y mlocate; updatedb; locate nginx
# 主机添加域名解析，即可通过 http://njust.gitlab.com:8929 访问，此容器创建后要等待许久才能访问，期间可能会是 502 错误
echo "127.0.0.1 njust.gitlab.com gitlab.example.comm" | sudo tee -a /etc/hosts > /dev/null

# 如果没设置 GITLAB_ROOT_PASSWORD 或者设置无效
# 则初次登录时，用户名 root 并查看文件获取初始密码，登录进去修改密码，此文件会在 24 小时候自动删除
docker exec -it gitlab-ce cat /etc/gitlab/initial_root_password

# 界面中修改管理员名称、开放普通用户权限（登录后会提示 sign-up 权限，点击 deactivate 进去，取消 enable 复选框保存）
# 创建项目 test 并以 http 方式克隆
git clone http://njust.gitlab.com/root/test.git
# 添加 SSH 公钥并以 ssh 方式克隆，！！注意 firefox 会出现添加 ssh keys 页面和注册用户等页面无响应以及一些显示问题。Safari 添加 ssh key 正常，注册用户会出现其他问题，但是用管理员新建用户可以登录，其实直接用 root 用户即可
git clone ssh://git@njust.gitlab.com:2424/root/test.git
# 或者在 .ssh/config 中添加 gitlab-ce.com 配置简化命令
git clone git@gitlab-ce.com:root/test.git
```

#### gitlab-runner

- 在 gitlab-ce 的仓库设置->CI/CD->Runner 添加 runner，设置标签，随后跳转到注册 Runner 页面，复制命令进行安装和注册，可以直接使用 `gitlab/gitlab-runner:ubuntu` 镜像，本机安装其实也就是安装了个二进制文件，此镜像本质上就是封装该二进制文件命令
- 文档中说的 docker-in-docker 是指 gitlab-runner 命令使用 excutor=docker 并且在阶段的脚本中还是用的 docker 命令，这种需求比较少见而且目前用不到
- ！！注意！！gitlab-runner 的容器不能和 gitlab-ce 在同一台机器上，注册时需要将 url 改成 ip:port 否则会在 CI 时克隆代码错误

```bash
# 直接运行容器命令
docker exec -it gitlab-runner bash -c "gitlab-runner register --non-interactive --name precision-docker-py3.10-RunnerInDocker --url http://192.10.84.160:7106 --clone-url http://192.10.84.160:7106 --executor 'docker' --docker-image docker.unsee.tech/python:3.10 --token glrt-t3_x2gx1TXzekzJyf3a2TMs"
docker exec -it gitlab-runner bash -c "gitlab-runner list"
docker exec -it gitlab-runner bash -c "gitlab-runner unregister --name precision-docker-py3.10-RunnerInDocker"

# 如果使用 docker 且代码中需要用到宿主机文件，则将需要的目录挂在进 gitlab-runner 容器中，且注册命令加 --docker-volumes 选项
docker exec -it gitlab-runner bash -c "gitlab-runner register --non-interactive --name precision-docker-py3.10-RunnerInDocker --url http://192.10.84.160:7106 --clone-url http://192.10.84.160:7106 --executor 'docker' --docker-image docker.unsee.tech/python:3.10 --token glrt-t3_52FD9gfbtGinusWvJVV6 --docker-volumes '/datasets:/datasets' --docker-volumes '/workspace:/workspace'"
# 更复杂的 docker run 命令
docker exec -it gitlab-runner bash -c "\
    gitlab-runner register --non-interactive --url http://192.10.84.160:7106 --clone-url http://192.10.84.160:7106 \
    --executor 'docker' --docker-network-mode 'host' --docker-privileged --docker-runtime 'nvidia' \
    --env 'NVIDIA_VISIBLE_DEVICES=all' \
    --docker-volumes '/datasets:/datasets' --docker-volumes '/workspace:/workspace' \
    --docker-image njust.docker.com/city945/pcdet:cuda11.3-python3.8-pytorch1.11-devel --name precision-pcdet-torch1.11 --token glrt-t1_nsx8_8pxRkz45eykHkBC"

# gitlab-runner 命令
gitlab-runner list # 列出当前注册的 Runner
gitlab-runner unregister --name precision-host

```
