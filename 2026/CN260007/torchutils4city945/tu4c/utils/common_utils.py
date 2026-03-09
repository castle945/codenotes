import logging
import random
import numpy as np
import torch

def create_logger(log_file=None, rank=0):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO if rank == 0 else 'ERROR')
    formatter = logging.Formatter('%(asctime)s  %(levelname)5s  %(message)s')
    # 打印到控制台
    console = logging.StreamHandler()
    console.setLevel(logging.INFO if rank == 0 else 'ERROR')
    console.setFormatter(formatter)
    logger.addHandler(console)
    # 打印到日志文件
    if log_file is not None:
        file_handler = logging.FileHandler(filename=log_file)
        file_handler.setLevel(logging.INFO if rank == 0 else 'ERROR')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.propagate = False # 不要再将该 logger 记录的日志消息传递给其父级 logger
    return logger

def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.benchmark = False      # 禁用 cuDNN 的自动优化，以确保结果的确定性
    torch.backends.cudnn.deterministic = True   # 启用确定性算法，以确保结果的确定性，pytorch <= 1.8.0 时，只能保证卷积操作确定
    torch.use_deterministic_algorithms(True, warn_only=True)    # 启用确定性算法，以确保结果的确定性，pytorch >= 1.9.0 时，可以保证所有操作的确定性，并且对于可能导致不确定的地方报错