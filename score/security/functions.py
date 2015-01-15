# coding: utf-8
"""
@author: d.bozhenko
"""
import string
import random
import os
import simplejson as json
import urllib2
import xml.dom.minidom
from security._security_orm import customPermsCursor, rolesCustomPermsCursor
from ru.curs.celesta.syscursors import PermissionsCursor, UserRolesCursor
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.dbutils import DataBaseXMLExchange
from java.io import File, FileInputStream, FileOutputStream
from common.grainssettings import SettingsManager

try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDownloadResult

class Settings():
    settings={}
    settingsTag = 'securitySettings'
    grainName = 'security'
    
    def __init__(self):        
        self.settingsInstance = SettingsManager()
    
#    def getSettingsJSONPath(self):
#        #settingsPath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'usersTypes.json')
#        settingsPath=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'grainsSettings.xml')
#        return settingsPath
    
    def getSettingsJSON(self):
        if self.settings=={}:
            names=self.settingsInstance.getGrainSettings("%s/parameter/@name" % self.settingsTag, self.grainName)
            values = self.settingsInstance.getGrainSettings("%s/parameter/@value" % self.settingsTag, self.grainName)
            settingsJson={}
            for i in range(len(names)):
                settingsJson[names[i]] = values[i]
            self.settings = settingsJson                                                                     
        return self.settings
#        if self.settings=={}:
#            settingsPath=self.getSettingsJSONPath()
#            f = open(settingsPath, 'r')
#            settingsJSON=json.loads(f.read())
#            f.close()
#            self.settings=settingsJSON
#        else:
#            settingsJSON=self.settings
#        return settingsJSON

    def isUseAuthServer(self):
        useAuthServer=self.getSettingsJSON()    
        return useAuthServer["useAuthServer"]==True or useAuthServer["useAuthServer"]=="true"
    
    def loginIsSubject(self):
        loginSubject=self.getSettingsJSON()
        return loginSubject["loginEqualSubject"]==True or loginSubject["loginEqualSubject"]=="true"
    
    def isEmployees(self):
        settingsJson=self.getSettingsJSON()
        result=settingsJson["employeesGrain"]<>None and settingsJson["employeesTable"]<>None and settingsJson["employeesName"]<>None and\
                settingsJson["employeesGrain"]<>"" and settingsJson["employeesTable"]<>"" and settingsJson["employeesName"]<>"" and\
                settingsJson["employeesGrain"]<>"null" and settingsJson["employeesTable"]<>"null" and settingsJson["employeesName"]<>"null"
        return result 
    
    def isSystemInitialised(self):
        system_init=self.getSettingsJSON()
        return system_init["isSystemInitialised"]==True or system_init["isSystemInitialised"]=="true" 

    def getEmployeesParam(self, param):
        employeesParam=self.getSettingsJSON()
        return employeesParam[param]

    def setEmployeesParam(self, param, value):
        if param in self.settings.keys():
            self.settings[param]=value
            self.settingsInstance.setGrainSettings("%s/parameter[@name='%s']/@value" % (self.settingsTag, param), value, self.grainName)
    
    def settingsJSONSave(self):
        pass
        #оставляем на случай, если метод где-то используется.
        #но теперь сохранение будет осуществляться методом setEmployeesParam             
#        settingsPath=self.getSettingsJSONPath()
#        f = open(settingsPath, 'w')        
#        f.write(json.dumps(self.settings))        
#        f.close()



