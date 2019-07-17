# vim: ts=4:sw=4:sts=4:et
# -*- coding:utf-8 -*-

MAX_FILE_UPLAOD_SIZE = int(1.5 * 1024 * 1024)
MAX_USER_FILE_UPLOAD_SIZE = int(3 * 1024 * 1024)
BIG_FILE_MAX_UPLAOD_SIZE = int(5 * 1024 * 1024)
BIG_FILE_CONTENT_TYPES = ['image/gif', 'audio/mp3']


def get_upload_limit_for_type(mime_type):
    max_length = MAX_FILE_UPLAOD_SIZE
    content_type = ''
    if mime_type and mime_type.lower() in BIG_FILE_CONTENT_TYPES:
        max_length = BIG_FILE_MAX_UPLAOD_SIZE

    return max_length, content_type
