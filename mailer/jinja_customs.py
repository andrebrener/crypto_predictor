# =============================================================================
#          File: jinja_customs.py
#        Author: Andre Brener
#       Created: 13 Jun 2017
# Last Modified: 13 Jun 2017
#   Description: description
# =============================================================================
import functools

import jinja2


def update_environment(env, filters):
    filters_ = {}
    for k, filter_ in filters.items():
        filters_[k] = functools.partial(filter_, env)
    env.filters.update(filters_)
    return env


def load_templates(templates_folder='templates',
                   extensions=['html'],
                   trim_blocks=True,
                   filters=None):
    loader = jinja2.FileSystemLoader(templates_folder)
    env = jinja2.Environment(loader=loader)
    if trim_blocks:
        env.trim_blocks = True
        env.lstrip_blocks = True
    if filters:
        env = update_environment(env, filters)
    templates = [
        t for t in loader.list_templates()
        if any(t.endswith(ext) for ext in extensions)
    ]
    return {t: env.get_template(t) for t in templates}
