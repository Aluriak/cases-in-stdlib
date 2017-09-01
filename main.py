"""Using the list found in the https://github.com/jackmaney/python-stdlib-list
project, determine cases used in stdlib, and show their inherent diversity.

"""

import re
import inspect
import importlib
from pprint import pprint
from functools import partial
from collections import defaultdict

LIBS_FILE = '3.6.txt'
CASES = {
    re.compile(r'[A-Z][a-z0-9]*([A-Z][a-z0-9]*)*'): 'MixedCase',
    re.compile(r'[a-z_0-9]+'): 'snake_case',
    re.compile(r'[a-z0-9]+([A-Z][a-z0-9]*)*'): 'camelCase',
    re.compile(r'[A-Z][a-z0-9]*(_[a-z0-9]+)*'): 'Mixed_snake_case',
    re.compile(r'[A-Z0-9_]+'): 'UPPER_CASE',
    re.compile(r'[A-Z][a-z0-9]*(_[A-Z][a-z0-9]*)*'): 'Mixed_Snake_Case',
    re.compile(r'([a-z0-9]+[A-Z][a-z0-9]+|[a-z0-9]+)(_([a-z0-9]+[A-Z][a-z0-9]+|[a-z0-9]+))+'): 'snakeCamel_case',
    re.compile(r'([a-z0-9]+|[A-Z0-9]+)(_([a-z0-9]+|[A-Z0-9]+))+'): 'changing_CASE',
    # Very special cases
    re.compile(r'Py[A-Z0-9]*(_([A-Z0-9]+|[A-Z0-9]+))+'): 'Py_CASES',
    re.compile(r'[A-Z0-9]*(_([A-Z0-9]+|[A-Z0-9]+))*_[A-Z0-9]+[_a-z0-9]+'): 'LOWFINAL_CAse',
    re.compile(r'[A-Z0-9_]+v[0-9\.]+[_A-Z0-9]+'): 'VERSIONv1.1_CASE',
    re.compile(r''): '_',
}


def real_case(name:str) -> str or ValueError:
    """Match a name with its case class"""
    for reg, case in CASES.items():
        if reg.fullmatch(name.lstrip('_')):
            return case
    raise ValueError("Word {} have no case".format(name))


def libs_names() -> iter:
    """Yield names of libraries found in LIBS_FILE"""
    with open(LIBS_FILE) as fd:
        yield from map(str.strip, fd)


def objects_in_lib(lib_name:str) -> iter:
    """Yield (object, object_name) found in lib of given name"""
    try:
        lib = importlib.import_module(lib_name, package=None)
    except ImportError as err:
        print('LIB IMPORT ERROR:', err.msg)
        return
    for obj_name, obj in lib.__dict__.items():
        if not obj_name.startswith('__'):
            yield obj, obj_name


def expected_case(obj:object, lib_name:str='') -> str:
    """Return the case expected to name the given object according to its type.

    """
    type_to_case = {
        inspect.isclass: 'MixedCase',
        inspect.isfunction: 'snake_case',
        inspect.ismodule: 'snake_case',
        lambda x: isinstance(x, (str, bytes, int, float, list, tuple, set, frozenset, dict)): 'UPPER_CASE',  # constants
        lambda x: inspect.isclass(type(x)): 'UPPER_CASE'  # constant also, or global instance
    }
    for type_, case in type_to_case.items():
        if type_(obj): return case
    raise ValueError("Object '{}' of type {} found in lib '{}' is not "
                     "handled by expected_case function"
                     "".format(obj, type(obj), lib_name))


def test_real_case():
    """Run pytest on this file to get the proof that regexes works in these cases"""
    for case in CASES.values():
        assert real_case(case) == case

    assert real_case('snake_case_two_more') == 'snake_case'
    assert real_case('UPPER_CASE_TWO_MORE') == 'UPPER_CASE'
    assert real_case('camelCaseTwoMore') == 'camelCase'
    assert real_case('MixedCaseTwoMore') == 'MixedCase'

    assert real_case('snake_42case') == 'snake_case'
    assert real_case('__hadoken') == 'snake_case'
    assert real_case('barry_as_FLUFL') == 'changing_CASE'
    assert real_case('this_isAtest') == 'snakeCamel_case'
    assert real_case('this_isAnother_one') == 'snakeCamel_case'



if __name__ == "__main__":
    acc = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))  # {lib: {expected_case: {real case: {(obj, obj name)}}}}
    counter = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # {lib: {expected_case: {real case: count}}}
    for lib_name in libs_names():
        for obj, obj_name in objects_in_lib(lib_name):
            acc[lib_name][expected_case(obj)][real_case(obj_name)].add((type(obj), obj_name))
            counter[lib_name][expected_case(obj)][real_case(obj_name)] += 1
    # simplify
    acc = {lib: {expc: {realc: values for realc, values in realcs.items()}
                 for expc, realcs in expcs.items()}
           for lib, expcs in acc.items()}
    counter = {lib: {expc: {realc: values for realc, values in realcs.items()}
                     for expc, realcs in expcs.items()}
               for lib, expcs in counter.items()}
    pprint(counter)
    print()
    pprint(counter['csv'])
    pprint(counter['functools'])
    pprint(counter['logging'])
    # TODO: found cases per lib, producing a context thus a lattice.
