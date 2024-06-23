from __future__ import print_function
import pyblog
import sys
import time
import argparse
from os import path, chdir
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

try:
    import http.server as http_server
    import socketserver as http_socketserver
except ImportError:
    import SimpleHTTPServer as http_server
    import SocketServer as http_socketserver

VERSION_STR = '%(prog)s ' + pyblog.VERSION + ' -- Lightweight python static blog generator'


class BlogBuilder(PatternMatchingEventHandler):

    def __init__(self, source, dest, config, quiet):
        """Creates the blog engine and sets up the ignored file list"""
        self.quiet = quiet
        self.blog = pyblog.Blog(source, dest, config)
        super(BlogBuilder, self).__init__(ignore_patterns=[
            self.blog.out_dir,
            path.join(self.blog.out_dir, "*"),
            '*/.git*', '*/.hg*', '*/.svn*',
            '*/.DS_Store'
        ])
        self.print_safe('Configuration file: %s' % self.blog.config_file)
        self.print_safe('            Source: %s' % self.blog.in_dir)
        self.print_safe('       Destination: %s' % self.blog.out_dir)

    def on_any_event(self, event):
        if not event.src_path.startswith(self.blog.out_dir):
            super(BlogBuilder, self).on_any_event(event)
            self.print_safe('Detected change.')
            # self.build()

    def print_safe(self, str, **kwargs):
        """Forwards to print only if not quiet"""
        if not self.quiet:
            print(str, **kwargs)

    def build(self):
        """Builds the blog"""
        self.print_safe('      Generating... ', end="")
        self.blog.compile()
        self.print_safe('done.')
        pass

    def watch(self):
        """Watches the blog's directory for changes and rebuilds"""
        observer = Observer()
        observer.schedule(self, self.blog.in_dir, recursive=True)
        observer.start()
        self.print_safe('\r\nWatching...')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.print_safe('done.')
        observer.join()

    def serve(self, url, port):
        """Creates the server and directory observer"""
        observer = Observer()
        observer.schedule(self, self.blog.in_dir, recursive=True)
        observer.start()
        chdir(self.blog.out_dir)
        Handler = http_server.SimpleHTTPRequestHandler
        try:
            httpd = http_socketserver.TCPServer((url, port), Handler)
            self.print_safe('\r\nServing at %s:%d...' % (url, port))
            self.blog.compile()
            while True:
                httpd.handle_request()
        except KeyboardInterrupt:
            observer.stop()
            self.print_safe('done.')
        observer.join()


def pyblog_build(args):
    """Builds a blog once or watches its directory for changes"""
    builder = BlogBuilder(args.source, args.dest, args.config, args.quiet)
    if args.watch:
        builder.watch()
    else:
        builder.build()


def pyblog_init(args):
    """Creates a new pyblog instance directory"""
    blog_path = path.abspath(args.path)
    pyblog.Blog.dir_init(blog_path)
    print('New blog installed in %s' % blog_path)


def pyblog_serve(args):
    print("pyblog_serve function called")
    """Serves the blog and watches the source directory for changes"""
    builder = BlogBuilder(args.source, args.dest, args.config, args.quiet)
    print("BlogBuilder created")
    builder.serve(args.host, args.port)


def main():
    print("pyblog_main function called")
    """Command line entry point for PyBlog build, serve & init"""
    parser = argparse.ArgumentParser(
        description='pyblog 0.5 -- Lightweight python static blog generator')
    parser.add_argument('-v', '--version',
                        help='Print the version',
                        action='version',
                        version=VERSION_STR)
    subparsers = parser.add_subparsers(title='commands')

    # Setup the build command

    build = subparsers.add_parser('build',
                                  help='Builds your blog',
                                  description='%(prog)s -- Builds your blog')
    build.add_argument('--config',
                       help='Custom configuration file',
                       metavar='FILE',
                       default=None)
    build.add_argument('-s', '--source',
                       help='Source directory (defaults to ./)',
                       metavar='DIR',
                       default='./')
    build.add_argument('-d', '--dest',
                       help='Destination directory (defaults to ./out)',
                       metavar='DIR',
                       default='./out')
    build.add_argument('-q', '--quiet',
                       action='store_true',
                       help='Silence output')
    build.add_argument('-w', '--watch',
                       action='store_true',
                       help='Watch for changes and rebuild')
    build.set_defaults(func=pyblog_build)

    # Setup the init command

    init = subparsers.add_parser('new',
                                 help='Create a new PyBlog blog skeleton',
                                 description='%(prog)s -- Creates a new PyBlog instance in <path>')
    init.add_argument('path',
                      help='Path of the new blog')
    init.set_defaults(func=pyblog_init)

    # Setup the serve command

    serve = subparsers.add_parser('serve',
                                  help='Serve your blog locally',
                                  description='%(prog)s -- Serve your blog locally')
    serve.add_argument('--config',
                       help='Custom configuration file',
                       metavar='FILE',
                       default=None)
    serve.add_argument('-s', '--source',
                       help='Source directory (defaults to ./)',
                       metavar='DIR',
                       default='./')
    serve.add_argument('-d', '--dest',
                       help='Destination directory (defaults to ./out)',
                       metavar='DIR',
                       default='./out')
    serve.add_argument('-q', '--quiet',
                       action='store_true',
                       help='Silence output')
    serve.add_argument('-H', '--host',
                       default='localhost',
                       help='Host to bind to (defaults to localhost)')
    serve.add_argument('-P', '--port',
                       default=4000,
                       type=int,
                       help='Port to listen on (defaults to 4000)')
    serve.set_defaults(func=pyblog_serve)

    # Parse the CLI arguments and dispatch

    args = parser.parse_args()
    if hasattr(args, 'func'):
        try:
            print("Calling function: ", args.func)
            args.func(args)
        except Exception as e:
            raise e
            sys.exit('error: ' + str(e))
