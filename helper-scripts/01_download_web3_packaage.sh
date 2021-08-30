#!/bin/bash
pip install -r ./requirements.txt
echo "please activate virtualenv before run this command"
mkdir ./package
pip install --target ./package web3