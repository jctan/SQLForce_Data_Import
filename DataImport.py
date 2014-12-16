__author__ = 'johntan'

import beatbox

service = beatbox.PythonClient()
service.login('jpmc@abilityhousing.org', 'chase123azdPMyIMd9AHBmej8WrrBTCXY')

object_dict = {'Name' : 'Tenant', 'type' : 'Tenant__c', 'Id' : 'a0BU000000er024MAA'}

# results = service.query("SELECT Id, Name FROM Tenant__c")
# records = results['records']
# total_records = results['size']
# query_locator = results
#
# print total_records
# print query_locator
#
#
# while results['done'] is False and len(records) < total_records:
#     results = self._service.queryMore(query_locator)
#     query_locator = results['queryLocator']
#     records += result['records']
#     print records
#     print query_locator
