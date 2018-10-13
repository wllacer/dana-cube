#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
"""
Part of  Global Common modules by Werner Llácer (c) 2012-2018

As an integral part of a project distributed under an Open Source Licence, the licence of the proyect
Used as  standalone module or outside the scope of  a project valid according to the  previous paragraph, or when  in doubt, distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html

"""
"""
  adaptado de http://stackoverflow.com/questions/3253301/howto-restore-qtreeview-last-expanded-state
  
"""


def saveExpandedState(view):
    expansionList = dict()
    for rowId in range(view.model().rowCount()):
        saveExpandedOnLevel(expansionList,view,view.model().index(rowId,0))
    return expansionList

def restoreExpandedState(expansionList,view):
    view.setUpdatesEnabled(False)
    for rowId in range(view.model().rowCount()):
        restoreExpandedOnLevel(expansionList,view,view.model().index(rowId,0))
    view.setUpdatesEnabled(True)
    expansionList.clear()

def saveExpandedOnLevel(expansionList,view,modelIdx):
    if view.isExpanded(modelIdx):
        if modelIdx.isValid():
            expansionList[modelIdx.data()] = True
        for rowId in range(modelIdx.model().rowCount(modelIdx)):
            saveExpandedOnLevel(expansionList,view,modelIdx.child(rowId,0))
            
def restoreExpandedOnLevel(expansionList,view,modelIdx):
    state = expansionList.get(modelIdx.data(),False)
    if state:
        view.setExpanded(modelIdx,state)
        for rowId in range(modelIdx.model().rowCount(modelIdx)):
            restoreExpandedOnLevel(expansionList,view,modelIdx.child(rowId,0))

"""
void MyWidget::saveExpandedState()
{
    for(int row = 0; row < tree_view_->model()->rowCount(); ++row)
        saveExpandedOnLevel(tree_view_->model()->index(row,0));
}

void Widget::restoreExpandedState()
{
    tree_view_->setUpdatesEnabled(false);

    for(int row = 0; row < tree_view_->model()->rowCount(); ++row)
        restoreExpandedOnLevel(tree_view_->model()->index(row,0));

    tree_view_->setUpdatesEnabled(true);
}

void MyWidget::saveExpandedOnLevel(const QModelIndex& index)
{
    if(tree_view_->isExpanded(index)) {
        if(index.isValid())
            expanded_ids_.insert(index.data(Qt::UserRole).toInt());
        for(int row = 0; row < tree_view_->model()->rowCount(index); ++row)
            saveExpandedOnLevel(index.child(row,0));
    }
}

void MyWidget::restoreExpandedOnLevel(const QModelIndex& index)
{
    if(expanded_ids_.contains(index.data(Qt::UserRole).toInt())) {
        tree_view_->setExpanded(index, true);
        for(int row = 0; row < tree_view_->model()->rowCount(index); ++row)
            restoreExpandedOnLevel(index.child(row,0));
    }
}
"""
