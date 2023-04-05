import cv2
import imutils
import numpy as np
from os import listdir, getcwd
from os.path import isfile, join

# https://github.com/devd/Academic-Writing-Check

# Config Variables
no_of_columns = 8  # number of columns of your Checkerboard
no_of_rows = 8  # number of rows of your Checkerboard
square_size = 30  # size of square on the Checkerboard in mm

height_of_imshow = 600
easy_mode = 1

row = no_of_rows - easy_mode
column = no_of_columns - easy_mode

gray = None


def calibrate_coef(corner_list):
    objp = np.zeros((row * column, 3), np.float32)
    objp[:, :2] = np.mgrid[0:row, 0:column].T.reshape(-1, 2)
    objpoints = [objp for _ in range(len(corner_list))]

    coef = cv2.calibrateCamera(objpoints, corner_list, gray.shape[::-1], None, None)

    return coef


def detect_corners_in_image(image, path):
    global gray

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
    # cv2.CALIB_CB_FAST_CHECK
    chessboard_flags = cv2.CALIB_CB_FAST_CHECK  # cv2.CALIB_CB_ADAPTIVE_THRESH +  + cv2.CALIB_CB_NORMALIZE_IMAGEq
    retval, corners = cv2.findChessboardCorners(gray, (column, row), chessboard_flags)

    if retval:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_size, 0.001)

        # https://docs.opencv.org/master/dd/d1a/group__imgproc__feature.html#ga354e0d7c86d0d9da75de9b9701a9a87e
        refined_corners = cv2.cornerSubPix(gray, corners, (row * 2 + 1, column * 2 + 1), (-1, -1), criteria)
        cv2.drawChessboardCorners(image, (column, row), refined_corners, retval)

        cv2.imwrite("love.png", image)
        while True:
            k = cv2.waitKey(1) & 0xFF  # Wait for a second
            if k == 27 or k == ord('q'):  # esc button and q button
                break

        return retval, image, refined_corners

    return retval, image, None


if __name__ == '__main__':
    # select video from available videos
    source = 0  # 1 switch size to 6x6

    picture_path = f"{getcwd()}/picture_{source}/good/"
    pictures_path = [f"{picture_path}/{f}" for f in listdir(picture_path) if isfile(join(picture_path, f))]

    corners_list = []

    x = 0

    for image_path in pictures_path:
        if image_path.find("undist") == -1:

            image = cv2.imread(image_path)
            og = image.copy()

            ret, image, corners = detect_corners_in_image(imutils.resize(image, height=480), image_path)

            if ret and len(corners) != 0:
                corners_list.append(corners)
                x += 1
                # hori = np.concatenate((imutils.resize(og, height=height_of_imshow),
                #                        imutils.resize(image, height=height_of_imshow)),
                #                       axis=1)
                #
                # cv2.imshow('Original', hori)

    # https://learnopencv.com/camera-calibration-using-opencv/
    # mtx = intrinsic_coef, dist = distortian_coef
    # cv2.imwrite("colour_corners.png", image)
    retval, mtx, dist, rvecs, tvecs = calibrate_coef(corners_list)

    if retval:
        for path in pictures_path:
            if path.find("og") != -1:
                image = cv2.imread(path)

                h, w = image.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

                # undistort
                dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

                # cv2.imwrite("undist_without_roi.png", dst)

                # crop the image
                x, y, w, h = roi
                dst = dst[y:y + h, x:x + w]

                cv2.namedWindow(path)  # Create a named window
                cv2.moveWindow(path, 40, 30)  # Move it to (40,30)
                cv2.imshow(path, dst)

                cv2.imwrite(f"{picture_path}/{path.split('/')[-1].split('_')[0]}_undist.png",
                            imutils.resize(dst, height=h, width=w))

                # cv2.imwrite("undist_og.png", dst)

                # Hold window until button press
                while True:
                    k = cv2.waitKey(1) & 0xFF  # Wait for a second
                    if k == 27 or k == ord('q'):  # esc button and q button
                        cv2.destroyAllWindows()
                        break
            else:
                cv2.destroyAllWindows()
