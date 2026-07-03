from pathlib import Path


class PathStore:
    def __init__(self, hash, audio_path):
        self.results_dir = Path(f'syncer_{hash}')
        self.aligned_texts = self.results_dir / 'aligned_texts.json'
        self.chapter_locations = self.results_dir / 'chapter_locations.json'
        self.aligned_audio = self.results_dir / 'aligned_audio.json'
        self.sync_map = self.results_dir / (
            'sync_map.json'
            if audio_path.is_dir()
            else audio_path.with_suffix('.json').name
        )
