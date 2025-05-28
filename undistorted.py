import glob
import numpy as np
import cv2
import sys
import os

DIM = (760, 1008)
K = np.array([
    [298.22243679252, 0.0, 406.81968066100045],
    [0.0, 298.1778557322871, 495.4712122502833],
    [0.0, 0.0, 1.0]
])
D = np.array([
    [-0.009757569012691618],
    [-0.002221376782856862],
    [-0.000747024854208213],
    [-0.00014651564633053746]
])

def undistort(img_path, output_dir):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    os.makedirs(output_dir, exist_ok=True)  # 创建输出目录（只做一次）

    # 获取原始文件名，例如 img_0001.png
    filename = os.path.basename(img_path)
    # 构建保存路径
    save_path = os.path.join(output_dir, filename)
    cv2.imwrite(save_path, undistorted_img)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python undistort.py <input_pattern> [output_dir]")
        print("Example: python undistort.py imgs/*.jpg undistorted/")
        sys.exit(1)

    input_paths = sys.argv[1:-1]         # 所有输入图像路径
    output_dir = sys.argv[-1]            # 最后一个参数是输出目录

    for path in input_paths:
        undistort(path, output_dir)
