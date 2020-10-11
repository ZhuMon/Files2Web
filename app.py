import os
import sys
import json
import argparse
import markdown

parser = argparse.ArgumentParser(
    description='Create a website from exist file')
parser.add_argument('-f', '--file', dest='outfile',
                    default='toc.md', help='choose file to store markdown')
parser.add_argument('-p', '--port', dest='port', default=8090,
                    help='change port to open')
args = parser.parse_args()


class md():
    def __init__(self, level, msg):
        self.level = level
        self.msg = msg
        self.child = []
        self.child_text = []

    def gen_child_text(self, msg, link):
        self.child_text.append(md.indent(self.level+1, f"[{msg}]({link})"))

    def gen_folder(self, msg):
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
    root_md = md(1, ".")
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


def getmd(files):
    None


def md2html(mdstr):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    html = '''
<html lang="zh-cn">
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type" />
<link rel="stylesheet" type="text/css" href="github-syntax-highlight.css">
  <link rel="stylesheet" type="text/css" href="github-markdown.css">
  <link rel="stylesheet" type="text/css" href="mjpage-html.css">
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


def main():
    md_out = files2md()
    html_out = md2html('[TOC]\n' + str(md_out))
    print(html_out)

if __name__ == "__main__":
    main()