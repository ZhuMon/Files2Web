import os
import sys
import json
import argparse
import markdown
from flask import Flask, send_from_directory

parser = argparse.ArgumentParser(
    description='Create a website from exist file')
parser.add_argument('-f', '--file', dest='outfile',
                    default='toc.md', help='choose file to store markdown')
parser.add_argument('-p', '--port', dest='port', default=8090,
                    help='change port to open')
args = parser.parse_args()

app = Flask("File2Web")

class md():
    def __init__(self, level, msg, father_path):
        self.level = level
        self.msg = msg
        self.child = []
        self.child_text = []
        self.pwd = father_path + '/' + msg if father_path != "" else msg

    def gen_child_text(self, msg, link):
        if msg == "info.txt":
            with open(self.pwd + '/' + msg, 'r') as f:
                for line in f.readlines():
                    self.child_text.append(md.indent(self.level+1, line))
        else:
            self.child_text.append(md.indent(self.level+1, f"[{msg}]({link})"))

    def gen_folder(self, msg):
        child = md(self.level+1, msg, self.pwd)
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
        
        return out

def files2md():
    path = "."
    root_md = md(1, ".", '')
    for (dirpath, dirnames, filenames) in os.walk(path):
        nowpath = dirpath.split('/')
        now_md = root_md
        
        for n in nowpath:
            now_md = now_md.get_child(n)

        for d in dirnames:
            now_md.gen_folder(d)

        for f in sorted(filenames):
            now_md.gen_child_text(f, (dirpath + "/" + f).replace(" ", "%20"))

    root_md.msg = "Abstract"
    root_md.child_text = []
    return root_md




def md2html(mdstr):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    html = '''
<html lang="zh-tw">
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type" />
<link rel="stylesheet" type="text/css" href="/css/github-syntax-highlight.css">
  <link rel="stylesheet" type="text/css" href="/css/github-markdown.css">
  <link rel="stylesheet" type="text/css" href="/css/mjpage-html.css">
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
    ret = markdown.markdown(mdstr,extensions=exts)
    return html % ret
    # return markdown2.markdown(md)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/<path:path>')
def send_file(path):
    if path[-3:] == "pdf":
        return send_from_directory('.', path)
    elif path == 'favicon.ico':
        return send_from_directory('.', "favicon_resized.png")
    elif path[-2:] == "md":
        f = open(path, 'r')
        data = f.read()
        f.close()
        return md2html(data)

@app.route("/")
def mainpage():
    md_out = files2md()
    html_out = md2html('[TOC]\n' + str(md_out))
    return html_out




if __name__ == "__main__":
    app.run(port=args.port)
