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


class Window(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        loadUi(UI_FILE_LOCATION, self)
        self.initialize()
        self.show()
            
    def initialize(self):
        self.expires_at = 0
        self.spotify = Spotify()
        self.playlists_list = []
        
        self.statusBar: QtWidgets.QStatusBar
        self.button_getPlaylists: QtWidgets.QPushButton
        
        self.button_import: QtWidgets.QPushButton
        self.button_export: QtWidgets.QPushButton
        
        self.button_shuffleSelected: QtWidgets.QPushButton
        self.button_uploadSelected: QtWidgets.QPushButton
        
        self.button_import.clicked.connect(self.importPlaylist)
        self.button_export.clicked.connect(self.exportPlaylist)
        self.button_getPlaylists.clicked.connect(self.getPlaylists)
        
        self.playlists_tree: QtWidgets.QTreeView
    
    def importPlaylist(self):
        file = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            str(CWD),
            "Playlist Json File (*.json)"
        )[0]
        
        if file:
            try:
                with open(file, 'r', encoding="UTF-8") as f:
                    playlists: dict = json.load(f)
            except json.JSONDecodeError:
                return msgbox("File is not valid.", 16)
                
            try:
                playlists.values()[0]['tracks']
            except KeyError:
                return msgbox("Backup file is not valid.", 16)
        
            return self.setTreeView(playlists)
        
    def exportPlaylist(self):
        pass
    
    def spotify_connect(self):
        if self.tokenExpired():
            self.spotify.refresh_token(self.spotify.get_credentials())
        
    def tokenExpired(self):
        file = Path("./.spotify_cache")
        if not file.exists():
            self.statusBar.showMessage("Not connected!")
            return True
        
        now = datetime.utcnow()
        expire_at = datetime.utcfromtimestamp(json.loads(file.read_text(encoding='UTF-8'))['expires_at'])
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
        playlists = self.spotify.get_playlists_songs()
        return self.setTreeView(playlists)
    
    def setTreeView(self, playlists: dict):
        model = QtGui.QStandardItemModel()
        Root = model.invisibleRootItem()
        
        for pid, ps in sorted(playlists.items(), key=lambda x: x[1]['name']):
            playlist = StandardItem(ps['name'], bold=True)
            for song_id, song_name in ps['tracks']:
                item = StandardItem(song_name, size=8, color=(199, 255, 238))
                playlist.appendRow(item)
            
            Root.appendRow(playlist)
        
        self.playlists_tree.setModel(model)


app = QtWidgets.QApplication([])

dark_stylesheet = qdarkstyle.load_stylesheet(qt_api="pyqt6")
app.setStyleSheet(dark_stylesheet)

window = Window()
sys.exit(app.exec())
