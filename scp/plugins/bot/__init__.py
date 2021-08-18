from scp import log


def __list_all_modules():
    from os.path import dirname, basename, isfile
    import glob

    # This generates a list of modules
    # in this folder for the * in __main__ to work.
    mod_paths = glob.glob(dirname(__file__) + '/*.py')
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith('.py') and not f.endswith('__init__.py')
    ]
    return all_modules


ALL_SETTINGS = sorted(__list_all_modules())
log.info('Assistant bot module loaded: %s', str(ALL_SETTINGS))
__all__ = ALL_SETTINGS + ['ALL_SETTINGS']