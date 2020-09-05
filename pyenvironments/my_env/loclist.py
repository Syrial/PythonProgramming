import json

loc_list = ['111-F1', 'Kador', 'Amarr', 'Maspah', 'Kamela', '5-N2EY']

with open('loclist.json', 'w') as filehandle:    
    json.dump(loc_list,filehandle)
