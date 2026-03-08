# docker build -t castle945/pytorch:2.2.0-cuda12.1-python3.10-devel --build-arg BASE_IMAGE='pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel' -f pytorch-based.Dockerfile .
ARG BASE_IMAGE='pytorch/pytorch:1.11.0-cuda11.3-cudnn8-devel'
FROM $BASE_IMAGE

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

# apt package
RUN apt update ; apt upgrade -y \
    && apt install -y zsh sudo wget curl git vim language-pack-zh-hans nfs-common tmux unzip tree \
    && apt autoclean && apt autoremove && rm -rf /var/lib/apt/lists/*

# oh-my-zsh
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone
RUN chsh -s /bin/zsh \
    && git clone https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh \
    && git -C ~/.oh-my-zsh/ checkout 871d4b98 \
    && echo 'export ZSH="$HOME/.oh-my-zsh"' >> ~/.zshrc \
    && echo 'ZSH_THEME="frisk" # robbyrussell sonicradish' >> ~/.zshrc \
    && echo 'plugins=(git docker zsh-autosuggestions safe-paste z)' >> ~/.zshrc \
    && echo "source \$ZSH/oh-my-zsh.sh" >> ~/.zshrc \
    && echo 'export ZSH_DISABLE_COMPFIX=true LANG=zh_CN.UTF-8' >> ~/.zshrc \
    && echo 'setopt HIST_IGNORE_DUPS no_nomatch' >> ~/.zshrc \
    && git clone https://github.com/zsh-users/zsh-autosuggestions.git -b v0.7.1 ~/.oh-my-zsh/plugins/zsh-autosuggestions \
    && git clone https://github.com/junegunn/fzf.git -b v0.67.0 ~/.fzf \
    && ~/.fzf/install --all \
    && echo '[ -f ~/.zsh_aliases ] && source ~/.zsh_aliases' >> ~/.zshrc \
    && echo '[ -f ~/.zsh_functions ] && source ~/.zsh_functions' >> ~/.zshrc \
    && rm -rf ~/.oh-my-zsh/.git ~/.oh-my-zsh/plugins/zsh-autosuggestions/.git ~/.fzf/.git
RUN conda init zsh
