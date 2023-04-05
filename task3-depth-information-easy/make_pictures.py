import cv2
import imutils
import numpy as np
from os import listdir, getcwd
from os.path import isfile, join

row = 6
column = 6


def create_and_wait(window_name, image, wait=True):
    cv2.namedWindow(window_name)  # Create a named window
    cv2.moveWindow(window_name, 40, 30)  # Move it to (40,30)
    cv2.imshow(window_name, imutils.resize(image, height=650))

    # Hold window until button press
    while wait:
        k = cv2.waitKey(1) & 0xFF  # Wait for a second
        if k == 27 or k == ord('q'):  # esc button and q button
            cv2.destroyAllWindows()
            break
        if k == ord('s'):
            file = video_list.get(source) + "_o1g.png"
            cv2.imwrite(file, image)
            print(f"Saved image {file}")


def calibrate_coef(corner_list, og):
    objp = np.zeros((row * column, 3), np.float32)
    objp[:, :2] = np.mgrid[0:row, 0:column].T.reshape(-1, 2)
    objpoints = [objp for _ in range(len(corner_list))]

    gray = cv2.cvtColor(og, cv2.COLOR_BGR2GRAY)

    coef = cv2.calibrateCamera(objpoints, corner_list, gray.shape[::-1], None, None)

    return coef


def detect_corners_in_image(image):
    global row, column

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
    chessboard_flags = cv2.CALIB_CB_FAST_CHECK  # + cv2.CALIB_CB_NORMALIZE_IMAGE  cv2.CALIB_CB_ADAPTIVE_THRESH
    retval, corners = cv2.findChessboardCorners(gray, (column, row), chessboard_flags)

    if retval:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # https://docs.opencv.org/master/dd/d1a/group__imgproc__feature.html#ga354e0d7c86d0d9da75de9b9701a9a87e
        refined_corners = cv2.cornerSubPix(gray, corners, (row * 2 + 1, column * 2 + 1), (-1, -1), criteria)
        # cv2.drawChessboardCorners(image, (column, row), refined_corners, retval)

        return retval, image, refined_corners

    return retval, image, None


if __name__ == '__main__':
    video_list = {0: "metal_printer", 1: "schwalbe", 2: "250"}
    source = 1

    video_path = f"{getcwd()}/{video_list.get(source)}/good/"
    videos_path = [f"{video_path}/{f}" for f in listdir(video_path) if isfile(join(video_path, f))]

    corners_list = []
    picture_list = []

    for index, image in enumerate(sorted(videos_path)):
        img = cv2.imread(image)
        ret, _, corners = detect_corners_in_image(img)

        if ret and len(corners) != 0:
            corners_list.append(corners)
            picture_list.append(img.copy())

        if len(videos_path) - 1 == index:
            love = img.copy()
    print(f"First: {len(picture_list)}/{len(videos_path)}")
    retval, mtx, dist, rvecs, tvecs = calibrate_coef(corners_list, love)

    if retval:
        print(mtx, "\n", dist)
        h, w = picture_list[-1].shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        corners_list = []

        # dst = cv2.undistort(picture_list[-1], mtx, dist, None, newcameramtx)
        # x, y, w, h = roi
        # dst = dst[y:y + h, x:x + w]
        # print(mtx, "\n", dist)
        # create_and_wait("love", dst)
        # exit()

        bong = None

        for index, image in enumerate(picture_list):
            # undistort
            dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

            # crop the image
            x, y, w, h = roi
            dst = dst[y:y + h, x:x + w]

            if len(picture_list) - 1 == index:
                bong = dst

            ret, _, corners = detect_corners_in_image(image)
            if ret and len(corners) != 0:
                corners_list.append(corners)
                picture_list[index] = dst.copy()

        print(f"Second: {len(picture_list)}/{len(videos_path)}")
        retval, mtx, dist, rvecs, tvecs = calibrate_coef(corners_list, love)

        if retval:
            print(mtx, "\n", dist)
            love = picture_list[-1]
            h, w = love.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

            dst = cv2.undistort(love, mtx, dist, None, newcameramtx)

            # crop the image
            x, y, w, h = roi
            dst = dst[y:y + h, x:x + w]

            create_and_wait("love", dst)
