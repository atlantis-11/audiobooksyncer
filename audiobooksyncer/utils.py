import hashlib
import json
import math
from functools import wraps
from pathlib import Path
from typing import Callable, TypeVar

import ffmpeg
import magic
from tqdm import tqdm

from .core.utils import get_audio_duration

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


def split_audio_file(file_path, max_duration_minutes, output_dir):
    """Split audio file into multiple smaller files."""
    file_path = Path(file_path)

    duration = get_audio_duration(file_path)
    parts = math.ceil(duration / (max_duration_minutes * 60))
    part_duration = duration / parts

    print(
        f'{file_path} is {int(duration / 60)} minutes, splitting into {parts} parts, each approx. {int(part_duration / 60)} minutes'
    )

    output_files = []

    for i in tqdm(range(parts)):
        start = i * part_duration
        output_file = Path(output_dir) / Path(
            f'{file_path.stem}_part{i + 1:02}{file_path.suffix}'
        )

        ffmpeg.input(file_path, ss=start, t=part_duration).output(
            str(output_file), c='copy', vn=None
        ).run(quiet=True)

        output_files.append(output_file)

    return output_files
