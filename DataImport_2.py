__author__ = 'johntan'

import csv
import SQLForce

class Table:
    def __init__(self,name):
        self.name = name
        self.headers = []
        self.rows = []

def createTable(fileName, sheetName):
    csv_fp = open(fileName, 'r')
    csv_reader = csv.reader(csv_fp, delimiter=',')

    table = Table(sheetName)
    current_row = 0
    for row in csv_reader:
        current_row += 1
        if current_row == 1: # get headers
            table.headers.append(row)
            continue
        if row not in table.rows:
            table.rows.append(row)
    print("Table " + table.name + " is created!")
    for i in table.headers:
        nCols = len(i)
    print("# of Columns: " + str(nCols) + "\n # of Rows: " + str(len(table.rows)) + "\n ***HEADERS***")

    print(table.headers)
    print(table.rows)

def templateFile(fileName, objectName):
    #Below password and token will be stored somewhere
    session = SQLForce.Session("Production", "jpmc@abilityhousing.org", "chase123", "azdPMyIMd9AHBmej8WrrBTCXY")
    fields = session.describeTable(objectName)
    columns = []
    print("\n\n" + objectName)
    for cols in fields:
        print("Field " + cols.name + " is of type " + cols.type )
    #csvOutFile = open(fileName, 'w', newline='')
    #writeOut = csv.writer(csvOutFile, dialect='excel')
    #writeOut.writerow(columns)
    #print(fileName + " is created!")

def getResults(objectName):
    #Below password and token will be stored somewhere
    session = SQLForce.Session("Production", "jpmc@abilityhousing.org", "chase123", "azdPMyIMd9AHBmej8WrrBTCXY")

def insertRecords(objectName):
    session = SQLForce.Session("Production", "jpmc@abilityhousing.org", "chase123", "azdPMyIMd9AHBmej8WrrBTCXY")
    #session.insert('', [,'',''], ['Medha', 'Jha', 'Head of household'] )
    #session.runCommands("INSERT INTO Tenant__c(Person_ID__c, First_Name__c, Last_Name__c, Relation__c ) VALUES('217, 'Medha', 'Jha', 'Head of household')")
    session.insert('Tenant__c', ['Person_ID__c', 'First_Name__c', 'Last_Name__c', 'Relation__c'], [[ '217', 'Medha', 'Jha', 'Head of household']] )


    print("Inserted!")

print("****************Creating template file****************")
fileName='/Users/johntan/documents/Tenant_2.csv'

print("**************Tables Structure************************")
objectName = 'Tenant__c'
templateFile(fileName, objectName)

objectName = 'SSN__c'
templateFile(fileName, objectName)

insertRecords(objectName)

#objectName = 'Household__c'
#templateFile(fileName, objectName)


print("\n\n****************Creating table for mapping****************")
fileName = '/Users/johntan/documents/Tenant.csv'
objectName = 'Tenant__c'
createTable(fileName, objectName)

#objectName = 'Tenant__c'
#getResults(objectName)
