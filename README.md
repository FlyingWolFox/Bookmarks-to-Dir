# Bookmarks to Dir
This script will convert a bookmarks html export from a browser to a directory structure and the way back.

## Depedencies
- [NetscapeBookmarksFileParser](https://github.com/FlyingWolFox/Netscape-Bookmarks-File-Parser)
- PIL
- SVGLIB

## How to use
```bash
bookmarks_to_dir <file> <dir_destination>
bookmarks_to_dir <dir> <file_destination>
```

Pass a bookmarks file as argument to be converted into a dir structure. If you pass
a directory as second argument, the dir will be put there.

After you're done, pass the folder created to the script and it'll convert to a
bookmarks file ready to be imported. If you pass a directory as second argument,
the file will be put there.

## How is the dir structure

A directory with the name of the file. Inside will be the bookmarks folder tree root
and a .meta file. The .meta file contains some info about the file. The bookmark root
will be named by the H1 tag of the file. Inside of it, there will be all folders and shortcuts.
The bookmarks shortcuts will be converted to internet shortcuts, what can change the names
of the shortcuts (mainly on Windows due to path limitations), same applies to bookmark
folders. Every folder has a .meta file that contains some properties of the folder.

In the same directory of the said directory with the file name, there will be a .icons
dir, there will be all icons of the shortcuts, if they're present on the html file.

#### PS: The order of the bookmarks is lost by converting the bookmarks

## Help

If you encounter any problems or bugs, create a new issue. If you're a dev and wants to help,
you can create a Pull Request. Everything helps!