def id_generator(size=8, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def getUsersFromAuthServer(server, sessionId):
    req = urllib2.Request(server+'/importusers?sesid='+sessionId,'<Request></Request>')
    data = urllib2.urlopen(req)
    users=data.read()
    return xml.dom.minidom.parseString(users)

def getActionJSON(add="", elementId="", caption="", height="", width=""):
    action={"@show_in": "MODAL_WINDOW",
                "#sorted":[{"main_context":"current"},
                           {"modalwindow":{"@caption": caption,
                                           "@height": height,
                                           "@width": width}
                            },
                           {"datapanel":{"@type": "current",
                                         "@tab": "current",
                                         "element": {"@id": elementId,
                                                     "add_context":add}
                                         }
                            }]
            }
    return action

def submissionGenPass(context, main=None, add=None, filterinfo=None, session=None, data=None):
    #raise Exception(data)
    instance=json.loads(data)
    instance["schema"]["user"]["@password"]=id_generator()        
    return XMLJSONConverter.jsonToXml(json.dumps(instance))

def generateGridSettings(columns={}, pagesize=25, gridHeight=250, delta=40, totalCount=0, profile="default.properties", header="", columnsSorted = None):
    settings = {"gridsettings":{"columns":{"col":[]}
                                }
                }
    gridWidth=0
    if columnsSorted is None:
        columnsSorted = sorted(columns.keys())
    for key in columnsSorted:
        gridWidth+=columns[key]
        settings["gridsettings"]["columns"]["col"].append({"@id":key, "@width": str(columns[key])+"px"})
    gridWidth+=delta    
    settings["gridsettings"]["properties"]={"@pagesize":pagesize,
                                            "@gridWidth":str(gridWidth)+"px",
                                            "@gridHeight":gridHeight,
                                            "@totalCount":totalCount,
                                            "@profile":profile}
    settings["gridsettings"]["labels"]={"header":header}
    return settings

def getPermissionsOfTypeAndUser(context, sid, permissionType=None):
    u"""
        Функция возвращает курсор с разрешениями данного типа,
        которые есть у данного пользователя. Работает для permissions и для customPermissions.
        Если разрешений нет, возвращает None
    """
    userRoles=UserRolesCursor(context)
    userRoles.setRange("userid", sid)
    filter_string=""
    if userRoles.tryFirst():
        filter_string="'"+userRoles.roleid+"'"
        while True:
            if userRoles.next():
                filter_string+="|'"+userRoles.roleid+"'"
            else:
                break
            
    if permissionType is None or permissionType=='tables':
        permissions=PermissionsCursor(context)
        if filter_string<>"":
            permissions.setFilter("roleid", filter_string)
        else:
            return None
    else:
        permissions=customPermsCursor(context)
        rolePermissions=rolesCustomPermsCursor(context)        
        rolePermissions.setFilter("roleid", filter_string)
        filter_string=""
        if rolePermissions.tryFirst():
            filter_string="'"+rolePermissions.permissionId+"'"
            while True:
                if rolePermissions.next():
                    filter_string+="|'"+rolePermissions.permissionId+"'"
                else:
                    break
        if filter_string<>"":
            permissions.setFilter("name", filter_string)
        else:
            return None
    return permissions

def userHasPermission(context, sid, permission):
    u"""
        Функция возвращает False, если разрешения не существует или
        у данного пользователя нет такого разрешения.
        В случае, если у данного пользователя разрешение есть,
        возвращает True
    """
    userRoles=UserRolesCursor(context)
    userRoles.setRange("userid", sid)
    permissions=customPermsCursor(context)
    if not permissions.tryGet(permission):
        return False
    rolePermissions=rolesCustomPermsCursor(context)
    if userRoles.tryFirst():
        while True:
            rolePermissions.setRange("roleid", userRoles.roleid)
            rolePermissions.setRange("permissionId", permission)
            if rolePermissions.tryFirst():
                return True            
            if not userRoles.next():
                break
    return False

def tableUpload(cursorInstance, fileData):    
    exchange = DataBaseXMLExchange(fileData, cursorInstance)
    exchange.uploadXML()
    #fileData.close()
    

def tableDownload(cursorInstance, fileName):
    filePath=os.path.join(os.path.dirname(os.path.abspath(__file__)), fileName+'.xml')
    dataStream = FileOutputStream(filePath)
    exchange = DataBaseXMLExchange(dataStream, cursorInstance)
    exchange.downloadXML()
    dataStream.close()
    report=File(filePath)    
    return JythonDownloadResult(FileInputStream(report),fileName+'.xml')