import importlib
import pkgutil

from flask import flash
from YAuB import plugins


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}".format(getattr(form, field).label.text, error), category)


def load_plugins():
    """Loads all plugins in the plugins dir"""
    plugs = []
    header_includes = []
    footer_includes = []
    for loader, name, is_pkg in pkgutil.walk_packages(plugins.__path__):
        try:
            plug = importlib.import_module('YAuB.plugins.' + name).plug()
            plugs.append(plug)
            for include in plug.header_includes:
                header_includes.append(include)
            for include in plug.footer_includes:
                footer_includes.append(include)

        except:  # ..TODO: Put a real exception here
            pass

    return plugs, header_includes, footer_includes
