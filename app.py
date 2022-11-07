import os
import re
import sys
import json
import argparse
import markdown2
from flask import Flask, send_from_directory, request
import subprocess

app = Flask("File2Web")
args = None
f2w_path = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    global args
    parser = argparse.ArgumentParser(
        description='Create a website from exist file')
    parser.add_argument('-i', '--ignore_file', dest='ignore_file',
                        default=f"{f2w_path}/ignore.txt",
                        help='file to ignore')
    parser.add_argument('-p', '--port', dest='port', default=8091,
                        help='change port to open')
    parser.add_argument('-d', '--dictionary', dest='root_dict', default='.',
                        help='the root dictionary to represent')
    parser.add_argument('--install', action="store_true",
                        help='install the command')
    args = parser.parse_args()


class md():
    ignore_folder = ['css', 'img']

    def __init__(self, level, msg):
        self.level = level
        self.msg = msg
        self.child = []  # the mds of subfolder in this folder
        self.child_text = []

    def gen_child_text(self, msg, link, full_path):
        if msg == "info.txt":
            with open(full_path + "/" + msg, 'r') as f:
                info_text = []
                # Place info.txt at first line
                for line in f.readlines():
                    info_text.append(md.indent(self.level+1, line))
                self.child_text = info_text + self.child_text
        else:
            self.child_text.append(md.indent(self.level+1, f"[{msg}]({link})"))

    def gen_folder(self, msg):
        if msg not in self.ignore_folder:
            child = md(self.level+1, msg)
            self.child.append(child)
            return child

    def indent(level, string):
        if level == 1:
            return f"# {string}\n"
        elif level == 2:
            return f"## {string}\n"
        elif level >= 3:
            return f"{'    '*(level-3)}* {string}\n"

    def get_child(self, name):
        """
        get a child md by name 
        (get a subfolder)
        """
        for c in self.child:
            if c.msg == name:
                return c

        if self.msg == name:
            return self

        return self.gen_folder(name)

    def check_child(self, name):
        return (name in [c.msg for c in self.child])

    def __str__(self):
        out = md.indent(self.level, self.msg)
        for text in self.child_text:
            out += text

        for child in self.child:
            out += str(child)

        # avoid unexpected indent at header
        return out if out[-2] == '\n' else out + '\n'


def get_ignore_files():
    rules = []
    folder_rules = []
    with open(args.ignore_file, 'r') as f:
        for l in f.readlines():
            if l[-2] == '/':
                folder_rules.append(re.compile(l[:-2], re.X))
            else:
                rules.append(re.compile(l[:-1], re.X))

    return rules, folder_rules


def files2md():
    path = args.root_dict
    root_md = md(1, path)
    rules, folder_rules = get_ignore_files()
    for (dirpath, dirnames, filenames) in os.walk(path):
        nowpath = dirpath[len(path)+1:].split('/')
        try:
            for ignore in md.ignore_folder:
                if ignore in nowpath:
                    raise Exception
            for r in folder_rules:
                result = r.match(dirpath)
                if result == None:
                    raise Exception
            # if nowpath == ['']:
                # raise Exception
        except Exception:
            continue

        now_md = root_md

        if nowpath != ['']:
            # In the subfolder of specified path, find the last folder
            for n in nowpath:
                now_md = now_md.get_child(n)

            # generate md of subfolder of this folder
            for d in dirnames:
                now_md.gen_folder(d)
        else:  # root md use next level to store files
            now_md = now_md.get_child(os.getcwd())

        # generate the text to display
        for f in sorted(filenames):
            # filter the file not to display
            flag = 0
            for r in rules:
                res = r.match(f)
                if res != None:
                    flag = 1
                    break
            if flag == 1:
                continue

            now_md.gen_child_text(
                f, (dirpath + "/" + f).replace(" ", "%20"), dirpath)

    root_md.msg = "Abstract"
    root_md.child_text = []
    return root_md


def md2html(mdstr):
    # exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc', 'markdown.extensions.codehilite']
    exts = ['cuddled-lists', 'fenced-code-blocks', 'markdown-in-html',
            'toc', 'spoiler', 'tables', 'strike', 'task_list', 'code-friendly']
    html = '''
<html lang="zh-tw">
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type" />
<link rel="stylesheet" type="text/css" href="/css/github-syntax-highlight.css">
  <link rel="stylesheet" type="text/css" href="/css/github-markdown.css">
  <link rel="stylesheet" type="text/css" href="/css/mjpage-html.css">
  <link rel="stylesheet" type="text/css" href="/css/styles.css">
  <style>
    .markdown-body {
      min-width: 200px;
      margin: 0 auto;
      padding: 30px;
    }
    #con-error {
      position: fixed;
      top: 0px;
      right: 0px;
      padding: 5px;
      background: white;
      color: red;
    }
  </style>
</head>
<body>
<div class="container">
<div class="item row1"></div>
<div class="item row1"></div>
<div class="item row2"></div>
<div class="item row2">
<div id="readme" class="boxed-group flush clearfix announce instapaer_body md">
<article class="markdown-body">
%s
</article>
</div>
</div>
<div class="item row2"></div>
<div class="item row3"></div>
<div class="item row3"></div>
<div class="item row3"></div>
</body>
</html>
'''
    #ret = markdown.markdown(mdstr,extensions=exts)
    ret = markdown2.markdown(mdstr, extras=exts)
    return html % (ret.toc_html + ret)
    # return markdown2.markdown(md)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(f'{f2w_path}/css', path)


@app.route('/<path:path>', methods=['GET'])
def send_file(path):
    if path[-3:] in ["pdf", "png"]:
        return send_from_directory('.', path)
    elif path == 'favicon.ico':
        return send_from_directory(f2w_path, "favicon_resized.png")
    elif path[-2:] == "md":
        f = open(path, 'r')
        data = f.read()
        f.close()
        return md2html(data)
    elif path[-3:] == "doc" or path[-4:] in ["docx", "pptx"]:
        global sysOS
        if sysOS.find("Linux") > -1:
            os.system("xdg-open "+path.replace(' ', '\ '))
        else:
            os.system("open "+path.replace(' ', '\ '))

        return "Opened file"


@app.route("/", methods=['GET'])
def mainpage():
    md_out = files2md()
    html_out = md2html(str(md_out))
    return html_out


@app.route('/', methods=['PUT'])
def update():
    # print(request.json())
    # return '200'
    md_out = files2md()
    html_out = md2html(str(md_out))
    return html_out


def install():
    # Add a alias to zshrc
    zshrc_dir = os.path.expanduser('~/.zshrc')
    alias_cmd = f'alias f="python3 {pwd}/app.py -d ."\n'
    with open(zshrc_dir, "a") as f:
        f.writelines([alias_cmd])

    print("Restart The terminal")


if __name__ == "__main__":
    parse_args()
    if args.install:
        install()
    else:
        global sysOS
        sysOS = subprocess.check_output("uname").decode('utf-8')

        # app.debug = True
        app.run(port=args.port)
