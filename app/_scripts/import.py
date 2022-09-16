# -*- coding: utf-8 -*-

"""
One off import of asanas into SOMA db with renaming the files and labelling
'difficulty' as user 'deko' (default superuser).

Requires `dirname`, whose subdirectories are being scanned recoursively.
A name of each sub-directory becomes a tag.

Warning! Only PNG images are being imported.

Naming files:
<name-of-asana>_<variant 0..N>__<difficulty 1..60>.png
"""

import os
import sys
import math
import random
import optparse

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from core.models import TaggedUserItem, Score, ScoredItem
from asana.models import Asana, AsanaForm


def get_info(fname):
    info = {
        'filename': fname,
        'name': '',
        'variant': None,
        'difficulty': -1,
        'errors': [],
        }
    name = os.path.basename(fname).replace('.png', '')
    try:
        name, difficulty = name.rsplit('__', 1)
        info['difficulty'] = int(difficulty)
    except ValueError:
        info['errors'].append('%s: difficulty not specified or wrong type' % fname)
        return info

    try:
        name, variant = name.rsplit('_', 1)
        variant = int(variant)
    except ValueError:
        info['errors'].append('%s: variant not specified or wrong type' % fname)
        return info

    info.update({
        'name': name.title(),
        'variant': variant
        })
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
    grayscale = True
    w, h = im1.size
    for i in range(w):
        for j in range(h):
            r, g, b = im1.getpixel((i, j))
            if r != g != b:
                grayscale = False
                break
    if not grayscale:
        info['errors'].append('%s: not monochrome' % fname)

    return info


def main(path):
    user = User.objects.get(username="deko")
    asana_form_ct = ContentType.objects.get(app_label='asana', model='asanaform')
    score, _ = Score.objects.get_or_create(name='difficulty', minval=0, maxval=40, user=user)

    for root, dirs, files in os.walk(path, topdown=False):
        tagname = os.path.basename(root)
        for filename in files:
            if filename.startswith('.'):
                continue

            if not filename.endswith('.png'):
                continue

            filename = os.path.join(root, filename)
            img = check_img(filename)
            if img['errors']:
                print("\n[!] Errors found in {}".format(filename))
                for err in img['errors']:
                    print("\t%s" % err)
                continue

            curr_name = "{name}_{variant}".format(**img)

            # upload and create a record of asana and its form
            upload_to = os.path.join(
                settings.MEDIA_ROOT,
                AsanaForm.pict.field.upload_to,
                curr_name+".png"
                # os.path.basename(img['filename'])
                )
            img['image'].save(upload_to)
            asana, _ = Asana.objects.get_or_create(name=img['name'])
            form = AsanaForm(asana=asana, variant=img['variant'])
            form.pict = upload_to
            form.save()

            # tag it
            tag, _ = TaggedUserItem.objects.get_or_create(name=tagname,
                                                          content_type=asana_form_ct,
                                                          object_id=form.id,
                                                          user=user)
            # score it
            scored, _ = ScoredItem.objects.get_or_create(score=score,
                                                         val=img['difficulty'],
                                                         content_type=asana_form_ct,
                                                         object_id=form.id)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: python %prog dirname')
    opts, args = parser.parse_args()

    try:
        dirname = args[0]
    except:
        sys.exit("ERROR: path not provided!")

    path = os.path.abspath(dirname)
    if not os.path.exists(path):
        sys.exit("ERROR: path {} does not exist!".format(dirname))
    if not os.path.isdir(path):
        sys.exit("ERROR: {} is not a directory!".format(dirname))

    main(path)
