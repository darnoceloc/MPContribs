import inspect, os

def get_user_explorer_name(path, view='index'):
    return '_'.join(
        os.path.dirname(os.path.normpath(path)).split(os.sep)[-4:] + [view]
    )

def duplicate_check(f):
    existing_identifiers = {}

    def wrapper(*args, **kwargs):

        module = inspect.getmodule(f)
        module_split = module.__name__.split('.')[:-1]
        mod_path = os.sep.join(module_split)
        from mpcontribs.users_modules import get_user_rester
        Rester = get_user_rester(mod_path)

        test_site = kwargs.get('test_site', True)
        with Rester(test_site=test_site) as mpr:
            for doc in mpr.query_contributions(criteria=mpr.query):
                existing_identifiers[doc['identifier']] = doc['_id']

        try:
            f(*args, **kwargs)
        except StopIteration:
            print('not adding more contributions')

        mpfile = args[0]
        update = 0
        for identifier in mpfile.ids:
            if identifier in existing_identifiers:
                cid = existing_identifiers[identifier]
                mpfile.insert_top(identifier, 'cid', cid)
                update += 1

        print(len(mpfile.ids), 'contributions to submit.')
        if update > 0:
            print(update, 'contributions to update.')

    wrapper.existing_identifiers = existing_identifiers
    return wrapper
