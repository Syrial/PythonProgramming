import json

ore_list = ['Veld', 'C.Veld', 'Scor', 'C.Scor', 'Pyro', 'C.Pyro', 'Plag', 'C.Plag', 'Omb', 'C.Omb', 'Ker', 'C.Ker', 'Jasp', 'C.Jasp', 'Herm', 'C.Herm', 'Hedb', 'C.Hedb', 'Spod', 'C.Spod', 'Dark', 'C.Dark', 'Gnes', 'C.Gnes', 'Crok', 'C.Crok', 'Bist', 'C.Bist', 'Merc', 'C.Merc', 'Ark', 'C.Ark']

with open('.json', 'w') as filehandle:
    
    json.dump(ore_list,filehandle)
