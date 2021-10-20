import csv
import config

def getiso3(digits):
	#lexvo mapping table http://www.lexvo.org/resources/lexvo-iso639-1.tsv
	TwoDigitLang = {
	"aa":"aar",
	"ab":"abk",
	"ae":"ave",
	"af":"afr",
	"ak":"aka",
	"am":"amh",
	"an":"arg",
	"ar":"ara",
	"as":"asm",
	"av":"ava",
	"ay":"aym",
	"az":"aze",
	"ba":"bak",
	"be":"bel",
	"bg":"bul",
	"bi":"bis",
	"bm":"bam",
	"bn":"ben",
	"bo":"bod",
	"br":"bre",
	"bs":"bos",
	"ca":"cat",
	"ce":"che",
	"ch":"cha",
	"co":"cos",
	"cr":"cre",
	"cs":"ces",
	"cu":"chu",
	"cv":"chv",
	"cy":"cym",
	"da":"dan",
	"de":"deu",
	"dv":"div",
	"dz":"dzo",
	"ee":"ewe",
	"el":"ell",
	"en":"eng",
	"eo":"epo",
	"es":"spa",
	"et":"est",
	"eu":"eus",
	"fa":"fas",
	"ff":"ful",
	"fi":"fin",
	"fj":"fij",
	"fo":"fao",
	"fr":"fra",
	"fy":"fry",
	"ga":"gle",
	"gd":"gla",
	"gl":"glg",
	"gn":"grn",
	"gu":"guj",
	"gv":"glv",
	"ha":"hau",
	"he":"heb",
	"hi":"hin",
	"ho":"hmo",
	"hr":"hrv",
	"ht":"hat",
	"hu":"hun",
	"hy":"hye",
	"hz":"her",
	"ia":"ina",
	"id":"ind",
	"ie":"ile",
	"ig":"ibo",
	"ii":"iii",
	"ik":"ipk",
	"io":"ido",
	"is":"isl",
	"it":"ita",
	"iu":"iku",
	"ja":"jpn",
	"jv":"jav",
	"ka":"kat",
	"kg":"kon",
	"ki":"kik",
	"kj":"kua",
	"kk":"kaz",
	"kl":"kal",
	"km":"khm",
	"kn":"kan",
	"ko":"kor",
	"kr":"kau",
	"ks":"kas",
	"ku":"kur",
	"kv":"kom",
	"kw":"cor",
	"ky":"kir",
	"la":"lat",
	"lb":"ltz",
	"lg":"lug",
	"li":"lim",
	"ln":"lin",
	"lo":"lao",
	"lt":"lit",
	"lu":"lub",
	"lv":"lav",
	"mg":"mlg",
	"mh":"mah",
	"mi":"mri",
	"mk":"mkd",
	"ml":"mal",
	"mn":"mon",
	"mr":"mar",
	"ms":"msa",
	"mt":"mlt",
	"my":"mya",
	"na":"nau",
	"nb":"nob",
	"nd":"nde",
	"ne":"nep",
	"ng":"ndo",
	"nl":"nld",
	"nn":"nno",
	"no":"nor",
	"nr":"nbl",
	"nv":"nav",
	"ny":"nya",
	"oc":"oci",
	"oj":"oji",
	"om":"orm",
	"or":"ori",
	"os":"oss",
	"pa":"pan",
	"pi":"pli",
	"pl":"pol",
	"ps":"pus",
	"pt":"por",
	"qu":"que",
	"rm":"roh",
	"rn":"run",
	"ro":"ron",
	"ru":"rus",
	"rw":"kin",
	"sa":"san",
	"sc":"srd",
	"sd":"snd",
	"se":"sme",
	"sg":"sag",
	"sh":"hbs",
	"si":"sin",
	"sk":"slk",
	"sl":"slv",
	"sm":"smo",
	"sn":"sna",
	"so":"som",
	"sq":"sqi",
	"sr":"srp",
	"ss":"ssw",
	"st":"sot",
	"su":"sun",
	"sv":"swe",
	"sw":"swa",
	"ta":"tam",
	"te":"tel",
	"tg":"tgk",
	"th":"tha",
	"ti":"tir",
	"tk":"tuk",
	"tl":"tgl",
	"tn":"tsn",
	"to":"ton",
	"tr":"tur",
	"ts":"tso",
	"tt":"tat",
	"tw":"twi",
	"ty":"tah",
	"ug":"uig",
	"uk":"ukr",
	"ur":"urd",
	"uz":"uzb",
	"ve":"ven",
	"vi":"vie",
	"vo":"vol",
	"wa":"wln",
	"wo":"wol",
	"xh":"xho",
	"yi":"yid",
	"yo":"yor",
	"za":"zha",
	"zh":"zho",
	"zu":"zul"
	}

	if len(digits) == 2:
		return TwoDigitLang[digits.lower()]
	elif len(digits) == 3:
		if digits in TwoDigitLang.values():
			return digits.lower()
		else:
			return None

