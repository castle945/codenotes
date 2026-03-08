FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

# apt package
RUN apt update && apt upgrade -y \
    && apt install -y zsh sudo wget curl git vim language-pack-zh-hans nfs-common tmux unzip tree \
    && apt autoclean && apt autoremove ; rm -rf /var/lib/apt/lists/*

# conda
ENV PATH=/opt/conda/bin:$PATH
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py38_23.5.2-0-Linux-x86_64.sh -O miniconda.sh \
    && bash miniconda.sh -b -f -p /opt/conda \
    && rm -f miniconda.sh && conda clean -a -y

# torch
RUN pip install --no-cache-dir torch==1.9.1+cu111 torchvision==0.10.1+cu111 torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html

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
