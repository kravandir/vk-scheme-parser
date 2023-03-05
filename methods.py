import json
from base import Import, check_name, get_file_path, get_dirs, gen_import, get_type, int_to_bool
from pydantic import BaseModel as BM
from typing import Optional
from loguru import logger


class Parameter(BM):
    name:str
    type:Optional[str] = None
    default:Optional[str|int] = None

    
    def __init__(self, **data) -> None:
        super().__init__(**data)
        if self.type == 'bool':
            self.default = int_to_bool(self.default)
        self.name = check_name(self.name)


    def __str__(self):
        '''Получаем примерно такое:
            peremen:str=\"sosi\"'''
        string = f'{self.name}:{self.type}'
        if self.default != None: 
            if self.type == 'int' or self.type == 'bool':
                string = string+f'={self.default}'
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
    description:str|None = None

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.parameters.sort(key=sort_parameters)


    def __str__(self) -> str:
        '''TODO: ВОЗВРАЩАТЬ НЕ СЫРОЙ А ОБРАБОТАННЫЙ ОТВЕТ
        Получаем примерно такое:
            async def sosi(self, xyi:str, times:int=1):
                r = await self.method(\"xyi.sosi\", **locals())
                return r'''

        if self.parameters == []: params = ''
        else: params = ', ' + get_params(self.parameters)
        if self.description == None: description = ''
        else:
            self.description = self.description.replace('"', "'") # Заменяем вдойную кавычку на одинарну во избежание проблем
            description = f'\t\t"""{self.description}"""\n'
        str = '\tasync def ' + self.name + f'(self{params}):\n' + description + '\t\tr = await self.method('
        str = str + f'"{self.class_name}.{self.name}", **locals())\n\t\treturn r'
        return str


def get_parameter(dict:dict):
    name = dict['name']
    type = dict['type']
    type = get_type(type, dict.get('items'))
    default = dict.get('default')
    default = None if default == [] else default
    return Parameter(name=name,type=type,default=default)


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
    r = 'class ' + class_name + '(BaseMethod):\n'
    for method in schema['methods']:
        name = method['name'].split('.')[-1]
        description = method.get('description')
        params = []
        if method.get('parameters') != None:
            for i in method['parameters']:
                params.append(get_parameter(i))
        method = Method(name=name, parameters=params, class_name=class_name, description=description)
        r = r + method.__str__() + '\n\n'
    return r + '\n'


def main():
    depencies = [Import(file_path='base', imports=['BaseMethod'])]
    check = 1
    for f in get_dirs():
        file = get_file_path(f, 'methods.json')
        if file == None: continue
        text = gen_file(file)
        if check == 1:
            for d in depencies:
                check = 0
                text = gen_import(d) + '\n\n' + text
        with open('gen/methods.py', 'a') as file:
            file.write(text)
    
if __name__ == "__main__": main()
