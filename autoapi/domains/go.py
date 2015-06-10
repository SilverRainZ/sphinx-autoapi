import json
import subprocess

from .base import PythonMapperBase, SphinxMapperBase


class GoDomain(SphinxMapperBase):

    '''Auto API domain handler for Go

    Parses directly from Go files.

    :param app: Sphinx application passed in as part of the extension
    '''

    def load(self, pattern, dir, ignore=[]):
        '''
        Load objects from the filesystem into the ``paths`` dictionary.

        '''
        data = self.read_file(dir)
        if data:
            self.paths[dir] = data

    def read_file(self, path, **kwargs):
        '''Read file input into memory, returning deserialized objects

        :param path: Path of file to read
        '''
        # TODO support JSON here
        # TODO sphinx way of reporting errors in logs?

        try:
            parsed_data = json.loads(subprocess.check_output(['godocjson', path]))
            return parsed_data
        except IOError:
            self.app.warn('Error reading file: {0}'.format(path))
        except TypeError:
            self.app.warn('Error reading file: {0}'.format(path))
        return None

    def create_class(self, data, _type=None):
        '''Return instance of class based on Go data

        Data keys handled here:

            _type
                Set the object class

            consts, types, vars, funcs
                Recurse into :py:meth:`create_class` to create child object
                instances

        :param data: dictionary data from godocjson output
        '''
        obj_map = dict(
            (cls.type, cls) for cls
            in ALL_CLASSES
        )
        try:
            # Contextual type data from children recursion
            if _type:
                self.app.debug('Forcing Go Type %s' % _type)
                cls = obj_map[_type]
            else:
                cls = obj_map[data['type']]
        except KeyError:
            self.app.warn('Unknown Type: %s' % data)
        else:
            if cls.inverted_names and 'names' in data:
                # Handle types that have reversed names parameter
                for name in data['names']:
                    data_inv = {}
                    data_inv.update(data)
                    data_inv['name'] = name
                    if 'names' in data_inv:
                        del data_inv['names']
                    for obj in self.create_class(data_inv):
                        yield obj
            else:
                # Recurse for children
                obj = cls(data, jinja_env=self.jinja_env)
                for child_type in ['consts', 'types', 'vars', 'funcs']:
                    for child_data in data.get(child_type, []):
                        obj.children += list(self.create_class(
                            child_data,
                            _type=child_type.replace('consts', 'const').replace('types', 'type').replace('vars', 'variable').replace('funcs', 'func')
                        ))
                yield obj


class GoBase(PythonMapperBase):

    language = 'go'
    inverted_names = False

    def __init__(self, obj, **kwargs):
        super(GoBase, self).__init__(obj, **kwargs)
        self.name = obj.get('name') or obj.get('packageName')
        self.id = self.name

        # Second level
        self.imports = obj.get('imports', [])
        self.children = []
        self.parameters = map(
            lambda n: {'name': n['name'],
                       'type': n['type'].lstrip('*')},
            obj.get('parameters', [])
        )
        self.docstring = obj.get('doc', '')

        # Go Specific
        self.notes = obj.get('notes', {})
        self.filenames = obj.get('filenames', [])
        self.bugs = obj.get('bugs', [])

    def __str__(self):
        return '<{cls} {id}>'.format(cls=self.__class__.__name__,
                                     id=self.id)

    @property
    def short_name(self):
        '''Shorten name property'''
        return self.name.split('.')[-1]

    @property
    def namespace(self):
        pieces = self.id.split('.')[:-1]
        if pieces:
            return '.'.join(pieces)

    @property
    def ref_type(self):
        return self.type

    @property
    def ref_directive(self):
        return self.type

    @property
    def methods(self):
        return self.obj.get('methods', [])


class GoVariable(GoBase):
    type = 'var'
    inverted_names = True


class GoMethod(GoBase):
    type = 'method'
    ref_directive = 'meth'


class GoConstant(GoBase):
    type = 'const'
    inverted_names = True


class GoFunction(GoBase):
    type = 'func'
    ref_type = 'function'


class GoPackage(GoBase):
    type = 'package'
    ref_directive = 'pkg'


class GoType(GoBase):
    type = 'type'


ALL_CLASSES = [
    GoConstant,
    GoFunction,
    GoPackage,
    GoVariable,
    GoType,
    GoMethod,
]
