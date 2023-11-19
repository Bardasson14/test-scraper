#!/bin/bash

declare -a repositories=(
    "https://github.com/apache/druid"
    "https://github.com/Activiti/Activiti"
    "https://github.com/dropwizard/dropwizard"
    "https://github.com/apache/flink"
    "https://github.com/gocd/gocd"
    "https://github.com/apache/hadoop"
    "https://github.com/adobe/incubator-druid"
    "https://github.com/mockito/mockito"
    # "https://github.com/neo4j/neo4j"
    "https://github.com/pinpoint-apm/pinpoint"
    "https://github.com/realm/realm-java"
    "https://github.com/redisson/redisson"
    "https://github.com/ReactiveX/RxJava"
    "https://github.com/zaproxy/zaproxy"
)

mkdir projects
mkdir projects/output

for value in ${repositories[@]}
do
    repo=$(echo $value | cut -d'/' -f5)
    mkdir projects/$repo
    echo "Clonando $repo..."
    git clone $value /projects/$repo
    echo $repo
    mkdir -p output/$repo
    touch output/$repo/history.csv
done