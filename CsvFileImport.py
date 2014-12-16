__author__ = 'johntan'

import xlrd
import csv
import codecs

CSVFILE = '/Users/johntan/Desktop/baseball.csv'
FIELDS = ['key', 'name', 'productcode', 'family', 'description']

file_handler = codecs.open(CSVFILE, 'rU', 'utf-16')
#file_handler = open(CSVFILE, "rb")
#next(file_handler)
#csv_reader = csv.DictReader(file_handler, FIELDS, delimiter=',')
csv_reader = csv.reader(file_handler)

rows = []
for line in csv_reader:
    rows.append(line)
#rows = list(csv_reader)


# file_location = '/Users/johntan/Desktop/baseball.xlsx'
# workbook = xlrd.open_workbook(file_location)
# sheet = workbook.sheet_by_index(0)

# for col in range(sheet.ncols):
#     print sheet.cell_value(0, col)
# data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]

