#!/bin/bash

cd external_converters/java
mvn clean package

cd ../../external_converters/node
npm install
npm run build