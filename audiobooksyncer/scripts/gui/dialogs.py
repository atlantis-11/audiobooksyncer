from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpacerItem,
)


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')

        self.settings = settings.copy()
        self.settings_inputs = {}

        layout = QFormLayout()

        for k, v in self.settings.items():
            setting_input = QLineEdit()
            setting_input.setValidator(QIntValidator())
            setting_input.setText(str(v))
            self.settings_inputs[k] = setting_input
            layout.addRow(f'{k.name.replace("_", " ").capitalize()}:', setting_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addItem(QSpacerItem(0, 20))
        layout.addWidget(buttons)
        layout.setHorizontalSpacing(20)

        self.setLayout(layout)

    def get_settings(self):
        return {
            k: int(self.settings_inputs[k].text() or v)
            for k, v in self.settings.items()
        }
