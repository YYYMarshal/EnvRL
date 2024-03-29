from torch.utils.data import Dataset
from PIL import Image
import os

"""
这个代码文件运行的时候，需要将 hymenoptera_data 文件夹放到桌面

2024-3-2 15:34:18：
将 hymenoptera_data 文件夹放进了 "项目目录/XtdPyTorch" 中，并添加进了 .gitignore 中，
所以如果采用了后者的方式，该代码文件中的部分代码需要做相应的修改。
"""


class MyData(Dataset):
    def __init__(self, root_dir, label_dir):
        self.root_dir = root_dir
        self.label_dir = label_dir
        self.path = os.path.join(self.root_dir, self.label_dir)
        self.img_path = os.listdir(self.path)

    def __getitem__(self, idx):
        img_name = self.img_path[idx]
        img_item_path = os.path.join(
            self.root_dir, self.label_dir, img_name)
        img = Image.open(img_item_path)
        label = self.label_dir
        return img, label

    def __len__(self):
        return len(self.img_path)


def test():
    # help(Dataset)
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    print(desktop_path)
    img_path = os.path.join(
        # desktop_path, r"hymenoptera_data\train\ants\0013035.jpg")
        desktop_path, r"hymenoptera_data\train\ants_image\0013035.jpg")
    print(img_path)
    img = Image.open(img_path)
    print(img.size)
    img.show()


def main():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    root_dir = os.path.join(desktop_path, r"hymenoptera_data\train")

    # ants_label_dir = r"ants"
    ants_label_dir = r"ants_image"
    ants_dataset = MyData(root_dir, ants_label_dir)

    # bees_label_dir = r"bees"
    bees_label_dir = r"bees_image"
    bees_dataset = MyData(root_dir, bees_label_dir)

    train_dataset = ants_dataset + bees_dataset

    ants_idx = 1
    ants_img, ants_label = ants_dataset[ants_idx]
    ants_img.show()

    idx = 124
    img, label = train_dataset[idx]
    img.show()


# test()
main()
