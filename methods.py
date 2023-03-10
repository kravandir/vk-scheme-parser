import json
from base import Import, check_name, get_class_name, get_file_path, get_dirs, gen_import, get_ref, get_type, int_to_bool
from pydantic import BaseModel as BM
from typing import Optional
from loguru import logger


class Parameter(BM):
    name:str
    type:Optional[str] = None
    default:Optional[str|int] = None
    required:bool = False
    
    def __init__(self, **data) -> None:
        super().__init__(**data)
        if self.type == 'bool':
            self.default = int_to_bool(self.default)
        self.name = check_name(self.name)
        if self.required == True:
            self.type = 'Optional[{}]'.format(self.type)
            self.default = 'None'


    def __str__(self):
        '''Получаем примерно такое:
            peremen:str=\"sosi\"'''
        string = f'{self.name}:{self.type}'
        if self.default != None: 
            if 'int' in str(self.type) or 'bool' in str(self.type):
                string = string+f'={self.default}'
            elif 'Optional' in str(self.type) and self.default == 'None':
                string = string + '=None'
            else:
                string = string+f'="{self.default}"'
        return string


def sort_parameters(p:Parameter):
    '''Функция для list.sort
    Сортирует по наличию дефолтного значения'''
    return p.default != None


class Method(BM):
    name:str
    parameters:list[Parameter]
    class_name:str
    response:list[str]
    description:str|None = None

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.parameters.sort(key=sort_parameters)

    def get_response(self):
        if len(self.response) == 1:
            return f'try: return {self.response[0]}(**r)\n\t\texcept: return r'
        elif len(self.response) > 1:
            response = self.response.__str__().replace("\'", "")
            return f'for i in {response}:\n\t\t\ttry: return i(**r)\n\t\t\texcept: return r'
        else: return 'return r'

    def __str__(self) -> str:
        if self.parameters == []: params = ''
        else: params = ', ' + get_params(self.parameters)
        if self.description == None: description = ''
        else:
            self.description = self.description.replace('"', "'") # Заменяем вдойную кавычку на одинарну во избежание проблем
            description = f'\t\t"""{self.description}"""\n'
        str = (
                '\tasync def ' + self.name + f'(self{params}):\n' + description +
                '\t\targs = locals()\n' +
                '\t\tfor i in (\'self\', \'__class__\'): args.pop(i)\n' +
                '\t\tr = await super().method('+ f'"{self.class_name}.{self.name}", **args)\n\t\t' +
                self.get_response() + '\n\n'
                )
        return str


def get_parameter(dict:dict):
    name = check_name(dict['name'])
    type = dict['type']
    type = get_type(type, dict.get('items'))
    default = dict.get('default')
    default = None if default == [] else default
    required = False if dict.get('required') == 'false' else True
    return Parameter(name=name,type=type,default=default, required=required)


def get_params(params:list[Parameter]):
    p = []
    for param in params:
        string = param.__str__()
        p.append(string)
    r = ', '.join(p)
    return r


@logger.catch
def gen_file(file_name:str):
    '''Тут пиздец'''
    with open(file=file_name) as f:
        schema = json.load(f)
    
    class_name = file_name.split('/')[1].capitalize()
    r = ('class ' + class_name + '(BaseMethod):\n' +
         '\tdef __init__(self, vk):\n'+
         '\t\tsuper().__init__(vk)\n\n')
    for method in schema['methods']:
        name = check_name(method['name'].split('.')[-1])
        description = method.get('description')
        params = []
        if method.get('parameters') != None:
            for i in method['parameters']:
                params.append(get_parameter(i))
        responses = method['responses']
        response = []
        for resp in responses.values():
            response.append(get_class_name(get_ref(resp['$ref'])))
        method = Method(name=name, parameters=params, class_name=class_name, description=description, response=response)
        r = r + method.__str__() + '\n'
    return r + '\n'


def main():
    depencies = 'from .base import BaseMethod\nfrom .objects import *\nfrom .responses import *\n\n'
    text = depencies
    for f in get_dirs():
        file = get_file_path(f, 'methods.json')
        if file == None: continue
        text = text + gen_file(file)

    with open('gen/methods.py', 'w') as file:
        file.write(text)
    
if __name__ == "__main__": main()
