# -*- coding: utf-8 -*-
import os
import optparse
from PIL import Image


def check_img(fname):
    """
    Checks if those params are correct:
    - name xxx-yyy-zzz_AA__BB
    - size (100x100px)
    - monochrome
    """
    im = Image.open(fname)
    if im.size != (100, 100):
        print "WRONG SIZE: %s\t%s" % (im.size, fname)

    im = im.convert('RGB')
    w, h = im.size
    for i in range(w):
        for j in range(h):
            r, g, b = im.getpixel((i, j))
            if r != g != b:
                print "NOT MONOCHROME: %s" % fname

    
def main(path):
    # preserve original path before chdir
    curr_path = os.path.abspath(os.path.curdir)
    if os.path.isdir(path):
        # cd into path to avoid dealing with spaces in path
        os.chdir(path)
        for root, dirs, files in os.walk(os.path.curdir, topdown=False):
            for filename in files:
                if filename.startswith("."):
                    continue
                if not filename.endswith(".png"):
                    continue
                check_img(filename)
    else:
        check_img(path)

    os.chdir(curr_path)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="usage: python %prog [OPTIONS] dirname")
    opts, args = parser.parse_args()

    try:
        dirname = args[0]
    except:
        print "ERROR: path not provided!"
        exit()

    path = os.path.abspath(dirname)
    if not os.path.exists(path):
        print "ERROR: path %s does not exist!" % dirname
        exit()

    main(path)