def getWikiLangCode(iso3):
	iso3towdcode = {
	"epo": "eo",
	"fra": "fr",
	"spa": "es",
	"fin": "fi",
	"eng": "en",
	"eus": "eu",
	"ekk": "et",
	"est": "et",
	"fas": "fa",
	"frp": "frp",
	"fao": "fo",
	"fry": "fy",
	"frr": "frr",
	"ext": "ext",
	"fij": "fj",
	"fur": "fur",
	"ful": "ff",
	"cat": "ca",
	"bul": "bg",
	"bel": "be",
	"bos": "bs",
	"ben": "bn",
	"bre": "br",
	"bua": "bxr",
	"bjn": "bjn",
	"bug": "bug",
	"ceb": "ceb",
	"bam": "bm",
	"cha": "ch",
	"chy": "chy",
	"bcl": "bcl",
	"che": "ce",
	"chr": "chr",
	"bis": "bi",
	"cdo": "cdo",
	"bpy": "bpy",
	"bxr": "bxr",
	"deu": "de",
	"dan": "da",
	"ces": "cs",
	"ell": "el",
	"cym": "cy",
	"zza": "diq",
	"dsb": "dsb",
	"ewe": "ee",
	"div": "dv",
	"dzo": "dz",
	"cos": "co",
	"chu": "cu",
	"chv": "cv",
	"cre": "cr",
	"csb": "csb",
	"chu": "cu",
	"ell": "el",
	"ckb": "ckb",
	"din": "din",
	"egl": "egl",
	"dty": "dty",
	"aym": "ay",
	"abk": "ab",
	"arg": "an",
	"aze": "az",
	"bak": "ba",
	"ara": "ar",
	"afr": "af",
	"ace": "ace",
	"ady": "ady",
	"aka": "ak",
	"amh": "am",
	"arc": "arc",
	"asm": "as",
	"ast": "ast",
	"bar": "bar",
	"ava": "av",
	"awa": "awa",
	"arz": "arz",
	"ban": "ban",
	"ang": "ang",
	"ary": "ary",
	"atj": "atj",
	"avk": "avk",
	"alt": "alt",
	"azb": "azb",
	"hin": "hi",
	"guj": "gu",
	"hrv": "hr",
	"gle": "ga",
	"heb": "he",
	"glg": "gl",
	"gla": "gd",
	"glv": "gv",
	"hsb": "hsb",
	"hak": "hak",
	"gag": "gag",
	"gan": "gan",
	"haw": "haw",
	"glk": "glk",
	"got": "got",
	"grn": "gn",
	"hif": "hif",
	"hau": "ha",
	"gsw": "gsw",
	"gcr": "gcr",
	"gor": "gor",
	"gom": "gom",
	"akl": "akl",
	"zun": "zun",
	"sms": "sms",
	"mic": "mic",
	"ase": "ase",
	"clc": "clc",
	"vot": "vot",
	"cbk": "cbk-zam",
	"gaa": "gaa",
	"fon": "fon",
	"loz": "loz",
	"liv": "liv",
	"krj": "krj",
	"nog": "nog",
	"non": "non",
	"ett": "ett",
	"kri": "kri",
	"kum": "kum",
	"nui": "nui",
	"sei": "sei",
	"wal": "wal",
	"wls": "wls",
	"cpx": "cpx",
	"prs": "fa-af",
	"aln": "aln",
	"sgs": "bat-smg",
	"nod": "nod",
	"lag": "lag",
	"bzg": "bzg",
	"pyu": "pyu",
	"gmh": "gmh",
	"guc": "guc",
	"khw": "khw",
	"nsk": "nsk",
	"tvx": "tvx",
	"ppu": "ppu",
	"ood": "ood",
	"osa": "osa",
	"bdr": "bdr",
	"btm": "btm",
	"gcf": "gcf",
	"srq": "srq",
	"rkt": "rkt",
	"sjm": "sjm",
	"ins": "ins",
	"rki": "rki",
	"fuf": "fuf",
	"jax": "jax",
	"dtp": "dtp",
	"zgh": "zgh",
	"bgn": "bgn",
	"yav": "yav",
	"und": "und",
	"zxx": "zxx",
	"isl": "is",
	"ita": "it",
	"jpn": "ja",
	"hye": "hy",
	"hun": "hu",
	"ind": "id",
	"ipk": "ik",
	"iku": "iu",
	"hat": "ht",
	"inh": "inh",
	"ibo": "ig",
	"iii": "ii",
	"ido": "io",
	"ile": "ie",
	"ina": "ia",
	"ilo": "ilo",
	"jam": "jam",
	"jbo": "jbo",
	"hyw": "hyw",
	"lat": "la",
	"ksh": "ksh",
	"kat": "ka",
	"kor": "ko",
	"khm": "km",
	"kaz": "kk",
	"kir": "ky",
	"cor": "kw",
	"kal": "kl",
	"kbd": "kbd",
	"kaa": "kaa",
	"jav": "jv",
	"kas": "ks",
	"kik": "ki",
	"kan": "kn",
	"kon": "kg",
	"krc": "krc",
	"kbp": "kbp",
	"kab": "kab",
	"kom": "kv",
	"kmr": "ku",
	"kur": "ku",
	"koi": "koi",
	"mlg": "mg",
	"ltz": "lb",
	"lav": "lv",
	"lvs": "lv",
	"lit": "lt",
	"lao": "lo",
	"mkd": "mk",
	"min": "min",
	"mdf": "mdf",
	"lez": "lez",
	"lug": "lg",
	"lmo": "lmo",
	"lij": "lij",
	"mai": "mai",
	"lad": "lad",
	"lld": "lld",
	"lbe": "lbe",
	"ltg": "ltg",
	"mad": "mad",
	"lin": "ln",
	"mal": "ml",
	"mri": "mi",
	"lzh": "lzh",
	"lim": "li",
	"lfn": "lfn",
	"mhr": "mhr",
	"mar": "mr",
	"nld": "nl",
	"mlt": "mt",
	"mya": "my",
	"msa": "ms",
	"mon": "mn",
	"nau": "na",
	"mwl": "mwl",
	"mnw": "mnw",
	"mzn": "mzn",
	"nno": "nn",
	"nob": "nb",
	"nds": "nds",
	"myv": "myv",
	"nep": "ne",
	"nap": "nap",
	"mni": "mni",
	"new": "new",
	"nov": "nov",
	"mrj": "mrj",
	"nia": "nia",
	"pol": "pl",
	"por": "pt",
	"que": "qu",
	"nav": "nv",
	"oci": "oc",
	"pms": "pms",
	"pdc": "pdc",
	"pfl": "pfl",
	"nya": "ny",
	"ory": "or",
	"pap": "pap",
	"orm": "om",
	"pag": "pag",
	"nso": "nso",
	"oss": "os",
	"pcd": "pcd",
	"pam": "pam",
	"pih": "pih",
	"olo": "olo",
	"pli": "pi",
	"pnt": "pnt",
	"pan": "pa",
	"pus": "ps",
	"pnb": "pnb",
	"nqo": "nqo",
	"rus": "ru",
	"ron": "ro",
	"slk": "sk",
	"hbs": "sh",
	"san": "sa",
	"roh": "rm",
	"rom": "rmy",
	"sin": "si",
	"sco": "sco",
	"rue": "rue",
	"rup": "rup",
	"kin": "rw",
	"run": "rn",
	"skr": "skr",
	"sme": "se",
	"sag": "sg",
	"sat": "sat",
	"scn": "scn",
	"srd": "sc",
	"snd": "sd",
	"sah": "sah",
	"shn": "shn",
	"tam": "ta",
	"swa": "sw",
	"tel": "te",
	"sqi": "sq",
	"swe": "sv",
	"slv": "sl",
	"tgk": "tg",
	"srp": "sr",
	"som": "so",
	"stq": "stq",
	"szl": "szl",
	"smn": "smn",
	"srn": "srn",
	"sun": "su",
	"sna": "sn",
	"smo": "sm",
	"ssw": "ss",
	"tet": "tet",
	"tcy": "tcy",
	"sot": "st",
	"szy": "szy",
	"tur": "tr",
	"urd": "ur",
	"ukr": "uk",
	"tha": "th",
	"uzb": "uz",
	"tuk": "tk",
	"udm": "udm",
	"uig": "ug",
	"tat": "tt",
	"ven": "ve",
	"vec": "vec",
	"tgl": "tl",
	"ton": "to",
	"tyv": "tyv",
	"tir": "ti",
	"tah": "ty",
	"tsn": "tn",
	"tum": "tum",
	"tpi": "tpi",
	"tso": "ts",
	"twi": "tw",
	"zho": "zh",
	"yid": "yi",
	"vie": "vi",
	"tlh": "tlh",
	"zul": "zu",
	"rcf": "rcf",
	"zha": "za",
	"xho": "xh",
	"sma": "sma",
	"fit": "fit",
	"xmf": "xmf",
	"vep": "vep",
	"bho": "bh",
	"crh": "crh",
	"xal": "xal",
	"ndo": "ng",
	"wln": "wa",
	"wol": "wo",
	"war": "war",
	"wuu": "wuu",
	"yor": "yo",
	"enm": "enm",
	"vol": "vo",
	"sou": "sou",
	"vls": "vls",
	"zea": "zea",
	"moe": "moe",
	"aar": "aa",
	"anp": "anp",
	"dag": "dag",
	"cho": "cho",
	"brh": "brh",
	"shy": "shy",
	"her": "hz",
	"syc": "syc",
	"kjh": "kjh",
	"hmo": "ho",
	"arn": "arn",
	"niu": "niu",
	"nrf": "nrm",
	"tru": "tru",
	"tvl": "tvl",
	"tsg": "tsg",
	"rif": "rif",
	"chn": "chn",
	"dlm": "dlm",
	"kau": "kr",
	"lus": "lus",
	"mah": "mh",
	"yrk": "yrk",
	"quc": "quc",
	"rar": "rar",
	"ksw": "ksw",
	"sju": "sju",
	"adx": "adx",
	"sli": "sli",
	"gml": "gml",
	"mus": "mus",
	"pwn": "pwn",
	"tay": "tay",
	"trv": "trv",
	"jut": "jut",
	"kua": "kj",
	"rgn": "rgn",
	"hbo": "hbo",
	"abs": "abs",
	"wya": "wya",
	"mrh": "mrh",
	"rmc": "rmc",
	"nys": "nys",
	"aoc": "aoc",
	"tsk": "tsk",
	"bcc": "bcc",
	"crl": "crl",
	"luz": "luz",
	"lrc": "lrc",
	"tce": "tce",
	"cnr": "cnr",
	"nor": "no",
	"eya": "eya",
	"cal": "cal",
	"gil": "gil",
	"ccp": "ccp",
	"bfi": "bfi",
	"dua": "dua",
	"bbc": "bbc",
	"ctg": "ctg",
	"brx": "brx",
	"sjd": "sjd",
	"mfe": "mfe",
	"sid": "sid",
	"oji": "oj",
	"crs": "crs",
	"yap": "yap",
	"shi": "shi",
	"ydg": "ydg",
	"ryu": "ryu",
	"yai": "yai",
	"agq": "agq",
	"bss": "bss",
	"fro": "fro",
	"peo": "peo",
	"grc": "grc",
	"prg": "prg",
	"ses": "ses",
	"cop": "cop",
	"pko": "pko",
	"nan": "zh-min-nan",
	"pis": "pis",
	"nbl": "nr",
	"sje": "sje",
	"smj": "smj",
	"umu": "umu",
	"khg": "khg",
	"fkv": "fkv",
	"xnb": "xnb",
	"ovd": "ovd",
	"vmf": "vmf",
	"fos": "fos",
	"sdc": "sdc",
	"frm": "frm",
	"pdt": "pdt",
	"sty": "sty",
	"bto": "bto",
	"mul": "mul",
	"yue": "zh-yue",
	"abq": "abq",
	"tli": "tli",
	"bej": "bej",
	"bfq": "bfq",
	"hoc": "hoc",
	"lkt": "lkt",
	"krx": "krx",
	"nxm": "nxm",
	"hil": "hil",
	"sjt": "sjt",
	"qya": "qya",
	"wym": "wym",
	"bnn": "bnn",
	"hrx": "hrx",
	"xpu": "xpu",
	"tzl": "tzl",
	"lzz": "lzz",
	"akz": "akz",
	"kae": "kae",
	"pjt": "pjt",
	"bzs": "bzs",
	"kcg": "kcg",
	"tvn": "tvn",
	"pmy": "pmy",
	"kbg": "kbg",
	"rwr": "rwr",
	"ruq": "ruq",
	"mwv": "mwv",
	"ttm": "ttm",
	"esu": "esu",
	"koy": "koy",
	"vro": "fiu-vro",
	"ckt": "ckt",
	"gsg": "gsg",
	"hai": "hai",
	"krl": "krl",
	"kha": "kha",
	"mnc": "mnc",
	"wbl": "wbl",
	"tly": "tly",
	"yrl": "yrl",
	"otk": "otk",
	"cak": "cak",
	"ami": "ami",
	"goh": "goh",
	"gez": "gez",
	"kea": "kea",
	"uun": "uun",
	"ota": "ota",
	"dru": "dru",
	"tzm": "tzm",
	"aeb": "aeb",
	"sjn": "sjn",
	"lki": "lki",
	"arq": "arq",
	"bsk": "bsk",
	"bqi": "bqi",
	"mui": "mui",
	"ssf": "ssf",
	"sxr": "sxr",
	"ckv": "ckv",
	"byq": "byq",
	"tsu": "tsu",
	"xsy": "xsy",
	"uzs": "uzs",
	"sdh": "sdh",
	"rmf": "rmf",
	"cps": "cps",
	"frc": "frc",
	"guw": "guw",
	"kjp": "kjp",
	"kiu": "kiu"
	}
	if iso3 in iso3towdcode:
		return iso3towdcode[iso3]
	else:
		return None

