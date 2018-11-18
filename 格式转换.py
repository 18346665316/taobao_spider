f = open('4-5.txt', 'r')
text = f.readline()
import json
dict_new = json.loads(text)
print(dict_new["valItemInfo"]["skuMap"])