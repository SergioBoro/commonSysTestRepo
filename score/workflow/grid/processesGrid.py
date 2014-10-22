# coding: utf-8

import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult




def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''

    activiti = ActivitiObject()
    processesList = activiti.getActualVersionOfProcesses()

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "version":[u"Версия"],
             "file":[u"Файл"],
             "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data    
    for process in processesList:
        procDict = {}
        procDict[_header["id"][1]] = process.key
        procDict[_header["pid"][1]] = process.key
        procDict[_header["name"][1]] = process.name
        procDict[_header["description"][1]] = process.description
        procDict[_header["version"][1]] = process.version
        procDict[_header["file"][1]] = u'Загрузить'
        procDict[_header["properties"][1]] = {"event":{"@name":"row_single_click",
                                         "action":{"#sorted":[{"main_context": 'current'},
                                                              {"datapanel":{'@type':"current",
                                                                            '@tab':"current",
                                                                            'element':{'@id':'processVersionsGrid'}
                                                                            }
                                                               }]
                                                   }
                                         }
                                }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1200px",
                                               "@gridHeight": "300",
                                               "@totalCount": len(processesList),
                                               "@profile":"default.properties"},
                                "labels":{"header":"Развернутые процессы"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["version"][0], "@width": "100px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "400px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["file"][0], "@width": "100px", "@type":"DOWNLOAD", "@linkId":"2"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[]}}


    data["gridtoolbar"]["item"].append({ "@text":"Схема",
                                        "@hint":"Схема процесса",
                                        "@disable": style,
                                        "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Схема процесса"
                                                                             }
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "processesImage"}
                                                                           }
                                                              }
                                                             ]
                                                  }
                                        })
    data["gridtoolbar"]["item"].append({"@text":"Развернуть",
                                        "@hint":"Развернуть процесс",
                                        "@disable": "false",
                                        "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Загрузить процесс",
                                                                             "@height": "300",
                                                                             "@width": "500"}
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "processUploadCard"}
                                                                           }
                                                              }]
                                                  }
                                        })



    return XMLJSONConverter.jsonToXml(json.dumps(data))

def downloadProcFile(context, main=None, add=None, filterinfo=None, session=None, elementId=None, recordId=None):
    u'''Процедура скачивание файла процесса.'''

    activiti = ActivitiObject()
    process = activiti.getProcessDefinition(recordId)
    fileName = process.resourceName
    data = activiti.getProcessXml(recordId)
    return JythonDownloadResult(data, fileName)