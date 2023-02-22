import os
from typing import Optional
from pydantic import BaseModel as BS
KAL = ['.git', '.gitignore', 'LICENSE', 'README.md', '.npmignore', 'package.json', 'composer.json', 
       'errors.json', 'schema.json', 'auth', 'downloadedGames', 'podcasts', 'streaming', 'tasks']
MORE_KAL = ['errors.json', 'objects.json', ]


def int_to_bool(i:int):
    return str(bool(i))


class Import(BS):
    file_path:str
    imports:list[str]


def get_type(str:str, item:Optional[dict]=None):
    match str:
        case 'string':
            return 'str'
        case 'integer':
            return 'int'
        case 'boolean':
            return 'bool'
        case 'array':
            if item == None: return 'Any'
            elif item.get('type') != None:
                if isinstance(item.get('type'), list):
                    i = []
                    for x in item.get('type'):
                        i.append(get_type(x))
                        return 'list['+'|'.join(i)+']'
                else:
                    return 'list['+get_type(item['type'])+']'
            elif item.get('$ref') != None:
                return 'str' #TODO
            else:
                return str
        case _:
            if isinstance(str, list):
                i = []
                for x in str:
                    i.append(get_type(x))
                    return 'list['+'|'.join(i)+']'
            else:
                return str


def get_file_path(file:str,json:str, kal=MORE_KAL) -> str:
    if file in kal:
        return file
    return 'vk_api_schema/' + file + '/'+ json


def gen_imports(i:dict):
    path = i['file_path']
    imports =', '.join(i['imports'])
    return 'from ..' + path + ' import ' + imports


def clean_dir(list:list, kal:list[str]=KAL) -> list[str]:
    for k in kal:
        list.remove(k)
    return list
    

def get_class_name(orig:str) -> str:
    name = orig.split('_')
    return name[0][0].upper() + name[0][1:] + ''.join(i.title() for i in name[1:])


def get_files(kal=KAL) -> list:
    work_dirs = os.listdir('vk_api_schema')
    return clean_dir(work_dirs, kal)


