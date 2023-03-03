import json, loguru
from pydantic import BaseModel as BM
from base import Optional, get_class_name, Import, get_dirs, get_file_path, gen_import, get_ref, get_type

DIDNT_READ_LOL =  ['required', 'additionalProperties', 'description']

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
        r = 'class '
        if isinstance(self.properties, str):
            return r + self.name + '(' + self.properties + '):\n\tpass\n\n'
        r = r + self.name + '(BS):\n'
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



def gen_file(file_name:str) -> str:
    with open(file_name) as f:
        schema = json.load(f)

    r = ''
    for response_name, responses in schema['definitions'].items():
        response = responses['properties']['response']
        if response.get('type') == 'object':
            response = responses['properties']
        response_name = get_class_name(response_name)
        # checking for ONLY $REF
        if response.get('$ref') != None:
            r = r + Response(name=response_name,
                             properties=get_class_name(get_ref(response['$ref']))).__str__()
        elif response.get('response') != None:
            response = response['response']['properties']
            properties = []
            for property_name, property in response.items():
                properties.append(Propetry(name=property_name,type=get_type(
                    property['type'] if property.get('type') != None else get_ref(property['$ref']))
                                           ))
            r = r + Response(name=response_name, properties=properties).__str__()
        else: r = r + Response(name=response_name,
                               properties=get_type(
                                   response['type'] if response.get('type') != None else get_ref(response['$ref'])
                                   )
                               ).__str__()
        # print(response_name)
        # print(response)
        # print()
    print(r)
    return ''


@loguru.logger.catch
def main():
    depencies = [Import(file_path='base', imports=['BaseMethod'])]
    check = 1
    text = ''
    for f in get_dirs():
        file = get_file_path(f, 'responses.json')
        if file == None: continue
        text = text + gen_file(file)
        if check == 1:
            for d in depencies:
                check = 0
                text = gen_import(d) + '\n\n' + text
#       with open(file.replace('.json', '.py'), 'w') as file:
    with open('gen/responses.py', 'a') as file:
        file.write(text)
    
if __name__ == "__main__": main()
