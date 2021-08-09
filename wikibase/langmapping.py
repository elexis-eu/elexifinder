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

def getqidfromiso(iso3):
	iso3toQid = {
	"hsb":"Q301",
	"hak":"Q302",
	"gag":"Q303",
	"gan":"Q304",
	"haw":"Q305",
	"glk":"Q306",
	"got":"Q307",
	"grn":"Q308",
	"hif":"Q309",
	"hau":"Q310",
	"gsw":"Q311",
	"gcr":"Q312",
	"gor":"Q313",
	"gom":"Q314",
	"akl":"Q315",
	"zun":"Q316",
	"sms":"Q317",
	"mic":"Q318",
	"ase":"Q319",
	"clc":"Q320",
	"vot":"Q321",
	"cbk":"Q322",
	"gaa":"Q323",
	"fon":"Q324",
	"loz":"Q325",
	"liv":"Q326",
	"krj":"Q327",
	"nog":"Q328",
	"non":"Q329",
	"ett":"Q330",
	"kri":"Q331",
	"kum":"Q332",
	"nui":"Q333",
	"sei":"Q334",
	"wal":"Q335",
	"wls":"Q336",
	"cpx":"Q337",
	"aln":"Q339",
	"prs":"Q338",
	"sgs":"Q340",
	"nod":"Q341",
	"lag":"Q342",
	"bzg":"Q343",
	"pyu":"Q344",
	"gmh":"Q345",
	"guc":"Q346",
	"khw":"Q347",
	"nsk":"Q348",
	"tvx":"Q350",
	"ppu":"Q351",
	"ood":"Q352",
	"osa":"Q353",
	"bdr":"Q355",
	"btm":"Q357",
	"gcf":"Q359",
	"srq":"Q362",
	"rkt":"Q363",
	"sjm":"Q365",
	"ins":"Q367",
	"rki":"Q369",
	"fuf":"Q371",
	"jax":"Q373",
	"dtp":"Q376",
	"zgh":"Q378",
	"bgn":"Q380",
	"yav":"Q382",
	"und":"Q384",
	"zxx":"Q386",
	"ruq":"Q388",
	"mwv":"Q390",
	"ttm":"Q392",
	"esu":"Q394",
	"koy":"Q395",
	"vro":"Q397",
	"ckt":"Q399",
	"gsg":"Q401",
	"hai":"Q403",
	"krl":"Q405",
	"kha":"Q407",
	"mnc":"Q409",
	"wbl":"Q411",
	"tly":"Q413",
	"otk":"Q417",
	"yrl":"Q415",
	"cak":"Q419",
	"ami":"Q421",
	"goh":"Q423",
	"gez":"Q425",
	"kea":"Q427",
	"uun":"Q429",
	"ota":"Q431",
	"dru":"Q433",
	"tzm":"Q435",
	"aeb":"Q437",
	"sjn":"Q439",
	"lki":"Q441",
	"arq":"Q443",
	"bsk":"Q445",
	"bqi":"Q446",
	"mui":"Q449",
	"eng":"Q201",
	"afr":"Q208",
	"dan":"Q203",
	"deu":"Q202",
	"fra":"Q206",
	"nor":"Q207",
	"slv":"Q209",
	"spa":"Q204",
	"swe":"Q205",
	"ita":"Q210",
	"nno":"Q211",
	"por":"Q212",
	"rus":"Q213",
	"nld":"Q215",
	"nob":"Q214",
	"cat":"Q217",
	"ell":"Q216",
	"eus":"Q218",
	"sme":"Q219",
	"fry":"Q220",
	"bel":"Q222",
	"fin":"Q221",
	"hrv":"Q223",
	"epo":"Q224",
	"ekk":"Q225",
	"est":"Q226",
	"fas":"Q227",
	"frp":"Q228",
	"fao":"Q229",
	"frr":"Q230",
	"ext":"Q231",
	"fij":"Q232",
	"fur":"Q233",
	"ful":"Q234",
	"ces":"Q235",
	"cym":"Q236",
	"zza":"Q237",
	"dsb":"Q238",
	"ewe":"Q239",
	"div":"Q240",
	"dzo":"Q241",
	"cos":"Q242",
	"chu":"Q243",
	"chu":"Q247",
	"chv":"Q244",
	"cre":"Q245",
	"csb":"Q246",
	"ckb":"Q248",
	"din":"Q249",
	"egl":"Q250",
	"dty":"Q251",
	"bul":"Q252",
	"bos":"Q253",
	"ben":"Q254",
	"bre":"Q255",
	"bua":"Q256",
	"bxr":"Q269",
	"bjn":"Q257",
	"bug":"Q258",
	"ceb":"Q259",
	"bam":"Q260",
	"cha":"Q261",
	"chy":"Q262",
	"bcl":"Q263",
	"che":"Q264",
	"chr":"Q265",
	"bis":"Q266",
	"cdo":"Q267",
	"aym":"Q270",
	"bpy":"Q268",
	"abk":"Q271",
	"arg":"Q272",
	"aze":"Q273",
	"bak":"Q274",
	"ara":"Q275",
	"ace":"Q276",
	"ady":"Q277",
	"aka":"Q278",
	"amh":"Q279",
	"arc":"Q280",
	"asm":"Q281",
	"ast":"Q282",
	"bar":"Q283",
	"ava":"Q284",
	"awa":"Q285",
	"arz":"Q286",
	"ban":"Q287",
	"ang":"Q288",
	"ary":"Q289",
	"atj":"Q290",
	"avk":"Q291",
	"alt":"Q292",
	"azb":"Q293",
	"hin":"Q294",
	"guj":"Q295",
	"gle":"Q296",
	"heb":"Q297",
	"glg":"Q298",
	"gla":"Q299",
	"glv":"Q300",
	"ssf":"Q451",
	"sxr":"Q452",
	"ckv":"Q454",
	"byq":"Q456",
	"tsu":"Q458",
	"xsy":"Q460",
	"uzs":"Q462",
	"sdh":"Q464",
	"rmf":"Q466",
	"cps":"Q468",
	"frc":"Q470",
	"guw":"Q472",
	"kjp":"Q474",
	"kiu":"Q476",
	"yue":"Q478",
	"yue":"Q523",
	"abq":"Q480",
	"tli":"Q482",
	"bej":"Q484",
	"bfq":"Q486",
	"hoc":"Q488",
	"lkt":"Q490",
	"krx":"Q492",
	"nxm":"Q494",
	"hil":"Q495",
	"sjt":"Q497",
	"qya":"Q499",
	"bnn":"Q503",
	"wym":"Q501",
	"hrx":"Q505",
	"xpu":"Q507",
	"tzl":"Q509",
	"lzz":"Q511",
	"akz":"Q513",
	"kae":"Q515",
	"pjt":"Q517",
	"bzs":"Q519",
	"kcg":"Q521",
	"tvn":"Q525",
	"pmy":"Q527",
	"kbg":"Q529",
	"rwr":"Q531",
	"isl":"Q533",
	"jpn":"Q535",
	"hye":"Q537",
	"hun":"Q539",
	"ind":"Q541",
	"iku":"Q545",
	"ipk":"Q543",
	"hat":"Q547",
	"inh":"Q549",
	"ibo":"Q551",
	"iii":"Q553",
	"ido":"Q555",
	"ile":"Q557",
	"ina":"Q559",
	"ilo":"Q561",
	"jam":"Q563",
	"jbo":"Q565",
	"hyw":"Q567",
	"lat":"Q569",
	"ksh":"Q571",
	"kat":"Q573",
	"kor":"Q575",
	"khm":"Q577",
	"kaz":"Q579",
	"kir":"Q581",
	"cor":"Q583",
	"kal":"Q585",
	"jav":"Q590",
	"kaa":"Q589",
	"kbd":"Q587",
	"kas":"Q592",
	"kik":"Q594",
	"kan":"Q596",
	"kon":"Q598",
	"krc":"Q600",
	"kbp":"Q602",
	"kab":"Q604",
	"kom":"Q606",
	"kmr":"Q608",
	"kur":"Q610",
	"koi":"Q611",
	"mlg":"Q613",
	"ltz":"Q615",
	"lav":"Q617",
	"lvs":"Q620",
	"lit":"Q622",
	"lao":"Q624",
	"mkd":"Q626",
	"min":"Q628",
	"lez":"Q632",
	"mdf":"Q630",
	"lug":"Q634",
	"lmo":"Q636",
	"lij":"Q638",
	"mai":"Q640",
	"lad":"Q642",
	"lld":"Q644",
	"lbe":"Q646",
	"ltg":"Q648",
	"mad":"Q650",
	"lin":"Q652",
	"mal":"Q654",
	"mri":"Q656",
	"lzh":"Q658",
	"lim":"Q660",
	"lfn":"Q662",
	"mhr":"Q664",
	"mar":"Q666",
	"mlt":"Q668",
	"mya":"Q670",
	"msa":"Q672",
	"mon":"Q674",
	"nau":"Q676",
	"mwl":"Q678",
	"mnw":"Q680",
	"mzn":"Q682",
	"nds":"Q684",
	"myv":"Q686",
	"nep":"Q688",
	"nap":"Q690",
	"mni":"Q692",
	"new":"Q694",
	"nov":"Q696",
	"mrj":"Q699",
	"nia":"Q701",
	"pol":"Q703",
	"que":"Q705",
	"nav":"Q707",
	"oci":"Q709",
	"pms":"Q711",
	"pdc":"Q712",
	"pfl":"Q714",
	"nya":"Q716",
	"ory":"Q718",
	"pap":"Q720",
	"orm":"Q722",
	"pag":"Q724",
	"nso":"Q726",
	"oss":"Q728",
	"pcd":"Q731",
	"pam":"Q733",
	"pih":"Q734",
	"olo":"Q736",
	"pli":"Q738",
	"pnt":"Q740",
	"pan":"Q743",
	"pus":"Q745",
	"pnb":"Q747",
	"nqo":"Q749",
	"ron":"Q751",
	"slk":"Q753",
	"hbs":"Q755",
	"roh":"Q758",
	"san":"Q757",
	"rom":"Q760",
	"sin":"Q762",
	"sco":"Q765",
	"rue":"Q766",
	"rup":"Q768",
	"kin":"Q770",
	"run":"Q772",
	"skr":"Q774",
	"sag":"Q776",
	"sat":"Q778",
	"scn":"Q780",
	"srd":"Q782",
	"snd":"Q784",
	"sah":"Q786",
	"shn":"Q788",
	"tam":"Q790",
	"swa":"Q792",
	"tel":"Q794",
	"sqi":"Q796",
	"tgk":"Q798",
	"som":"Q802",
	"srp":"Q800",
	"stq":"Q804",
	"szl":"Q806",
	"smn":"Q808",
	"srn":"Q811",
	"sun":"Q812",
	"sna":"Q814",
	"smo":"Q816",
	"ssw":"Q818",
	"tet":"Q820",
	"tcy":"Q822",
	"sot":"Q824",
	"szy":"Q826",
	"tur":"Q828",
	"urd":"Q830",
	"ukr":"Q832",
	"tha":"Q834",
	"uzb":"Q836",
	"tuk":"Q838",
	"udm":"Q840",
	"uig":"Q842",
	"tat":"Q844",
	"ven":"Q846",
	"vec":"Q848",
	"tgl":"Q850",
	"ton":"Q852",
	"tyv":"Q854",
	"tir":"Q856",
	"tah":"Q858",
	"tsn":"Q860",
	"tum":"Q862",
	"tpi":"Q863",
	"tso":"Q866",
	"twi":"Q868",
	"zho":"Q870",
	"yid":"Q872",
	"vie":"Q873",
	"tlh":"Q875",
	"zul":"Q877",
	"rcf":"Q879",
	"zha":"Q881",
	"xho":"Q883",
	"sma":"Q886",
	"fit":"Q888",
	"xmf":"Q890",
	"vep":"Q892",
	"bho":"Q894",
	"crh":"Q895",
	"xal":"Q897",
	"ndo":"Q899",
	"wln":"Q901",
	"wol":"Q903",
	"war":"Q905",
	"wuu":"Q907",
	"yor":"Q909",
	"enm":"Q911",
	"cnr":"Q913",
	"eya":"Q916",
	"cal":"Q918",
	"gil":"Q920",
	"ccp":"Q922",
	"bfi":"Q924",
	"dua":"Q926",
	"bbc":"Q928",
	"brx":"Q932",
	"ctg":"Q930",
	"sjd":"Q934",
	"mfe":"Q936",
	"sid":"Q938",
	"oji":"Q940",
	"crs":"Q942",
	"yap":"Q944",
	"shi":"Q946",
	"ydg":"Q948",
	"ryu":"Q950",
	"yai":"Q952",
	"agq":"Q954",
	"bss":"Q956",
	"fro":"Q958",
	"peo":"Q960",
	"grc":"Q962",
	"prg":"Q963",
	"ses":"Q965",
	"cop":"Q968",
	"pko":"Q970",
	"nan":"Q972",
	"pis":"Q974",
	"nbl":"Q976",
	"sje":"Q978",
	"smj":"Q980",
	"umu":"Q982",
	"khg":"Q984",
	"fkv":"Q986",
	"xnb":"Q988",
	"ovd":"Q989",
	"vmf":"Q992",
	"fos":"Q994",
	"sdc":"Q996",
	"frm":"Q998",
	"pdt":"Q1000",
	"sty":"Q1002",
	"bto":"Q1004",
	"mul":"Q1006",
	"vol":"Q1008",
	"sou":"Q1010",
	"vls":"Q1012",
	"zea":"Q1014",
	"aar":"Q1018",
	"moe":"Q1016",
	"anp":"Q1020",
	"dag":"Q1022",
	"cho":"Q1024",
	"brh":"Q1026",
	"shy":"Q1028",
	"her":"Q1030",
	"syc":"Q1032",
	"kjh":"Q1034",
	"hmo":"Q1036",
	"arn":"Q1038",
	"niu":"Q1040",
	"nrf":"Q1042",
	"tru":"Q1044",
	"tvl":"Q1046",
	"tsg":"Q1048",
	"rif":"Q1050",
	"chn":"Q1052",
	"dlm":"Q1054",
	"kau":"Q1056",
	"lus":"Q1058",
	"mah":"Q1060",
	"yrk":"Q1062",
	"quc":"Q1064",
	"rar":"Q1066",
	"ksw":"Q1068",
	"sju":"Q1070",
	"adx":"Q1072",
	"sli":"Q1073",
	"gml":"Q1075",
	"mus":"Q1077",
	"pwn":"Q1080",
	"tay":"Q1082",
	"trv":"Q1084",
	"jut":"Q1086",
	"kua":"Q1088",
	"rgn":"Q1090",
	"hbo":"Q1092",
	"abs":"Q1094",
	"wya":"Q1096",
	"mrh":"Q1098",
	"nys":"Q1102",
	"rmc":"Q1100",
	"aoc":"Q1104",
	"tsk":"Q1106",
	"bcc":"Q1108",
	"crl":"Q1110",
	"luz":"Q1112",
	"lrc":"Q1114",
	"tce":"Q1116"
	}
	if iso3 in iso3toQid:
		return iso3toQid[iso3]
	else:
		return None
