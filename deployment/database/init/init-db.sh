#!/bin/bash
set -e

clickhouse client -n <<-EOSQL
    CREATE DATABASE IF NOT EXISTS webservice;
    CREATE TABLE IF NOT EXISTS webservice.requests 
    (headers String, body String)
    ENGINE = MergeTree
    ORDER BY (headers, body);
EOSQL