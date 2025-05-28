import cv2
import numpy as np
import os
import glob

CHECKERBOARD = (6, 9)
subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

calibration_flags = (cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW
                     # + cv2.fisheye.CALIB_CHECK_COND
                     )

objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
_img_shape = None
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob('imgs/*.jpg')
imgcnt = 0

for fname in images:
    img = cv2.imread(fname)
    if _img_shape == None:
        _img_shape = img.shape[:2]
    else:
        assert _img_shape == img.shape[:2], "All images must share the same size."
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    imgcnt += 1
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,
                                             cv2.CALIB_CB_ADAPTIVE_THRESH
                                             + cv2.CALIB_CB_FAST_CHECK
                                             + cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp.copy())
        # objpoints.append(objp)
        cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), subpix_criteria)
        imgpoints.append(corners)

        # 打印图像文件名与角点数
        # print(f"[OK] {fname}, num corners: {len(corners)}")

        # 显示图像和角点
        # vis = img.copy()
        # cv2.drawChessboardCorners(vis, CHECKERBOARD, corners, ret)
        # cv2.imshow("Corners Check", vis)
        # cv2.waitKey(10000)  # 手动看角点分布质量，按下任意键继续

    else:
        print(f"[FAIL] {fname} - findChessboardCorners failed")

# for i, o in enumerate(objpoints):
#     print(f"objpoints[{i}] id: {id(o)}")

# for i, obj in enumerate(objpoints):
#     print(f"objpoints[{i}].shape: {obj.shape}, dtype: {obj.dtype}")
#
# for i, imgp in enumerate(imgpoints):
#     print(f"imgpoints[{i}].shape: {imgp.shape}, dtype: {imgp.dtype}")
#
# print("Image size passed to calibrate:", gray.shape[::-1])


N_OK = len(objpoints)
K = np.zeros((3, 3))
D = np.zeros((4, 1))

rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
rms, _, _, _, _ = \
    cv2.fisheye.calibrate(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("imgcnt:", imgcnt)
print("Found " + str(N_OK) + " valid images for calibration")
print("DIM=" + str(_img_shape[::-1]))
print("K=np.array(" + str(K.tolist()) + ")")
print("D=np.array(" + str(D.tolist()) + ")")
