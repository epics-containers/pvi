import importlib


def lookup_component(component_type, filename, lineno):

    pkg, ident = component_type.rsplit(".", 1)
    pkg = "pvi.modules.%s" % pkg

    try:
        ob = importlib.import_module(pkg)
    except ImportError as e:
        print("\n%s: %d: \n%s" % (filename, lineno, e))

    try:
        ob = getattr(ob, ident)
    except AttributeError:
        print("\n%s:%d:\nPackage %s has no ident %s" %
              (filename, lineno, pkg, ident))

    return ob
