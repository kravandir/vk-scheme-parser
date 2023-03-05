import json, loguru
from pydantic import BaseModel as BM
from base import get_class_name, Import, get_dirs, get_file_path, gen_import, get_imports, get_ref, get_type

DIDNT_READ_LOL =  ['required', 'additionalProperties', 'description']
depencies = []

class Propetry(BM):
    name:str
    type:str
    
    def __str__(self) -> str:
        # if self.type[0].istitle(): self.type = "'"+self.type+"'"
        return f'{self.name}:{self.type}\n'


class Response(BM):
    name:str
    properties:list[Propetry]|str

    def __str__(self) -> str:
        if isinstance(self.properties, str):
            return self.name + ' = ' + self.properties + '\n\n'
        r = 'class ' + self.name + '(BM):\n'
        for property in self.properties:
            r = r + '\t' + property.__str__()
        return r + '\n'


class Responses(BM):
    rspns:list[Response]

    def __str__(self) -> str:
        r = ''
        for i in self.rspns:
            r = r + i.__str__()
        return r + '\n'


def get_depencies(r:Responses):
    depencies = []
    tmp = []
    for i in r.rspns:
        if isinstance(i.properties, str):
            if i.properties.startswith('list'):
                type = i.properties.split('[')[1][:-1] # ]
            else: type = i.properties
            if type[0].istitle():
                tmp.append(type)
                continue

        for property in i.properties:
            if isinstance(property, Propetry):
                if property.type.startswith('list'):
                    type = property.type.split('[')[1][:-1] # ]
                else: type = property.type
            else:
                type = property
            if type[0].istitle():
                tmp.append(type)
        depencies = list(set(depencies)) + list(set(tmp))
        tmp = []
    return depencies


def gen_file(file_name:str) -> str:
    global depencies
    with open(file_name) as f:
        schema = json.load(f)

    r = []
    for response_name, responses in schema['definitions'].items():
        response = responses['properties']['response']
        if response.get('type') == 'object':
            response = responses['properties']
        response_name = get_class_name(response_name)
        # мнн лкнь делать для этой хуйни чето отдельное
        if response_name == 'MessagesDeleteResponse':
            r.append(Response(name=response_name, properties='bool'))
            continue
        
        if response.get('$ref') != None:
            r.append(Response(name=response_name,
                             properties=get_class_name(get_ref(response['$ref']))))
        elif response.get('response') != None:
            response = response['response']['properties']
            properties = []
            for property_name, property in response.items():
                type = get_type(
                    property['type'] if property.get('type') != None else get_class_name(
                        get_ref(property['$ref'])), property.get('items'))
                properties.append(Propetry(name=property_name,type=type))
            r.append(Response(name=response_name, properties=properties))
        else: 
            type = get_type(
                    response['type'] if response.get('type') != None else get_class_name(
                        get_ref(response['$ref'])), response.get('items'))
            r.append(Response(name=response_name,
                               properties=get_type(
                                   response['type'] if response.get('type') != None else get_ref(response['$ref']),
                                   response.get('items'))
                               ))
        # print(response_name)
        # print(response)
        # print()
    depencies = depencies + get_depencies(Responses(rspns=r))
    return Responses(rspns=r).__str__()


@loguru.logger.catch
def main():
    global depencies
    check = 1
    text = ''
    for f in get_dirs():
        file = get_file_path(f, 'responses.json')
        if file == None: continue
        text = text + gen_file(file)
        # if check == 1:
        #     for d in depencies:
        #         check = 0
        #         text = gen_import(d) + '\n\n' + text
    depencies = list(set(depencies))
    imports = Import(file_path='objects', imports=depencies).__str__() + 'from base import BM\n'
    text = imports + '\n' + text
    
    with open('gen/responses.py', 'w') as file:
        file.write(text)


if __name__ == "__main__": main()
