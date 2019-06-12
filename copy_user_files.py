# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (c) 2019 Brennan Goewert

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

import os
import sys
import shutil
import argparse
import logging
from fnmatch import fnmatch

__version__ = '1.1.0'

log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'copy_user_files.log')
logging.basicConfig(level=logging.INFO,
                    filename=log_path,
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S')
argp = argparse.ArgumentParser(description='Copies all the important ' +
                               'files and folders from the user profile.')
argp.add_argument('-d', '--destination', type=str,
                  help='Set the destination directory.',
                  action='store',
                  required=False)
argp.add_argument('-u', '--username', type=str,
                  help='Set the user\'s name of the ' +
                       'profile folder to copy from.',
                  action='store',
                  required=False)


def getUserName(tries=0):
    username = None

    args = argp.parse_known_args(sys.argv[1:])
    print(args)
    try:
        if tries < 5:
            if args[0].username is not None:
                username = args[0].username
                homepath = (os.path.dirname(os.environ['HOME']) +
                            os.sep + username)
                if not os.path.exists(homepath):
                    print('That was not a folder...')
                    print(homepath)
                    input('Try another user name...')
                    argparse.ArgumentParser.exit()
            else:
                username = input('Name of user folder: ')
                homepath = (os.path.dirname(os.environ['HOME']) +
                            os.sep + username)
                if not os.path.exists(homepath):
                    print('That was not a folder...')
                    print(homepath)
                    getUserName(tries+1)
        else:
            print('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!! (ノಠ益ಠ)ノ彡┻━┻')
            logging.warning('Too many attempts to define ' +
                            'a user folder.')
            quit()
    except:
        logging.exception(str('Something bad just happened, check stacktrace' +
                          ' to see the logs (＃ﾟДﾟ)').encode('UTF-8'))
    logging.info('User profile selected: %s' % username)
    return username


def getUserDir(tries=0):
    userDir = None

    args = argp.parse_known_args(sys.argv[1:])

    if tries < 5:
        if args[0].destination is not None:
            userDir = os.path.abspath(args[0].destination)
            if os.path.isfile(userDir):
                print('That was not a folder...')
                argparse.ArgumentParser.exit()
        else:
            userDir = os.path.abspath(input('Destination folder to copy' +
                                            ' user files/folders to: '))
            if os.path.isfile(userDir):
                print('That was not a folder...')
                print(userDir)
                getUserDir(tries+1)
    else:
        print('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!! (ノಠ益ಠ)ノ彡┻━┻')
        logging.warning('Too many attempts to select ' +
                        'a user destination directory.')
        quit()
    logging.info('User destination directory selected: %s' % userDir)
    return userDir


def findfile(pattern, path):
    result = []

    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result


def copy(src, dst):
    try:
        for root, dirs, files in os.walk(src):
            if not os.path.isdir(root):
                os.makedirs(root)
                logging.info('Root directory created: %s' % root)

            for f in files:
                if not os.path.isdir(dst):
                    os.makedirs(dst)
                    logging.info('Destination directory created: %s' % dst)

                nf_path = os.path.join(dst, f)
                f_path = os.path.join(root, f)
                shutil.copy(f_path, nf_path)
                logging.info('New file copied: %s' % str(nf_path))

    except Exception as err:
        logging.exception('Exception occurred trying to copy')


def app():
    print('\n* This script does not copy ' +
          'anything from the downloads folder. *\n')
    username = getUserName()
    userDir = getUserDir()

    folders = [
        r'C:\Users\%s\Documents' % username,
        r'C:\Users\%s\Desktop' % username,
        r'C:\Users\%s\Favorites' % username,
        r'C:\Users\%s\Pictures' % username,
        r'C:\Users\%s\Videos' % username,
        r'C:\Users\%s\AppData\Local\Microsoft\Outlook' % username,
        r'C:\Users\%s\AppData\Roaming\Microsoft\Outlook' % username,
        r'C:\Users\%s\AppData\Roaming\Microsoft\Outlook\RoamCache' % username,
        r'C:\Users\%s\AppData\Roaming\Microsoft\Signatures' % username,
        r'C:\Users\%s\AppData\Local\Mozilla\Firefox' % username,
        r'C:\Users\%s\AppData\Roaming\Mozilla\Firefox' % username,
        r'C:\Users\%s\AppData\Local\Google\Chrome' % username
        ]

    for path in folders:
        path = os.path.abspath(path)
        newDst = path.replace(os.sep.join(path.split(os.sep)[:3]),
                              userDir + os.sep + '%s' % username)

        if 'Outlook' in path and 'Local' in path:
            for f in findfile('*.pst', path):
                copy(f, os.path.join(newDst, f))

        elif ('Outlook' in path and
              'RoamCache' not in path and
              'Roaming' in path):
            for f in findfile('*.nk2', path):
                copy(f, os.path.join(newDst, f))

        else:
            copy(path, newDst)

    # os.system('pause')

app()
