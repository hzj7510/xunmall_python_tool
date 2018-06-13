import os
import re
import shutil


def copy_files(path, dis_path):
    try:
        files = os.listdir(path)
        for file in files:
            if os.path.isdir(os.path.join(path, file)):
                os.mkdir(os.path.join(dis_path, file))
                yield from copy_files(os.path.join(path, file), os.path.join(dis_path, file))
            else:
                name, ext = os.path.splitext(file)
                if ext != '.webp':
                    ma = re.match(r'.*_800$', name)
                    if ma:
                        shutil.copy(os.path.join(path, file), os.path.join(dis_path, file))
                        yield '{}       to      {}'.format(os.path.join(path, file), os.path.join(dis_path, file))
    except Exception as e:
        print(e)
