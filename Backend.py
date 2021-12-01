"""
PersonalKnowledgeEngine

GUI Events call functions housed in this file; serves "GUI"
"""


# IMPORTS (remember to list installed packages in "requirements.txt")
from pathlib import Path
import sys


# GLOBAL HARDCODED VARS (no magic numbers; all caps for names)
SEARCH_CONTEXT_WORDS = 11


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
        for i, line in enumerate(f):
            if key in line:  # if this line contains the key at least once
                line = line.strip(" \n\r\t")
                # Bold any instances of the key inside the line
                key_value = 0
                key_counter = 0
                trimmed_array = []
                bolded_line = line.replace(key, bolded_key)
                split_line = bolded_line.split(" ")

                # Shorten the line to only contain the first instance of the key term 
                # and the first few words afterwards
                for words in split_line:
                    if bolded_key in words:
                        key_value = key_counter
                        break
                    key_counter += 1
                split_key = []
                start = key_value - SEARCH_CONTEXT_WORDS // 2
                end = start + SEARCH_CONTEXT_WORDS
                split_key = split_line[max(0, start):end]
                for word in split_key:
                    trimmed_array.append(word)
                trimmed_line =  "..."+" ".join(trimmed_array)+"..."
                key_instances.append((trimmed_line, i+1))

    return key_instances


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
    if exclude_paths is None:
        exclude_paths = []

    include_paths = [Path(path).absolute() for path in include_paths]
    exclude_paths = [Path(path).absolute() for path in exclude_paths]

    for path in include_paths:
        if not path.exists():
            raise FileNotFoundError(str(path))
    for path in exclude_paths:
        if not path.exists():
            raise FileNotFoundError(str(path))

    def is_excluded(path: Path, exclude_paths: list):
        """Returns whether a file is excluded by `exclude_paths`
        """
        for exclude_path in exclude_paths:
            if exclude_path in path.parents or exclude_path == path:
                return True
        return False

    def is_extension_included(path: Path):
        """Returns whether a file is included by `include_paths`
        """
        if include_exts is not None:
            if path.suffix in include_exts:
                return True
        else:
            return True
        return False

    def rec_helper(path: Path, exclude_paths: list):
        """Recursively calls `func` on all matching descendant file paths.
        """
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
        except UnicodeDecodeError:
            pass
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
    """Search each line of every matching file for a string key

    :param result_callback: function to call with a search hit
    :param finished_callback: function to call when the search is over.
                              called even if the search is terminated early
    :param terminate_search: single-element list containing a bool that says
                             whether to terminate the search early
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
        """This is called in foreach_file with every matching file path.
        """
        output_instances = search_file_for_string(path, key)
        if output_instances:
            result_callback(path, output_instances)

    foreach_file(search_file_func,
                 terminate_search,
                 include_paths,
                 include_exts,
                 exclude_paths)

    finished_callback()
