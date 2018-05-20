from django.conf import settings
from django.db import models

import hashlib
import time
import os

# Handler for a collection upload
def handle_uploaded_file(file):

    # for every file, calculate a new name
    print('\n--------')
    print(file.name, file.read())
    print('--------\n')


    # craft the file location
    new_filename    = md5_name_gen(file.chunks())
    collection_name = 'col-' + str(time.time())
    STORAGE_PATH    = os.path.join(settings.COLLECTION_UPLOADS, collection_name)
    FILE_PATH       = os.path.join(STORAGE_PATH, new_filename)

    print('Writing at ', FILE_PATH)

    # write file directory to server filesystem
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)

    # write file itself to server filesystem
    with open(FILE_PATH, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return True

# Returns MD5 checksum for file @fname
def md5_name_gen(chunks):
    md5 = hashlib.md5()
    for chunk in chunks:
        md5.update(chunk)
    return md5.hexdigest()
