from django.conf import settings
from pathlib import Path
import zlib

def parse_path_string(path: str):
    path = path.split("/")
    path = path if path[-1] != "" else path[:-1]
    return path

def get_repo_path(test, submission):
    repo_path = settings.SUBMISSIONS_DIR / test.test_id / submission.student.index_no / ".texam"
    return repo_path

def get_objects_path(test, submission):
    repo_path = get_objects_path(test, submission)
    return repo_path / "objects"

def get_root_commit_hash(repo_path: Path):
    HEAD_FILE = repo_path / "HEAD"
    return HEAD_FILE.read_text()

def get_object_path(repo_path: Path, hash):
    return repo_path / "objects" / hash[:2] / hash[2:]

def get_object_parts(path):
    with open(path, "rb") as f:
        data = zlib.decompress(f.read())
        header, body = data.split(b"\x00")
    return header, body

def get_root_commit(repo_path: Path):
    root_commit_hash = get_root_commit_hash(repo_path)
    commit_obj_path = get_object_path(repo_path, root_commit_hash)
    commit_data = zlib.decompress(commit_obj_path.read_bytes())
    return commit_data

def get_root_tree_hash(repo_path: Path):
    root_commit_hash = get_root_commit_hash(repo_path)
    commit_obj_path = get_object_path(repo_path, root_commit_hash)
    _, hash = get_object_parts(commit_obj_path)
    return hash

def get_tree(repo_path: Path, hash=None):
    if hash is None:
        tree_hash = get_root_tree_hash(repo_path).decode()
    else:
        tree_hash = hash
    root_tree_path = get_object_path(repo_path, tree_hash)
    header, body = get_object_parts(root_tree_path)
    if header != b"tree":
        raise Exception("Not a tree")
    tree_entries_txt = body.decode()
    entries = []
    for entry in tree_entries_txt.split("\n"):
        entries.append(tuple(entry.split()))
    return entries

def get_path_obj_entry(repo_path: Path, path_array=None, start_tree=None):
    tree = get_tree(repo_path, start_tree) # root tree if start_tree is None
    if path_array is None:
        return ("tree", get_root_tree_hash(repo_path).decode(), "/")
    for type, hash, obj_txt in tree:
        # current entry is a tree and 
        # is not the last element in path
        if type == "tree" and obj_txt != path_array[-1]:
            try:
                current_obj_index = path_array.index(obj_txt)
            except ValueError:
                print(obj_txt, type)
                print("Got here")
                continue
            return get_path_obj_entry(repo_path, path_array[current_obj_index + 1:], hash)
        # if the end has been reached
        # and a match has been found
        elif len(path_array) == 1 and obj_txt == path_array[-1]:
            return (type, hash, obj_txt)
    return None

def render_tree_content(content):
    content = content.split("\n")
    tree_content = []
    for tree in content:
        (type, hash, obj_name) = tree.split()
        tree_content.append(obj_name)
    return tree_content


def render_blob_content(content):
    content = content
    print("Content", content)
    return content

def get_content(repo_path: Path, hash):
    object_path = get_object_path(repo_path, hash)
    header, body = get_object_parts(object_path)
    header = header.decode()
    body = body.decode()
    if header == "tree":
        return render_tree_content(body)
    elif header == "blob":
        return render_blob_content(body)
    raise Exception("Invalid object type {}".format(header))