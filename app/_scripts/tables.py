# -*- coding: utf-8 -*-
import os
import math
import random
import optparse

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


IMG_NUM = 6

FONT = ImageFont.truetype('/System/Library/Fonts/Monaco.dfont', 8)
FONT_PAGE_NUM = ImageFont.truetype('/System/Library/Fonts/Monaco.dfont', 16)
LINE_VERT = Image.new('RGBA', (1, 125), (125, 125, 125))
LINE_HORZ = Image.new('RGBA', (100, 1), (125, 125, 125))

TABLE_HEAD = Image.new('RGBA', (100*IMG_NUM+25, 25), (255, 255, 255))
draw = ImageDraw.Draw(TABLE_HEAD)
for i in range(IMG_NUM):
    draw.text((i*100+75, 10), str(i+1), (0, 0, 0), font=FONT)

TABLE_SPINE = Image.new('RGBA', (25, 125*IMG_NUM+25), (255, 255, 255))
draw = ImageDraw.Draw(TABLE_SPINE)
for i in range(IMG_NUM):
    draw.text((10, i*125+87), str(i+1), (0, 0, 0), font=FONT)


def get_info(fname):
    info = {
        'filename': fname,
        'name': '',
        'complexity': -1,
        'errors': [],
        }
    name = fname.replace('.png', '')
    try:
        name, complexity = name.rsplit('__', 1)
        info['complexity'] = int(complexity)
    except ValueError:
        info['errors'].append('%s: complexity not specified or wrong type' % fname)
        return info

    try:
        name, ver = name.rsplit('_', 1)
        ver = int(ver)
    except ValueError:
        info['errors'].append('%s: version not specified or wrong type' % fname)
        return info

    info['name'] = name.title()
    if ver > 0:
        info['name'] += (' ' + str(ver))

    return info

    
def check_img(fname):
    """
    Checks if those params are correct:
    - size (100x100px)
    - monochrome
    """
    info = get_info(fname)
    im = Image.open(fname)
    info.update({'image': im})
    if im.size != (100, 100):
        info['errors'].append('%s: wrong size %s' % (fname, im.size))

    im1 = im.convert('RGB')
    w, h = im1.size
    for i in range(w):
        for j in range(h):
            r, g, b = im1.getpixel((i, j))
            if r != g != b:
                info['errors'].append('%s: not monochrome' % fname)
    return info


def prepare(img, caption):
    img_cap = Image.new('RGBA', (100, 125), (255, 255, 255))
    img_cap.paste(img, (0, 0))

    # XXX do the smart line breaks
    if len(caption) > 18:
        capt = ''
        while len(caption) > 0:
            capt += caption[:17] + '-\n'
            capt = capt.replace('--', '-')
            caption = caption[17:]
        caption = capt.strip()[:-1]

    # add text
    draw = ImageDraw.Draw(img_cap)
    draw.text((5, 100), caption, (0, 0, 0), font=FONT)

    # make border
    img_cap.paste(LINE_VERT, (0, 0))
    img_cap.paste(LINE_VERT, (99, 0))
    img_cap.paste(LINE_HORZ, (0, 0))
    img_cap.paste(LINE_HORZ, (0, 124))

    return img_cap


def new_page(num):
    im = Image.new('RGBA', (100*IMG_NUM+25, 125*IMG_NUM+25))
    im.paste(TABLE_SPINE, (0, 0))
    im.paste(TABLE_HEAD, (0, 0))

    draw = ImageDraw.Draw(im)
    draw.text((5, 5), str(num), (0, 0, 0), font=FONT_PAGE_NUM)

    x_offset = TABLE_SPINE.size[0]
    y_offset = TABLE_HEAD.size[1]
    return im, x_offset, y_offset


def make_tables(images, curr_path):
    # random.shuffle(images) # do i need it?
    page_num = 1
    page, x_offset, y_offset = new_page(page_num)
    rows = 0
    for i, img in enumerate(images):
        img_cap = prepare(img['image'], img['name'])
        page.paste(img_cap, (x_offset, y_offset))

        x_offset += img_cap.size[0]

        # end of line
        if x_offset >= (100*IMG_NUM):
            rows += 1
            x_offset = TABLE_SPINE.size[0]
            y_offset += img_cap.size[1]

            # end of section - write to file, init blank image
            if rows == IMG_NUM:
                rows = 0
                page.save('test_%d.jpg' % page_num)
                page_num += 1
                page, x_offset, y_offset = new_page(page_num)

    # last one
    page.save('test_%d.jpg' % page_num)
    print "exported %d images" % (i+1)


def main(path):
    # preserve original path before chdir
    curr_path = os.path.abspath(os.path.curdir)
    # cd into path to avoid dealing with spaces
    os.chdir(path)
    images = []
    errors = []
    for root, dirs, files in os.walk(os.path.curdir, topdown=False):
        for filename in files:
            if filename.startswith('.'):
                continue
            if not filename.endswith('.png'):
                continue
            img = check_img(filename)
            images.append(img)
            errors.extend(img['errors'])

    os.chdir(curr_path)
    if errors:
        print 'ERRORS FOUND:'
        for err in errors:
            print err
        return

    make_tables(images, curr_path)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: python %prog [OPTIONS] dirname')
    opts, args = parser.parse_args()

    try:
        dirname = args[0]
    except:
        print 'ERROR: path not provided!'
        exit()

    path = os.path.abspath(dirname)
    if not os.path.exists(path):
        print 'ERROR: path %s does not exist!' % dirname
        exit()
    if not os.path.isdir(path):
        print 'ERROR: %s is not a directory!' % dirname
        exit()

    main(path)
