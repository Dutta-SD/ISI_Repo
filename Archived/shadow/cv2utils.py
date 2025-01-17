import cv2
import numpy as np


def kmeans_segment(image, K, attempts):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    twoDimage = img.reshape((-1, 3))
    twoDimage = np.float32(twoDimage)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    ret, label, center = cv2.kmeans(
        twoDimage,
        K,
        None,
        criteria,
        attempts,
        cv2.KMEANS_PP_CENTERS,
    )
    center = np.uint8(center)
    res = center[label.flatten()]
    result_image = res.reshape((img.shape))

    return result_image


def threshold_binary(img, frac=0.5, gray=True, inverse=False):
    maxval = np.max(img)
    thresh = maxval * frac

    if gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # thresh_method = cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY
    # thresh_method = cv2.THRESH_OTSU + (cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY)
    thresh_method = cv2.ADAPTIVE_THRESH_MEAN_C

    _, im_th = cv2.threshold(img, thresh, maxval, thresh_method)
    return im_th


def blur(img, kernel_dims=(3, 3)):
    return cv2.blur(img, kernel_dims)


def sharpen_3x3(img):
    filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(img, -1, filter)


def custom_edge_3x3(img):
    # edge detection filter
    kernel = np.array([[0.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 0.0]])

    kernel = kernel / (np.sum(kernel) if np.sum(kernel) != 0 else 1)

    return cv2.filter2D(img, -1, kernel)


def dilate(img, kernel_size=(2, 2), iter=1):
    kernel = np.ones(kernel_size, np.uint8)
    img_dilation = cv2.dilate(img, kernel, iterations=iter)
    return img_dilation


def compress_by_2(img):
    return cv2.resize(img, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)


def expand_by_2(img):
    return cv2.resize(img, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_LINEAR)


def hist_eq(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
    cl1 = clahe.apply(img)
    return cl1


def median_blur(img):
    return cv2.medianBlur(img, 3)


def erode(img, itr=1):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(img, kernel, iterations=itr)


def bgr_to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def bgr_to_hls(img):
    return cv2.cvtColor(
        img,
        cv2.COLOR_BGR2HLS,
    )


def normalize(img):
    M = np.max(img)
    m = np.min(img)

    img = ((img - m) / (M - m)) * 255
    return np.array(img, dtype=np.uint8)


def gamma_corr(img, gamma=0.7):
    i = img.copy()
    i = (i / 255) ** gamma
    i = np.array(i * 255, dtype=np.uint8)
    return i


def transform1(img):
    res = bgr_to_gray(img)
    res = hist_eq(res)
    res = compress_by_2(res)
    res = dilate(res, kernel_size=(3, 3), iter=2)
    res = kmeans_segment(res, 10, 20)
    res = expand_by_2(res)
    res = threshold_binary(res, inverse=True)

    return res


def view(img, x):
    cv2.imshow("Original", img)
    cv2.imshow("Shadow Mask", x)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def log_stretch(img: np.ndarray, c=1.0):
    x: np.ndarray = img.copy().astype(np.float)
    # Normalise to [0, 1]
    vec_log = np.vectorize(np.math.log)
    x += 1
    x = c * vec_log(x)
    return x.astype(np.uint8)


def transform2(img, gamma):
    res = img.copy()
    B, G, R = cv2.split(res)
    R = gamma_corr(R, gamma=gamma)
    res = cv2.merge([B, G, R])
    return res


def transform3(img):
    res = bgr_to_hls(img.copy())
    B, G, R = cv2.split(res)
    return B
