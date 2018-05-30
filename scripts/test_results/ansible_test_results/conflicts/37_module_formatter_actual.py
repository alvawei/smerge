#!/usr/bin/env python
# (c) 2012, Jan-Piet Mens <jpmens () gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import yaml
import codecs
import json
import ast
from jinja2 import Environment, FileSystemLoader
import re
import getopt
import time
import datetime
import subprocess

# modules that are ok that they do not have documentation strings
BLACKLIST_MODULES = [
   'async_wrapper'
]

MODULEDIR="/Users/jpm/Auto/pubgit/ansible/ansible/library"

BOILERPLATE = '''
---
module: foo
author: AUTHORNAME
short_description: A short description, think title
description:
  - First paragraph explains what the module does. More paragraphs can
    be added.
  - Second para of description. You can use B(bold), I(italic), and
    C(constant-width). To refer to another M(module) use that, and
    U(url) exists too.
version_added: "0.x"
options:
  dest:
    required: true
    description:
      - What does this option do, and bla bla bla
      - More than one paragraph allowed here as well. Formatting
        with B(bold), etc. work too.
  remove:
    required: false
    choices: [ yes, no ]
    default: "maybe"
    aliases: [ kill, killme, delete ]
    description:
      - The foo to do on M(module) but be careful of lorem ipsum
'''

# There is a better way of doing this!
# TODO: somebody add U(text, http://foo.bar/) as described by Tim in #991

_ITALIC = re.compile(r"I\(([^)]+)\)")
_BOLD   = re.compile(r"B\(([^)]+)\)")
_MODULE = re.compile(r"M\(([^)]+)\)")
_URL    = re.compile(r"U\(([^)]+)\)")
_CONST  = re.compile(r"C\(([^)]+)\)")

def latex_ify(text):
    t = _ITALIC.sub("\\I{" + r"\1" + "}", text)
    t = _BOLD.sub("\\B{" + r"\1" + "}", t)
    t = _MODULE.sub("\\M{" + r"\1" + "}", t)
    t = _URL.sub("\\url{" + r"\1" + "}", t)
    t = _CONST.sub("\\C{" + r"\1" + "}", t)

    return t


def html_ify(text):
    t = _ITALIC.sub("<em>" + r"\1" + "</em>", text)
    t = _BOLD.sub("<b>" + r"\1" + "</b>", t)
    t = _MODULE.sub("<span class='module'>" + r"\1" + "</span>", t)
    t = _URL.sub("<a href='" + r"\1" + "'>" + r"\1" + "</a>", t)
    t = _CONST.sub("<code>" + r"\1" + "</code>", t)
    return t





def rst_ify(text):
    t = _ITALIC.sub(r'*' + r"\1" + r"*", text)
    t = _BOLD.sub(r'**' + r"\1" + r"**", t)
    t = _MODULE.sub(r'``' + r"\1" + r"``", t)
    t = _URL.sub(r"\1", t)
    t = _CONST.sub(r'``' + r"\1" + r"``", t)

    return t


def json_ify(text):
    t = _ITALIC.sub("<em>" + r"\1" + "</em>", text)
    t = _BOLD.sub("<b>" + r"\1" + "</b>", t)
    t = _MODULE.sub("<span class='module'>" + r"\1" + "</span>", t)
    t = _URL.sub("<a href='" + r"\1" + "'>" + r"\1" + "</a>", t)
    t = _CONST.sub("<code>" + r"\1" + "</code>", t)

    return t


def return_data(text, args, outputname, module):
    if args.output_dir is not None:
        f = open(os.path.join(args.output_dir, outputname % module), 'w')
        f.write(text)
        f.close()
    else:
        print text


def man_ify(text):
    t = _ITALIC.sub(r'\\fI' + r"\1" + r"\\fR", text)
    t = _BOLD.sub(r'\\fB' + r"\1" + r"\\fR", t)
    t = _MODULE.sub(r'\\fI' + r"\1" + r"\\fR", t)
    t = _URL.sub(r'\\fI' + r"\1" + r"\\fR", t)
    t = _CONST.sub(r'\\fC' + r"\1" + r"\\fR", t)

    return t


