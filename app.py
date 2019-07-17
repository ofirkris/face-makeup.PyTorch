import base64
import time
from io import BytesIO

import cv2
import numpy
import requests
from flask import Flask, request, jsonify

from makeup import gen, TimePoint
from e3_storage.kvstorage import vv_storage_instance

app = Flask('face-makeup')


def read_im(fname):
    if isinstance(fname, str):
        if 'base64,' in fname:
            imgString = base64.b64decode(fname.split(',')[1])
            nparr = numpy.fromstring(imgString, numpy.uint8)
            im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            im = cv2.imread(fname, cv2.IMREAD_COLOR)
    elif isinstance(fname, bytes):
        im = numpy.asarray(bytearray(fname), dtype='uint8')
        im = cv2.imdecode(im, cv2.IMREAD_COLOR)
    elif hasattr(fname, 'read'):
        im = numpy.asarray(bytearray(fname.read()), dtype='uint8')
        im = cv2.imdecode(im, cv2.IMREAD_COLOR)
    else:
        raise ValueError('type {} is not support.'.format(type(fname)))
    return im


@app.route('/api/face-makeup', methods=['POST'])
def api_face_makeup():
    s = time.time()
    try:
        payload = request.get_json()
        url = payload['url']
        parts = payload['parts']
        colors = payload['colors']
    except Exception as ex:
        app.logger.warning('invalid params, {}'.format(ex))
        return jsonify({'errcode': 1, 'errmsg': 'Invalid params, {}'.format(ex)})

    tp = TimePoint()
    img_content = BytesIO(requests.get(url, timeout=8).content)
    tp.tick('download')
    im = read_im(img_content)
    tp.tick('cv2 read')
    app.logger.warning(im.shape)

    ret = gen(im, parts, colors)
    tp.tick('gen')
    ret_url = vv_storage_instance().upload_file('{}.png'.format(time.time()),
                                                 ret,
                                                 prefix='test/face-makeup')
    tp.tick('upload')
    app.logger.warning(time.time() - s)
    return jsonify({'errcode': 0, 'errmsg': '', 'data': ret_url})


if __name__ == '__main__':
    app.run('0.0.0.0', 8079)
