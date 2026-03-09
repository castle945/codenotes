FROM osrf/ros:noetic-desktop-full

# 个人 shell 环境
apt update ; \
apt install -y git && \
git clone --depth 1 https://gitee.com/city945/oh-my-ubuntu.git ~/.oh-my-ubuntu && \
bash .oh-my-ubuntu/install ; \
rm -rf /var/lib/apt/lists/ && cd && rm -rf .cache .vscode*

# ros conda
# @ manual: install miniconda
conda init zsh
echo "source /opt/ros/setup.zsh" >> .zshrc
pip install rospkg rospy catkin_tools empy numpy opencv-python open3d
rm -rf /var/lib/apt/lists/ && cd && rm -rf .cache .vscode*

# fix bug 
# https://blog.csdn.net/qq_38606680/article/details/129118491
cd /root/miniconda3/lib && mv libffi.so.7 libffi.so.7.bak && ln -s /lib/x86_64-linux-gnu/libffi.so.7.1.0 libffi.so.7
