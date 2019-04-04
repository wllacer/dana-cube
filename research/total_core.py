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
 

