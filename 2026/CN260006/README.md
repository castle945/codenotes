# Nginx 反向代理

### 知识点 [ [1](https://github.com/dunwu/nginx-tutorial) [2](https://javabetter.cn/nginx/nginx.html#%E4%B8%80%E3%80%81nginx-%E7%9A%84%E4%BD%9C%E7%94%A8) ]

- 简介：轻量级的 Web 服务器 、反向代理服务器及电子邮件（IMAP/POP3）代理服务
- 反向代理：反向代理服务器接收外网连接请求，转发给内部网络的服务器。正向的代理服务器是接收内部各服务器的请求，发送到外网
- 安装
    ```bash
    docker pull nginx:1.27-bookworm-perl
    docker run -itd --network=host --name nginx-server nginx:1.27-bookworm-perl
    docker exec -it nginx-server bash
    # 访问 http://localhost:80

    # 配置文件
    /etc/nginx/conf.d/
    # 首页路径
    /usr/share/nginx/
    ```
- 命令大全
    ```bash
    nginx           # 启动
    nginx -s stop   # 停止
    nginx -s quit   # 安全退出，保存信息
    nginx -s reload # 重新加载配置文件
    nginx -t    # 检查配置文件是否正确
    nginx -V    # 显示 nginx 的版本，编译器版本和配置参数。
    ```

### demo0001 - 简单反向代理示例

访问 http://demo0001.com 转发到 本地 9010 端口的服务

```bash
python -m http.server 9010 # 启动一个 http 服务，http://localhost:9010

# set cfg_path='xxx/demo0001.conf'
docker run -itd --network=host -v $cfg_path:/etc/nginx/conf.d/demo0001.conf --name nginx-server nginx:1.27-bookworm-perl

echo "127.0.0.1 demo0001.com" >> /etc/hosts # 添加域名解析
# 访问 http://demo0001.com 即可

# 若修改配置文件，进容器重新加载
docker exec -it nginx-server bash
nginx -s reload # 重新加载配置文件

```
