"""
PersonalKnowledgeEngine

GUI Events call functions housed in this file; serves "GUI"
"""


# IMPORTS (remember to list installed packages in "requirements.txt")
from pathlib import Path
import ntpath
import sys


# GLOBAL HARDCODED VARS (no magic numbers; all caps for names)


# DEFINITIONS (define all backend functions)

def search_file_for_string(path: str, key: str) -> list:
    """
    Search each line of a single file for a string key
    :param path: the relative or absolute path of the file to be searched
    :param key: The string to search through the file for
    :return: [(line# of key occurrence #1, full line of key occurrence #1), ...]
    """
    key_instances = []
    bolded_key = "<b>"+key+"</b>"
    with open(path) as f:
        # TODO: use mmap to allow searching across lines?
        # TODO: note that regex can also be done with mmap
        # TODO: https://realpython.com/python-mmap/
        # BELOW COPY PASTED FROM INTERNET
        # with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
        #     mmap_obj.find(b" the ")
        for i, line in enumerate(f):
            if key in line:  # if this line contains the key at least once
                key_value = 0
                key_counter = 0
                trimmed_array = []
                bolded_line = line.replace(key, bolded_key)
                split_line = bolded_line.split(" ")
                for words in split_line:
                    if bolded_key in words:
                        key_value = key_counter
                        break
                    key_counter += 1
                split_key = []
                if len(split_line) == 1:
                    split_key = split_line
                elif len(split_line) > 1:
                    if key_value < len(split_line)-1:
                        split_key = split_line[key_value:key_value+2]
                    elif key_value == len(split_line) - 1:
                        split_key = split_line[key_value-1:key_value+1]
                for word in split_key:
                    trimmed_array.append(word)
                trimmed_line =  "..."+" ".join(trimmed_array)+"..."
                key_instances.append((i+1, trimmed_line))
    
    return key_instances


def search_files_for_string(paths: list, key: str) -> list:
    """Searchs each line of a multiple files for a string key
    :param paths: a list of the relative or absolute paths to the files to be
                  searched
    :param key: The string to search through the files for
    :return: [ (path to file#1, [(line# of key occurrence #1, full line of keyoccurrence #1), ...] ) ...]
            ^ a list of tuples: file path, and the list of occurrences in file path
    """
    file_hits = []

    for file in paths:
        output_instances = search_file_for_string(file, key)
        if output_instances:
            file_hits.append((file, output_instances))
    return file_hits


def foreach_file(func,
                 terminate_early: list,
                 include_paths: list,
                 include_exts: list = None,
                 exclude_paths: list = None) -> None:
    """
    Calls the given function on every file that matches the given criteria.
    :param func: function to call. Receives only the file path as argument
    :param include_paths: list of directories/files to include
    :param include_exts: list of file extensions to include
    :param exclude_paths: list of directories/files to exclude

    Paths in include_paths will all be included regardless of exclude_paths
    and include_exts.
    """
    if include_exts is None:
        include_exts = []
    if exclude_paths is None:
        exclude_paths = []

    include_paths = [Path(path).absolute() for path in include_paths]
    exclude_paths = [Path(path).absolute() for path in exclude_paths]

    # print('include_paths:', include_paths)
    # print('exclude_paths:', exclude_paths)

    for path in include_paths:
        if not path.exists():
            raise FileNotFoundError(str(path))
    for path in exclude_paths:
        if not path.exists():
            raise FileNotFoundError(str(path))

    def is_excluded(path: Path, exclude_paths: list):
        for exclude_path in exclude_paths:
            if exclude_path in path.parents or exclude_path == path:
                return True
        return False

    def is_extension_included(path: Path):
        if include_exts is not None:
            if path.suffix in include_exts:
                return True
        return False

    def rec_helper(path: Path, exclude_paths: list):
        try:
            nonlocal terminate_early
            if terminate_early[0]:
                return
            if is_excluded(path, exclude_paths):
                return
            if path.is_dir():
                for subpath in path.glob('*'):
                    sub_exclude_paths = [
                        p for p in exclude_paths if path in p.parents
                    ]
                    rec_helper(subpath, sub_exclude_paths)
            else:
                if is_extension_included(path):
                    func(str(path))
        except OSError as e:
            print(e, file=sys.stderr)
        except UnicodeDecodeError as e:
            print('{}: {}'.format(e, path))
        except Exception as e:
            print(type(e), e, file=sys.stderr)

    for path in include_paths:
        if path.is_dir():
            # Narrow the list of excluded paths to only those that are inside
            # the current directory path
            sub_exclude_paths = [
                p for p in exclude_paths if path in p.parents
            ]
            rec_helper(path, sub_exclude_paths)
        else:
            func(str(path))


def search_for_string(result_callback,
                      finished_callback,
                      terminate_search,
                      key: str,
                      include_paths: list,
                      include_exts: list = None,
                      exclude_paths: list = None) -> None:
    """
    Search each line of every matching file for a string key
    :param key: the string to search through the files for
    :param include_paths: a list of paths of directories/files to be included
    :param include_exts: a list of file extensions to include
    :param exclude_paths: a list of path of directories/files to be excluded
    """
    print('search_for_string(')
    print('\tkey = \'%s\'' % key)
    print('\tinclude_paths =', include_paths)
    print('\tinclude_exts =', include_exts)
    print('\texclude_paths =', exclude_paths)
    print(')')

    def search_file_func(path: str):
        output_instances = search_file_for_string(path, key)
        if output_instances:
            result_callback(path, output_instances)

    foreach_file(search_file_func,
                 terminate_search,
                 include_paths,
                 include_exts,
                 exclude_paths)

    finished_callback()


def convert_readable(file_hits):
    """
    Returns tuple of: list of file names, list of line where key was found
    File names will be repeated in case of multiple hits in a file
    :file_hits: output from search_for_string()
    """
    file_names = []
    line_hits = []

    for file_output in file_hits:
        for line_info in file_output[1]:
            line_hits.append(line_info[1])
            file_names.append(ntpath.basename(file_output[0]))

    return (file_names, line_hits)
