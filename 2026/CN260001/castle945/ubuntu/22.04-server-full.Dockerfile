FROM castle945/pytorch:2.2.0-cuda12.1-python3.10-devel

# code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --version 4.108.0 \
    && rm -rf ~/.cache

# aliyunpan
RUN wget https://github.com/tickstep/aliyunpan/releases/download/v0.3.7/aliyunpan-v0.3.7-linux-amd64.zip -O aliyunpan.zip \
    && unzip aliyunpan.zip -d /tmp/ && mv /tmp/aliyunpan-*/aliyunpan /usr/local/bin/ \
    && rm -rf aliyunpan.zip /tmp/*

# pu4c
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir numpy==1.26.0 opencv-python==4.9.0.80 'open3d<=0.18.0' pu4c ipykernel setuptools wheel twine

# apt package
RUN apt update ; apt upgrade -y \
    && apt install -y rsync unrar git-lfs lsof net-tools iputils-ping \
    && apt install -y supervisor openssh-client \
    && apt autoclean && apt autoremove && rm -rf /var/lib/apt/lists/*

# Supervisor
ENV CODE_PASSWD=root
RUN mkdir -p /root/.config/code-server && cat > /root/.config/code-server/config.yaml <<EOF
bind-addr: 0.0.0.0:9117
auth: password
password: $CODE_PASSWD
cert: false
EOF
RUN cat > /etc/supervisor/conf.d/code-server.conf <<EOF
[program:code-server]
command=code-server
EOF
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]

# 改密码
