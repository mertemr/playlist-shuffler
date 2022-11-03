import json
import sys
import random
from typing import List

from datetime import datetime, timedelta
from pathlib import Path

import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt 
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets
from PyQt6.uic.load_ui import loadUi

import qdarkstyle
from win32api import MessageBoxEx

from app.globals import DEFAULT_TITLE, UI_FILE_LOCATION, CWD
from app.utils import StandardItem
from app.search_gui import SearchWindow
from spotify import Spotify


def msgbox(msg: str, type: int, title: str = DEFAULT_TITLE):
    return MessageBoxEx(0, msg, title, type)
       

class Window(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        loadUi(UI_FILE_LOCATION, self)
        self.initialize()
        self.show()

    def initialize(self):
        self.search_widget = SearchWindow()
        
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
        self.changed_lists = {}
        self.playlists_tree: QtWidgets.QTreeView
        # self.playlists_tree.clicked.connect(self.changeSelected)
        # self.playlists_tree.connect(self.changeSelected)

    def shuffleSelectedList(self):
        t = self.playlists_tree.currentIndex()
        if t.data() == None:  # Not selected anything
            return
        
        while True:
            x, t = t, t.parent()
            if t.data() == None:
                break
        
        col, row = x.column(), x.row()
        
        songs = []
        for _,j in self.playlists_dict.items():
            if j['name'] == x.data():
                for song in j['tracks']:
                    songs.append(song)
                break
            
        self.Model.removeColumn(col)
        random.shuffle(songs)
        
        playlist = StandardItem(j["name"], bold=True)
        for _, song_name in songs:
            item = StandardItem(song_name, size=8, color=(199, 255, 238))
            playlist.appendRow(item)

        self.Model.appendRow(playlist)
        print(songs)
            
        # items = self.Model.findItems)(x.data())
        # self.Model.index(
        # )
        
        
    def searchEvent(self):
        t = self.search_query.text()
        self.search_widget.search(self.spotify.search_query(t))
        if not self.search_widget.isVisible():
            self.search_widget.show()
        else:
            self.search_widget.focusWidget()
        
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
        self.Model = QtGui.QStandardItemModel()
        self.Root = self.Model.invisibleRootItem()

        for __pid, ps in sorted(playlists.items(), key=lambda x: x[1]["name"]):
            playlist = StandardItem(ps["name"], bold=True)
            for __song_id, song_name in ps["tracks"]:
                item = StandardItem(song_name, size=8, color=(199, 255, 238))
                playlist.appendRow(item)

            self.Root.appendRow(playlist)

        self.enable_buttons()
        
        self.playlists_tree.setModel(self.Model)
        self.playlists_tree.clearSelection()

        selectionmodel = self.playlists_tree.selectionModel()
        selectionmodel.selectionChanged.connect(self.changeSelected)

app = QtWidgets.QApplication([])

dark_stylesheet = qdarkstyle.load_stylesheet(qt_api="pyqt6")
app.setStyleSheet(dark_stylesheet)

window = Window()
sys.exit(app.exec())
