#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from util.jsonmgr import *
from util.tree import *
from util.record_functions import norm2List,norm2String

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


ITEM_TYPE=set(['#entry','#ientry','default','cubo','connect','fields','guides','favorites',
               'vista',
               'guide','prod','favorite',
               'domain','values',
               'join','case',
               'join_table','join_clause','category'])

     #'categories',
     #'clause',
     #'connect',
     #'cubo',
     #'fields',
     #'grouped by',
     #'guides',
     #'prod',
     #'related via',
     #'source',
     #'vista',
     #'values',
     #'case_sql'])
PARENT_TYPE = {'conn':('cube',),
               'fields': ('guide','cube',),
               'guides':('cube',),
               'favorites':('cube',),
               'guide':('guides'),
               'prod':('guide',),
               'domain':('guide',),
               'values':('guide',),
               'join':('guide',),
               'case':('guide',),
               'join_table':('join',),
               'join_clause':('join_table',),
               'category':('case',),
               'vista':('default','favorites')
               #'prod':('guide','prod'),
               #'domain':('prod',),
               #'case':('prod',),
               #'join':('prod',),
               #'date':('prod',),
              }
CHILD_TYPE = {  'case': ('category',),
                'cube': ('conn', 'favorites', 'fields', 'guides'),
                'default': ('vista',),
                'favorites': ('vista',),
                'guide': ('prod',),
                'prod': ('case', 'domain', 'fields','join', 'values'),
                'guides': ('guide',),
                'join': ('join_table',),
                'join_table': ('join_clause',)
              }

ITEM_ATTR = { 'cube':('table','base filter'),
               'conn':('driver','dbname','dbhost','dbuser','dbpass'),
               'fields': (None,),
               #'guides':None,
               #'favorites':None,
               'guide':('name','class','type'),
               'prod':('name','class','type'),
               'domain':('name','elem','filter','table','desc','grouped_by'),
               'values':('name','elem','date_fmt','case_sql','fmt','enum_fmt'),
               #'guide':('class','type'),   #type is a leftover
               #'prod':('elem','name'),
               #'domain':('name','filter','table','code','desc','grouped by'),
               'case':('name','elem','fmt','enum_fmt','categories','case_sql'),
               #'join': None,
               'join_table':('name','filter','table','join operator'),
               'join_clause':('left','condition','right'),
               'category':('default','result','condition','right_values'),
               'default':('cubo',),
               'vista':('row','col','agregado','elemento'),
               'favorite':('name',),
               #'date':('name','elem','type'),
              }
LIST_ATTR = ('elem','desc','grouped_by','right_values')
ATTR_TRANS = {'code':'elem',
              'rel_elem':'right',
              'base_elem':'left',
              'grouped by':'grouped_by',
              'values':'right_values',
              'source':'domain',
             }
TYPE_VALUES = {'d':('name','elem','date_fmt'),
               'c':('name','elem','fmt','enum_fmt'),
               'o':('name','elem','fmt'),
              }

class CubeItem(TreeItem):
    
    def __init__(self,type, key, ord=None, desc=None, data=None, parent=None):
        #if type not in ITEM_TYPE:
            #raise NotImplementedError()
        #else:
           #self.type = type
        self.type = type
        self.key= key
        
        if desc is None:
            self.desc = key
        elif isinstance(desc,(list,tuple)):
            self.desc = ', '.join(desc)
        else:
            self.desc = desc
            
