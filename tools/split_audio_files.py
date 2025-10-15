import math
from pathlib import Path

import click
import ffmpeg

from audiobooksyncer.core.utils import get_audio_duration
from audiobooksyncer.utils import get_audio_files


@click.command()
@click.argument(
    'audio_dir', type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    '--minutes',
    default=60,
    show_default=True,
    help='Maximum duration (in minutes) for each audio segment',
)
def main(audio_dir: Path, minutes: int):
    max_segment_seconds = minutes * 60

    files_to_split = [
        f
        for f in get_audio_files(audio_dir)
        if get_audio_duration(f) > max_segment_seconds
    ]

    for f in files_to_split:
        duration = get_audio_duration(f)
        parts = math.ceil(duration / max_segment_seconds)
        segment_duration = duration / parts

        print(
            f'{f} is {int(duration / 60)} minutes, splitting into {parts} parts, each approx. {int(segment_duration / 60)} minutes'
        )

        for i in range(parts):
            start = i * segment_duration
            output_file = f.with_name(f'{f.stem}_part{i + 1:02}{f.suffix}')

            ffmpeg.input(f, ss=start, t=segment_duration).output(
                str(output_file), c='copy', vn=None
            ).run(quiet=True)

        print('Finished splitting')
        f.unlink()
        print('Deleted original file')


if __name__ == '__main__':
    main()
