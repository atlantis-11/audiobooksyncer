import hashlib
import json
from functools import wraps
from pathlib import Path
from typing import Callable, TypeVar

import magic

C = TypeVar('C', bound=Callable)


def save_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_from_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def cache(cache_file):
    def decorator(func: C) -> C:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if Path(cache_file).is_file():
                print(f'Using cached {cache_file}')
                return load_from_json(cache_file)
            else:
                res = func(*args, **kwargs)
                save_to_json(res, cache_file)
                return res

        return wrapper  # type: ignore[return-value]

    return decorator


def hash_files(*paths, hash_length=8):
    digest_obj = hashlib.md5()
    buffer_size = 2**18

    buffer = bytearray(buffer_size)  # Reusable buffer to reduce allocations.
    view = memoryview(buffer)

    for path in paths:
        with open(path, 'rb') as f:
            while size := f.readinto(buffer):
                digest_obj.update(view[:size])

    return digest_obj.hexdigest()[:hash_length]


def is_text_plain(file_path):
    return magic.from_file(file_path, mime=True) == 'text/plain'


def is_audio(file_path):
    # m4b is detected as video/mp4
    return (
        magic.from_file(file_path, mime=True).split('/')[0] == 'audio'
        or file_path.suffix == '.m4b'
    )


def get_audio_files(dir_path):
    return sorted([p for p in Path(dir_path).iterdir() if p.is_file() and is_audio(p)])
