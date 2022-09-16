# -*- coding: utf-8 -*-

"""
One off import of asanas into Yogascape db with renaming the files and
labelling 'difficulty' as admin (the earliest created superuser).

Requires `dirname`, whose subdirectories are being scanned recoursively.
A name of each sub-directory becomes a tag.

Warning! Only PNG images are being imported.

Naming files:
<name-of-asana>_<variant 0..N>__<difficulty 1..60>.png
"""

import os

from PIL import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

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
        info['errors'].append(f'{fname}: difficulty not specified or wrong type')
        return info

    try:
        name, variant = name.rsplit('_', 1)
        variant = int(variant)
    except ValueError:
        info['errors'].append(f'{fname}: variant not specified or wrong type')
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
        info['errors'].append(f'{fname}: wrong size {im.size}')

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
        info['errors'].append(f'{fname}: not monochrome')

    return info

def get_user():
    users = User.objects.filter(is_superuser=True).order_by('date_joined')
    return users[0]

def main(**kwargs):
    path = kwargs.get('dirname', None)
    if not path:
        raise Exception('Directory name is missing!')

    user = get_user()
    asana_form_ct = ContentType.objects.get(app_label='asana',
                                            model='asanaform')
    score, _ = Score.objects.get_or_create(name='difficulty',
                                           minval=0,
                                           maxval=40,
                                           user=user)

    for root, _, files in os.walk(path, topdown=False):
        tagname = os.path.basename(root)
        for filename in files:
            if filename.startswith('.'):
                continue

            if not filename.endswith('.png'):
                continue

            filename = os.path.join(root, filename)
            img = check_img(filename)
            if img['errors']:
                print(f'\n[!] Errors found in {filename}')
                for err in img['errors']:
                    print(f'\t{err}')
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
            asana_form = AsanaForm(asana=asana, variant=img['variant'])
            asana_form.pict = upload_to
            asana_form.save()

            # tag it
            tag, _ = TaggedUserItem.objects.get_or_create(
                name=tagname,
                content_type=asana_form_ct,
                object_id=asana_form.id,
                user=user
                )
            # score it
            scored, _ = ScoredItem.objects.get_or_create(
                score=score,
                val=img['difficulty'],
                content_type=asana_form_ct,
                object_id=asana_form.id
                )


class Command(BaseCommand):
    help = """Import asanas from directory."""

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--dry',
            action='store_true', dest='dry', default=False,
            help='Dry run (do not perform anything, only report).')
        parser.add_argument(
            action='store', dest='dirname',
            help='Directory name with images.'
            )

    def handle(self, *args, **opts):
        main(**opts)
