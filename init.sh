#!/bin/bash

ROOT="."
LANG="en_US.UTF-8"

#=================================================================================================#
#检查操作系统
OS=$(uname -a|awk '{print $1}')
if [[ ${OS} == "Darwin" ]];then
    echo -e "OS Version:" "\033[32m" ${OS} "\033[0m"
elif [[ ${OS} == "Linux" ]];then
    echo -e "OS Version:" "\033[32m" ${OS} "\033[0m"
else
    echo "Unknown OS Version '${OS}', maybe chatbot will not run successfully."
fi

#检查python版本
PYTHON=$(python -V 2>&1)
if [[ $(echo ${PYTHON}|grep -E "command not found") == "" ]];then
    U_V1=$(echo ${PYTHON}|awk '{print $2}'|awk -F '.' '{print $1}')
    U_V2=$(echo ${PYTHON}|awk '{print $2}'|awk -F '.' '{print $2}')
    U_V3=$(echo ${PYTHON}|awk '{print $2}'|awk -F '.' '{print $3}')
    E_V1=2
    E_V2=7
    echo -e "Except python version: \033[32m2.7.x\033[0m"
    if [[ ${U_V1} == ${E_V1} ]] && [[ ${U_V2} == ${E_V2} ]];then
        echo -e "Local python version: \033[32m$U_V1.$U_V2.$U_V3\033[0m"
    else
        echo -e "Local python version: \033[31m$U_V1.$U_V2.$U_V3\033[0m"
        exit 1
    fi
else
    echo -e "\033[31mThere is no python in your computer\033[0m"
    echo -e "\033[31mInstall it and run this script again!\033[0m"
fi

#检查python依赖的库
#itchat
LIB1="itchat"
RESULT1=$(python -c "import $LIB1" 2>&1)
if [[ $RESULT1 == "" ]];then
    echo -e "Module $LIB1 status:" "\033[32mOK\033[0m"
else
    echo -e "Module $LIB1 status:" "\033[31mNot found\033[0m"
fi

#创建image
if !(test -d "$ROOT/image");then
    mkdir -p "$ROOT/image"
fi
#mkdir ${ROOT}/image
