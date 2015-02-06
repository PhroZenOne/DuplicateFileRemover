import os, sys, hashlib
import tkinter
import tkinter.filedialog

START_BYTES = 4;

def start(folder):
    folder = os.path.normpath(folder)
    print("Finding all files\n ")
    list_of_files, count = create_list_of_files(folder, 0);

    print("\nFound a total of " + str(count) + " files, lets start comparing them")
    chunks = sort_by_size(list_of_files);
    
    print(str(len(chunks)) + " unique file sizes.")

    #filter out chunks with only one file as it can only be unique    
    chunks = {key: value for key, value in chunks.items() if len(value) > 1}
    
    chunk_size = len(chunks)
    print(str(chunk_size) + " file groups with same file size.")
    
    #filter out those file who has unique first START_BYTES bytes.
    for chunk in chunks.values():
        remove_if_not_same_first_bytes(chunk);
        chunk_size = chunk_size  - 1
        print("\rSorted files remaining:" + str(chunk_size), end="",  file=sys.stdout, flush=True)

    #filter out chunks with only one file as it can only be unique
    chunks = {key: value for key, value in chunks.items() if len(value) > 1}
    chunk_size = len(chunks)

    print("\n-------------------------------")
    print(str(chunk_size) + " file groups with same size and first " + str(START_BYTES) + " bytes.")
    input("any key to continue")

    total_removed = 0
    for chunk in chunks.values():
        total_removed += remove_if_same_md5(chunk);
        chunk_size = chunk_size  - 1
        print("\r" + str(chunk_size) + " chunks left. Removed " + str(total_removed) + " files.", end="",  file=sys.stdout, flush=True)


def create_list_of_files(folder, i):
    list_of_files = []
    for path, dirs, files in os.walk(folder):
        for name in files:
            p = os.path.join(path, name).replace("\\","/")
            list_of_files.append(p)
            i = i + 1
            print("\rFiles found: " + str(i), end="",  file=sys.stdout, flush=True)
    return list_of_files, i;


def sort_by_size(list_of_files):
    chunks = dict()
    for file in list_of_files:
        statinfo = os.stat(file)
        if not statinfo.st_size in chunks:
            chunks[statinfo.st_size] = []
        chunks[statinfo.st_size].append(file)
    return chunks


def remove_if_not_same_first_bytes(chunk):
    first_bytes = dict()
    for path in chunk:
        with open(path, "rb") as f:
            first = f.read(START_BYTES)
            if not first in first_bytes:
                first_bytes[first] = []
            first_bytes[first].append(path)
    all_single_ones = [value[0] for value in first_bytes.values() if len(value) == 1]
    chunk[:] = [x for x in chunk if not x in all_single_ones]

        
def remove_if_same_md5(chunk):
    removed = 0
    hashes = dict();
    for path in chunk:
        with open(path, "rb") as f:
            md5 = md5_for_file(f)
            f.close()
            if md5 in hashes :
                try:
                    os.remove(path)
                    removed = removed + 1
                except OSError as e:
                    print(e)
            else:
                hashes[md5] = path
    return removed


def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()


root = tkinter.Tk()
root.withdraw()
file_path = tkinter.filedialog.askdirectory()

start(file_path)

print("\nFinshed!")
input("\nAny key to end!")
