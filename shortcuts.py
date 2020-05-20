import platform
import pathlib

structure = ''
is_linux = platform.system() == 'Linux'


def slugify(value):
    if is_linux:
        value = value.replace('/', '\\')
        value = "".join(x for x in value if not x == '\x00')
    else:
        for x in ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']:
            value = value.replace(x, '-')
        for x in ['CON', 'PRN', 'AUX', 'NUL', 'COM0', 'COM1', 'COM2',
                  'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
                  'COM9', 'LPT0', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
                  'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']:
            value = value.replace(x, x[0] + '_' + x[1:])
        if value.count('.') == len(value):
            value = value.replace('.', '_')
        if value.endswith('.') or value.endswith(' '):
            value = value[:-1] + '_'
    return value


def create_shortcut(shortcut_path: pathlib.Path, icon: str, attributes: dict):
    url = attributes.get('HREF', '')
    name = attributes.get('NAME', shortcut_path.name)
    inside = structure.format(url=url, icon=icon, name=name)
    inside += '\n'.join(("{}={}".format(*i) for i in attributes.items()))
    inside += '\n'
    if shortcut_path.exists():
        number = 2
        while (shortcut_path.parent / (shortcut_path.stem + ' (' + str(number) + ').url')).exists():
            number += 1
        shortcut_path = shortcut_path.parent / (shortcut_path.stem + ' (' + str(number) + ').url')
    with open(shortcut_path, 'w') as shortcut:
        shortcut.write(inside)


def get_shortcut(shortcut_path: pathlib.Path):
    attributes = dict()
    with open(shortcut_path, 'r') as shortcut:
        inside = shortcut.readlines()
    for line in inside:
        if line[0] == '[':
            continue
        equal = line.find('=')
        end = line.rfind('\n')
        attributes[line[:equal]] = line[equal + 1:end]

    return attributes


if is_linux == 'Linux':
    structure = '''[Desktop Entry]
Encoding=UTF-8
Name={name}
Type=Link
URL={url}
Icon={icon}
'''
    illegal = {'/': '\\', '\x00': ''}
else:
    structure = '''[InternetShortcut]
IconIndex=0
URL={url}
IconFile={icon}
'''
