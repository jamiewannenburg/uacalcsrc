from SPARQLWrapper import SPARQLWrapper, XML


sparql = SPARQLWrapper("http://dbpedia.org/sparql")
#"http://dbpedia.org/sparql"
#"https://query.wikidata.org/sparql"
#
#

sparql.setQuery("""
    ASK WHERE { 
        ?x ?x ?x
    }    
""")
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print results.toxml()