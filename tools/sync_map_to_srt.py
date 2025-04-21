import json
from datetime import timedelta
from pathlib import Path

import click
import srt


def ms_to_timedelta(ms):
    return timedelta(milliseconds=ms)


@click.command()
@click.argument('sync_map_file', type=click.Path(exists=True, dir_okay=False))
def sync_map_to_srt(sync_map_file):
    with open(sync_map_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    subtitles = [
        srt.Subtitle(
            index=i + 1,
            start=ms_to_timedelta(fr['begin']),
            end=ms_to_timedelta(fr['end']),
            content=f'{fr["src"]}\n-\n{fr["tgt"]}',
        )
        for i, fr in enumerate(data)
    ]

    with open(Path(sync_map_file).parent / 'subtitles.srt', 'w', encoding='utf-8') as f:
        f.write(srt.compose(subtitles))


if __name__ == '__main__':
    sync_map_to_srt()
