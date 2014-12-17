#coding:utf-8

from java.lang import Class
from java.sql import Connection, SQLException, DriverManager
from ru.curs.showcase.runtime import ConnectionFactory,AppInfoSingleton
from com.ziclix.python.sql import zxJDBC,PyConnection
from ru.curs.showcase.core.jython import JythonProc;

    
from workflow.processUtils import ActivitiObject

def taskCompleteHandler(context,event):
    act = ActivitiObject()
#     processEngine = EngineFactory.getActivitiProcessEngine()
#     runtimeService = processEngine.getRuntimeService()
    processInstanceId = event.getProcessInstanceId()
    processInstance = act.runtimeService.createProcessInstanceQuery().processInstanceId(processInstanceId).singleResult()
    processDefId = processInstance.getProcessDefinitionId()
    processDef = act.repositoryService.createProcessDefinitionQuery().processDefinitionId(processDefId).singleResult()
    processKey = processDef.getKey()
    if processKey == 'documentApprovingProcess':
        pyConn = ConnectionFactory.getPyConnection();
        pyConn.autocommit = True
        docVersion = act.runtimeService.getVariable(processInstanceId,'documentVersion')
        docId = act.runtimeService.getVariable(processInstanceId,'docId')
        #createProcessInstanceQuery().processInstanceId(processInstanceId).includeProcessVariables().singleResult()    
        try:
            cur = pyConn.cursor()
            try:
                cur.executemany("""update "testTable"
                                        set "orderVersion"=?
                                            where "ordersId"=?""", [(docVersion,docId)])
#                 cur.executemany("""update [dbo].[orders]
#                                         set orderVersion=?
#                                             where ordersId=?""", [(docVersion,docId)])
                print 'qwe'
            except:     
                print 'asd'
        finally:
            cur.close()
    