import subprocess
from pathlib import Path

import yt_dlp
from behave import given, then, when
from utils import get_paste

# ruff: noqa

texts = {
    'English': 'W8SQUkvz',
    'French': 'EdcmSZFV',
    'Ukrainian': 'qu6DjZef',
}

audios = {
    'English': 'PL3rkKR0yL0XtsiNRPhly4JeNlfr1hln40',
    'French': 'PLByCwBBiZjzm8I0f53jQ4eu83mCmPBKvM',
}


@given('{language} text')
def step_impl(context, language):
    file_path = context.data_dir.name + f'/{language}.txt'

    with open(file_path, 'w+', encoding='utf-8') as f:
        f.write(get_paste(texts[language]))

    context.cmd.append(file_path)


@given('{language} audio')
def step_impl(context, language):
    playlist_url = audios[language]

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
            }
        ],
        'playlist_items': '1-2',
        'outtmpl': context.data_dir.name + '/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    context.cmd.append(context.data_dir.name)


@when('run the app')
def step_impl(context):
    context.cmd.append('-y')
    p = subprocess.run(context.cmd, capture_output=True, text=True)

    for line in p.stdout.splitlines():
        dir = line.split('Saving results to ')

        if len(dir) == 2:
            context.results_dir = dir[1]
            break


@then('we get a folder with sync map')
def step_impl(context):
    assert (Path(context.results_dir) / 'sync_map.json').is_file()
