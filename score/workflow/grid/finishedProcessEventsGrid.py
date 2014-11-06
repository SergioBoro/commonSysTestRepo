# coding: utf-8

'''
Created on 27.10.2014

@author: tr0glo)|(I╠╣
'''


import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from java.text import SimpleDateFormat
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult




def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех запущенных процессов. '''
    session = json.loads(session)
    #raise Exception(session)
    procId = session["sessioncontext"]['related']['gridContext']["currentRecordId"]
    activiti = ActivitiObject()
    procInstance = activiti.historyService.createHistoricProcessInstanceQuery().processInstanceId(procId).singleResult()
    answerList = list()
    pushList = list()
    pushList.append(procInstance.getStartTime())
    pushList.append(procInstance.getId()+'pis')
    pushList.append(procInstance.getName())
    pushList.append(u'Старт процесса')
    pushList.append(procInstance.getId())
    pushList.append('')
    answerList.append(pushList)
    pushList = list()
    pushList.append(procInstance.getEndTime())
    pushList.append(procInstance.getId()+'pif')
    pushList.append(procInstance.getName())
    pushList.append(u'Завершение процесса')
    pushList.append(procInstance.getId())
    pushList.append('')
    answerList.append(pushList)
    taskList = activiti.historyService.createHistoricTaskInstanceQuery().processInstanceId(procInstance.getId()).list()
    
    for task in taskList:
        if task.getStartTime() is not None:
            pushList = list()
            pushList.append(task.getStartTime())
            pushList.append(task.getId()+'s')
            pushList.append(task.getName())
            pushList.append(u'Старт задачи')
            pushList.append(task.getId())
            pushList.append('')
            answerList.append(pushList)
            
        if task.getEndTime() is not None:
            pushList = list()
            pushList.append(task.getEndTime())
            pushList.append(task.getId()+'f')
            pushList.append(task.getName())
            pushList.append(u'Конец задачи')
            pushList.append(task.getId())
            pushList.append('')
            answerList.append(pushList)
    #raise Exception(answerList)
    variableList = activiti.historyService.createHistoricDetailQuery().processInstanceId(procInstance.getId()).list()
    for variable in variableList:
        pushList = list()
        pushList.append(variable.getTime())
        pushList.append(variable.getId()+'v')
        pushList.append(variable.getName())
        pushList.append(u'Изменение переменной')
        pushList.append(variable.getId())
        pushList.append(variable.getValue())
        answerList.append(pushList)
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код"],
             "name":[u"Название"],
             "description":[u"Описание"],
             "type":[u"Тип"],
             "date":[u"Дата"],
             "properties":[u"properties"],
             "value":[u"Значение"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    #raise Exception(processesList)
    
    for instance in sorted(answerList, reverse=True):
        procDict = {}
        procDict[_header["id"][1]] = instance[1]
        procDict[_header["pid"][1]] = instance[4]
        procDict[_header["name"][1]] = instance[2]
        procDict[_header["type"][1]] = instance[3]
        procDict[_header["value"][1]] = instance[5]
        procDict[_header["date"][1]] = SimpleDateFormat("HH:mm dd-MM-yyyy").format(instance[0])
#         procDict[_header["schema"][1]] = {"div":
#                                            {"@align": "center",
#                                             "img":
#                                             {"@src": "solutions/default/resources/flowblock.png", "@height": "20px"}}}
        #procDict[_header["description"][1]] = process.description
        #procDict[_header["version"][1]] = process.version
        procDict[_header["properties"][1]] = { }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1000px",
                                               "@gridHeight": "300",
                                               "@totalCount": len(answerList),
                                               "@profile":"default.properties"},
                                "labels":{"header":"События"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "50px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["type"][0], "@width": "100px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["value"][0], "@width": "100px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["date"][0], "@width": "100px"})
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["version"][0], "@width": "100px"})
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "400px"})
    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

#     if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
#         style = "true"
#     else:
#         style = "false"

    data = {"gridtoolbar":{"item":{}}}


#     data["gridtoolbar"]["item"].append({ "@text":"Остановить",
#                                         "@hint":"Остановить процесс",
#                                         "@disable": style,
#                                         "action":{"@show_in": "MODAL_WINDOW",
#                                                   "#sorted":[{"main_context":"current"},
#                                                              {"modalwindow":{"@caption": "Остановка процесса"
#                                                                              }
#                                                               },
#                                                              {"datapanel":{"@type": "current",
#                                                                            "@tab": "current",
#                                                                            "element": {"@id": "suspendProcessCard"}
#                                                                            }
#                                                               }
#                                                              ]
#                                                   }
#                                         })



    return XMLJSONConverter.jsonToXml(json.dumps(data))
