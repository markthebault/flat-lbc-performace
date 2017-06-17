import pandas as pd
import json


json_file = open("output-buy-price.json", "r").read()
df=pd.read_json(json_file)

print df.iloc[0]
