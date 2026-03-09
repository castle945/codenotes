
from mmengine.dataset.base_dataset import BaseDataset
from mmdemo.registry import DATASETS
import os

@DATASETS.register_module()
class ImageNet10Dataset(BaseDataset):
    def parse_data_info(self, raw_data_info):
        data_info = raw_data_info
        img_prefix = self.data_prefix.get('img_path', None)
        if img_prefix is not None:
            classname = self._metainfo['classes'][data_info['img_label']]
            data_info['img_path'] = os.path.join(img_prefix, classname, data_info['img_path'])
        return data_info
