# coding: utf-8
'''
Created on 01.07.2014

@author: d.bozhenko.
'''

import json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDownloadResult

from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common._common_orm import numbersSeriesCursor
from common.dbutils import tableDownload, DataBaseXMLExchange

def cardData(context, main, add, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":"",
                            "context":{"@add":add}
                            }
                  }
    xformssettings = {"properties":{"event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":[{"@id": "numbersSeriesGrid",
                                                                                "add_context": 'current'},
                                                                                {"@id": "linesNumbersSeriesGrid",
                                                                                "add_context": 'hide'}]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    return

def numbersSeriesDownload(context, main=None, add=None, filterinfo=None, session=None, elementId=None, data=None):
    numbersSeries = numbersSeriesCursor(context)
    fileName = 'numbersSeries'
    return tableDownload(numbersSeries, fileName)

def numbersSeriesUpload(context, main=None, add=None, filterinfo=None, session=None, elementId=None, data=None, fileName=None, file=None):
    numbersSeries = numbersSeriesCursor(context)
    exchange = DataBaseXMLExchange(file, numbersSeries)
    exchange.uploadXML()
    return context.message(u"Данные успешно загружены в таблицу")