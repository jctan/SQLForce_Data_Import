__author__ = 'johntan'

import xlrd
import re
import SQLForce


class Table:
    def __init__(self,name):
        self.name = name
        self.columns = []
        self.rows = []

class TableColumn:
    def __init__(self, name, refName = None):
        self.name = name
        self.refName = refName

class TableRow:
    def __init__(self,key):
        self.key = key
        self.data = []


def processSpreadSheet(SFSession, filename, clearData=True):
    workbook = xlrd.open_workbook(filename)

    spreadSheet = workbook.sheet_by_name('Reload')

    nRows = spreadSheet.nrows
    nCols = spreadSheet.ncols

    if(clearData and 'Reload' in workbook.sheet_names()):
        for row in range(0, nRows):
            rowData = spreadSheet.cell_value(row,0)
            if rowData:
                print("Executing : " + rowData)
                SFSession.runCommands(rowData)

    for spreadSheet in workbook.sheet_names():
        if spreadSheet == 'Reload':
            continue
        print("Loading: " + spreadSheet)
        table = createTable(spreadSheet, workbook.sheet_by_name(spreadSheet))
        importData(SFSession, table)

    '''
    if(clearData and 'Product2' in workbook.sheet_names()):
        for row in range(0, nRows):
            rowData = spreadSheet.cell_value(row,0)
            print('-'*40)
            print('Row: %s' % row)
            for col in range(0,nCols):
                colData = spreadSheet.cell_value(0,col)
                cell_value = spreadSheet.cell_value(row,col)
                print('Column: [%s], cell_value: [%s]' % (colData,cell_value))
    '''

    '''
    for spreadSheetName in workbook.sheet_names():
        if spreadSheetName == 'CT':
            continue
        table = createTable(spreadSheetName, workbook.sheet_by_name(spreadSheetName))
    '''

#import data into salesforce
def importData(SFSession, table):
    colNames = []
    appendedRows = []
    RefKeyRows = []
    RefKeyColNames = []
    RefKeyColIndexes = []
    RefKeyCount = 0

    '''
    surrogate key as unique identifiers for an entity
    '''
    for indexCols in range(0,len(table.columns)):
        col = table.columns[indexCols]
        colNames.append(col.name)
        if col.refName == table.name:
            RefKeyColNames.append(col.name)
            RefKeyColIndexes.append(indexCols)

    for row in table.rows:
        newRow = []
        for indexCols in range(0,len(colNames)):
            col = table.columns[indexCols]
            if col.refName:
                if col.refName == table.name:
                    newRow.append(None)
                    if row.data[indexCols]:
                        RefKeyCount += 1
                else:
                    key = row.data[indexCols]
                    newRow.append(getTableHashMap(col.refName)[key])
            else:
                newRow.append(row.data[indexCols])
        if RefKeyCount:
            RefKeyRows.append(row)
        appendedRows.append(newRow)

    rowIds = SFSession.insert(table.name, colNames, appendedRows)


    '''
    set mapping from the surrogate key to the new generated salesforce ids
    '''

    mapId = getTableHashMap(table.name)
    for indexCols in range(0, len(rowIds)):
        mapId[table.rows[indexCols].key] = rowIds[indexCols]

    '''
    if the same columns referencing to the same table, put them together
    '''

    if RefKeyRows:
        appendedRows = []
        for row in RefKeyRows:
            newRow = [mapId[row.key]]
            for colIndex in RefKeyColIndexes:
                value = row.data[colIndex]
                if value:
                    newRow.append(mapId[value])
                else:
                    newRow.append(None)
            appendedRows.append(newRow)

        SFSession.update(table.name, RefKeyColIndexes, appendedRows)

'''
import the excel spreadsheet into a runtime table that's craeted
first row are the names of the fields to populate in salesforce.
If the newTableName already has the appended column names, then they're a key for another table
'''
def createTable(newTableName, spreadSheet):
    table = Table(newTableName)
    columns = spreadSheet.ncols
    rows = spreadSheet.nrows

    for indexCols in range(0, columns):
        colName = spreadSheet.cell_value(0, indexCols)
        matchObj = ColumnPattern.match(colName)
        col = TableColumn(matchObj.groups()[0], matchObj.groups()[2])
        table.columns.append(col)

    for row in range(1, rows):
        key = spreadSheet.cell_value(row, 0)
        tableRow = TableRow(key)
        for indexCols in range(0, columns):
            value = spreadSheet.cell_value(row,indexCols)
            tableRow.data.append(value)
        table.rows.append(tableRow)
    return table

ColumnPattern = re.compile("^([^-]+)(->(.*)){0,1}")
tableHashMap = {}

def getTableHashMap(newTableName):
        global tableHashMap
        if newTableName not in tableHashMap.keys():
            tableHashMap[newTableName] = {}
        return tableHashMap[newTableName]


if __name__ == '__main__':
    SFSession = SQLForce.Session('PRODUCTION', 'jpmc@abilityhousing.org', 'chase123', 'azdPMyIMd9AHBmej8WrrBTCXY')
    processSpreadSheet(SFSession, "/Users/johntan/Downloads/Cardinals/TestSalesforceData/Tenant.xlsx", True)