#        if parent is not None:
#            if parent.getType() not in PARENT_TYPE[self.type]:
#                raise KeyError()
        self.parentItem = parent
        
        if ord is None:
            self.ord = self.parent().childCount()
        else:
            self.ord = ord
            
        self.itemData = data
        self.childItems = []
        
    def getType(self):
        return self.type
    
    def __getitem__(self,key):
        # no especialmente rapido    
        if isinstance(key,int):
            return self.itemData[key]
        elif key in ITEM_ATTR[self.type]:
            return self.itemData[ITEM_ATTR[self.type].index(key)]
        #if key == 'attr' and self.type in ('#entry','#ientry'):
            #return self.desc
        #elif key == 'type':
            #return self.type
        #elif key == 'ord':
            #return self.ord
        #elif key == 'desc':
            #return self.desc
        #elif key == 'data' or key == self.desc:
            #return self.itemData
        #elif ( self.type not in ('#entry','#ientry') and
             #self.type in ITEM_ATTR and 
             #key in ITEM_ATTR[self.type] ):
            #for hijo in self.childItems:
                #if hijo.type in ('#entry','#ientry') and hijo.desc == key :
                    #return hijo.itemData
            #else:
                #if key == 'name':
                    #return self.key.split(DELIMITER)[-1] + '*'
                #else:
                    #return None
        #elif key == 'name':
            #return self.key.split(DELIMITER)[-1] + '**'
        #elif ( self.type not in ('#entry','#ientry') and
               #self.type in CHILD_TYPE and
               #key in CHILD_TYPE[self.type] ):
            #return [ hijo for hijo in self.childItems if hijo.type == key]
        else:
            return None
        
            

    #def appendChild(self, item):
        #self.childItems.append(item)

    #def child(self, row):
        #return self.childItems[row]

    #def childCount(self):
        #return len(self.childItems)

    #def columnCount(self):
        #return len(self.itemData)

    def data(self, column):
        try:
            if isinstance(self.itemData,dict):
                #clave = ITEM_ATTR[self.type][column]
                #return '{}:{}'.format(clave,self.itemData[clave])
                claves = [key for key in self.itemData]
                return '{}:{}'.format(claves[column],self.itemData[claves[column]])
            elif isinstance(self.itemData,(list,tuple)):
                return self.itemData[column]
            elif column == 1:
                return self.itemData
            else:
                return None
        except (IndexError, KeyError):
            return None

    #def setData(self,data):
        #self.itemData = data
        
    #def parent(self):
        #return self.parentItem

    #def row(self):
        #if self.parentItem:
            #return self.parentItem.childItems.index(self)

        #return 0
    
    #def depth(self):
        #"""
          #la profundidad del arbol en ese punto. Empezando desde 1
        #"""
        #ind = 0
        #papi = self.parentItem
        #while papi is not None:
            #papi = papi.parentItem
            #ind += 1
        #return ind
    
    #def getLevel(self):
        #"""
          #el nivel actual. empieza en 0
        #"""
        #return self.depth() -1
    
    #def getFullDesc(self):
        #fullDesc = [] #let the format be done outside
        #fullDesc.append(self.desc)
        #papi = self.parentItem
        #while papi is not None:
            #if papi.parentItem is None:  #FIXME esto es un chapu
                #break
            #fullDesc.insert(0,papi.desc) #Ojo insert, o sea al principio
            #papi = papi.parentItem
        #return fullDesc
    
    #def __str__(self): 
        #return '{}->{}'.format(self.key,self.desc)
        
    #def __repr__(self): 
        #return 'TreeItem({},{},{})'.format(self.key,self.ord,self.desc)

#cube = load_cubo()

#cubeTree = TreeDict()
"""
  tipos de elementos:
     entrada de cubo 
         datos de conexion *1
         campos de calculo *n
         guias * n
             reglas de produccion * n (recursive)
                 source 1
                    filter
                    table
                    code
                    desc
                    grouped_by * n
                 related via * n
                    
                 case 1
"""
DELIMITER=':'


