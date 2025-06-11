# audiobooksyncer

An application to synchronize an audiobook with text and its translation.

The purpose of this app is to simplify the experience of listening to audiobooks in a foreign language, so you can quickly look up what's being said and check the translation if needed.

Under the hood, the following packages are used:
- [aeneas](https://github.com/readbeyond/aeneas) - to sync text with audio
- [bertalign](https://github.com/bfsujason/bertalign) - to sync text with translation
- [whisper](https://github.com/openai/whisper) - to find where the audio files begin in text.

## Requirements

This app can only be used on Linux and you need a GPU with CUDA support (though you can run it on CPU). Tested with Python 3.10.

You also need the following packages installed:
- gcc/clang
- libespeak-dev
- ffmpeg

These are mostly needed by aeneas, for troubleshooting check it's [dependencies](https://github.com/readbeyond/aeneas/blob/master/install_dependencies.sh).

## Installation

`requirements.txt` contains pinned versions of all dependencies, which are guaranteed to work.

```bash
# if you only want to install the dependencies
pip install -r requirements.txt
# if you want to install the app
pip install . -c requirements.txt
```

## Usage

If you install the app, you can use `audiobooksyncer` script. Otherwise, you can run the package directly with `python -m audiobooksyncer`.

As an input provide book's text, translation (plain text files) and a directory which contains audiobook's files.

```bash
python -m audiobooksyncer book_de.txt book_en.txt audiobook/
```

The shorter the audio files, the better the result, around an hour is fine. You can set `--aeneas_dtw_margin` for longer files (default is 120 seconds).

Text to audio sync requires quite a bit of RAM. The audio files are processed in parallel, with the number of processes equal to CPU count by default (can be set with `--aeneas_processes`). RAM is mostly used up in the second part of processing of each file, so if you have several big files with the same duration, this peak might add up.

There is also a Docker image, you can run the container using:
```bash
docker run -it --gpus all -v .:/work atlantisj11/audiobooksyncer book_de.txt book_en.txt audiobook/
```

Make sure to put files for alignment into the mounted directory.

To use the GPU follow [this](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) guide.

## Results

Results will be stored in a directory created in CWD, the directory's name is unique for different inputs, each step's result will be stored in a json file and reused on consecutive runs.

The sync map file contains json array with each element containing part of the text, part of the translation and time interval in ms.

```json
[
  {
    "src": "Der Hobbit",
    "tgt": "The Hobbit",
    "begin": 0,
    "end": 1880
  },
  ...
]
```

Sync map can be converted into subtitles files using:

```bash
python tools/sync_map_to_srt.py syncer_abcd1234/sync_map.json
```

Usage example:

```bash
mpv --force-window --merge-files --sub-file=syncer_abcd1234/subtitles.srt audio/*
```

You can also use [AudiobookSyncerReader](https://github.com/atlantis-11/AudiobookSyncerReader) app for Android.
