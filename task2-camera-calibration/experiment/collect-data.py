import cv2
import imutils
import numpy as np
from os import listdir, getcwd
from os.path import isfile, join
from checkerboard import detect_checkerboard

from count_frames import count_frames, timing

# Config Variables
no_of_columns = 8  # number of columns of your Checkerboard
no_of_rows = 8  # number of rows of your Checkerboard
square_size = 30  # size of square on the Checkerboard in mm

row = -1  # 6
column = -1  # 6
chessboard_flags = cv2.CALIB_CB_FAST_CHECK  # + cv2.CALIB_CB_NORMALIZE_IMAGE  # cv2.CALIB_CB_ADAPTIVE_THRESH


def detect_corners_in_image(image):
    # row = no_of_rows - 2
    # column = no_of_columns - 2

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
    ret, _ = cv2.findChessboardCorners(gray, (column, row), chessboard_flags)

    return ret


@timing
def timing_love(videos_path, height):
    list = 0

    for video, length in videos_path:
        # length = count_frames(video)
        out = 0



        # print(f"Total number of {length} frames in video: {video.split('/')[-1]}")

        cap = cv2.VideoCapture(video)

        # https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
        # https://github.com/ObeidaElJundi/Camera-Calibration/blob/master/calibration_GUI.py

        while cap.isOpened() and out <= length:
            success, frame = cap.read()
            out += 1

            for i in [120, 240, 360, 480, 720, 1080]:
                x = imutils.resize(frame, height=i)
                print(x.shape)

            print()

            if out > 0 and success:
                # img = frame.copy()
                ret = detect_corners_in_image(imutils.resize(frame, height=height))

                if ret:
                    # print(f"Frame: {out}, Status: {ret}")
                    # cv2.imwrite(f"{getcwd()}/picture_{source}/{out}.png", img)
                    list += 1

                # if (out % 50) == 0:
                # print(f"Frame: {out}, List: {list}, {int((out / length) * 100)}%")

        cap.release()
    return list


if __name__ == '__main__':
    video_path = f"{getcwd()}/vids"
    videos_path = [f"{video_path}/{f}" for f in listdir(video_path) if isfile(join(video_path, f))]

    combo = [(x, count_frames(x)) for x in videos_path]

    heights = [120, 240, 360, 480, 720, 1080]
    corner_sizes = [(7, 7), (7, 6), (6, 7), (6, 6)]

    print(f"Total frame value: {sum([x[1] for x in combo])}")

    for row, column in corner_sizes:
        print("------------------------")
        print(f"Used corner size: {row}x{column}")

        for height in heights:
            print(f"--{height}p")
            timing_love(combo, height)

    print("Finished with all frames")
