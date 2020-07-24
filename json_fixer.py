"""
Author: Barrett F. Davis
Affiliation: Purdue University, School of Biomedical Engineering
Contact: davis797@purdue.edu

About: Used to create a JSON file for a given US state's counties. The spellFix
dictionary is used to keep county names consistent with the COVID database's
records. Indiana's state code is 18. 

"""

from urllib.request import urlopen
import json 


lo_res = 'https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json'
md_res = 'https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_5m.json'
hi_res = 'https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_500k.json'
url = md_res

jfile = json.loads(urlopen(url).read().decode("latin-1"))

loader = []
spellFix = {'DeKalb': 'De Kalb', 'LaGrange': 'Lagrange', 'LaPorte': 'La Porte'}


for idx, j in enumerate(jfile['features']):
    
    if j['properties']['STATE'] == '18':
        
        countyname = j['properties']['NAME']
        if countyname in spellFix.keys():
            j['properties']['NAME'] = spellFix[countyname]
        
        loader.append({k: j[k] for k in ['type','geometry','properties']})                
                
final = {"type": "FeatureCollection", "features": loader}
with open('json_indiana.json', 'w') as file:
     file.write(json.dumps(final))