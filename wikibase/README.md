# elexifinder/wikibase

Scripts for bibliodata migration from Zotero LexBib collection to LexBib Wikibase, and for migration to Elexifinder JSON format (needed for eventregistry service)

LexBib Zotero Group: https://www.zotero.org/groups/lexbib

LexBib Wikibase : https://lexbib.elex.is

Elexifinder user interface: http://finder.elex.is

* lwb.py contains functions for reading and writing to LexBib Wikibase.
* config.py contains basic configurations for interacting with LexBib Wikibase and LexBib Zotero.
* nlp.py contains functions for lemmatizing and cleaning (English) text, and for extracting text bodies from GROBID TEI fulltext representations.
* langmapping.py contains mappings between ISO 639-1, ISO 639-2, wikilanguage codes, and BabelNet language codes.
* buildbodytxt.py builds a JSON object containing full text data.
* buildtermindex.py finds LexVoc terms in full text bodies.
* zotexport.py processes a Zotero JSON export, and uploads statements regarding container items (BibCollection items).
* bibimport.py uploads statements describing BibItems to LexBib Wikibase.
