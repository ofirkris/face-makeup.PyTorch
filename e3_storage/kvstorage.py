# vim: ts=4:sw=4:sts=4:et
# -*- coding:utf-8 -*-
import io
import json
import logging
import random

import cv2
import numpy
import oss2
import requests

import settings

logger = logging.getLogger(__name__)


class BaseKVStorageClient(object):
    def setv(self, key, value, group=None, prefix=""):
        raise NotImplementedError

    def getv(self, prefix, key):
        raise NotImplementedError

    def upload_file(self, filename, image_obj, group=None, prefix=""):
        raise NotImplementedError


class OSSKVStorageClient(BaseKVStorageClient):

    def __init__(self):
        self.OSS_KV_STORAGE = settings.OSS_KV_STORAGE
        self.OSS_KV_ENDPOINT = settings.OSS_KV_ENDPOINT
        self.cdn_domain = settings.CDN_DOMAIN

        endpoint = self.OSS_KV_ENDPOINT
        access_key_id = settings.ACCESS_KEY_ID
        access_key_secret = settings.ACCESS_KEY_SECRET
        group = settings.OSS_KV_STORAGE
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret),
                                  endpoint, group, session=oss2.Session())

    def setv(self, key, value, group=None, prefix="", file_type=""):
        pass

    def getv(self, key, prefix, group=None):
        pass

    def upload_file(self, filename, image_obj, group=None,
                    prefix="", content_type='png', enable_cdn=True):
        if not group:
            group = self.OSS_KV_STORAGE

        if content_type == "gif" and type(image_obj) == io.BytesIO:
            buffer_content = image_obj.getvalue()
        else:
            if isinstance(image_obj, numpy.ndarray):
                is_success, np_buffer = cv2.imencode('.' + content_type, image_obj)
                buffer = io.BytesIO(np_buffer)
            else:
                buffer = io.BytesIO()
                image_obj.save(buffer, format=content_type)
            buffer_content = buffer.getvalue()

        self.bucket.put_object(prefix + filename, buffer_content)
        if enable_cdn:
            static_url = "{}/{}{}".format(self.cdn_domain, prefix, filename)
        else:
            static_url = 'http://{}.{}/{}{}'.format(group,
                                                    self.OSS_KV_ENDPOINT,
                                                    prefix, filename)
        return static_url

    def upload_file_bytes(self, filename, image_bytes, group=None,
                          prefix="", enable_cdn=True):
        if not group:
            group = self.OSS_KV_STORAGE
        import oss2
        buffer_content = image_bytes

        endpoint = self.OSS_KV_ENDPOINT
        access_key_id = settings.ACCESS_KEY_ID
        access_key_secret = settings.ACCESS_KEY_SECRET
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret),
                             endpoint, group)
        bucket.put_object(prefix + filename, buffer_content)
        if enable_cdn:
            static_url = "{}/{}{}".format(self.cdn_domain, prefix, filename)
        else:
            static_url = 'http://{}.{}/{}{}'.format(group,
                                                    self.OSS_KV_ENDPOINT,
                                                    prefix, filename)
        return static_url


vv_storage = None


def vv_storage_instance():
    global vv_storage
    if vv_storage:
        return vv_storage
    vv_storage = OSSKVStorageClient()
    return vv_storage
