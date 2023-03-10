import json
from base import check_name, gen_enum, get_class_name, get_type, Import, get_dirs, get_file_path, gen_import
from pydantic import BaseModel as BM


class Property(BM):
    name:str
    type:str

    def __str__(self) -> str:
        if self.type[0].istitle(): self.type = f'"{self.type}"'
        return f'{self.name}:Optional[{self.type}] = None'


class Object(BM):
    name:str
    properties:list[Property] = []
    depencies:list[str] = []

    def __str__(self) -> str:
        r = 'class '+self.name+'(BM):\n'
        if self.depencies != [] :
            r = r.replace('BM', ', '.join(self.depencies))
        if self.properties == []:
            r = r + '\tpass'
        else:
            for p in self.properties:
                r = r + '\t'+p.__str__()+'\n'
        return r + '\n'


class Objects(BM):
    objects:list[Object]

    def __str__(self) -> str:
        r = ''
        for i in self.objects:
            if i.depencies != []:
                global some_shit
                some_shit.append(i)
                continue
            r = r + i.__str__() + '\n'
        return r


def gen_file(file_name:str):
    global x
    with open(file_name) as f:
        schema = json.load(f)

    objects = []
    r = ''
    for object_name, object in schema['definitions'].items():
        properties = []
        depencies = []
        object_name = get_class_name(object_name)
        if object.get('enum') != None:
            r = r+gen_enum(object_name, object['enum'], object.get('enumNames'))
            continue
        elif object.get('type') != 'object' and object.get('type') != None:
            objects.append(Property(name=object_name, type=get_type(object['type'])))
            continue
        elif object.get('$ref') != None and object.get('type') == None:
            type = get_class_name(object['$ref'].split('/')[-1])
            objects.append(Property(name=object_name, type=type))
            continue
        elif object.get('allOf') != None:
            has_properties = False
            for i in object['allOf']:
                if i.get('$ref') != None:
                    depencies.append(get_class_name(i['$ref'].split('s/')[-1]))
                else: 
                    has_properties = True
                    object = i
            if not has_properties: 
                x = x + Object(name=object_name, properties=[], depencies=depencies).__str__()
                continue
            elif object.get('properties') != None:
                for property_name, property in object['properties'].items():
                    property_type = get_type(property.get('type'), property)
                    properties.append(Property(name=check_name(property_name), type=property_type))    
                x = x + Object(name=object_name, properties=properties, depencies=depencies).__str__()
                continue
            else: print(object_name,1)
        elif object.get('$ref') != None:
            depencies.append(get_class_name(object['$ref']))
            objects.append(Object(name=object_name, depencies=depencies))
            continue
        if object.get('properties') != None:
            for property_name, property in object['properties'].items():
                property_type = get_type(property.get('type'), property)
                properties.append(Property(name=check_name(property_name), type=property_type))
        objects.append(Object(name=object_name, properties=properties, depencies=depencies))
    r = r+Objects(objects=objects).__str__()
    # print(r)
    return r + '\n\n'

some_shit = []
x = ''

def main():
    global x
    depencies = [Import(file_path='base', imports=['BM']), 
    Import(file_path='typing', imports=['Optional']),
    Import(file_path='enum', imports=['Enum'])]
    check = 1
    for f in get_dirs():
        file = get_file_path(f, 'objects.json')
        if file == None: continue
        text = gen_file(file)
        if check == 1:
            for d in depencies:
                check = 0
                text = gen_import(d) + '\n\n' + text

        #with open(file.replace('.json', '.py'), 'w') as file:
        with open('gen/objects.py', 'a') as file:
            file.write(text)

    global some_shit
    text = Objects(objects=some_shit).__str__()
    with open('gen/objects.py', 'a') as file:
        file.write(text+x)

           
    
if __name__ == "__main__": main()
