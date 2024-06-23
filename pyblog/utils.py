import markdown
import jinja2
from os import path, makedirs, listdir
import re
import distutils.dir_util
from datetime import datetime

md = markdown.Markdown(extensions=[
    'markdown.extensions.fenced_code',
    'markdown.extensions.attr_list',
    'markdown.extensions.tables',
    'markdown.extensions.smarty',
    'markdown.extensions.codehilite'],
    extension_configs={
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': False
        }
    })


# Filesystem shortcuts

def dir_copy(src, dist):
    distutils.dir_util.copy_tree(src, dist)


def dir_make(dir_path):
    if not path.exists(dir_path):
        makedirs(dir_path)


def file_get(file_path):
    """Returns the UTF-8 decoded contents of a file"""
    with open(file_path, 'r') as f:
        return f.read()


def file_put(file_path, contents):
    """Saves a utf-8 string to a file"""
    dir_make(path.dirname(file_path))
    with open(file_path, 'w') as f:
        f.write(contents)


def file_list(dir_path, ext=''):
    return [f for f in listdir(dir_path) if
            path.isfile(path.join(dir_path, f)) and f.endswith(ext)]


def file_mtime(file_path):
    return datetime.fromtimestamp(path.getmtime(file_path))


# Blog utilities

def parse_headers(str):
    """Parses a HTTP-style headers"""
    headers = {}
    for line in str.split('\n'):
        if len(line) == 0: continue
        key, value = line.split(': ', 1)
        headers[key] = value
    return headers


def create_jinja_env(tpl_path):
    """Creates a PyBlog/Jinja2 environment"""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(tpl_path))
    env.filters['markdown'] = markdown
    env.filters['shortdate'] = shortdate
    env.filters['longdate'] = longdate
    env.filters['rssdate'] = rssdate
    env.filters['slugify'] = slugify
    return env


# Filters, used for jinja

def slugify(text):
    """Creates a url-valid slug fro a string"""
    slug = text.encode('ascii', 'ignore').lower().decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    return slug


def markdown(text):
    """Markdownify a piece of text"""
    return jinja2.Markup(md.convert(text))


def shortdate(t):
    """Returns a british-formatted date without the year"""
    return t.strftime('%b %d')


def longdate(t):
    """Returns a british-formatted date with the year"""
    return t.strftime('%b %d, %Y')


def rssdate(t):
    """Returns a RSS-valid date without the year"""
    return t.strftime('%a, %d %b %Y %H:%M:%S %z')
