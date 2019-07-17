import cv2
import os
import numpy as np
from skimage.filters import gaussian
from test import evaluate, evaluate_with_im
import argparse


def parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument('--img-path', default='imgs/116.jpg')
    return parse.parse_args()


def sharpen(img):
    img = img * 1.0
    gauss_out = gaussian(img, sigma=5, multichannel=True)

    alpha = 1.5
    img_out = (img - gauss_out) * alpha + img

    img_out = img_out / 255.0

    mask_1 = img_out < 0
    mask_2 = img_out > 1

    img_out = img_out * (1 - mask_1)
    img_out = img_out * (1 - mask_2) + mask_2
    img_out = np.clip(img_out, 0, 1)
    img_out = img_out * 255
    return np.array(img_out, dtype=np.uint8)


def hair(image, parsing, part=17, color=[230, 50, 20]):
    b, g, r = color      #[10, 50, 250]       # [10, 250, 10]
    tar_color = np.zeros_like(image)
    tar_color[:, :, 0] = b
    tar_color[:, :, 1] = g
    tar_color[:, :, 2] = r

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    tar_hsv = cv2.cvtColor(tar_color, cv2.COLOR_BGR2HSV)

    if part == 12 or part == 13:
        image_hsv[:, :, 0:2] = tar_hsv[:, :, 0:2]
    else:
        image_hsv[:, :, 0:1] = tar_hsv[:, :, 0:1]

    changed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)

    if part == 17:
        changed = sharpen(changed)

    changed[parsing != part] = image[parsing != part]
    return changed

last = 0


def t(msg=''):
    global last
    now = time.time()
    print(msg, now - last)
    last = now


class TimePoint:
    def __init__(self):
        self.start_time = self.now()
        self.last = self.start_time

    def now(self):
        import time
        return time.time()

    def tick(self, msg=''):
        now = self.now()
        print(msg, now - self.last)
        self.last = now


def gen(origin_image, parts, colors):
    """
    :param origin_image:  cv2 image
    :param parts: list  transform types.
    :param colors: list  target BGR colors.

    transform_type = {
        'hair': 17,
        'upper_lip': 12,
        'lower_lip': 13,
        'teeth': 11,
        'face': 1
    }
    """
    tp = TimePoint()
    # image_path = args.img_path
    cp = 'cp/79999_iter.pth'

    # image = cv2.imread(image_path)
    image = origin_image.copy()
    parsing = evaluate_with_im(image, cp)
    parsing = cv2.resize(parsing, image.shape[0:2], interpolation=cv2.INTER_NEAREST)

    for part, color in zip(parts, colors):
        image = hair(image, parsing, part, color)
        tp.tick('hair, part: {}, color: {}'.format(part, color))

    return image


if __name__ == '__main__':
    import time
    start_time = time.time()
    last = start_time

    # 1  face
    # 11 teeth
    # 12 upper lip
    # 13 lower lip
    # 17 hair

    args = parse_args()

    table = {
        'hair': 17,
        'upper_lip': 12,
        'lower_lip': 13,
        'teeth': 11,
        'face': 1
    }

    image_path = args.img_path
    cp = 'cp/79999_iter.pth'

    image = cv2.imread(image_path)
    t('read')
    ori = image.copy()
    t('copy')
    parsing = evaluate(image_path, cp)
    t('parsing')
    parsing = cv2.resize(parsing, image.shape[0:2], interpolation=cv2.INTER_NEAREST)
    t('parsing2')

    parts = [table['hair'], table['upper_lip'], table['lower_lip'], table['teeth'], table['face']]

    colors = [[127, 127, 127], [0, 255, 0], [255, 0, 0], [0, 255, 255], [129, 64, 255]]

    for part, color in zip(parts, colors):
        image = hair(image, parsing, part, color)
        t('hair')

    if False:
        cv2.imshow('image', cv2.resize(ori, (512, 512)))
        cv2.imshow('color', cv2.resize(image, (512, 512)))

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    import time
    cv2.imwrite('/tmp/{}.jpg'.format(time.time()), image)
    t('write')















