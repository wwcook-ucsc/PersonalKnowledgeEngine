"""
PersonalKnowledgeEngine



GUI Events call functions housed in this file; serves "GUI_Master_Script"
"""



# IMPORTS (remember to list installed packages in "requirements.txt")


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
    with open(path) as f:
        # TODO: use mmap to allow searching across lines?
        # TODO: note that regex can also be done with mmap
        # TODO: https://realpython.com/python-mmap/
        # BELOW COPY PASTED FROM INTERNET
        # with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
        #     mmap_obj.find(b" the ")
        for i, line in enumerate(f):
            if key in line:  # if this line contains the key at least once
                key_instances.append((i+1, line))
    return key_instances

def search_files_for_string(paths: list, key: str) -> list:
    """
    Search each line of a multiple files for a string key
    :param paths: a list of the relative or absolute paths to the files to be searched
    :param key: The string to search through the files for
    :return: [ (path to file#1, [(line# of key occurrence #1, full line of key occurrence #1), ...] ) ...]
            ^ a list of tuples: file path, and the list of occurrences in file path
    """
    file_hits = [] 

    for file in paths:
        output_instances = search_file_for_string(file, key)
        if output_instances:
            file_hits.append((file, output_instances))
    return file_hits