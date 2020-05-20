import base64
import io
import pathlib
import sys
import uuid

from NetscapeBookmarksFileParser import *
from NetscapeBookmarksFileParser import creator
from NetscapeBookmarksFileParser import parser
from PIL import Image

import shortcuts

icons_path = pathlib.Path.cwd()


def create_folder(bookmark_folder: BookmarkFolder, destination: pathlib.Path):
    if destination.exists():
        number = 2
        while (destination.parent / (destination.name + ' (' + str(number) + ')')).exists():
            number += 1
        destination = destination.parent / (destination.name + ' (' + str(number) + ')')
    destination = destination.parent / shortcuts.slugify(destination.name)
    destination.mkdir(parents=True)
    meta = open(destination / '.meta', 'w')
    items = bookmark_folder.items
    bookmark_folder.items = []
    meta.writelines(creator.folder_creator(bookmark_folder)[0])
    meta.close()
    bookmark_folder.items = items
    for shortcut in bookmark_folder.shortcuts:
        ico_path = ''
        if shortcut.icon_base64 and 'data:image/png;base64' in shortcut.icon_base64[:25]:
            encoded = shortcut.icon_base64[shortcut.icon_base64.find(','):]
            data = base64.b64decode(encoded)
            ico = Image.open(io.BytesIO(data))
            ico_path = icons_path / (str(uuid.uuid4()) + '.ico')
            ico.save(ico_path)
            ico_path = ico_path.resolve()
            ico_path = ico_path.absolute()

        s = creator.shortcut_creator(shortcut)
        attributes = parser.attribute_extractor(s[0][6:])
        attributes['NAME'] = shortcut.name
        if len(s) == 2:
            attributes['COMMENT'] = shortcut.comment
        if shortcut.name:
            shortcut_path = destination / (shortcuts.slugify(shortcut.name) + '.url')
        else:
            shortcut_path = destination / '_.url'
        shortcuts.create_shortcut(shortcut_path, ico_path, attributes)

    for child in bookmark_folder.children:
        child_destination = destination / child.name
        create_folder(child, child_destination)


def get_folder(dir_path: pathlib.Path):
    folder = BookmarkFolder()
    meta = dir_path / '.meta'
    if meta.exists():
        tag = meta.open().readlines()[0]
        folder = parser.folder_handler(0, tag, [])
    for item in dir_path.iterdir():
        if item.is_file() and item.suffix == '.url':
            attributes = shortcuts.get_shortcut(item)
            comment = attributes.get('COMMENT', '')
            attributes['NAME'] = attributes.get('Name', item.stem)
            attributes['HREF'] = attributes['URL']
            icon_path = attributes.get('Icon', attributes.get('IconFile'))
            if icon_path:
                icon = Image.open(icon_path)
                img = io.BytesIO()
                icon.save(img, format='PNG')
                icon.close()
                attributes['ICON'] = 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode("utf-8")

            attributes = '<DT><A' + creator.attribute_printer(attributes) + '>' + attributes['NAME'] + '</A>'
            shortcut = parser.shortcut_tag_extractor(attributes)
            shortcut.comment = comment
            folder.items.append(shortcut)
        if item.is_dir():
            folder.items.append(get_folder(item))
    folder.split_items()
    return folder


def bookmark_to_dir(file_path: pathlib.Path, destination=None):
    if destination is None:
        destination = file_path.parent
    bookmarks = None
    with open(file_path) as file:
        f = NetscapeBookmarksFile(file)
        f.parse()
        bookmarks = f.bookmarks
    if bookmarks == BookmarkFolder():
        raise Exception('No bookmarks found')

    global icons_path
    icons_path = destination / '.icons'
    icons_path.mkdir(parents=True)
    destination = destination / file_path.stem

    if destination.exists():
        number = 2
        while destination.exists():
            destination = destination.parent / (destination.name + ' (' + str(number) + ')')
            number += 1
    destination.mkdir(parents=True)

    f.bookmarks = BookmarkFolder()
    f.html = ''
    f.create_file()
    with open(destination / '.meta', 'w') as meta:
        meta.write(f.html)
    folder = destination / bookmarks.name
    create_folder(bookmarks, folder)


def dir_to_bookmark(dir_path: pathlib.Path, file_destination: pathlib = None):
    if file_destination is None:
        file_destination = dir_path.parent / (dir_path.name + '.html')
    meta = dir_path.parent / '.meta'
    file = NetscapeBookmarksFile()
    if meta.exists():
        file = NetscapeBookmarksFile(meta.open().read())
        file.parse()
    for item in dir_path.iterdir():
        if item.is_dir() and not item.name == '.icons':
            file.bookmarks = get_folder(item)
            break

    file.create_file()
    with open(file_destination, 'w') as bookmarks:
        bookmarks.write(file.html)


def main():
    if len(sys.argv) == 1:
        print('''usage: 
bookmarks_to_dir <file> <dir_destination>
bookmarks_to_dir <dir> <file_destination>
destination is optional
''')

    if len(sys.argv) > 1:
        item = pathlib.Path(sys.argv[1])
        destination = None
        if len(sys.argv) > 2:
            destination = pathlib.Path(sys.argv[2])
        function = None
        if item.is_file():
            function = bookmark_to_dir
        elif item.is_dir():
            function = dir_to_bookmark

        if destination:
            function(item, destination)
        else:
            function(item)


if __name__ == "__main__":
    main()
