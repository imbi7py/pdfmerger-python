from fbs_runtime.application_context import ApplicationContext
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import PyPDF2, sys


import document as doc


class DocumentTableModel(QAbstractTableModel):
    def __init__(self, document_list, parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.documents = document_list
        self.headers = ['File', 'Start', 'End']

    def rowCount(self, parent):
        return len(self.documents)

    def columnCount(self, parent):
        return len(self.headers)

    def flags(self, index):
        row = index.row()
        col = index.column()
        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == Qt.EditRole:
            if col == 1:
                return self.documents[row].start
            elif col == 2:
                return self.documents[row].end

        if role == Qt.DisplayRole:
            if col == 0:
                return self.documents[row].path
            elif col == 1:
                return self.documents[row].start
            elif col == 2:
                return self.documents[row].end

    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            max_value = self.documents[row].pdf.numPages
            old_start = self.documents[row].start
            old_end = self.documents[row].end

            try:
                new_value = int(value)
                if col == 1 and new_value > 0 and new_value <= old_end:
                    self.documents[row].start = new_value
                    self.dataChanged.emit(index, index)
                    return True
                elif (col == 2 and new_value >= old_start
                        and new_value <= max_value):
                    self.documents[row].end = new_value
                    self.dataChanged.emit(index, index)
                    return True
            except TypeError:
                return False
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "Not implemented"

    def insertRows(self, row, count, parent = QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self.documents.insert(row, Document())
        self.endInsertRows()
        
        return True

    def removeRows(self, row, count, parent = QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1);
        for i in range(count):
            self.documents.pop(row)
        self.endRemoveRows()

        return True

    def addDocument(self, document):
        self.layoutAboutToBeChanged.emit()
        self.documents.append(document)
        self.layoutChanged.emit()


class PDFMergerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.docs = []
        self.table = QTableView(self)
        self.model = DocumentTableModel(self.docs)
        self.table.setModel(self.model)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.setCentralWidget(self.table)

        self.add_action = QAction('Add', self)
        self.add_action.triggered.connect(self.addFile)

        self.clear_action = QAction('Clear', self)
        #self.clear_action.triggered.connect(self.removeAll)

        self.duplicate_action = QAction('Duplicate', self)
        #self.duplicate_action.triggered.connect(self.duplicate)

        self.remove_action = QAction('Remove', self)
        self.remove_action.triggered.connect(self.remove)

        self.move_up_action = QAction('Move Up', self)
        #self.move_up_action.triggered.connect(self.move_up)

        self.move_down_action = QAction('Move Down', self)
        #self.move_down_action.triggered.connect(self.move_down)

        self.merge_action = QAction('Merge', self)
        #self.merge_action.triggered.connect(self.merge)

        toolbar = self.addToolBar('Main')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.clear_action)
        toolbar.addSeparator()
        toolbar.addAction(self.duplicate_action)
        toolbar.addAction(self.remove_action)
        toolbar.addSeparator()
        toolbar.addAction(self.move_up_action)
        toolbar.addAction(self.move_down_action)
        toolbar.addSeparator()
        toolbar.addAction(self.merge_action)

    def addFile(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fname = file_dialog.getOpenFileName(
                self, caption = 'Open file', filter = '*.pdf')

        if fname[0]:
            pdf = doc.Document(fname[0])
            self.model.addDocument(pdf)

    def remove(self):
        current = self.table.selectionModel().currentIndex().row()
        self.model.removeRows(current, 1)


class AppContext(ApplicationContext):           # 1. Subclass ApplicationContext
    def run(self):                              # 2. Implement run()
        window = PDFMergerWindow()
        version = self.build_settings['version']
        window.setWindowTitle("PDFMerger v" + version)
        window.resize(600, 400)
        window.show()
        return self.app.exec_()                 # 3. End run() with this line


if __name__ == '__main__':
    appctxt = AppContext()                      # 4. Instantiate the subclass
    exit_code = appctxt.run()                   # 5. Invoke run()
    sys.exit(exit_code)