# LWB ISO3 mapping

# select ?iso3 ?langqid where {?langqid ldp:P32 ?iso3 . }

with open(config.datafolder+'mappings/lwb_iso3.csv', 'r', encoding="utf-8") as csvfile:
	mappings = csv.DictReader(csvfile)
	iso3toQid = {}
	for mapping in mappings:
		iso3toQid[mapping['iso3']] = mapping['langqid'].replace("http://lexbib.elex.is/entity/","")

def getqidfromiso(iso3):
	global iso3toQid
	if iso3 in iso3toQid:
		return iso3toQid[iso3]
	else:
		return None

# ELEXIS languages
# This maps iso-639-3 (keys) to BabelNet language codes (values)

langcodemapping = {
"sqi":"SQ", # Albanian
"eus":"EU", # Basque
"bel":"BE", # Belarusian
"bul":"BG", # Bulgarian
"cat":"CA", # Catalan
"hrv":"HR", # Croatian
"ces":"CS", # Czech
"dan":"DA", # Danish
"nld":"NL", # Dutch
"eng":"EN", # English
"est":"ET", # Estonian
"fin":"FI", # Finnish
"fra":"FR", # French
"glg":"GL", # Galician
"deu":"DE", # German
"ell":"EL", # Greek
"heb":"HE", # Hebrew
"hun":"HU", # Hungarian
"isl":"IS", # Icelandic
"gle":"GA", # Irish
"ita":"IT", # Italian
"lav":"LV", # Latvian
"lit":"LT", # Lithuanian
"ltz":"LB", # Luxembourgish
"mkd":"MK", # Macedonian
"mlt":"MT", # Maltese
"cnr": None, # Montenegrin
"nob":"NO", # Norwegian Bokmal
"nno":"NN", # Nynorsk
"pol":"PL", # Polish
"por":"PT", # Portuguese
"ron":"RO", # Romanian
"rus":"RU", # Russian
"srp":"SR", # Serbian
"slk":"SK", # Slovak
"slv":"SL", # Slovene
"spa":"ES", # Spanish
"swe":"SV", # Swedish
"ukr":"UK", # Ukrainian
}

# Problematic cases (TBD):
# Montenegrin	cnr	- DOES NOT EXIST in babelnet -
# Norwegian (Mixed)	nor	- DOES NOT EXIST in babelnet -
# Norwegian "nor" indexed items should be interpreted as Norwegian Bokmal??

def getiso3lang(babellang):
	global langcodemapping
	for iso3lang in langcodemapping.keys():
		if langcodemapping[iso3lang] == babellang:
			return iso3lang