def js_ify(text):
    t = _ITALIC.sub(r'*' + r"\1" + r"*", text)
    t = _BOLD.sub(r'**' + r"\1" + r"**", t)
    t = _MODULE.sub(r'``' + r"\1" + r"``", t)
    t = _URL.sub(r"\1", t)
    t = _CONST.sub(r'``' + r"\1" + r"``", t)

    return t

# Helper for Jinja2 (format() doesn't work here...)
def rst_fmt(text, fmt):
    return fmt % (text)

def rst_xline(width, char="="):
    return char * width

def load_examples_section(text):
    return text.split('***BREAK***')

def get_docstring(filename, verbose=False):
    """
    Search for assignment of the DOCUMENTATION variable in the given file.
    Parse that from YAML and return the YAML doc or None.
    """

    doc = None

    try:
        # Thank you, Habbie, for this bit of code :-)
        M = ast.parse(''.join(open(filename)))
        for child in M.body:
            if isinstance(child, ast.Assign):
                if 'DOCUMENTATION' in (t.id for t in child.targets):
                    doc = yaml.load(child.value.s)

    except:
        if verbose:
            raise
        else:
            print "unable to parse %s" % filename

    return doc

def main():
    class Object(object):
        pass

    args = Object()
    args.ansible_version = 'unknown'
    args.module_dir = MODULEDIR
    args.template_dir = 'hacking/templates'
    args.type = 'latex'
    args.module_list = []
    args.verbose = False
    args.output_dir = None
    args.includes_file = None
    try:
        opts, arguments = getopt.getopt(sys.argv[1:], 'A:M:T:t:m:vo:I:GVh',
            [ 'ansible-version=', 'module-dir=', 'template-dir=', 'type=',
              'module=', 'verbose', 'output-dir=', 'includes-file=',
              'generate', 'version', 'help', ])
<<<<<<< REMOTE
    except getopt.error, e:
        print >>sys.stderr, 'ERROR: %s'% str(e)
        sys.exit(1)


=======

