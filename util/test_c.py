import sys
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import *


app = QApplication(sys.argv)
model = QStandardItemModel()

items = [("ABC", True),
         ("DEF", False),
         ("GHI", False)]

for text, checked in items:

    text_item = QStandardItem(text)
    checked_item = QStandardItem()
    checked_item.setData(QVariant(checked), Qt.CheckStateRole)
    model.appendRow([text_item, checked_item])

view = QTreeView()
view.header().hide()
view.setRootIsDecorated(False)

combo = QComboBox()
combo.setView(view)
combo.setModel(model)
combo.show()

sys.exit(app.exec_())