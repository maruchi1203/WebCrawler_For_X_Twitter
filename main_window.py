from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate
from crawling import WebCrawler
from excel import ExcelEdit
from ui_main_window import Ui_MainWindow
import json
import sys, os

def get_packaged_files_path():
    if getattr(sys, 'frozen', False):
        path = sys._MEIPASS
    else:
        path = '.'

    return path


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        filepath = get_packaged_files_path()
        filename = os.path.join(filepath, 'data.json')

    def init_ui(self):
        filepath = get_packaged_files_path()
        filename = os.path.join(filepath, 'data.json')

        with open(filename) as f:
            data = json.load(f)

            self.id_edt.setText(data["id"])
            self.pw_edt.setText(data["pw"])
            self.url_edt.setText(data["url"])
            self.date_edt.setDate(QDate.currentDate())
            self.file_edt.setText(data["file"])

        self.confirm_btn.clicked.connect(self.activate)
        self.file_btn.clicked.connect(self.set_file_url)

    def set_file_url(self):
        fname = QFileDialog.getOpenFileName(self, "파일선택", "C:\\", "Files (*.xlsx)")
        self.file_edt.setText(fname[0])

    def activate(self):
        try:
            id, eml = self.id_edt.text().split("/")
            pw = self.pw_edt.text()
            url = self.url_edt.text()
            base_date = self.date_edt.text()
            file_url = self.file_edt.text()

            if file_url == "":
                raise Exception()
        except Exception:
            msg = QMessageBox()

            msg.warning(msg, '경고', "이거 다 적어야 함")
            return

        wc = WebCrawler(eml=eml, id=id, password=pw, url=url, base_date=base_date)
        data = wc.get_data()
        wc.close_crawling()

        ex = ExcelEdit(file_url)
        ex.extract_file(data)

        filepath = get_packaged_files_path()
        filename = os.path.join(filepath, 'data.json')

        with open(filename, "r") as f:
            json_data = json.load(f)
            json_data.update({"id": id+"/"+eml, "pw": pw, "url": url, "file": file_url})

        with open(filename, "w") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        self.close()
