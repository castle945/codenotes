ARG TARGET_TAG=22.04
FROM ubuntu:$TARGET_TAG

ENV DEBIAN_FRONTEND=noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# mate desktop
RUN apt update && apt upgrade -y \
    && apt install -y ubuntu-mate-desktop \
    && apt autoclean && apt autoremove && rm -rf /var/lib/apt/lists/*

# apt package
RUN apt update \
    && apt install -y tigervnc-standalone-server tigervnc-common novnc supervisor gosu \
    && apt install -y zsh sudo wget curl git vim language-pack-zh-hans nfs-common tmux unzip tree \
    && apt autoclean && apt autoremove && rm -rf /var/lib/apt/lists/*
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# user
# If you use the desktop system as root, there will be various GUI program errors.
ENV USER=ubuntu PASSWD=ubuntu
RUN useradd -m -s /bin/bash -G sudo $USER \
    && echo $USER:$PASSWD | /usr/sbin/chpasswd \
    && echo "$USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $USER
WORKDIR /home/$USER/

# supervisor
RUN sudo tee /etc/supervisor/supervisord.conf >/dev/null <<EOF
; supervisor config file for non-root user
[unix_http_server]
file=/tmp/supervisor.sock   ; (the path to the socket file)
chmod=0700                  ; sockef file mode (default 0700)
[supervisord]
logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
childlogdir=/tmp/            ; ('AUTO' child log dir, default $TEMP)
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket
[include]
files = /etc/supervisor/conf.d/*.conf
EOF
RUN sudo tee /etc/supervisor/conf.d/vnc.conf >/dev/null <<EOF
[program:vnc]
command=vncserver :1 -fg -geometry 1920x1080 -SecurityTypes None
[program:novnc]
command=/usr/share/novnc/utils/launch.sh --listen 6081 --vnc localhost:5901
EOF
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
