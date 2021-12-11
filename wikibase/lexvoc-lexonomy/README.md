# elexifinder/wikibase/lexvoc-lexonomy

Scripts for conversion to and from Lexonomy XML format, and for extracting statistics about translation progress

Description of the translation workflow: https://lexbib.elex.is/wiki/LexVoc_Translation_on_Lexonomy

* buildlexonomy.py builds 38 bilingual Lexonomy XML dictionaries with LexVoc data.
* mergeddict3lwb.py collects translation equivalents from Lexonomy XML (merged on Lexonomy server), and writes them to LexBib wikibase.
* getdicts.py collects translation equivalents from Lexonomy XML (single dictionary).
* statsfrommergeddict.py and getstats.py produce data rows about translation progress
