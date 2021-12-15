datafolder = "D:/LexBib/"
lwbuser = "DavidLbot"

with open(datafolder+'zoteroapi/zotero_api_key.txt', 'r', encoding='utf-8') as pwdfile:
	zotero_api_key = pwdfile.read()

lwb_prefixes = """
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <http://lexbib.elex.is/prop/reference/>
PREFIX lno: <http://lexbib.elex.is/prop/novalue/>

"""

# Properties with constraint: max. 1 value
max1props = [
#"P1",
"P2",
"P3",
"P6",
"P8",
"P9",
"P10",
"P11",
"P15",
"P16",
"P17",
"P22",
"P23",
"P24",
"P29",
"P30",
"P32",
"P36",
"P38",
"P40",
"P41",
"P43",
"P52",
"P53",
"P54",
"P64",
"P65",
"P66",
"P68",
"P69",
"P70",
"P71",
#"P80",
"P84",
"P85",
"P87",
"P92",
"P93",
"P97",
"P100",
"P101",
"P102",
"P109",
"P117",
"P128"
]
