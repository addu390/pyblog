from __future__ import print_function
from . import utils
from dateutil import parser
from os import path

DEFAULT_CONFIG = """name: A PyBlog Blog
tagline: Demoing PyBlog, a lightweight python static blog generator
permalinks: /@year/@month/@slug.html
root_url: https://blog.com
"""


class Page:

    def __init__(self, file_path):
        """Creates a generic page from a file"""

        self.title = u''
        self.template = None
        self.url = u''
        self.date = None
        self.slug = None

        parts = utils.file_get(file_path).split('\n\n', 1)
        if len(parts) == 2:
            meta = utils.parse_headers(parts[0])
            self.content = parts[1]
            self.insert_fields(meta)
            if self.date:
                self.date = parser.parse(meta['date'])
            else:
                self.date = utils.file_mtime(file_path)
        else:
            self.content = parts[0]
            self.date = utils.file_mtime(file_path)

    def insert_fields(self, data={}):
        """Inserts values from a dictionary as fields"""
        for key in data:
            setattr(self, key, data[key])

    def make_url(self, fmt):
        return (fmt.replace('@year', self.date.strftime('%Y'))
                .replace('@month', self.date.strftime('%m'))
                .replace('@day', self.date.strftime('%d'))
                .replace('@slug', self.slug)
                .strip('/'))

    @staticmethod
    def make_post(blog, file):
        """Creates a post object"""
        post = Page(path.join(blog.posts_dir, file))
        if not post.slug:
            post.slug = utils.slugify(post.title)
        post.url = post.make_url(blog.url_format)
        return post

    @staticmethod
    def make_page(blog, file):
        """Creates a page object"""
        page = Page(path.join(blog.pages_dir, file))
        page.slug = file
        page.url = file
        tpl = blog.env.from_string(page.content)
        page.content = tpl.render(blog=blog)
        return page

    def __repr__(self):
        return 'Blog.Page(%s)' % self.slug


class Blog:
    posts = None
    pages = None

    def __init__(self, in_dir, out_dir, config_file=None):
        """Creates the blog object from the config file"""
        if config_file:
            self.config_file = path.abspath(config_file)
        else:
            self.config_file = path.abspath(path.join(in_dir, 'config.txt'))
        self.templates_dir = path.abspath(path.join(in_dir, '_templates'))
        self.static_dir = path.abspath(path.join(in_dir, '_static'))
        self.pages_dir = path.abspath(path.join(in_dir, '_pages'))
        self.posts_dir = path.abspath(path.join(in_dir, '_posts'))
        self.in_dir = path.abspath(in_dir)
        self.out_dir = path.abspath(out_dir)

        options = utils.parse_headers(utils.file_get(self.config_file))

        self.name = options['name']
        self.tagline = options['tagline']
        self.root_url = options['root_url']
        if 'permalinks' in options:
            self.url_format = options['permalinks']
        else:
            self.url_format = '/@year/@month/@day/@slug.html'

        utils.dir_make(out_dir)
        self.env = utils.create_jinja_env(self.templates_dir)
        #self.posts = self.__get_posts()
        #self.pages = self.__get_pages()

    def __get_posts(self):
        """returns a list of all post objects"""
        files = utils.file_list(self.posts_dir, '.txt')
        self.posts = sorted([Page.make_post(self, file) for file in files],
                            key=lambda x: x.date, reverse=True)
        return self.posts

    def __get_pages(self):
        """returns a list of all pages objects"""
        files = utils.file_list(self.pages_dir)
        self.pages = sorted([Page.make_page(self, file) for file in files],
                            key=lambda x: x.date, reverse=True)
        return self.pages

    def write_html(self, post):
        """writes a post or page to its HTML file"""
        if post.template:
            template = self.env.get_template(post.template)
            utils.file_put(path.join(self.out_dir, post.url),
                           template.render(blog=self, post=post))
        else:
            utils.file_put(path.join(self.out_dir, post.url),
                           post.content)

    @staticmethod
    def dir_init(input_dir):
        utils.dir_make(path.join(input_dir, '_posts'))
        utils.dir_make(path.join(input_dir, '_pages'))
        utils.dir_make(path.join(input_dir, '_static'))
        utils.dir_make(path.join(input_dir, '_templates'))
        utils.file_put(path.join(input_dir, 'config.txt'), DEFAULT_CONFIG)
        pass

    def compile(self):
        """Used for command-line usage, compiles the blog"""
        utils.dir_copy(self.static_dir, self.out_dir)
        for post in self.__get_posts():
            self.write_html(post)
        for page in self.__get_pages():
            self.write_html(page)

    def __repr__(self):
        return 'Blog.Engine(%s)' % self.root_url
