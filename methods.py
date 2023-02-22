import json
from base import Import, get_class_name, get_file_path, get_files, gen_imports, clean_dir, get_type, int_to_bool
from pydantic import BaseModel as BS
from typing import Literal, Optional
from loguru import logger

KAL = ['.git', '.gitignore', 'LICENSE', 'README.md', '.npmignore', 'package.json', 'composer.json', 
       'errors.json', 'schema.json', 'addresses', 'audio', 'base', 'callback', 'calls', 'client', 'comment', 
       'events', 'tasks', 'stickers', 'podcast', 'owner', 'oauth', 'link', 'base.py']
BAD_NAMES = ['global', 'extended']

class Parameter(BS):
    name:str
    type:Optional[str] = None
    default:Optional[str|int] = None

    
    def __init__(self, **data) -> None:
        super().__init__(**data)
        if self.type == 'bool':
            self.default = int_to_bool(self.default)
        if self.name in BAD_NAMES:
            self.name = '_'+self.name


    def __str__(self):
        string = f'{self.name}:{self.type}'
        if self.default != None: 
            if self.type == 'int' or self.type == 'bool':
                string = string+f'={self.default}'
            # elif type == 'str':
            else:
                string = string+f'="{self.default}"'
        return string


def sort_parameters(p:Parameter):
    return p.default != None


class Method(BS):
    name:str
    parameters:list[Parameter]
    class_name:str

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.parameters.sort(key=sort_parameters)


    def __str__(self) -> str:
        if self.parameters == []:
            params = ''
        else: 
            params = ', ' + get_params(self.parameters)
        str = '\tasync def ' + self.name + f'(self{params}):\n' + '\t\tr = await self.method('
        str = str + f'"{self.class_name}.{self.name}", **locals())\n\t\treturn r'
        return str


def get_parameter(dict:dict):
    name = dict['name']
    type = dict['type']
    type = get_type(type, dict.get('items'))
    default = dict.get('default')
    default = None if default == [] else default
    return Parameter(name=name,type=type,default=default)


def get_params(params:list[Parameter], need_typing:bool=True):
    p = []
    for param in params:
        string = param.__str__()
        p.append(string)
    r = ', '.join(p)
    return r


@logger.catch
def work(file_name:str):
    with open(file=file_name) as f:
        scheme = json.load(f)
    
    class_name = file_name.split('/')[1].capitalize()
    r = 'class ' + class_name + '(BaseMethod):\n'
    for method in scheme['methods']:
        name = method['name'].split('.')[-1]
        params = []
        if method.get('parameters') != None:
            for i in method['parameters']:
                params.append(get_parameter(i))
        method = Method(name=name, parameters=params, class_name=class_name)
        r = r + method.__str__() + '\n\n'
        # print(method.__str__(), '\n\t\t\n\n')
    return r


depencies = [Import(file_path='base', imports=['BaseMethod'])]
files = []
for f in get_files(KAL):
    file = get_file_path(f, 'methods.json')
    text = work(file)
    for d in depencies:
        text = gen_imports(d.__dict__) + '\n\n' + text
    with open(file.replace('.json', '.py'), 'w') as file:
        file.write(text)
    
