# list of term labels not to be considered (not to be sent to keyword_processor)
# These term labels are very ambiguous and bound to produce many false positives
# (at the moment, English only)


stopterms = """example
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
person""".split('\n')


print('\nWill load stopterms:')
print(str(stopterms)+'\n')
