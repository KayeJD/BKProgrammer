from PyQt5.QtWidgets import QApplication, QWidget

import sys

app = QApplication(sys.argv)

window = QWidget()
window.show()

# Start the event loop.
app.exec()
