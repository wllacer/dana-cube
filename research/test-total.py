#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2019

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

Vamos a probar el uso de rollup para generar la vista
"""
import sys
sys.path.append('/home/werner/projects/dana-cube.git')

from base.tree import *
from support.util import decorators
from base.core import *
from PyQt5.QtWidgets import QApplication,QDialog,QDialogButtonBox,QComboBox,QLabel,QVBoxLayout
from pprint import pprint
import  base.config

def test_genera_comp():
    """
    probar todas las combinaciones posibles y las diferencias de implementacion
    
    """
    from support.util.jsonmgr import load_cubo
    from support.util.numeros import avg
    from random import randint
    mis_cubos = load_cubo('testcubo.json')
    cubo = Cubo(mis_cubos['datos locales pg'])
    for guia in cubo.lista_guias:
        for guia2 in cubo.lista_guias:
            if guia['name'] == 'geo-detail' or guia2['name'] == 'geo-detail':
               continue
            print ('procesando ',guia['name'],guia2['name'])
            test_comp(cubo,guia['name'],'partido')
        #test_comp(cubo,'partido',guia['name'])     
 
@stopwatch
def with_rollup(cubo,row,col):
    vista = Vista(cubo,row,col,'sum','votes_presential',totalizado=False)
    vista.toNewTree2D()
    return vista 

@stopwatch
def with_clone(cubo,row,col):
    vista = Vista2(cubo,row,col,'sum','votes_presential',totalizado=False)
    vista.toNewTree2D()
    return vista 


def test_comp(cubo,rowname,colname,show=False):
    """
    Comprobar el comportamiento del rollup
    FIXME  ¿Como distingue el rollup de los nulos de cabecera con los nulos de uso practico ?
    """
    vista = with_clone(cubo,rowname,colname) 
    wisout = []
    for row in vista.row_hdr_idx.traverse():
        wisout.append((row.text(),row.getPayload()))

    vista2 = with_rollup(cubo,rowname,colname) 
    wisin = []
    for row in vista2.row_hdr_idx.traverse():
        wisin.append((row.text(),row.getPayload()))
    
    if wisout != wisin:
        print('NO coinciden las ejecuciones para fila {} y columna {}'.format(rowname,colname))
    if show:
        print('sin ',len(wisout),'con',len(wisin))
        for k in range(min(len(wisout),len(wisin))):
                print(wisout[k])
                print(wisin[k])
                print()
    return

def short_test_sim():
    """
    Comprobar el comportamiento del rollup
    FIXME  ¿Como distingue el rollup de los nulos de cabecera con los nulos de uso practico ?
    """
    from support.util.jsonmgr import load_cubo
    from support.util.numeros import avg
    from random import randint
    mis_cubos = load_cubo('../testcubo.json')
    cubo = Cubo(mis_cubos['datos locales'])
    row = 'partido'
    col = 'geo'
    vista = Vista2(cubo,row,col,'sum','votes_presential',totalizado=True)
    #pprint(vista.array)
    #for item in vista.col_hdr_idx.traverse():
        #print(item.text(),item.getFullHeadInfo(content='key',format='array'))
    for line in vista.toList():
        print(line)
    print()
    for line in vista.toList(rowHdrContent='key',rowFilter=lambda x:x.type() == TOTAL):
        print(line)

    #vista.toNewTree2D()
    #for fila in vista.row_hdr_idx.traverse():
        #print(fila.text(),fila.getPayload())
    #return vista 
    #return
  


class Vista2(Vista):
    def _setGuideTrees(self,row,col):    
        """
        Creamos los dos arboles que nos serviran de guias
        """
        for item in (row,col):
            #TODO TOT-V
            self.cubo.lista_guias[item]['dir_row'],self.cubo.lista_guias[item]['contexto']=\
                self.cubo.fillGuia(item,
                                            total=self.totalizado, # if item == row else False,
                                            cartesian=self.cartesian if item == row else False)
            if row == col: #no merece la pena repetirlo, pequeña optimización
                break 

        self.dim_row = len(self.cubo.lista_guias[row]['contexto'])
        self.dim_col = len(self.cubo.lista_guias[col]['contexto'])
            
        self.row_hdr_idx = self.cubo.lista_guias[row]['dir_row']
        #SIMETRICAS
        #El codigo a continuacion se activa cuando podamos clonar correctamente el arbol
        if row != col:
            self.col_hdr_idx = self.cubo.lista_guias[col]['dir_row']
        else:
            # cuerpo del delito para simetricas, tengo que hacer una copia de la guia, sin total
            #
            if self.totalizado:
                start = self.row_hdr_idx.invisibleRootItem().child(0)
            else:
                start = None
            self.col_hdr_idx = self.row_hdr_idx.cloneSubTree(entryPoint=start,payload=False,withEntry=False,ordRole=Qt.DisplayRole)
                
        self.row_hdr_idx.orthogonal = None
        self.row_hdr_idx.vista = None
        self.col_hdr_idx.orthogonal = None
        self.col_hdr_idx.vista = None
        
    def  _setDataMatrix(self):
        """
        __setDateFilter
        __prepareJoin
        Hay paths separados para ROLLUP y sin ROLLUP.
        Las pruebas realizadas aparentemente no dan ventaja, en "elapsed time" a ninguna de las dos aproximaciones
        
        """
        #TODO clarificar el codigo
        basePfx = 'base'
        baseTable =self.cubo.definition['table'] 
        #REFINE solo esperamos un campo de datos. Hay que generalizarlo
        self.array = []
        sqlDef = dict()
        #sqlDef['select_modifier']=None
        sqlDef['tables']=[ [baseTable,basePfx],]
        sqlDef['base_filter']=mergeString(self.filtro,self.cubo.definition.get('base filter',''),'AND')
        sqlDef['where'] = []
        sqlDef['where'] += self._setDateFilter()
        ## si no copio tengo sorpresas
        contexto_row = self.cubo.lista_guias[self.row_id]['contexto'][:]
        contexto_col = self.cubo.lista_guias[self.col_id]['contexto'][:]
        """
        TODO de momento solo totales en row, como era la version anterior.
        Incluir totales de columan tiene una serie de efectos secundarios en todas las operaciones de columna.
        Debería estudiarlo porque merece la pena
        """
        with_rollup = False
        if SUPPORTS_ROLLUP[self.cubo.dbdriver]:
            #print(self.cubo.dbdriver,' soporta ROLLUP')
            #self.totalizado = True
            with_rollup = True
        if self.totalizado:
            contexto_row.insert(0,{'elems':["'//'",],'linkvia':[]})
            contexto_col.insert(0,{'elems':["'//'",],'linkvia':[]})
            #TOT-Y contexto_col.insert(0,{'elems':["'//'",],'linkvia':[]})
        maxRowElem = len(contexto_row[-1]['elems'])
        maxColElem = len(contexto_col[-1]['elems'])
        
        for x,row in enumerate(contexto_row):
            for y,col in enumerate(contexto_col):
                """
                #Garantizar que la optimización no se lleva el prefijo por delante
                """
                tmpLinks = []
                if row['linkvia']:
                    pfx = 'r{}_{}'.format(x,y)
                    tmpLinks += self.__prepareJoin(row['linkvia'],sqlDef['tables'],'r{}_{}'.format(x,y))
                    trow = setPrefix(row['elems'],row['linkvia'][-1]['table'],pfx)
                    #trow = list(map(lambda i:setPrefix(i,row['linkvia'][-1]['table'],pfx),row['elems']))
                else:
                    trow = row['elems'][:]
                if col['linkvia']:
                    pfx  ='c{}_{}'.format(x,y)
                    tmpLinks += self.__prepareJoin(col['linkvia'],sqlDef['tables'],'c{}_{}'.format(x,y))
                    tcol = setPrefix(col['elems'],col['linkvia'][-1]['table'],pfx)
                    #tcol = list(map(lambda i:setPrefix(i,col['linkvia'][-1]['table'],pfx),col['elems']))
                else:
                    tcol = col['elems'][:]
                sqlDef['join'] = tmpLinks
                
                #trow = row['elems'][:]
                #tcol = col['elems'][:]
                if self.totalizado: #and x != 0:
                    try:
                        pos = trow.index("'//'")
                        del trow[pos]
                    except ValueError:
                        pass
                    try:
                        pos = tcol.index("'//'")
                        del tcol[pos]
                    except ValueError:
                        pass
                sqlDef['group'] = trow + tcol
                if self.totalizado:
                    rowFields =["'//'",] + trow 
                    numRowElems = len(rowFields)
                    print(tcol)
                    colFields = tcol
                    numColElems = len(colFields)
                    sqlDef['fields'] = rowFields + colFields + [(self.campo,self.agregado)]
                else:
                    sqlDef['fields'] =sqlDef['group']  + [(self.campo,self.agregado)]
                    rowFields = trow
                    numRowElems = len(rowFields)
                    colFields = tcol
                    numColElems = len(colFields)
                #FIXME  creo que en totalizado no acaba de ordenar por la ultima columna         
                if self.totalizado:
                    array_offset = 2
                else:
                    array_offset = 1
                sqlDef['order'] = [ str(x + array_offset) for x in range(len(sqlDef['group']))]
            
                sqlDef['driver'] = self.cubo.dbdriver
                sqlDef = setPrefix(sqlDef,baseTable,basePfx,excludeDict=('tables','table','ltable'))
                if not with_rollup:
                    sqlstring=queryConstructor(**sqlDef)
                    lista_compra={'row':{'nkeys':numRowElems,},
                                    'rdir':self.row_hdr_idx,
                                    'col':{'nkeys':numColElems,
                                            'init':numRowElems,},
                                    'cdir':self.col_hdr_idx,
                                    'rollup':with_rollup,
                                    'total':self.totalizado,
                                    }
                    cursor = getCursor(self.cubo.db,sqlstring,regTreeGuide,**lista_compra)
                    self.array +=cursor 
                    if config.DEBUG:
                        print(time.time(),'Datos ',queryFormat(sqlstring))
        if with_rollup:
            # hay que cambiar el orden porque he descubierto que con rollup es mas practico poner las columnas delante
            # finalmente he optado por  ROLLUP(columna,fila(s) ORDER BY GROUPING
            # si la columna tiene jerarquia la mejor manera que he encontrado es una secuencia de ROLLUPS (col[0],filas),...ROLLUP(cols[0:n],filas) ... y la clausula DISTINCT para evitar procesar los duplicacdos que aparecen
            rowElems= list(map(lambda x:strip_as(x),sqlDef['group'][:-1* numColElems]))
            colElems  = list(map(lambda x:strip_as(x),sqlDef['group'][-1* numColElems:]))
            limpia = colElems + rowElems
            sqlDef['group'] =  [{'type':'CUBE','elems':limpia},]
            #sqlDef['having'] = (('GROUPING({})'.format(norm2String(limpia)),'<',2**len(limpia)-1),)
            ## incluyo el grouping para poder seleccionar mejor en la salida
            sqlDef['fields'].append('GROUPING({}) AS gid'.format(norm2String(limpia)))
            sqlDef['select_modifier'] = 'DISTINCT'
            sqlDef['order'].insert(0,'gid DESC')
            sqlstring=queryConstructor(**sqlDef)
            lista_compra={'row':{'nkeys':numRowElems,},
                'rdir':self.row_hdr_idx,
                'col':{'nkeys':numColElems,
                        'init':numRowElems,},
                'cdir':self.col_hdr_idx,
                'rollup':with_rollup,
                'total':self.totalizado,
                }
            self.array = getCursor(self.cubo.db,sqlstring,regTreeGuide,**lista_compra)
            if config.DEBUG:
                print(time.time(),'Datos ',queryFormat(sqlstring))            
 

        #pprint(self.array)
if __name__ == '__main__':    
    app = QApplication(sys.argv)
    config.DEBUG = False
    function = short_test_sim
    parms = []
    if len(sys.argv) > 1:
        function = locals()[sys.argv[1]]
        if len(sys.argv) > 2:
            parms = sys.argv[2:]
    function(*parms)
