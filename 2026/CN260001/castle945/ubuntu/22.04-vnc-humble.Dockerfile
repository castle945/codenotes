FROM castle945/ubuntu:22.04-vnc

# ROS
RUN sudo tee fish_install.yaml >/dev/null <<EOF
chooses:
- { choose: 1, desc: "一键安装(推荐):ROS(支持ROS/ROS2,树莓派Jetson)" }
- { choose: 1, desc: "更换系统源再继续安装" }
- { choose: 2, desc: "更换系统源并清理第三方源" }
- { choose: 1, desc: "自动测速选择最快的源" }
- { choose: 1, desc: "中科大镜像源 (推荐国内用户使用)" }
- { choose: 1, desc: "humble(ROS2)" }
- { choose: 1, desc: "humble(ROS2)桌面版" }
EOF
RUN sudo -E apt update \
    && sudo -E apt install -y build-essential python3-pip python3-yaml \
    && wget http://fishros.com/install -O fishros && /bin/bash fishros \
    && sudo -E apt install -y python3-colcon-common-extensions \
    && sudo apt autoclean && sudo apt autoremove && sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* fish_install.yaml
RUN echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc \
    && sudo bash -c "echo 'eval \"\$(register-python-argcomplete3 ros2)\"' >> /opt/ros/humble/setup.bash" \
    && sudo bash -c "echo 'eval \"\$(register-python-argcomplete3 colcon)\"' >> /opt/ros/humble/setup.bash" \
    && sudo bash -c "echo 'eval \"\$(register-python-argcomplete3 ros2)\"' >> /opt/ros/humble/setup.zsh" \
    && sudo bash -c "echo 'eval \"\$(register-python-argcomplete3 colcon)\"' >> /opt/ros/humble/setup.zsh"
