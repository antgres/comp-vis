import cv2
import imutils
from operator import itemgetter
import numpy as np
from os import listdir, getcwd
from os.path import isfile, join

save_path = f"{getcwd()}/"
circle_radius = 10
draw_line = 5


def is_inside(corner_list, point):
    """
	Compare radius of circle with distance of its center
	from given point
    """

    x, y = point
    rad = 30

    for circle_x, circle_y in corner_list:
        if (x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad:
            return True


def max_min_point(list):
    """Find the biggest and the smallest point in the list"""

    result_point = []

    x_list = sorted(list, key=itemgetter(0))
    result_point.append(x_list[-1])
    result_point.append(x_list[0])

    l3 = []
    for point in list:
        if not is_inside(result_point, point):
            l3.append(point)

    y_list = sorted(l3, key=itemgetter(1))

    result_point.append(y_list[0])
    result_point.append(y_list[-1])

    return result_point


def biggest_contour(contours):
    """Find the biggest contour cv2 can find"""

    biggest = np.array([])
    max_area = 0
    max = 0

    # search for biggest arclength
    for i in contours:
        peri = cv2.arcLength(i, False)

        if peri > max_area:
            # Contour Approximation
            biggest = cv2.approxPolyDP(i, 0.05 * peri, True)
            max = i
            max_area = peri

    return biggest, max


def order_points(points):
    # coordinates will be in the order
    # (top-left, top-right, bottom-right, bottom-left)
    ordered = np.zeros((4, 2), dtype=np.float32)

    sum = np.sum(points, axis=1)
    ordered[0] = points[np.argmin(sum)]  # x + y will be very low
    ordered[2] = points[np.argmax(sum)]  # x + y will be very high

    diff = np.diff(points, axis=1)
    ordered[1] = points[np.argmin(diff)]  # x - y will be very low
    ordered[3] = points[np.argmax(diff)]  # x - y will be very high

    return ordered


def transform(corners, image):
    corners = order_points(corners)

    tl, tr, br, bl = corners

    top_width = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    bottom_width = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))

    width = int(np.min([top_width, bottom_width]))

    left_height = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    right_height = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))

    height = int(np.min([left_height, right_height]))

    # Redefine corner positions in array for cv2 function
    dst = np.array([[0, 0],
                    [width - 1, 0],
                    [width - 1, height - 1],
                    [0, height - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(image, M, (width, height))


def scan(image):
    # Edge Detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blurred, 0, 84)

    # save found edges
    # cv2.imwrite(save_path + "edged.png", edged)

    # Find contours
    # alternatively: cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE
    # cv2.RETR_EXTERNAL or cv2.CHAIN_APPROX_SIMPLE
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    og = image.copy()
    cv2.drawContours(og, contours, -1, (0, 0, 255), draw_line)
    # cv2.imshow("", imutils.resize(og, height=650))
    cv2.imwrite(save_path + "all_contours.png", og)

    # save biggest found contoured
    # cv2.imwrite(save_path + "contours.png", og)

    # sort for biggest contour
    biggest, max = biggest_contour(contours)
    if biggest.size == 0:
        exit("Error")

    # draw approxed contour
    og = image.copy()
    cv2.drawContours(og, [biggest], -1, (255, 0, 0), draw_line)
    # cv2.imwrite(save_path + "contours_approx.png", og)

    # draw the approximated corners into the image
    og = image.copy()
    points_corn = [np.ndarray.tolist(i) for i, *_ in biggest]
    for point in points_corn:
        x, y = point
        cv2.circle(og, (x, y), circle_radius, (100, 180, 0), -1)
    # cv2.imwrite(save_path + "contours_corner.png", og)

    # Extract points
    if len(biggest) >= 4:
        og = image.copy()
        print("Found")
        points = [np.ndarray.tolist(i) for i, *_ in biggest]
        corners = max_min_point(points)
        for point in corners:
            x, y = point
            cv2.circle(og, (x, y), 2 * circle_radius, (0, 255, 0), -1)

        # save found corners
        # cv2.imshow("Corner", imutils.resize(og, height=650))
        # cv2.imwrite(save_path + "found_corners.png", og)

        return corners

    return None


if __name__ == '__main__':
    image_path = f"{getcwd()}/test-images"
    images_path = [f"{image_path}/{f}" for f in listdir(image_path) if isfile(join(image_path, f))]

    for file in images_path:
        image = cv2.imread(file)
        original_image = image.copy()

        corners = scan(image)

        if not corners:
            print(f"Not found: {file}")
            continue

        warped_image = transform(corners, image)

        hori = np.concatenate((imutils.resize(warped_image, height=650),
                               imutils.resize(original_image, height=650)),
                              axis=1)

        # cv2.imshow('Original', hori)

        # Binary Image
        grayImage = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(grayImage, 5)
        th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        cv2.imshow('Original', th3)

        # cv2.imwrite(save_path + 'result.jpg', th3, [cv2.IMWRITE_JPEG_QUALITY, 100])

        k = cv2.waitKey(0)
        if k == 27:  # wait for ESC key to exit
            cv2.destroyAllWindows()
            break
