# -*- coding:utf8 -*-
#!/user/bin/env python

import requests
import time
import os

image_path = "../image/"

def download_image(url):
    path = image_path + str(int(time.time()))
    rsp = requests.get(url)
    with open(path, "wb") as f:
        f.write(rsp.content)
    return path

if __name__ == '__main__':
    url = "http://image.bee-ji.com/21928"
    print download_image(url)
