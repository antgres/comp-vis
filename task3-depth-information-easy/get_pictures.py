import cv2
import imutils
from os import listdir, getcwd, makedirs
from os.path import isfile, join
from count_frames import count_frames

row = 7
column = 7


def detect_corners_in_image(image):
    global row, column

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
    chessboard_flags = cv2.CALIB_CB_FAST_CHECK  # + cv2.CALIB_CB_NORMALIZE_IMAGE  cv2.CALIB_CB_ADAPTIVE_THRESH
    retval, corners = cv2.findChessboardCorners(gray, (column, row), chessboard_flags)

    if retval:
        return True
    else:
        return False


if __name__ == '__main__':
    video_path = f"{getcwd()}/vids"
    videos_path = [f"{video_path}/{f}" for f in listdir(video_path) if isfile(join(video_path, f))]

    video_list = {0: "metal_printer", 1: "schwalbe", 2: "250"}

    corners_list = []

    # select video from available videos
    source = 2
    videos_path = [videos_path[source]]

    makedirs(f"{getcwd()}/{video_list.get(source)}", exist_ok=True)

    # https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
    # https://github.com/ObeidaElJundi/Camera-Calibration/blob/master/calibration_GUI.py
    for video in videos_path:
        length = count_frames(video)
        print(f"Total number of {length} frames in video: {video.split('/')[-1]}")

        out = 0
        list = 0

        cap = cv2.VideoCapture(video)

        while cap.isOpened() and out <= length:
            success, frame = cap.read()
            out += 1

            if out > 0 and success:
                img = frame.copy()
                ret = detect_corners_in_image(imutils.resize(frame, height=480))

                if ret:
                    #cv2.imwrite(f"{getcwd()}/{video_list.get(source)}/{out}.png", img)
                    list += 1

                if (out % 50) == 0:
                    print(f"Frame: {out}, List: {list}, {int((out / length) * 100)}%")
                    # break
