#!/bin/bash

ENV_PATH='/usr/local/bin/termbot'

# 1. Build termbot
#
go build .

# 2. Add termbot to path
read -p "Add termbot to path $ENV_PATH? (y/n): " ANSWER
if [ "$ANSWER" = "y" ]; then
  sudo mv termbot $ENV_PATH
fi

echo "Run termbot with 'termbot'"
