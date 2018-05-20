from django.conf import settings
from django.db import models

import hashlib
import time
import os

# Handler for a collection upload
def handle_uploaded_files(file_list):

    collection_name = 'col-' + str(time.time())
    STORAGE_PATH    = os.path.join(settings.COLLECTION_UPLOADS, collection_name)

    for file in file_list:

        # craft the file location
        new_filename    = md5_name_gen(file.chunks()) + '.' + file.name
        FILE_PATH       = os.path.join(STORAGE_PATH, new_filename)

        # write file directory to server filesystem
        if not os.path.exists(STORAGE_PATH):
            os.makedirs(STORAGE_PATH)

        # write file itself to server filesystem
        with open(FILE_PATH, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        print('Uploaded ', file.name)

    return True

# Returns MD5 checksum for file @fname
def md5_name_gen(chunks):
    md5 = hashlib.md5()
    for chunk in chunks:
        md5.update(chunk)
    return md5.hexdigest()
