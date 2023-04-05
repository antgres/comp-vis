import cv2
import imutils
from os import listdir, getcwd
from os.path import isfile, join


from count_frames import count_frames

# Config Variables
no_of_columns = 8  # number of columns of your Checkerboard
no_of_rows = 8  # number of rows of your Checkerboard
square_size = 30  # size of square on the Checkerboard in mm


def detect_corners_in_image(image):
    # row = no_of_rows - 2
    # column = no_of_columns - 2

    row = 6
    column = 6

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
    chessboard_flags = cv2.CALIB_CB_FAST_CHECK  # + cv2.CALIB_CB_NORMALIZE_IMAGE  cv2.CALIB_CB_ADAPTIVE_THRESH
    ret, corners = cv2.findChessboardCorners(gray, (column, row), chessboard_flags)

    # not finding for blurred or rotated, lighnting conditions

    # if ret:
    #     # termination criteria
    #     criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_size, 0.001)
    #
    #     refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    #     #cv2.drawChessboardCorners(image, (column, row), refined_corners, ret)

    return ret, image


if __name__ == '__main__':
    video_path = f"{getcwd()}/vids"
    videos_path = [f"{video_path}/{f}" for f in listdir(video_path) if isfile(join(video_path, f))]

    # select video from available videos
    # source = 0

    # video = videos_path[source]
    # length = count_frames(video)
    # out = 0
    # list = 0

    # print(f"Total number of {length} frames in video: {video.split('/')[-1]}")

    # cap = cv2.VideoCapture(video)

    # https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
    # https://github.com/ObeidaElJundi/Camera-Calibration/blob/master/calibration_GUI.py
    for video in videos_path:
        length = count_frames(video)
        out = 0
        list = 0

        print(f"Total number of {length} frames in video: {video.split('/')[-1]}")

        cap = cv2.VideoCapture(video)

        while cap.isOpened() and out <= length:
            success, frame = cap.read()
            out += 1

            if out > 0 and success:
                img = frame.copy()
                ret, figure = detect_corners_in_image(imutils.resize(frame, height=360))

                if ret:
                    # print(f"Frame: {out}, Status: {ret}")
                    # cv2.imwrite(f"{getcwd()}/picture_{source}/{out}.png", img)
                    list += 1

                if (out % 50) == 0:
                    print(f"Frame: {out}, List: {list}, {int((out / length) * 100)}%")

                # cv2.imshow('frame', imutils.resize(figure, height=650))

                # https://github.com/lambdaloop/checkerboard
                # A perfectly detected checkerboard would have a score of 0, whereas a bad detection would
                # have a score of 1.
                # size = (7, 7)
                # corners, score = detect_checkerboard(img, size)

                # if corners:
                #     print(f"Frame: {out}, Score: {score}")
                #     # cv2.imwrite(f"{getcwd()}/picture_0/{out}.png", img)
                #     # list.append(out)
                #
                # elif (out % 50) == 0:
                #     print(f"Frame: {out}, Score: {score}, {int((out / length) * 100)}%")

        print(list)
        print("Finished with all frames")
