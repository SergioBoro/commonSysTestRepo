# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus

задачи, на которые пользователь назначен
задачи, у которых он кандидат
задачи, у которых кандидат - его группа
'''

import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from workflow import processUtils
from workflow._workflow_orm import formCursor
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor
from security._security_orm import loginsCursor

def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    activiti = ActivitiObject()
    userRoles = UserRolesCursor(context)
    roles = RolesCursor(context)
    form = formCursor(context)
    u'''получение данных из фильтра'''
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        processName = "%%%s%%" % ' '.join(info["@process"].split())
    else:
        taskName = '%'
        processName = '%'
    userRoles.setRange('userid', sid)

    rolesList = []
    if userRoles.tryFirst():
        while True:
            rolesList.append(userRoles.roleid)
            if not userRoles.next():
                break
#     задачи, у которых кандидат - группа
    groupTasksList = activiti.taskService.createTaskQuery().taskCandidateGroupIn(rolesList).taskNameLike(taskName).processDefinitionNameLike(processName).list()
#     задачи, у которых кандидат или исполнитель - юзер
    userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid).taskNameLike(taskName).processDefinitionNameLike(processName).list()
    taskDict = {}
#     чтобы не дублировались задачи
    for task in userTasksList:
        taskDict[task.id] = task
    for task in groupTasksList:
        if task.id not in taskDict:
            taskDict[task.id] = task
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
               "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "assign":[u"Принять"],
               "process": [u"Название процесса"],
               "document": [u"Документ"],
               "reassign": [u"Передать задачу"],
               "userAss": [u"Назначена на"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

#     runtimeService = activiti.runtimeService
    taskService = activiti.taskService
    logins = loginsCursor(context)

#     Проходим по таблице и заполняем data
    for task in taskDict.values():
#         смотрим связи задачи
        identityLinks = taskService.getIdentityLinksForTask(task.id)
        taskDict = {}
#         отображается немного разное в зав-ти юзер или группа
        for link in identityLinks:
            if link.userId == sid:
                logins.setRange("subjectId", sid)
                logins.first()
                if not (link.type == 'candidate' and _header["userAss"][1] in taskDict):
                    taskDict[_header["userAss"][1]] = logins.userName
            elif link.groupId in rolesList:
                roles.get(link.groupId)
                taskDict[_header["userAss"][1]] = u"""Группа "%s\"""" % roles.description

        taskDict[_header["id"][1]] = task.id
        processInstanceId = task.getProcessInstanceId()
#         получаем процесс, чтобы потом получить его имя
        process = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(task.getProcessDefinitionId()).singleResult()
#         docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
#                               runtimeService.getVariable(processInstanceId, 'docName'))
        taskDict[_header["process"][1]] = "%s" % (process.name)
#         картинка, по нажатию переходим на схему

        taskDict[_header["schema"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": "./?userdata=%s&mode=image&processId=%&formType=approve" \
                                                            % (session["userdata"], processInstanceId),
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/flowblock.png"}}}}

        taskDict[_header["name"][1]] = task.name
        taskDict[_header["properties"][1]] = {"event":
                                              []}
        if taskDict[_header["userAss"][1]] != logins.userName:
            taskDict[_header["assign"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/ok.png"}}}
            taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
                                                                "@column": _header["assign"][0],
                                                                "action":
                                                                    {"#sorted":
                                                                     [{"main_context": 'current'},
                                                                      {"server":
                                                                       {"activity":
                                                                        {"@id": "assign",
                                                                         "@name": "workflow.grid.activeTasksGrid.assign.celesta",
                                                                         "add_context": task.id}}},
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'tasksGrid'}}}]}})
        else:
            taskDict[_header["assign"][1]] = ""

        if form.tryGet(process.key, task.formKey):
            link = processUtils.setVariablesInLink(activiti, processInstanceId, task.id, form.link)
        else:
            link = "./?userdata=%s&mode=task&processId=%s&taskId=%s" % (session["userdata"], processInstanceId, task.id)
        taskDict[_header["document"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": link,
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/play.png"}}}} \
                                                    if taskDict[_header["userAss"][1]] == logins.userName else ""
#         {"link":
#                                               {"@href":"./?mode=task&processId=%s&taskId=%s" % (processInstanceId, task.id),
#                                                "@image":"solutions/default/resources/play.png",
#                                                "@text":"Выполнить",
#                                                "@openInNewTab":"true"
#                                                  }
#                                               } if taskDict[_header["userAss"][1]] == logins.userName else {"link": ""}
        if len(identityLinks) > 1:
            taskDict[_header["reassign"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/user.png"}}}
            taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
                                                                "@column": _header["reassign"][0],
                                                                "action":
                                                                    {"@show_in": "MODAL_WINDOW",
                                                                     "#sorted":
                                                                     [{"main_context": 'current'},
                                                                      {"modalwindow":
                                                                          {"@caption": "Выбор пользователя"
                                                                           }
                                                                        },
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'reassign'}}}]}})
        else:
            taskDict[_header["reassign"][1]] = ""

#         if processName == '' or processName in taskDict[_header["process"][1]]:
#
        data["records"]["rec"].append(taskDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1100px",
                                               "@gridHeight": "500",
                                               "@totalCount": len(data["records"]["rec"]),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0],
                                                       "@width": "40px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["assign"][0],
                                                       "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["reassign"][0],
                                                       "@width": "85px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["document"][0],
                                                       "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "215px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
                                                       "@width": "500px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["userAss"][0],
                                                       "@width": "100px"})

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)),
                     XMLJSONConverter.jsonToXml(json.dumps(settings)))

def assign(context, main, add=None, filterinfo=None, session=None, elementId=None):
    sid = json.loads(session)['sessioncontext']["sid"]
    activiti = ActivitiObject()
    activiti.taskService.claim(add, sid)
    context.message(u'Задача взята на исполнение')
