import platform
import pathlib

structure = ''


def create_shortcut(shortcut_path: pathlib.Path, icon: str, attributes: dict):
    url = attributes.get('HREF', '')
    name = attributes.get('NAME', shortcut_path.name)
    inside = structure.format(url=url, icon=icon, name=name)
    inside += '\n'.join(("{}={}".format(*i) for i in attributes.items()))
    inside += '\n'
    if shortcut_path.exists():
        number = 2
        while shortcut_path.exists():
            destination = shortcut_path.parent / (shortcut_path.name + ' (' + str(number) + ')')
            number += 1
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


if platform.system() == 'Linux':
    structure = '''[Desktop Entry]
Encoding=UTF-8
Name={name}
Type=Link
URL={url}
Icon={icon}
'''
else:
    structure = '''[InternetShortcut]
IconIndex=0
URL={url}
IconFile={icon}
'''
