# coding: UTF-8

'''@package common.api.datapanels.datapanel Модуль содержит классы и функции для работы
с информационной панелью.
Created on 26 мая 2015 г.

@author: tugushev.rr

@todo:layout для tab.
@todo Определения стилей для элементов и тэгов <tr> <td>
@todo элементы plugin, geomap, chart
'''

from common.api.core import ShowcaseBaseElement, ShowcaseBaseNamedElement, IXMLSerializable
from common.api.utils.tools import procname

elementsToJson = lambda elList: map(lambda x: x.toJSONDict(), elList)
isIdExists = lambda el, elList: len(filter(lambda x: x.id == el.id, elList)) > 0

def getElementsFromContainer(elementId, elementsList):
    """Возвращает элементы по @a elementId из контейнера элементов Showcase
    @a elementsList
    
    @param elementId (@c string)
    @param elementsList (<em>list of common.api.datapanels.datapanel.DatapanelElement</em>)
    @return <em>list of common.api.datapanels.datapanel.DatapanelElement</em> или
    *None*, если ничего не найдено
    
    @note Обычно контейнер элементов содержит элементы с уникальным ИД, поэтому
    результирующий список как правило будет содержать 1 элемент. Поведение, 
    возвращающее именно список, а не сам элемент реализовано для унификации
    процесса поиска, т.к. по сути @a elementList может быть любым списком
    элементов Showcase, в том числе и с повторяющимися ИД. 
    """
    elemets = filter(lambda x: x.id() == elementId, elementsList)
    if elemets:
        return elemets
    
    return None


class TabOrder(object):
    """Описывает порядок вкладок на информационной панели"""
    ## Текущая вкладка
    CURRENT='current'
    ## Первая или текущая вкладка
    FIRST_OR_CURRENT='firstOrCurrent'


class DatapanelElementTypes:
    """Описывает возможные типы элементов информационной панели"""
    
    ## Неопределено
    UNDEFINED = None
    ## Грид
    GRID = u'grid'
    ## XForms
    XFORMS = u'xforms'
    ## webtext
    WEBTEXT = u'webtext'


class ProcTypes:
    """Описывает типы процедур-обработчиков для элементов информационной панели"""
    ## Неопределено
    UNDEFINED = None
    ## Процедура сохранения данных
    SAVE = u'SAVE'
    ## Процедура скачивания 
    DOWNLOAD = u'DOWNLOAD'
    ## Процедура загрузки
    UPLOAD = u'UPLOAD'