#def load1(file):
    #def append_elem(tipo,id,estructura,padre,ord=None):
        #if padre is None:
            #clave=id
            #cubeTree.append(CubeItem(tipo,id,desc=id,ord=ord))
        #else:
            #papiKey = padre.key 
            #clave = '{}{}{}'.format(papiKey,DELIMITER,id)
            #cubeTree.append(CubeItem(tipo,clave,desc=id,ord=ord,parent=padre))

        #if isinstance(estructura,dict):
            #data={}
            #for attr in estructura:
                #if attr in ITEM_ATTR:
                    #print(attr,estructura[attr])
                    #cubeTree.append(CubeItem('#entry',clave+":"+attr,data={attr:estructura[attr]},desc=attr,parent=cubeTree[clave]))
        #elif isinstance(estructura,(list,tuple)):
            #data = []
            #data = estructura[:]
        #cubeTree[clave].setData(data)
        #return clave 
    
    #cube = load_cubo(file)
    #cubeTree = TreeDict()
    #for ind,key in enumerate(cube):
        #if key == 'default':
            #continue
        #append_elem('cube',key,cube[key],None,ord=ind)
        #print(cubeTree.content)
        #cubo = cube[key]
        #append_elem('conn','conn',cubo['connect'],cubeTree[key])
        #append_elem('fields','fields',cubo['fields'],cubeTree[key])
        #for idx,guide in enumerate(cubo['guides']):

            #clave= append_elem('guide',guide['name'],guide,cubeTree[key],ord=idx)
            #for id3,rule in enumerate(guide['prod']):
                #nkey ='{}_{}'.format(id3,rule.get('name',''))
                #krule = append_elem('prod',nkey,rule,cubeTree[clave],ord=id3)
                #if guide.get('class') == 'd' or rule.get('class') == 'd':
                    #nkey = 'date' 
                    #kgenerator = append_elem('date',nkey,rule,cubeTree[krule])
                    #if 'type' in guide:
                        #cubeTree[kgenerator].itemData['type']=guide['type']
                #elif guide.get('class') == 'c' or rule.get('class') == 'c':
                    #nkey = 'case' 
                    #kgenerator = append_elem('case',nkey,rule,cubeTree[krule])
                #elif 'source' in rule:
                    #nkey = 'domain' 
                    #kgenerator = append_elem('domain',nkey,rule['source'],cubeTree[krule])
                #elif 'related via' in rule:
                    #nkey = 'related via' 
                    #kgenerator = append_elem('case',nkey,rule['related via'],cubeTree[krule])
    #return cubeTree
           ##else:
              ##pass
           ##print(rule)
           ##clave = key + '>' + guide['name'] + str(id3)
           ##if 'name' in rule:
               ##desc = rule['name']
           ##else:
               ##desc = rule['elem']    
           ##id3 += 1
           ##cubeTree.append(CubeItem('prod',clave,id3,desc,cubeTree[key + '>' + guide['name']]))
       ##id2 += 1
##pprint(cubeTree.content)
##for entry in cubeTree.traverse(mode=1):
   ##print('\t'*cubeTree[entry].depth(),entry,cubeTree[entry].ord,cubeTree[entry].itemData)

#def load2(pArbol,estructura,clave=None,level=None):
    
    #if level is None:
       #glevel = 0
    #else:
        #glevel = level + 1
    #nombre = ''
    #if isinstance(estructura,dict):
        #tipo = 'd'
        #if 'name' in estructura:
            #nombre = estructura['name']
    #else:
        #tipo = 'l'
    #ind = 0
    #for key in estructura:
        #if tipo == 'd':
            #entrada = estructura[key]
            #if clave is None:
                #indice = key
            #else:
                #indice = '{}:{}'.format(clave,key)
        #else:
            #entrada = key
            #indice = '{}:{}'.format(clave,ind)
            
        #if isinstance(entrada,(dict,list,tuple)):
            ##print(glevel,key,indice)
            #if clave is not None:
                #pArbol.append(CubeItem(indice.split(':')[-1],indice,parent=pArbol[clave],ord=ind))
            #else:
                #pArbol.append(CubeItem('cubo',indice,parent=None,ord=ind))
            ##print(glevel,'\t'*glevel,'key:{}'.format(indice))
            #load2(pArbol,entrada,clave=indice,level=glevel)
        #else:
            #print(glevel,key,indice)
            #pArbol.append(CubeItem("#entry",indice,parent=pArbol[clave],ord=ind))
            #pArbol[indice].setData({key:entrada})
            ##print(glevel,'\t'*glevel,'key:{}  value:{}'.format(indice,entrada))
            
        #ind += 1

