from os.path import dirname, basename, isfile
import glob


def loadModule(modDir: str):
    hy_paths = glob.glob(dirname(__file__) + '/' + modDir + '/*.hy')
    py_paths = glob.glob(dirname(__file__) + '/' + modDir + '/*.py')
    mod_paths = hy_paths + py_paths
    return sorted([
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f)
        and f.endswith('.hy')
        or f.endswith('.py')
        and not f.endswith('__init__.py')
    ])
