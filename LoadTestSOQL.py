__author__ = 'johntan'

'''
Created on Mar 19, 2014

Populate a salesforce database with test data from Excel.

This script illustrates how to import data into multiple Salesforce tables from an
Excel workbook where each sheet contains data for a single table. The script also
knows how to "link related records together" using a concept called "synthetic keys."
Example: Import contacts are linked to the respective parent accounts.

The Excel workbook format is simple:
1. If a wooksheet is called "Reset" then is assumed to contain SOQL statements that will be run before
   the import. This is useful to clear existing database before importing new.
2. All other worksheets are assumed to be data to be imported (one per worksheet) and will be imported
   into Excel from left to right.

The first row of each data worksheet is special.
1. Column #1 contains the (optional) synthetic key for a record.
2. Column's #2-#n contains either:
   + a Salesforce column name
   + a label of the form: SalesforceColumnName->SourceTable

     This format indicates that the value of the column should be the unique Salesforce Id that
     Salesforce assigns to the record in the "Source Table". The values in rows #2-#n contain a synthetic key
     for specified by a row in the "Source Table"

     Example: One account has the Synthetic Key "Cardinals". The worksheet for Contacts contains a column named AccountId->Account.
     The contact record for "Lou Brock" contains the value "Cardinals" in the AccountId->Account column. This tells the script to link
     the "Lou Brock" record to the Salesforce Id assigned to the "Cardinals" acccount.

Rows #2-#n simply contains field data for each record to import.

@author: gsmithfarmer@gmail.com
'''

import xlrd
import re
import SQLForce

'''
The Table/TableRow/TableColumn structures are used to hold the contents of an Excel worksheet in memory.
'''
class TableColumn:
    def __init__(self, name, referenceTo = None):
        self.name = name
        self.referenceTo = referenceTo

class TableRow:
    def __init__(self, key):
        self.key = key
        self.data = []

class Table:
    def __init__(self, name ):
        self.name = name
        self.columns = []
        self.rows = []


_ColumnNamePattern = re.compile("^([^-]+)(->(.*)){0,1}")

'''
The "tableKeyMap" maps table name the a structure that maps all synthetic keys defined in Excel
to the Salesforce Ids created what a record was inserted.
'''
tableKeyMap = {}

def _getTableKeyMap( tableName ):
    global tableKeyMap
    if tableName not in tableKeyMap.keys():
        tableKeyMap[tableName] = {}

    return tableKeyMap[tableName]

def _loadFixedDataKeys(session):
    global tableKeyMap
    myMap = _getTableKeyMap("Pricebook2")
    for rec in session.selectRecords("SELECT id, name FROM Pricebook2"):
        myMap[rec.name] = rec.id

'''
Load an Excel worksheet into the runtime Table data structure.
'''
def _createTableFromSheet( tableName, sheet ):

    '''
    The first row contains the names of the fields in Salesforce to populate.
    If a column name has an appended (tablename) then the value is a key for a record in another table.
    '''

    table = Table(tableName)
    nColumns = sheet.ncols

    for ii in range(1, nColumns):
        colName = sheet.cell_value(0, ii )
        matchObj = _ColumnNamePattern.match(colName)
        col = TableColumn( matchObj.groups()[0], matchObj.groups()[2])
        table.columns.append(col)


    for row in range(1, sheet.nrows ):
        key = sheet.cell_value(row, 0 )
        tableRow = TableRow(key)
        for ii in range(1, nColumns ):
            value = sheet.cell_value(row, ii)
            tableRow.data.append(value)

        table.rows.append(tableRow)

    return table

'''
Insert all records from a in-memory table into Salesforce.

'''
def _importToSalesforce( session, table ):
    colNames = []
    rows = []
    selfRefColNames = []
    selfRefRows = []
    selfRefColIndexes = []

    #
    # If a column contains a synthetic key then remember it here for later processing
    #
    for ii in range(0, len(table.columns)):
        col = table.columns[ii]
        colNames.append(col.name)
        if col.referenceTo == table.name:
            selfRefColNames.append(col.name)
            selfRefColIndexes.append(ii)

    for row in table.rows:
        thisRow = []
        selfRefCount = 0
        for ii in range(0, len(colNames)):
            col = table.columns[ii]
            if col.referenceTo:
                if col.referenceTo == table.name:
                    thisRow.append(None)
                    if row.data[ii]:
                        selfRefCount += 1
                else:
                    key = row.data[ii]
                    thisRow.append( _getTableKeyMap(col.referenceTo)[key])

            else:
                thisRow.append( row.data[ii])

        if selfRefCount:
            selfRefRows.append(row)

        rows.append(thisRow)

    rowIds = session.insert(table.name, colNames, rows )

    '''
    Stash away a mapping from the spreadsheet synthetic  keys to the newly generated Salesforce ids.
    '''
    idMap = _getTableKeyMap(table.name)
    for ii in range( 0, len(rowIds)):
        idMap[table.rows[ii].key] = rowIds[ii]

    '''
    If there were any columns that reference this same table (like Account->parentId) then patch
    these records.
    '''

    if selfRefRows:
        rows = []
        for row in selfRefRows:
            thisRow = [ idMap[row.key]]
            for nn in selfRefColIndexes:
                value = row.data[nn]
                if value:
                    thisRow.append( idMap[value] )
                else:
                    thisRow.append(None)
            rows.append(thisRow)

        session.update(table.name, selfRefColNames, rows )


def loadSpreadsheet( session, filename, clearData=True):
    _loadFixedDataKeys(session)

    workbook = xlrd.open_workbook(filename)

    if( clearData and 'Reset' in workbook.sheet_names()):
        sheet = workbook.sheet_by_name('Reset')
        for row in range(0, sheet.nrows ):
            soql = sheet.cell_value(row,0)

            if soql:
                print("running: " + soql)
                session.runCommands(soql)

    for sheetName in workbook.sheet_names():
        if sheetName == 'Reset':
            continue

        print( "Loading: " + sheetName )
        table = _createTableFromSheet( sheetName, workbook.sheet_by_name(sheetName))
        _importToSalesforce(session, table )


if __name__ == '__main__':
    session = SQLForce.Session("gsmithfarmer")
    loadSpreadsheet(session, "TestSalesforceData/Baseball.xls", True)