def load3(file):
    def append_elem(tipo,id,estructura,padre,ord=None):
        if padre is None:
            clave=id
            cubeTree.append(CubeItem(tipo,id,desc=id,ord=ord))
        else:
            papiKey = padre.key 
            clave = '{}{}{}'.format(papiKey,DELIMITER,id)
            cubeTree.append(CubeItem(tipo,clave,desc=id,ord=ord,parent=padre))
        if tipo not in ITEM_ATTR or len(ITEM_ATTR[tipo]) == 0:
            return clave
        data = [None for idx in range(len(ITEM_ATTR[tipo]))]
        if isinstance(estructura,dict):
            for attr in estructura:
                if attr in ATTR_TRANS:
                    kattr = ATTR_TRANS[attr]
                else:
                    kattr = attr
                if attr in ITEM_TYPE:
                    continue
                if kattr in ITEM_ATTR[tipo]:
                    kidx = ITEM_ATTR[tipo].index(kattr)
                    if kattr in LIST_ATTR:
                        #print(kattr,attr,estructura[attr])
                        valores = norm2String(estructura[attr])
                        #cubeTree.append(CubeItem('#ientry',nclave,data=valores,desc=kattr,parent=cubeTree[clave]))
                        data[kidx]=valores
                    else:
                        #nclave ='{}{}{}'.format(clave,DELIMITER,kattr)
                        #cubeTree.append(CubeItem('#entry',nclave,data=estructura[attr],desc=kattr,parent=cubeTree[clave]))
                        data[kidx]= estructura[attr]
                else:
                    #pass
                    print(attr,'not in ',tipo)
                cubeTree[clave].setData(data)   
        elif isinstance(estructura,(list,tuple)):
            for ind,item in enumerate(estructura):
                nclave ='{}{}{}'.format(clave,DELIMITER,ind)
                cubeTree.append(CubeItem('#entry',nclave,data=item,parent=cubeTree[clave],ord=ind))
        return clave 
    
    #def append_elemOld(tipo,id,estructura,padre,ord=None):
        #if padre is None:
            #clave=id
            #cubeTree.append(CubeItem(tipo,id,desc=id,ord=ord))
        #else:
            #papiKey = padre.key 
            #clave = '{}{}{}'.format(papiKey,DELIMITER,id)
            #cubeTree.append(CubeItem(tipo,clave,desc=id,ord=ord,parent=padre))

        #if isinstance(estructura,dict):
            #for attr in estructura:
                #kattr = attr
                #if attr in ATTR_TRANS:
                    #kattr = ATTR_TRANS[attr]
                #if kattr in ITEM_ATTR[tipo]:
                    #if kattr in LIST_ATTR:
                        ##nclave ='{}{}{}'.format(clave,DELIMITER,kattr)
                        ##cubeTree.append(CubeItem('#entry',nclave,None,desc=kattr,parent=cubeTree[clave]))
                        ##valores = norm2List(estructura[kattr])
                        ##for ind,dato in enumerate(valores):
                            ##print(kattr,dato)
                            ##mclave ='{}{}{}'.format(nclave,DELIMITER,ind)
                            ##cubeTree.append(CubeItem('#entry',mclave,data=dato,desc=kattr,parent=cubeTree[nclave],ord=ind))
                        #nclave ='{}{}{}'.format(clave,DELIMITER,kattr)
                        #valores = norm2List(estructura[attr])
                        #cubeTree.append(CubeItem('#ientry',nclave,data=valores,desc=kattr,parent=cubeTree[clave]))

                    #else:
                        #nclave ='{}{}{}'.format(clave,DELIMITER,kattr)
                        #cubeTree.append(CubeItem('#entry',nclave,data=estructura[attr],desc=kattr,parent=cubeTree[clave]))
                #else:
                    #print(attr,'not in ',tipo)
                    
        #elif isinstance(estructura,(list,tuple)):
            #for ind,item in enumerate(estructura):
                #nclave ='{}{}{}'.format(clave,DELIMITER,ind)
                #cubeTree.append(CubeItem('#entry',nclave,data=item,parent=cubeTree[clave],ord=ind))
        #return clave 
    
    def procesaGuias(definicion,clave_base):
        for ind,item in enumerate(definicion):
            clave='{}{}{}'.format(clave_base,DELIMITER,item.get('name',ind))
            clave_guia = append_elem('guide',clave,item,cubeTree[clave_base],ord=ind)
            for idx in range(0,len(item['prod'])):
                reglas = item['prod'][idx]
                clave='{}{}{}'.format(clave_guia,DELIMITER,reglas.get('name',idx))
                clave_papa = append_elem('prod',clave,reglas,cubeTree[clave_guia],ord=idx)
                clave = '{}{}{}'.format(clave_papa,DELIMITER,'values')
                clave_regla = append_elem('values',clave,reglas,cubeTree[clave_papa],ord=ind)
                if 'source' in reglas:
                    clave = '{}{}{}'.format(clave_papa,DELIMITER,'domain')
                    append_elem('domain',clave,reglas['source'],cubeTree[clave_papa])
                if 'categories' in reglas:
                    clave = '{}{}{}'.format(clave_papa,DELIMITER,'case')
                    clave_case = append_elem('case',clave,reglas,cubeTree[clave_papa])
                    for idx,entrada in enumerate(reglas['categories']):
                            clave='{}{}{}'.format(clave_case,DELIMITER,entrada.get('result','default'))
                            append_elem('category',clave,entrada,cubeTree[clave_case],ord=idx)                           
                if 'related via' in reglas:
                    clave = '{}{}{}'.format(clave_papa,DELIMITER,'join')
                    clave_join = append_elem('join',clave,None,cubeTree[clave_papa])
                    for idx,entrada in enumerate(reglas['related via']):
                        clave = '{}{}entry_{}'.format(clave_join,DELIMITER,idx)
                        clave_join_entry = append_elem('join_table',clave,entrada,cubeTree[clave_join],ord=idx)
                        #? por que no funciona el enumerate como en el resto
                        for id3 in range(len(entrada['clause'])):
                            clausula = entrada['clause'][id3]
                            clave = '{}{}clause_{}'.format(clave_join_entry,DELIMITER,id3)
                            append_elem('join_clause',clave,clausula,cubeTree[clave_join_entry],ord=id3)
           
                
            
        
    cube = load_cubo(file)
    cubeTree = TreeDict()
    for ind,key in enumerate(cube):
        if key == 'default':
            clavedef = append_elem('default',key,cube[key],None,ord=ind)
            append_elem('vista',key + DELIMITER+ 'vista',cube[key]['vista'],cubeTree[clavedef])
        else:
            append_elem('cube',key,cube[key],None,ord=ind)
            cubo = cube[key]
            append_elem('conn','conn',cubo['connect'],cubeTree[key])
            append_elem('fields','fields',cubo['fields'],cubeTree[key])
            clave_base = append_elem('guides','guides',None,cubeTree[key])
            procesaGuias(cubo['guides'],clave_base)
            append_elem('favorites','favorites',None,cubeTree[key])
    return cubeTree


