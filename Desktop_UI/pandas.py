import json
import ast
import pandas as pd
mystr = """
{'tags': [{'name': 'Temperature1',
  'results': [{'attributes': {'Location': ['3rd Floor'],
  'Sensor-Serial-Number': ['PT100']},
  'groups': [{'name': 'type', 'type': 'number'}],
  'values': [[1460958592800, 24.2, 3],
  [1460958602800, 24.1, 1],
  [1460958612800, 23.9, 1],
  [1460958622800, 24.2, 1],
  [1460958632800, 24.5, 1],
  [1460958642800, 24.9, 1],
  [1460958652800, 24.6, 1],
  [1460958662800, 24.7, 1],
  [1460958672800, 24.7, 1]]}],
 'stats': {'rawCount': 9}}]}
"""
val = ast.literal_eval(mystr)
val1 = json.loads(json.dumps(val))
val2 = val1['tags'][0]['results'][0]['values']
print pd.DataFrame(val2, columns=["time", "temperature", "quality"])