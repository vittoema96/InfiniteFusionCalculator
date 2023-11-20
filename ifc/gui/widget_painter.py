import logging
import re
from typing import Dict, List, Union

from PyQt6 import QtNetwork
from PyQt6.QtCore import QUrl, QByteArray
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from data import utils
from gui.singleton import Singleton


class WidgetPainter(metaclass=Singleton):

    """ Map with urls as keys"""
    _map: Dict[str, List[QLabel]]

    _nam: QtNetwork.QNetworkAccessManager

    def __init__(self):
        self._map = dict()

        self._nam = QtNetwork.QNetworkAccessManager()
        self._nam.finished.connect(self.on_image_result)

    def put(self, url: str, labels: Union[QLabel, List[QLabel]]):
        val = self._map.get(url) if self._map.get(url) else []
        if isinstance(labels, QLabel):
            labels = [labels]
        for label in labels:
            val.append(label)
        self._map[url] = val

        qurl = QtNetwork.QNetworkRequest(QUrl(url))
        self._nam.get(qurl)

    def delete(self, url: str) -> List[QLabel]:
        return self._map.pop(url)

    def get(self, url: str):
        return self._map.get(url, [])

    def keys(self):
        return self._map.keys()

    def on_image_result(self, reply: QtNetwork.QNetworkReply):
        """
        Called when the QNetworkAccessManager has finished downloading 1 image.
        Checks for failed download and tries all alternatives.

        :param reply:
        :return:
        """
        error = reply.error()
        url: str = reply.url().url()

        if url in self.keys():
            if error == QtNetwork.QNetworkReply.NetworkError.NoError:
                labels: List[QLabel] = self.get(url)

                bytes_string = reply.readAll()
                for label in labels:
                    self.set_pixmap(bytes_string, label)
                self.delete(url)

            else:
                if 'black-white' in url:
                    replace_from = 'black-white'
                    replace_to = 'sun-moon'
                elif 'sun-moon' in url:
                    replace_from = 'sun-moon'
                    replace_to = 'x-y'
                elif 'main/CustomBattlers' in url:
                    replace_from = 'main/CustomBattlers'
                    replace_to = 'master/Battlers'
                elif re.search(r'master/Battlers/\d+.\d+\.png', url):
                    idx = url.split('/')[-1].split('.')[0]
                    replace_from = 'master/Battlers/'
                    replace_to = f'master/Battlers/{idx}/'
                elif re.search(r'master/Battlers/\d+/\d+.\d+\.png', url):
                    replace_from = 'custom'
                    replace_to = 'autogen'
                else:
                    logging.warning(f"Could not find an alternative url for '{url}'")
                    return

                labels = self.delete(url)

                url = url.replace(replace_from, replace_to)
                self.put(url, labels)

                qurl = QtNetwork.QNetworkRequest(QUrl(url))
                self._nam.get(qurl)

    @staticmethod
    def set_pixmap(image: QByteArray, label: QLabel):
        """
        Given a QByteArray and a QLabel, it sets the image of the label.
        """
        pixmap = QPixmap()

        pixmap.loadFromData(image)

        pixmap = pixmap.scaledToHeight(utils.SPRITE_SIZE)

        try:
            label.setPixmap(pixmap)
        except RuntimeError as e:
            logging.warning(e)
            logging.warning("A Runtime error occurred. Caught it and skipped ahead.")
