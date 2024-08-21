import click
import warnings
import hashlib
from pathlib import Path
from ..core.texts_aligner import *
from ..core.text_audio_aligner import *
from ..core.chapter_locator import *
from ..core.output_generator import *
from ..utils import *
from ..pathstore import *

warnings.filterwarnings('ignore')

def _get_hash(*paths):
    abs_paths = [os.path.abspath(p) for p in paths]
    return hashlib.md5(''.join(abs_paths).encode()).hexdigest()[:8]

def _ask_to_continue(skip_confirmation):
    if skip_confirmation:
        return
    if not click.confirm('Done. Continue?', default=True):
        exit(0)

@click.command()
@click.argument('src_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('tgt_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('audio_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--yes', '-y', is_flag=True)
def main(src_path, tgt_path, audio_dir, yes):
    paths = PathStore(_get_hash(src_path, tgt_path, audio_dir))

    global align_texts
    global locate_chapters
    global align_text_with_audio

    align_texts = cache(paths.aligned_texts)(align_texts)
    locate_chapters = cache(paths.chapter_locations)(locate_chapters)
    align_text_with_audio = cache(paths.aligned_audio)(align_text_with_audio)

    ac = lambda: _ask_to_continue(yes)

    os.environ['TOKENIZERS_PARALLELISM'] = 'true'

    print(f'Saving results to {paths.results_dir}')
    Path(paths.results_dir).mkdir(exist_ok=True)

    print('\nSTEP 1: Aligning text and translation')
    aligned_texts = align_texts(src_path, tgt_path)
    src_fragments = [i['src'] for i in aligned_texts['data']]

    ac()

    print('\nSTEP 2: Locating where each audio file starts')
    split_indexes = locate_chapters(src_fragments, audio_dir)

    ac()

    print('\nSTEP 3: Aligning text and audio')
    aligned_audio = align_text_with_audio(src_fragments, split_indexes, audio_dir, aligned_texts['src_lang_code'])

    ac()

    print(f'\nSTEP 4: Saving result to {paths.sync_map}')
    save_to_json(get_sync_map(aligned_texts['data'], aligned_audio), paths.sync_map)