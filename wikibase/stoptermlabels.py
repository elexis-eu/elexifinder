# list of term labels not to be considered (not to be sent to keyword_processor)
# These term labels are very ambiguous and bound to produce many false positives
# (at the moment, English only)
stoptermlabels = {}

stoptermlabels['eng'] = """
example
case
aspect
survey
voice
filter
article
entry
number
context
usage
translation
customization
innovative feature
several number
design
access
frequency
label
style
variant
size
register
illustration
device
interface
dual
modal
particle
clarity
progressive
note
person
degree
perfect
""".split('\n')

stoptermlabels['spa'] = """
ejemplo
caso
aspecto
persona
diverso
entrada
artículo
diferencia
acceso
contexto
grado
diseño
determinante
customization
filtro
futuro
figura
accidente
irreal
marca
recepción
modo
modal
negación
portada
partícula
pasado
perfecto
frase
presente
cita
base
raíz
radical
grafía
estilo
sentido
versión
atributo
número
negación
extraer
durativo
función
consulta
variedad
extensión
comparación
claridad
lucidez
nitidez
terminología
""".split('\n')
