import json
import sys
from typing import List

from datetime import datetime, timedelta
from pathlib import Path

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets
from PyQt6.uic.load_ui import loadUi

import qdarkstyle
from win32api import MessageBoxEx

from app.globals import DEFAULT_TITLE, UI_FILE_LOCATION, CWD
from app.utils import StandardItem

from spotify import Spotify


def msgbox(msg: str, type: int, title: str = DEFAULT_TITLE):
    return MessageBoxEx(0, msg, title, type)


# class SearchWindow(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
        

class Window(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        loadUi(UI_FILE_LOCATION, self)
        self.initialize()
        self.show()

    def initialize(self):
        self.expires_at = 0
        self.spotify = Spotify()
        self.playlists_dict = {}
        self.last_path = str(CWD)

        self.statusBar: QtWidgets.QStatusBar
        self.button_getPlaylists: QtWidgets.QPushButton

        self.button_import: QtWidgets.QPushButton
        self.button_export: QtWidgets.QPushButton

        self.button_shuffleSelected: QtWidgets.QPushButton
        self.button_uploadSelected: QtWidgets.QPushButton

        self.button_shuffleSelected.clicked.connect(self.shuffleSelectedList)
        self.button_import.clicked.connect(self.importPlaylist)
        self.button_export.clicked.connect(self.exportPlaylist)
        self.button_getPlaylists.clicked.connect(self.getPlaylists)
        
        self.button_search: QtWidgets.QPushButton
        self.search_query: QtWidgets.QLineEdit
        
        self.button_search.clicked.connect(self.searchEvent)
        
        self.selected_item = None
        self.playlists_tree: QtWidgets.QTreeView
        # self.playlists_tree.clicked.connect(self.changeSelected)
        # self.playlists_tree.connect(self.changeSelected)

    def shuffleSelectedList(self):
        ... # TODO get selected row and childs.
            # shuffle list
        
    def searchEvent(self):
        t = self.search_query.text()
        data = self.spotify.search_query(t)
        # with open("searchquery.json", 'w', encoding="UTF-8") as f:
        #     json.dump(
        #         data, f, indent=4, ensure_ascii=False
        #     )
        wid = QtWidgets.QWidget()
        wid.setWindowTitle("Search results")
        loadUi("./app/search_ui.ui", wid)
        
        qlw: QtWidgets.QListWidget = wid.search_list
        
        for d in dict(data)['tracks']['items']:
            song_url = d['external_urls']['spotify']
            song_name = d['name']
            album_id = d['album']['id']
            artists = [
                (i['name'], i['id']) for i in d['artists'] 
            ]
            item = QtWidgets.QListWidgetItem(f"{song_name}, {artists}, {song_url}, {album_id}")
            qlw.addItem(item)
        
        wid.show()
        
            
    def changeSelected(self):
        x = self.playlists_tree.currentIndex()
        
        self.selected_item = x
        if x.parent().data():
            self.selected_item = x.parent()

    def importPlaylist(self):
        file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", self.last_path, "Playlist Json File (*.json)"
        )[0]

        if not file:
            return

        self.last_path = str(Path(file).absolute())
        try:
            with open(file, "r", encoding="UTF-8") as f:
                playlists: dict = json.load(f)
        except json.JSONDecodeError:
            return msgbox("File is not valid.", 16)

        try:
            list(playlists.values())[0]["tracks"]
        except KeyError:
            return msgbox("Backup file is not valid.", 16)

        self.enable_buttons()
        self.disable_buttons()
        return self.setTreeView(playlists)

    def enable_buttons(self):
        self.button_export.setEnabled(True)
        self.button_shuffleSelected.setEnabled(True)
        self.button_uploadSelected.setEnabled(True)
        
    def disable_buttons(self):
        self.button_export.setEnabled(False)
        self.button_shuffleSelected.setEnabled(False)
        self.button_uploadSelected.setEnabled(False)
        
    def exportPlaylist(self):
        if not self.playlists_dict:
            return msgbox("No playlist found.", 32)

        file = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save playlist", self.last_path, "Playlist Json File (*.json)"
        )[0]

        if not file:
            return

        self.last_path = str(Path(file).absolute())

        try:
            with open(file, "w", encoding="UTF-8") as f:
                json.dump(self.playlists_dict, f, indent=4)
        except OSError:
            msgbox("File cannot saved.", 16)

    def spotify_connect(self):
        if self.tokenExpired():
            self.spotify.refresh_token(self.spotify.get_credentials())

    def tokenExpired(self):
        file = Path("./.spotify_cache")
        if not file.exists():
            self.statusBar.showMessage("Not connected!")
            return True

        now = datetime.utcnow()
        expire_at = datetime.utcfromtimestamp(
            json.loads(file.read_text(encoding="UTF-8"))["expires_at"]
        )
        delta = expire_at - now
        self.expires_at = expire_at

        if delta < timedelta(seconds=0):
            self.statusBar.showMessage("Token Expired!")
            return True

        self.statusBar.showMessage("Connected!")
        return False

    def getNewToken(self):
        token = self.spotify.get_credentials()
        self.spotify.refresh_token(token)

    def getPlaylists(self):
        self.button_getPlaylists.setText("Refresh")
        self.button_export.setEnabled(False)
        playlists = self.spotify.get_playlists_songs()
        self.playlists_dict = playlists
        return self.setTreeView(playlists)

    def setTreeView(self, playlists: dict):
        model = QtGui.QStandardItemModel()
        Root = model.invisibleRootItem()

        for pid, ps in sorted(playlists.items(), key=lambda x: x[1]["name"]):
            playlist = StandardItem(ps["name"], bold=True)
            for song_id, song_name in ps["tracks"]:
                item = StandardItem(song_name, size=8, color=(199, 255, 238))
                playlist.appendRow(item)

            Root.appendRow(playlist)

        self.enable_buttons()
        
        self.playlists_tree.setModel(model)
        self.playlists_tree.clearSelection()

        model = self.playlists_tree.selectionModel()
        model.selectionChanged.connect(self.changeSelected)


app = QtWidgets.QApplication([])

dark_stylesheet = qdarkstyle.load_stylesheet(qt_api="pyqt6")
app.setStyleSheet(dark_stylesheet)

window = Window()
sys.exit(app.exec())