def load(file):
    #cube = load_cubo(file)
    #cubeTree = TreeDict()
    #load(cubeTree,cube)
    return load3(file)

def pfx(elem):
    return '    '*elem.depth()

def fullPrint(item):
    px = pfx(item)
    print(px,'{} -> {}'.format(item.type,item['name']))
    if item.type in ('#entry','#ientry'):
        print(px,'    {} : {}'.format(item['attr'],item['data']))
    if item.type in ITEM_ATTR:
        for entrada in ITEM_ATTR[item.type]:
            print(px,'    {} : {}'.format(entrada,item[entrada]))
    if item.type in CHILD_TYPE:
        for entrada in CHILD_TYPE[item.type]:
            if item[entrada] is None:
                continue
            for elemento in item[entrada]:
                fullPrint(elemento)
    
if __name__ == '__main__':
    fichero = 'cubo.json'
    #CHILD_TYPE=dict()
    #for m in PARENT_TYPE:
        #entrada = PARENT_TYPE[m]
        #for item in entrada:
            #if item not in CHILD_TYPE:
                #CHILD_TYPE[item]=set()
            #CHILD_TYPE[item].add(m)
    #pprint(CHILD_TYPE)

    cubeTree = load3(fichero)
    
    for entrada in cubeTree.rootItem.childItems:
        fullPrint(entrada)
 
        
    #types=set()
    #kwds =set()
    #for k in cubeTree.traverse(mode=1):
        #print('{}  {}   {}'.format(k,cubeTree[k].type,cubeTree[k].itemData))
    #for item in cubeTree.content:
        #types.add(cubeTree[item].type)
        #if cubeTree[item].itemData is not None:
            #print( cubeTree[item].key, cubeTree[item].itemData )
            #kwds.update([k for k in cubeTree[item].itemData])
        
    #pprint(types)
    #pprint(kwds)