class DatapanelElement(ShowcaseBaseElement):
    """Базовый класс для элементов информационной панели"""
    
    def __init__(self, elementId, elementType, procName=None):
        """
        @param elementId (@c string) ИД элемента
        @param elementType (@c DatapanelElementTypes) тип элемента
        @param procName (<tt>string or function object</tt>) фунция-обработчик
        загрузки данных для элемента
        """
        super(DatapanelElement, self).__init__(elementId)

        self.__procId = 0
        
        self.__type = elementType
        self.__hideOnLoad = False
        self.__neverShowInPanel = False
        
        
        self.setProc(procName)
        
        self.__elementProc = []
        self.__related = []
    
    
    def type(self):
        """Возвращает тип элемента
        @return @c DatapanelElementTypes
        """
        return self.__type
    
    
    def hideOnLoad(self):
        """Возвращает флаг, определяющий, нужно ли скрывать элемент при
        загрузке информационной панели
        @return @c bool
        """
        return self.__hideOnLoad
    
    
    def setHideOnLoad(self, value):
        """Устанавливает флаг, определяющий, нужно ли скрывать элемент при
        загрузке информационной панели
        @param value (@c bool)
        @return ссылка на себя 
        """
        self.__hideOnLoad = value
        return self
    
    
    def neverShowInPanel(self):
        """Возвращает флаг, определяющий, нужно ли отображать элемент на 
        информационной панели
        @return @c bool
        """
        return self.__neverShowInPanel
    
    
    def setNeverShowInPanel(self, value):
        """Устанавливает флаг, определяющий, нужно ли отображать элемент на
        информационной панели
        @param value (@c bool)
        @return ссылка на себя 
        """
        self.__neverShowInPanel = value
        return self
    
    
    def proc(self):
        """Возвращает функцию-обработчик загрузки данных в элемент
        @return (@c string) полное имя функции (*qualified name*)
        """
        return self.__proc
    
    
    @procname
    def setProc(self, value):
        """Устанавливает функцию-обработчик загрузки данных в элемент.
        @param value (<tt>string or function object</tt>) фунция-обработчик
        загрузки данных
        @return ссылка на себя
        """
        self.__proc = value
        return self
    
    
    def saveProc(self):
        """Возвращает функцию-обработчик сохранения данных
        @return (@c string) полное имя функции (*qualified name*)
        """
        return self._getProc(ProcTypes.SAVE)
    
    
    def setSaveProc(self, value):
        """Устанавливает функцию-обработчик сохранения данных.
        @param value (<tt>string or function object</tt>) фунция-обработчик
        сохранения данных
        @return ссылка на себя
        """
        self._addProc(ProcTypes.SAVE, value)
        return self
    
    
    def downloadProc(self):
        """Возвращает функцию-обработчик скачивания данных
        @return (@c string) полное имя функции (*qualified name*)
        """
        return self._getProc(ProcTypes.DOWNLOAD)
    
    
    def setDownloadProc(self, value):
        """Устанавливает функцию-обработчик скачивания данных.
        @param value (<tt>string or function object</tt>) фунция-обработчик
        скачивания данных
        @return ссылка на себя
        """
        self._addProc(ProcTypes.DOWNLOAD, value)
        return self
    
    
    def uploadProc(self):
        """Возвращает функцию-обработчик загрузки данных на сервер
        @return (@c string) полное имя функции (*qualified name*)
        """
        return self._getProc(ProcTypes.UPLOAD)
    
    
    def setUploadProc(self, value):
        """Устанавливает функцию-обработчик загрузки данных на сервер.
        @param value (<tt>string or function object</tt>) фунция-обработчик
        загрузки данных на сервер
        @return ссылка на себя
        """
        self._addProc(ProcTypes.UPLOAD, value)
        return self
    
    
    def addRelated(self, datapanelElement):
        """Добавлеят связанный элемент
        @param datapanelElement (@c DatapanelElement)
        @return ссылка на себя
        """
        self.__related.append(datapanelElement)
        return self
    
    
    @procname
    def _addProc(self, procType, procName):
        self.__procId += 1
        self.__elementProc.append( {
          "@id": u"%sp%i" % (self.id(), self.__procId), 
          "@name": procName,
          "@type": procType
        })
    
    
    def _getProc(self, inProcType):
        p = filter(lambda x: x['@type'] == inProcType, self.__elementProc)
        return p and p[0] or None
       
     
    def toJSONDict(self):
        if not self.__proc:
            raise Exception(u"Procedure @proc for element id = '%s' is not set!" % self.id())

        d = super(DatapanelElement, self).toJSONDict()
                
        d['@type'] = self.type()
        d['@hideOnLoad'] = unicode(self.hideOnLoad()).lower()
        d['@neverShowInPanel'] = unicode(self.neverShowInPanel()).lower()
        
        d['@proc'] = self.proc()
        
        if self.__elementProc:
            d['proc'] = self.__elementProc
        
        if self.__related:
            d['related'] = map(lambda x: {'@id': x.id()}, self.__related)
            
        return d


class XForm(DatapanelElement):
    """Описывает элемент с типом XForm"""
    
    def __init__(self, elementId, templateName=None, procName=None):
        """
        @param elementId (@c string) ИД элемента
        @param templateName (@c string) имя файла шаблона
        @param procName (<tt>string or function object</tt>) фунция-обработчик
        загрузки данных для элемента
        """
        super(XForm, self).__init__(elementId, DatapanelElementTypes.XFORMS, procName)
        
        self.setTemplate(templateName)

    
    def template(self):
        """Возвращает имя файла шаблона XForms
        @return (@c string)
        """
        return self.__template
    
    
    @procname
    def setTemplate(self, value):
        """Устанавливает имя файла шаблона XForms
        @param value (<tt>string or function object</tt>) имя файла шаблона
        @return ссылка на себя
        """
        self.__template = value
        return self
        
        
    def toJSONDict(self):
        if not self.__template:
            raise ValueError(u"Template for XForms element id = '%s' is not set!" % self.id())
        
        d = super(XForm, self).toJSONDict()
        
        d["@template"] = self.template()
        
        return d
        
        
class Webtext(DatapanelElement):
    """Описывает элемент с типом Webtext"""
    
    def __init__(self, elementId, procName, transform=None):
        """
        @param elementId (@c string) ИД элемента
        @param procName (<tt>string or function object</tt>) фунция-обработчик
        загрузки данных для элемента
        @param transform (@c string) имя файла XSL-преобразования
        """
        super(Webtext, self).__init__(elementId, DatapanelElementTypes.XFORMS, procName)
        
        self.__transform = transform
    
    
    def transform(self):
        """Возвращает имя файла XSL-преобразования
        @return (@c string)
        """
        return self.__transform
    
    
    def setTransform(self, value):
        """Устанавливает имя файла XSL-преобразования
        @param value (@c string)
        @return ссылка на себя
        """
        self.__transform = value
        return self
    
        
    def toJSONDict(self):
        if not self.proc():
            raise ValueError(u"Proc for Webtext element id = '%s' is not set!" % self.id)
        
        d = super(XForm, self).toJSONDict()
        
        d["@transform"] = self.transform()
        
        return d



