import os

import requests

api_dev_key = os.environ['api_dev_key']

api_user_key = requests.post(
    'https://pastebin.com/api/api_login.php',
    {
        'api_dev_key': api_dev_key,
        'api_user_name': os.environ['api_user_name'],
        'api_user_password': os.environ['api_user_password'],
    },
).content


def get_paste(paste_key):
    return requests.post(
        'https://pastebin.com/api/api_post.php',
        {
            'api_dev_key': api_dev_key,
            'api_user_key': api_user_key,
            'api_paste_key': paste_key,
            'api_option': 'show_paste',
        },
    ).content.decode('utf-8')
