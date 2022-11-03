import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Union

from win32api import MessageBoxEx

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
# import PyQt6.QtWidgets as QtWidgets

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStatusBar,
    QPushButton,
    QTreeView,
    QLineEdit,
    QFileDialog
)

from PyQt6.QtCore import Qt
from PyQt6.uic.load_ui import loadUi
import qdarkstyle

from app.globals import CWD, DEFAULT_TITLE, UI_FILE_LOCATION
from app.search_gui import SearchWindow
from app.utils import StandardItem

from spotify import Spotify

    
def msgbox(msg: str, type: int, title: str = DEFAULT_TITLE):
    return MessageBoxEx(0, msg, title, type)

class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        loadUi(UI_FILE_LOCATION, self)
        self.init_window()
        self.search_widget = SearchWindow()
        self.playlists_dict = {}
        self.last_path = str(CWD)
        self.show()

    def init_window(self):
        self.statusBar: QStatusBar
        self.button_getPlaylists: QPushButton

        self.button_import: QPushButton
        self.button_export: QPushButton

        self.button_shuffleSelected: QPushButton
        self.button_uploadSelected: QPushButton

        
        self.button_search: QPushButton
        self.search_query: QLineEdit
        
        self.button_shuffleSelected.clicked.connect(self.shuffleSelectedList)
        self.button_import.clicked.connect(self.importPlaylist)
        self.button_export.clicked.connect(self.exportPlaylist)
        self.button_getPlaylists.clicked.connect(self.getPlaylists)
        self.button_search.clicked.connect(self.searchEvent)
        
        self.selected_item = None
        self.changed_lists = {}
        self.playlists_tree: QTreeView
        
        self.spotify = Spotify()
        self.renewTokenIfExpired()
        
    def shuffleSelectedList(self):
        t = self.playlists_tree.currentIndex()
        if t.data() == None:  # Not selected anything
            return
        
        while not t.data() is None:
            x, t = t, t.parent()  # Get parent
        
        col, row = x.column(), x.row()
        
        songs = []
        for _,j in self.playlists_dict.items():
            if j['name'] == x.data():
                for song in j['tracks']:
                    songs.append(song)
                break
        
        self.Model.removeRow(col)
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
        file = QFileDialog.getOpenFileName(
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

        
    def exportPlaylist(self):
        if not self.playlists_dict:
            return msgbox("No playlist found.", 32)

        file = QFileDialog.getSaveFileName(
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
        if self.renewTokenIfExpired():
            self.spotify.refresh_token(self.spotify.get_credentials())

    def renewTokenIfExpired(self):
        def getNewToken():
            token = self.spotify.get_credentials()
            self.spotify.refresh_token(token)
        
        file = Path("./.spotify_cache")
        
        if not file.exists():
            self.statusBar.showMessage("Not connected!")
            return getNewToken()

        now = datetime.utcnow()
        expire_at = datetime.utcfromtimestamp(
            json.loads(file.read_text(encoding="UTF-8"))["expires_at"]
        )
        delta = expire_at - now

        if delta < timedelta(seconds=0):
            self.statusBar.showMessage("Token Expired!")
            return getNewToken()

        self.statusBar.showMessage("Connected!")
        return


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

    def enable_buttons(self):
        self.button_export.setEnabled(True)
        self.button_shuffleSelected.setEnabled(True)
        self.button_uploadSelected.setEnabled(True)
        
    def disable_buttons(self):
        self.button_export.setEnabled(False)
        self.button_shuffleSelected.setEnabled(False)
        self.button_uploadSelected.setEnabled(False)


app = QApplication([])

dark_stylesheet = qdarkstyle.load_stylesheet(qt_api="pyqt6")
app.setStyleSheet(dark_stylesheet)

window = Window()
sys.exit(app.exec())