class Tab(ShowcaseBaseNamedElement):
    """Описывает вкладку информационной панели.
    
    Вкладка имеет наименование, ИД и содержит в себе элементы информационной
    панели.
    """
    
    def __init__(self, tabId, tabName=u""):
        """
        @param tabId (@c string) ИД вкладки
        @param tabName (@c string) наименование вкладки
        """
        super(Tab, self).__init__(tabId, tabName)
        self.__elements = []
    
        
    def elements(self):
        """Возвращает список элементов вкладки.
        Эсли на вкладке нет элементов, возвращает пустой список.
        
        @return <em>list of common.api.datapanels.datapanel.DatapanelElement</em>
        """
        return self.__elements
    
    
    def getElement(self, byId):
        """Ищет на вкладке элемент с @a byId.
        @param byId (@c string) ИД элемента 
        @return @c common.api.datapanels.datapanel.DatapanelElement или @c None,
        если элемент не найден
        """
        elements =  getElementsFromContainer(byId, self.elements())
        
        return elements and elements[0] or None
    
    
    def addElement(self, datapanelElement):
        """Добавляет элемент на вкладку
        @param datapanelElement (@c common.api.datapanels.datapanel.DatapanelElement)
        @return ссылка на себя
        @throw ValueError если элемент с таким ИД уже существует на вкладке
        """
        if isIdExists(datapanelElement, self.__elements):
            raise ValueError(u"Error adding element to the tab id = '%s': element with the same id = '%s' already exists!" % (self.id, datapanelElement.id))
        
        self.__elements.append(datapanelElement)
        return self
    
        
    def toJSONDict(self):
        d = super(Tab, self).toJSONDict()

        d['element'] = elementsToJson(self.__elements)
        
        return d


class Datapanel(IXMLSerializable):
    """Описывает информационную панель.
    
    Информационная панель представляет собой контейнер вкладок, которые уже
    явялются контейнерами самих элементов
    """
    
    def __init__(self):
        self.__tabs = []
    
    
    def tabs(self):
        """Возвращает список вкладок.
        Если на информационной панели нет вкладок, возвращает пустой список.
        @return <em>list of common.api.datapanels.datapanel.Tab</em>
        """
        return self.__tabs
    
    
    def getTab(self, tabId):
        """Ищет вкладку с @a tabId.
        @param tabId (@c string) ИД вкладки 
        @return @c common.api.datapanels.datapanel.Tab или @c None,
        если вкладка не найдена
        """
        tabs_ = getElementsFromContainer(tabId, self.tabs())
        return tabs_ and tabs_[0] or None
    
    
    def addTab(self, tab):
        """Добавляет вкладку на информационную панель
        @param tab (@c common.api.datapanels.datapanel.Tab)
        @return ссылка на себя
        @throw ValueError если вкладка с таким ИД уже существует
        """
        if isIdExists(tab, self.__tabs):
            raise ValueError(u"Error adding tab: tab with the id = '%s' already exists!" % tab.id)
        
        self.__tabs.append(tab)
        return self
    
    
    def getElement(self, byId):
        """Ищет на информационной панели элемент с @a byId.
        Поиск осущесвтляется на всех вкладках.
        
        @param byId (@c string) ИД элемента 
        @return @c common.api.datapanels.datapanel.DatapanelElement или @c None,
        если элемент не найден
        """
        for t in self.tabs():
            element =  t.getElement(byId)
            if element:
                return element
            
        return None
    
    def toJSONDict(self):
        d = {
            'datapanel': {
                "tab": elementsToJson(self.__tabs)
            }  
        }
        
        return d
    

def testProc():
    pass
    

if __name__ == '__main__':
    
    from grids import PageGrid
    
    t = Tab(u't1', u"Таб 1")
    pg = PageGrid(u"pg1", u"test.grid.proc.name")
    t.addElement(pg)
    
    f1 = XForm(u"xf1", u"f1.xml", u"test.forms.form1.data")
    f1.setSaveProc(testProc) # (u'test.forms.form1.save')
     
    f1.addRelated(pg)
     
    t.addElement(f1)
    
    d = Datapanel()
    d.addTab(t)
    
    print d.toXML()



    
        
