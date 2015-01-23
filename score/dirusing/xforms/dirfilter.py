# coding: utf-8
'''
Created on 18.12.2014

@author: Konnova
'''

import simplejson as json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport


def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''
    
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']

    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    #contragTypeId = json.loads(main)['contragTypeId']
    
    # Пустая структура данных, связнная с текущим справочником
    xformsdata = {"schema":{"@xmlns":"",
                            "buttonShow":u"Показать",
                            "buttonClear":u"Очистить",
                            "columns":[]}}

    for col in table_meta.getColumns():
        if json.loads(table_meta.getColumn(col).getCelestaDoc())['fieldTypeId'] == '9':
            name=json.loads(table_meta.getColumn(col).getCelestaDoc())['name']
            column={"column":
         {
          "@id":col,
         "@name":name,
         "filter":{}
         }
         }
    
            xformsdata["schema"]["columns"].append(column)
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": "view"
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
#    for rec in currentTable.iterate():
#         recId = getattr(rec, "id")
#         name = getattr(rec, "name")
#         data={"@id":recId, "@name":name}
#         xformsdata["schema"]["types"]["type"].append(data)
#     xformsdata["schema"]["types"]["type"].append({"@id":-1, "@name":"Все"})

    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())
    