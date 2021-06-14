datafolder = "D:/LexBib/"
lwbuser = "DavidL"

with open(datafolder+'zoteroapi/zotero_api_key.txt', 'r', encoding='utf-8') as pwdfile:
	zotero_api_key = pwdfile.read()

lwb_prefixes = """
PREFIX lwb: <http://data.lexbib.org/entity/>
PREFIX ldp: <http://data.lexbib.org/prop/direct/>
PREFIX lp: <http://data.lexbib.org/prop/>
PREFIX lps: <http://data.lexbib.org/prop/statement/>
PREFIX lpq: <http://data.lexbib.org/prop/qualifier/>
PREFIX lpr: <http://data.lexbib.org/prop/reference/>
"""

# Properties with constraint: max. 1 value
max1props = [
"P1",
"P2",
"P3",
#"P4", # wikidata item
"P6",
"P8",
"P9",
"P10",
"P11",
"P14",
"P15",
"P16",
"P17",
"P22",
"P23",
"P24",
"P29",
"P30",
"P32",
"P34",
"P35",
"P36",
"P37",
"P38",
"P40",
"P41",
"P46",
"P65",
"P70",
"P71",
#"P80",
"P85",
"P87",
"P93",
"P100"
]
