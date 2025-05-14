import re

from loguru import logger
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ...core import config
from ...utils import get_audio_files, is_text_plain
from .dialogs import SettingsDialog
from .enums import (
    ActionButtonState,
    InputType,
    ProcessingState,
    Settings,
)


class App(QMainWindow):
    WIDGETS_HEIGHT = 30

    def __init__(self):
        super().__init__()
        self.setWindowTitle('audiobooksyncer')
        self.resize(700, 350)

        self.inputs = {
            InputType.src: None,
            InputType.tgt: None,
            InputType.audio: None,
        }
        self.settings = {
            Settings.aeneas_dtw_margin: config.aeneas_dtw_margin,
            Settings.aeneas_processes: config.aeneas_processes,
        }
        self.processing_state = ProcessingState.NotProcessing

        self.init_ui()

    def init_ui(self):
        self.src_label, self.src_btn = self.create_file_selector(
            'Source text:', InputType.src
        )
        self.tgt_label, self.tgt_btn = self.create_file_selector(
            'Target text:', InputType.tgt
        )
        self.audio_label, self.audio_btn = self.create_file_selector(
            'Audio dir:', InputType.audio
        )

        grid_layout = QGridLayout()

        grid_layout.addWidget(self.src_label, 0, 0)
        grid_layout.addWidget(self.src_btn, 0, 1)

        grid_layout.addWidget(self.tgt_label, 1, 0)
        grid_layout.addWidget(self.tgt_btn, 1, 1)

        grid_layout.addWidget(self.audio_label, 2, 0)
        grid_layout.addWidget(self.audio_btn, 2, 1)

        self.step_label = QLabel()

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(self.WIDGETS_HEIGHT)

        self.action_btn = QPushButton(ActionButtonState.Run.name)
        self.action_btn.setFixedHeight(self.WIDGETS_HEIGHT)
        self.action_btn.clicked.connect(self.handle_action)

        self.confirm_cb = QCheckBox('Auto confirm')

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.action_btn, stretch=1)
        action_layout.addWidget(self.confirm_cb, stretch=0)

        self.status_bar = QStatusBar()
        self.status_bar_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_bar_label)
        self.setStatusBar(self.status_bar)

        layout = QVBoxLayout()
        layout.addLayout(grid_layout)
        layout.addWidget(self.step_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(action_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')

        open_settings_action = settings_menu.addAction('Configure...')
        open_settings_action.triggered.connect(self.open_settings)

        self.reset_ui()

    def create_file_selector(self, label_text, key):
        label = QLabel(label_text)
        button = QPushButton('Select')
        button.setFixedHeight(self.WIDGETS_HEIGHT)
        button.setStyleSheet('QPushButton { padding: 0px 20px; }')
        button.clicked.connect(lambda: self.select_file_or_dir(key))
        return label, button

    def reset_ui(self):
        self.action_btn.setText(ActionButtonState.Run.name)
        self.status_bar_label.setText('')
        self.step_label.hide()
        self.progress_bar.hide()

    def start_ui(self):
        self.action_btn.setText(ActionButtonState.Cancel.name)
        self.step_label.setText('Started')
        self.progress_bar.setValue(0)
        self.step_label.show()
        self.progress_bar.show()

    def select_file_or_dir(self, key):
        selected = None
        error = None

        if key == InputType.audio:
            selected = QFileDialog.getExistingDirectory(self)
            if selected and not get_audio_files(selected):
                error = 'No audio files'
        else:
            selected, _ = QFileDialog.getOpenFileName(self)
            if selected and not is_text_plain(selected):
                error = 'Not plain text'

        if not selected or self.inputs[key] == selected:
            return

        if error:
            QMessageBox.warning(self, 'Input Error', error)
            return

        self.inputs[key] = selected
        button = getattr(self, f'{key.name}_btn')
        button.setText(selected)

        if self.processing_state != ProcessingState.NotProcessing:
            self.handle_cancel()

    def handle_action(self):
        if self.processing_state == ProcessingState.NotProcessing:
            self.handle_start()
        elif self.processing_state == ProcessingState.Processing:
            self.handle_cancel()
        elif self.processing_state == ProcessingState.Waiting:
            self.handle_confirm()

    def handle_start(self):
        if not all([v for v in self.inputs.values()]):
            QMessageBox.warning(self, 'Input Error', 'Some inputs are empty')
            return

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.start(
            'python',
            [
                '-m',
                'audiobooksyncer',
                self.inputs[InputType.src],
                self.inputs[InputType.tgt],
                self.inputs[InputType.audio],
            ]
            + [f'--{k.name}={v}' for k, v in self.settings.items()],
        )
        logger.info('New process started')
        self.processing_state = ProcessingState.Processing

        self.start_ui()

    def handle_cancel(self):
        self.processing_state = ProcessingState.NotProcessing
        self.process.terminate()
        self.reset_ui()

    def handle_confirm(self):
        self.process.write(b'y\n')
        self.processing_state = ProcessingState.Processing
        self.action_btn.setText(ActionButtonState.Cancel.name)

    def handle_stdout(self):
        output = self.process.readAllStandardOutput().data().decode().splitlines()
        for line in output:
            logger.info(line)
            if line.startswith('Saving results'):
                self.status_bar_label.setText(line)
            elif line.startswith('STEP'):
                self.step_label.setText(line)
                self.progress_bar.setValue(0)
            elif line.startswith('Done'):
                self.progress_bar.setValue(100)
                if self.confirm_cb.isChecked():
                    self.handle_confirm()
                else:
                    self.action_btn.setText(ActionButtonState.Next.name)
                    self.processing_state = ProcessingState.Waiting
            elif line.startswith('Using cached'):
                self.step_label.setText(f'{self.step_label.text()}\n{line}')

    def handle_stderr(self):
        output = self.process.readAllStandardError().data().decode().splitlines()
        for line in output:
            logger.error(line)
            if match := re.search(r'(\d+)%', line):
                self.progress_bar.setValue(int(match.group(1)))
            elif line != '':
                self.step_label.setText('An unexpected error occured')

    def process_finished(self):
        logger.info('Process finished')
        self.processing_state = ProcessingState.NotProcessing
        self.progress_bar.setValue(100)
        self.action_btn.setText(ActionButtonState.Run.name)

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings = dialog.get_settings()
            logger.info(f'Settings updated: {self.settings}')
