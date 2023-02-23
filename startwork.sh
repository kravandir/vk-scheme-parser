#!/usr/bin/env bash
rm -rf ./vk_api_schema > /dev/null
git clone https://github.com/VKCOM/vk-api-schema
mv vk-api-schema vk_api_schema 
cp ./base_gen.py ./vk_api_schema/base.py

echo -e '\n\tAll done!'
