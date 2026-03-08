# Dockerfile 编写


### vnc.Dockerfile - 构建带 VNC 服务的 Ubuntu 桌面镜像 [ [W](https://github.com/AtsushiSaito/docker-ubuntu-sweb) ]

```bash
# 构建
docker build -t castle945/ubuntu:22.04-vnc --build-arg TARGET_TAG=22.04 -f vnc.Dockerfile .
docker build -t castle945/ubuntu:22.04-vnc-humble -f 22.04-vnc-humble.Dockerfile .
# 启动
docker run -itd --privileged=true --ipc=host --network=host --name vnc castle945/ubuntu:22.04-vnc # 末尾不要加命令覆盖之前定义的 CMD
docker run -itd --privileged=true --ipc=host --network=host --restart=always -v ~/workspace:/home/ubuntu/workspace --name ubuntu-desktop castle945/ubuntu:22.04-desktop-full
# 容器内启动/停止/重启进程
supervisorctl start/stop/restart novnc
supervisorctl status   # 查看所有进程的状态
supervisorctl fg novnc # 进程调到前台查看实时打印
# 容器内运行 GUI 程序，或 export DISPLAY=:1
DISPLAY=:1 rviz2
# 清除构建缓存
docker builder prune
```
### 知识点

- 关于 apt 的 --no-install-recommends 参数：别用，会导致依赖不完整后期使用各种 Bug
- ~~多架构镜像：（无用，真机上无法运行）~~

  ```bash
  ---
  # 创建并切换到多架构构建器，创建一次即可
  docker buildx create --use --name multiarch
  docker buildx inspect multiarch --bootstrap # 启动该多架构构建器
  # 构建多架构镜像并发布，强制发布，无法先保存本地故需要事先单架构镜像测试完备
  docker buildx build --platform linux/amd64,linux/arm64 -t castle945/ubuntu:22.04-vnc --build-arg TARGET_TAG=22.04 -f vnc.Dockerfile --push .
  ```

### Dockerfile 代码片段

```dockerfile
ENV DEBIAN_FRONTEND noninteractive          # apt 安装时不要交互按默认选项执行即可
```
