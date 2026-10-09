"""Public schemas contain allowed vocabulary, never hidden correct answers."""
from copy import deepcopy

CITATION = {'type':'object','properties':{
 'document_id':{'type':'string','minLength':1,'maxLength':100},
 'locator':{'type':'string','minLength':1,'maxLength':150},
 'quote':{'type':'string','minLength':20,'maxLength':12000}},
 'required':['document_id','locator','quote'],'additionalProperties':False}

def output_schema(task):
    props={}
    for f in task['findings']:
        props[f['id']]={'type':'object','properties':{
          'answer':deepcopy(f['answer_schema']),
          'support':{'type':'array','items':deepcopy(CITATION),'minItems':1,'maxItems':8,'uniqueItems':True},
          'counter':{'type':'array','items':deepcopy(CITATION),'maxItems':6,'uniqueItems':True}},
          'required':['answer','support','counter'],'additionalProperties':False}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object',
      'properties':{'findings':{'type':'object','properties':props,'required':list(props),'additionalProperties':False}},
      'required':['findings'],'additionalProperties':False}


def bounded(schema):
    """Bound variable-size values without encoding the correct answer."""
    schema=deepcopy(schema)
    if schema.get('type')=='string': schema.setdefault('maxLength',2048)
    if schema.get('type')=='array': schema.setdefault('maxItems',64)
    for key in ('properties','$defs'):
        if key in schema: schema[key]={k:bounded(v) for k,v in schema[key].items()}
    if isinstance(schema.get('items'),dict): schema['items']=bounded(schema['items'])
    for key in ('anyOf','oneOf','allOf'):
        if key in schema: schema[key]=[bounded(s) for s in schema[key]]
    return schema
