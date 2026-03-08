FROM castle945/ubuntu:22.04-vnc-humble

# apt package
RUN sudo -E apt update \
    && sudo -E apt install -y rsync unrar git-lfs lsof net-tools iputils-ping \
    && sudo apt autoclean && sudo apt autoremove && sudo rm -rf /var/lib/apt/lists/*

# conda
ENV PATH=/home/$USER/miniconda3/bin:$PATH
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py310_24.4.0-0-Linux-aarch64.sh -O miniconda.sh \
    && bash miniconda.sh -b -f \
    && rm -f miniconda.sh && conda clean -a -y

# pu4c
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN conda create -n pu4c python=3.10 -y \
    && conda run -n pu4c pip install --no-cache-dir numpy==1.26.0 opencv-python==4.9.0.80 'open3d<=0.18.0' pu4c ipython \
    && conda clean -a -y

# rospyutils
# 关于 ros+conda: 一旦 source 完会将 ros 中安装的 Python 包加到所有 conda 环境，这里需要一起算故 source，日常用 conda 不要 source
SHELL ["/bin/zsh", "-c"]
RUN source /opt/ros/humble/setup.zsh && conda run -n base pip install --no-cache-dir 'numpy<2' opencv-python pu4c pandas easydict nuscenes-devkit==1.1.11

# oh-my-zsh
RUN sudo chsh -s /bin/zsh $USER \
    && git clone --depth 1 https://gitee.com/city945/oh-my-ubuntu.git -b city945 \
    && bash oh-my-ubuntu/install \
    && rm -rf oh-my-ubuntu

# misc
RUN conda init zsh \
    && echo 'export DISPLAY=:1' >> ~/.zshrc \
    && sudo mkdir /datasets /workspace
# && echo 'source /opt/ros/humble/setup.zsh' >> ~/.zshrc # 不要加上，影响 conda 的使用

# supervisor
RUN sudo tee /etc/supervisor/conf.d/pu4c.conf >/dev/null <<EOF
[program:pu4c]
command=$HOME/miniconda3/envs/pu4c/bin/python -c 'import pu4c; pu4c.common.start_rpc_server()'
environment=DISPLAY=:1
autorestart=true
EOF
RUN sudo tee /etc/supervisor/conf.d/startup.conf >/dev/null <<EOF
[program:startup]
command=/bin/bash $HOME/.startup.sh
priority=999       ; 1 for first run, usually 999 for latest run
autorestart=false
startretries=0
EOF
RUN sudo tee $HOME/.startup.sh >/dev/null <<EOF
sudo mount 192.10.84.60:/datasets /datasets 
sudo mount 192.10.84.60:/home/xc/workspace /workspace
sudo service cron start
tail -f /dev/null
EOF

# crontab
# RUN echo "30 6 * * * rsync -av --stats --delete --exclude-from='/workspace/codevault/.rsync-exclude' /workspace/codevault/ /home/$USER/workspace/codevault/ >> /tmp/cron_backup_ws.log" | crontab -u $USER -

# 改分辨率、改用户密码、设置 plank 并自启、改终端配色
# apt install -y cmake g++ gdb pkg-config mlocate libgoogle-glog-dev libyaml-cpp-dev libpcap-dev