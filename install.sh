#!/bin/sh
set -xe

if [ $SHELL = '/bin/bash' ]
then
    echo "alias f=\"python3 $PWD/app.py -d .\"" >> ~/.bashrc
elif [ $SHELL = '/bin/zsh' ]
then
    echo "alias f=\"python3 $PWD/app.py -d .\"" >> ~/.zshrc
fi
