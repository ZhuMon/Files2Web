# Files2Web
Change files representation at localhost to markdown-liked website

## Introduction
Let you read lots of pdf files more conveniently.
The program also help you open the doc/docx file by command (`xdg-open` or `open`) 

## Prerequisite
* python3
* flask
* markdown2
* install dependency
    ```
    $ pip3 install -r requirement.txt
    ```


## Usage
```
$ python3 app.py --help
usage: app.py [-h] [-f OUTFILE] [-p PORT]

Create a website from exist file

optional arguments:
  -h, --help            show this help message and exit
  -f OUTFILE, --file OUTFILE
                        choose file to store markdown
  -p PORT, --port PORT  change port to open
```
