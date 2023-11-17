from PyQt6.QtWidgets import QLabel

from gui.singleton import Singleton


@Singleton
class WidgetPainter:

    def __init__(self):
        self._map = dict()

    def put(self, url: str, label: QLabel):
        val = self._map.get(url) if self._map.get(url) else []
        val.append(label)
        self._map[url] = val

    def delete(self, url: str) -> QLabel:
        return self._map.pop(url)[0]

    def get(self, url: str):
        return self._map.get(url, [])

    def keys(self):
        return self._map.keys()
