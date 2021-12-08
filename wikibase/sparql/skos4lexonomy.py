# This query defines those LexVoc terms that will be exported to Lexonomy for translation.

query = """


# get SKOS concepts valid for translation in Lexonomy:
#
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <http://lexbib.elex.is/prop/reference/>
PREFIX lno: <http://lexbib.elex.is/prop/novalue/>

select distinct (strafter(str(?concepturi),"http://lexbib.elex.is/entity/") as ?term) ?termlabel
# (concat('[ ',(group_concat(distinct concat('{"',lang(?preflabel),'": "',?preflabel,'"}');SEPARATOR=", ")),' ]') as ?langpreflabels)
# (concat('[ ',(group_concat(distinct concat('{"',lang(?altlabel),'": "',?altlabel,'"}');SEPARATOR=", ")),' ]') as ?langaltlabels)

(sample(?hits) as ?count)

 where {
  ?facet ldp:P131 lwb:Q1 .
  ?concepturi ldp:P5 lwb:Q7 .
 filter not exists { ?concepturi ldp:P149 ?inferslabel . } # exclude those that infer labels from another concept node
   { ?concepturi ldp:P72* ?facet .} # present in narrower-broader-tree with "Lexicography" as root node
   UNION
   {?concepturi ldp:P76|ldp:P77 ?closeMatch. ?closeMatch ldp:P72* ?facet . } # includes closeMatch or related items without own broader-rels

   ?concepturi rdfs:label ?termlabel . FILTER (lang(?termlabel)="en")

   ?concepturi lp:P109 [ lps:P109 ?hits ].
                #  lpq:P84 ?source . filter(?source="LexBib Nov 2021 stopterms").

 #  ?concepturi ldp:P129 ?preflabel.

 #  OPTIONAL { ?concepturi ldp:P130 ?altlabel. }

 #  OPTIONAL { ?Term ldp:P2 ?wd.}


} GROUP BY ?concepturi ?termlabel # ?langpreflabels ?langaltlabels
?count
ORDER BY LCASE(?termlabel)

"""
