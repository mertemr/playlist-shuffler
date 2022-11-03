from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem
from PyQt6.uic.load_ui import loadUi

class SearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("./app/search_ui.ui", self)
        self.setWindowTitle("Search results")
        self.qlw: QListWidget = self.search_list
    
    def search(self, search_string: str = ""):
        if not self.qlw.count() == 0:
            self.qlw.clear()
            
        try:
            _dict = dict(search_string)['tracks']['items']
        except IndexError:
            return
        
        for d in _dict:
            song_url = d['external_urls']['spotify']
            song_name = d['name']
            album_id = d['album']['id']
            artists = [
                (i['name'], i['id']) for i in d['artists'] 
            ]
            item = QListWidgetItem(f"{song_name}, {artists}, {song_url}, {album_id}")
            self.qlw.addItem(item)
        