def __list_all_modules():
    from os.path import dirname, basename, isfile
    import glob
    hy_paths = glob.glob(dirname(__file__) + '/*.hy')
    py_paths = glob.glob(dirname(__file__) + '/*.py')
    mod_paths = hy_paths + py_paths
    return [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f)
        and f.endswith('.hy')
        or f.endswith('.py')
        and not f.endswith('__init__.py')
    ]


ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ['ALL_MODULES']