>>>>>>> LOCAL
    for opt, arg in opts:
        if opt in ('-A', '--ansible-version'):
            args.ansible_version = arg
        elif opt in ('-M', '--module-dir'):
            args.module_dir = arg
        elif opt in ('-T', '--template-dir'):
            args.template_dir = arg
        elif opt in ('-t', '--type'):
            args.type = arg
            if args.type not in type_choices:
                print >>sys.stderr, 'ERROR: Type %s not in possible types %s.' % (args.type, type_choices)
                sys.exit(1)
        elif opt in ('-m', '--module'):
            args.module_list.append(arg)
        elif opt in ('-v', '--verbose'):
            args.verbose = True
        elif opt in ('-o', '--output-dir'):
            args.output_dir = arg
        elif opt in ('-I', '--includes-file'):
            args.includes_file = arg
        elif opt in ('-G', '--generate'):
            args.do_boilerplate = True
        elif opt in ('-V', '--version'):
            print >>sys.stderr, '%(prog)s 1.0'
        elif opt in ('-h', '--help'):
            print >>sys.stderr, '''Convert Ansible module DOCUMENTATION strings to other formats

 -A, --ansible-version=     Ansible version number
 -M, --module-dir=          Ansible modules/ directory
 -T, --template-dir=        Directory containing Jinja2 templates
 -t, --type=                Output type
 -m, --module=              Add modules to process in module_dir
 -v, --verbose              Verbose
 -o, --output-dir=          Output directory for module files
 -I, --includes-file=       Create a file containing list of processed modules
 -G, --generate             Generate boilerplate DOCUMENTATION to stdout
'''
            sys.exit(0)
        else:
            print >>sys.stderr, 'ERROR: Option %s unknown to getopt' % opt
            sys.exit(1)







    if args.type == 'js':
        env.filters['jpfunc'] = js_ify
        template = env.get_template('js.j2')
        outputname = "%s.js"

    # Temporary variable required to genrate aggregated content in 'js' format.
    js_data = []
    if args.type == 'js':
        docs = {}
        docs['json'] = json.dumps(js_data, indent=2)
        text = template.render(docs)
        return_data(text, args, outputname, 'modules')

    # print "M: %s" % args.module_dir
    # print "t: %s" % args.type
    # print "m: %s" % args.module_list
    # print "v: %s" % args.verbose
    if args.do_boilerplate:
        boilerplate()
        sys.exit(0)

    if not args.module_dir:
        print "Need module_dir"
        sys.exit(1)

    if not args.template_dir:
        print "Need template_dir"
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(args.template_dir),
        variable_start_string="@{",
        variable_end_string="}@",
        trim_blocks=True,
        )
    env.globals['xline'] = rst_xline
    if args.type == 'latex':
        env.filters['jpfunc'] = latex_ify
        template = env.get_template('latex.j2')
        outputname = "%s.tex"
        includecmt = "% generated code\n"
        includefmt = "\\input %s\n"
    if args.type == 'html':
        env.filters['jpfunc'] = html_ify
        template = env.get_template('html.j2')
        outputname = "%s.html"
        includecmt = ""
        includefmt = ""
    if args.type == 'man':
        env.filters['jpfunc'] = man_ify
        template = env.get_template('man.j2')
        outputname = "ansible.%s.3"
        includecmt = ""
        includefmt = ""
    if args.type == 'rst':
        env.filters['jpfunc'] = rst_ify
        env.filters['html_ify'] = html_ify
        env.filters['fmt'] = rst_fmt
        env.filters['xline'] = rst_xline
        template = env.get_template('rst.j2')
        outputname = "%s.rst"
        includecmt = ".. Generated by module_formatter\n"
        includefmt = ".. include:: modules/%s.rst\n"
    if args.type == 'json':
        env.filters['jpfunc'] = json_ify
        outputname = "%s.json"
        includecmt = ""
        includefmt = ""

    if args.includes_file is not None and includefmt != "":
        incfile = open(args.includes_file, "w")
        incfile.write(includecmt)

    for module in sorted(os.listdir(args.module_dir)):
        if len(args.module_list):
            if not module in args.module_list:
                continue

        fname = os.path.join(args.module_dir, module)
        extra = os.path.join("inc", "%s.tex" % module)
        if fname.endswith(".swp"):
            continue


        print " processing module source ---> %s" % fname


        doc = get_docstring(fname, verbose=args.verbose)

        if doc is None and module not in BLACKLIST_MODULES:
            sys.stderr.write("*** ERROR: CORE MODULE MISSING DOCUMENTATION: %s ***\n" % module)
            #sys.exit(1)

        if not doc is None:
            doc['filename']         = fname
            doc['docuri']           = doc['module'].replace('_', '-')
            doc['now_date']         = datetime.date.today().strftime('%Y-%m-%d')
            doc['ansible_version']  = args.ansible_version

            if args.includes_file is not None and includefmt != "":
                incfile.write(includefmt % module)

            if args.verbose:
                print json.dumps(doc, indent=4)


            if args.type == 'json':
                text = json.dumps(doc, indent=2)
            return_data(text, args, outputname, module)
<<<<<<< REMOTE
            else:
                print text


=======

>>>>>>> LOCAL
            if args.type == 'latex':
                if os.path.exists(extra):
                    f = open(extra)
                    extradata = f.read()
                    f.close()

                    doc['extradata'] = extradata
#def boilerplate():
#
#    # Sneaky: insert author's name from Git config
#
#    cmd = subprocess.Popen("git config --get user.name", shell=True,
#            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    out, err = cmd.communicate()
#
#    if len(out.split('\n')) == 2:
#        author = out.split('\n')[0]
#        print author

#    else:
#        author = "Your Name"
#

#    # I can't dump YAML in ordered fasion, so I use this boilerplate string
#    # and verify it is parseable just before printing it out to the user.
#
#    try:
#        boilplate = yaml.load(BOILERPLATE)
#    except:
#        print "Something is wrong with the BOILERPLATE"
#        sys.exit(1)
#
#    print """
#DOCUMENTATION = '''
#%s
#'''
#"""[1:-1] % (BOILERPLATE.replace('AUTHORNAME', author) [1:-1] )
if __name__ == '__main__':
    main()

