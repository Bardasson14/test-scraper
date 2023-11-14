#!/bin/bash

declare -a repositories=(
    # "https://github.com/ankidroid/Anki-Android"
    # "https://github.com/Activiti/Activiti"
    # "https://github.com/antlr/antlr4"
    # "https://github.com/arduino/arduino"
    # "https://github.com/apereo/cas"
    # "https://github.com/eclipse/che"
    # "https://github.com/dbeaver/dbeaver"
    # "https://github.com/dropwizard/dropwizard"
    # "https://github.com/apache/druid"
    # "https://github.com/elastic/elasticsearch"
    # "https://github.com/google/ExoPlayer"
    "https://github.com/gephi/gephi"
    # "https://github.com/gocd/gocd"
    # "https://github.com/apache/hadoop"
    # "https://github.com/adobe/incubator-druid"
    # "https://github.com/sunbufu/incubator-shardingsphere"
    # "https://github.com/jenkinsci/jenkins"
    # "https://github.com/libgdx/libgdx"
    # "https://github.com/netty/netty"
    "https://github.com/sparklemotion/nokogiri"
    # "https://github.com/pinpoint-apm/pinpoint"
    # "https://github.com/processing/processing"
    # "https://github.com/realm/realm-java"
    # "https://github.com/redisson/redisson"
    # "https://github.com/ReactiveX/RxJava"
    # "https://github.com/apache/skywalking"
    # "https://github.com/spring-projects/spring-framework"
    # "https://github.com/zaproxy/zaproxy"
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