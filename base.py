import os, keyword
from typing import Optional
from pydantic import BaseModel as BM
KAL = ['.git', 'auth', 'downloadedGames', 'podcasts', 'streaming', 'tasks']

class Import(BM):
    file_path:str
    imports:list[str]


def int_to_bool(i):
    '''Из нуля получаем строку False'''
    return str(bool(i))


def get_type(str:str|list|None, item:Optional[dict]|None=None) -> str:
    match str:
        case 'string':
            return 'str'
        case 'integer'|'number':
            return 'int'
        case 'boolean':
            return 'bool'
        case 'array':
            if item == None: return 'list'
            elif item.get('type') != None:
                if isinstance(item.get('type'), list):
                    i = []
                    for x in item['type']:
                        i.append(get_type(x))
                    return 'list['+'|'.join(i)+']'
                else:
                    return 'list['+get_type(item['type'])+']'
            elif item.get('$ref') != None:
                return 'list['+get_class_name(item['$ref'].split('/')[-1])+']'
            else:
                return 'list'
        case None:
            if item != None:
                if item.get('$ref') != None:
                    return get_class_name(item['$ref'].split('/')[-1])
                else: return 'Any'
            else: return 'Any'

        case _:
            if isinstance(str, list):
                i = []
                for x in str:
                    i.append(get_type(x))
                return 'list['+'|'.join(i)+']'
            else:
                return str


def gen_enum(name:str, enum:list[str],enum_names:list[str]|None=None) -> str:
    if enum_names == None: enum_names = enum
    r = 'class ' + name + '(Enum):\n'
    for x, y in zip(enum_names, enum):
        x = check_name(str(x))
        if not isinstance(y, int) : y = f'"{y}"'
        r = r + f'\t{x.upper()} = {y}\n'
    return r + '\n'


def get_file_path(file:str,json:str) -> str|None:
    '''Получаем путь к файлу, в случае ненахода None'''
    if os.path.exists(file+'/'+json):
        return file + '/'+ json
    else: return None


def gen_import(a:Import):
    path = a.file_path
    imports =', '.join(a.imports)
    return 'from ' + path + ' import ' + imports


def clean_dir(list:list) -> list[str]:
    '''Чистим от НЕ директорий'''
    for i in list[:]:
        if not os.path.isdir(i) or i == '.git':
            list.remove(i)
    return list
    

def get_class_name(orig:str) -> str:
    '''base_shit -> BaseShit'''
    name = orig.split('_')
    return name[0][0].upper() + name[0][1:] + ''.join(i.title() for i in name[1:])


def get_dirs() -> list:
    '''Получаем директории'''
    work_dirs = os.listdir('vk_api_schema')
    for i in work_dirs[:]:
        work_dirs.remove(i)
        work_dirs.append('vk_api_schema/'+i)
    return clean_dir(work_dirs)


def check_name(name:str) -> str:
    if keyword.iskeyword(name):  name = '_'+name
    if name[0].isdigit(): name = '_'+name
    name = name.replace(' ', '_')
    return name
