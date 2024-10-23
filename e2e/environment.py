import tempfile


def before_scenario(context, scenario):
    context.cmd = ['python', '-m', 'audiobooksyncer']
    context.data_dir = tempfile.TemporaryDirectory()
