#!/bin/sh

# ./target/release/latency plot --delivery alo -t "Q1 Sys/Boki" -o plots/boki-1-alo.png data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms/*
# ./target/release/latency plot --delivery eo -t "Q1 Sys/Boki" -o plots/boki-1-eo.png data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms/*

# ./target/release/latency plot --delivery alo -t "Q2 Sys/Boki" -o plots/boki-2-alo.png data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms/*
# ./target/release/latency plot --delivery eo -t "Q2 Sys/Boki" -o plots/boki-2-eo.png data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms/*

# ./target/release/latency plot --delivery alo -t "Q3 Sys/Boki" -o plots/boki-3-alo.png data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q3 Sys/Boki" -o plots/boki-3-eo.png data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q4 Sys/Boki" -o plots/boki-4-alo.png data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q4 Sys/Boki" -o plots/boki-4-eo.png data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q5 Sys/Boki" -o plots/boki-5-alo.png data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q5 Sys/Boki" -o plots/boki-5-eo.png data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q6 Sys/Boki" -o plots/boki-6-alo.png data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q6 Sys/Boki" -o plots/boki-6-eo.png data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q7 Sys/Boki" -o plots/boki-7-alo.png data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q7 Sys/Boki" -o plots/boki-7-eo.png data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q8 Sys/Boki" -o plots/boki-8-alo.png data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q8 Sys/Boki" -o plots/boki-8-eo.png data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms/*

# # Kafka

# ./target/release/latency plot --delivery alo -t "Q1 Kafka" -o plots/kafka-1-alo.png data/kafka/q1-kafka-180s-0swarm-100ms-src10ms/*
# ./target/release/latency plot --delivery eo -t "Q1 Kafka" -o plots/kafka-1-eo.png data/kafka/q1-kafka-180s-0swarm-100ms-src10ms/*

# ./target/release/latency plot --delivery alo -t "Q2 Kafka" -o plots/kafka-2-alo.png data/kafka/q2-kafka-180s-0swarm-100ms-src10ms/*
# ./target/release/latency plot --delivery eo -t "Q2 Kafka" -o plots/kafka-2-eo.png data/kafka/q2-kafka-180s-0swarm-100ms-src10ms/*

# ./target/release/latency plot --delivery alo -t "Q3 Kafka" -o plots/kafka-3-alo.png data/kafka/q3-kafka-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q3 Kafka" -o plots/kafka-3-eo.png data/kafka/q3-kafka-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q4 Kafka" -o plots/kafka-4-alo.png data/kafka/q4-kafka-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q4 Kafka" -o plots/kafka-4-eo.png data/kafka/q4-kafka-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q5 Kafka" -o plots/kafka-5-alo.png data/kafka/q5-kafka-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q5 Kafka" -o plots/kafka-5-eo.png data/kafka/q5-kafka-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q6 Kafka" -o plots/kafka-6-alo.png data/kafka/q6-kafka-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q6 Kafka" -o plots/kafka-6-eo.png data/kafka/q6-kafka-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q7 Kafka" -o plots/kafka-7-alo.png data/kafka/q7-kafka-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q7 Kafka" -o plots/kafka-7-eo.png data/kafka/q7-kafka-180s-0swarm-100ms-src100ms/*

# ./target/release/latency plot --delivery alo -t "Q8 Kafka" -o plots/kafka-8-alo.png data/kafka/q8-kafka-180s-0swarm-100ms-src100ms/*
# ./target/release/latency plot --delivery eo -t "Q8 Kafka" -o plots/kafka-8-eo.png data/kafka/q8-kafka-180s-0swarm-100ms-src100ms/*

# # Distributions

# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d alo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-alo.png
# ./target/release/latency compare -t "Q2 Kafka vs. Sys" -d alo -k data/kafka/q2-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms --output distributions/q2-alo.png
# ./target/release/latency compare -t "Q3 Kafka vs. Sys" -d alo -k data/kafka/q3-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms --output distributions/q3-alo.png
# ./target/release/latency compare -t "Q4 Kafka vs. Sys" -d alo -k data/kafka/q4-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms --output distributions/q4-alo.png
# ./target/release/latency compare -t "Q5 Kafka vs. Sys" -d alo -k data/kafka/q5-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms --output distributions/q5-alo.png
# ./target/release/latency compare -t "Q6 Kafka vs. Sys" -d alo -k data/kafka/q6-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms --output distributions/q6-alo.png
# ./target/release/latency compare -t "Q7 Kafka vs. Sys" -d alo -k data/kafka/q7-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms --output distributions/q7-alo.png
# ./target/release/latency compare -t "Q8 Kafka vs. Sys" -d alo -k data/kafka/q8-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms --output distributions/q8-alo.png

# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo.png
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-4000.png --include 4000
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-16000.png --include 16000
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-32000.png --include 32000
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-64000.png --include 64000
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-72000.png --include 72000
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-80000.png --include 80000
# ./target/release/latency compare -t "Q1 Kafka vs. Sys" -d eo -k data/kafka/q1-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q1-boki-180s-0swarm-100ms-src10ms --output distributions/q1-eo-88000.png --include 88000

# ./target/release/latency compare -t "Q2 Kafka vs. Sys" -d eo -k data/kafka/q2-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms --output distributions/q2-eo-4000.png --include 4000
# ./target/release/latency compare -t "Q2 Kafka vs. Sys" -d eo -k data/kafka/q2-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms --output distributions/q2-eo-64000.png --include 64000
# ./target/release/latency compare -t "Q2 Kafka vs. Sys" -d eo -k data/kafka/q2-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms --output distributions/q2-eo-80000.png --include 80000
# ./target/release/latency compare -t "Q2 Kafka vs. Sys" -d eo -k data/kafka/q2-kafka-180s-0swarm-100ms-src10ms -s data/sys-boki/q2-boki-180s-0swarm-100ms-src10ms --output distributions/q2-eo-100000.png --include 100000

# ./target/release/latency compare -t "Q3 Kafka vs. Sys" -d eo -k data/kafka/q3-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms --output distributions/q3-eo-16000.png --include 16000
# ./target/release/latency compare -t "Q3 Kafka vs. Sys" -d eo -k data/kafka/q3-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms --output distributions/q3-eo-32000.png --include 32000
# ./target/release/latency compare -t "Q3 Kafka vs. Sys" -d eo -k data/kafka/q3-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q3-boki-180s-0swarm-100ms-src100ms --output distributions/q3-eo-48000.png --include 48000
./target/release/latency compare -t "Q3 Kafka vs. Sys" -d eo -k curated/kafka/q3-kafka-180s-0swarm-100ms-src100ms -s curated/sys-boki/q3-boki-180s-0swarm-100ms-src100ms --output distributions/q3-eo-64000.png --include 64000

# ./target/release/latency compare -t "Q4 Kafka vs. Sys" -d eo -k data/kafka/q4-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms --output distributions/q4-eo-500.png --include 500
# ./target/release/latency compare -t "Q4 Kafka vs. Sys" -d eo -k data/kafka/q4-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms --output distributions/q4-eo-750.png --include 750
# ./target/release/latency compare -t "Q4 Kafka vs. Sys" -d eo -k data/kafka/q4-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q4-boki-180s-0swarm-100ms-src100ms --output distributions/q4-eo-1000.png --include 1000

# ./target/release/latency compare -t "Q5 Kafka vs. Sys" -d eo -k data/kafka/q5-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms --output distributions/q5-eo-6000.png --include 6000
# ./target/release/latency compare -t "Q5 Kafka vs. Sys" -d eo -k data/kafka/q5-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms --output distributions/q5-eo-12000.png --include 12000
# ./target/release/latency compare -t "Q5 Kafka vs. Sys" -d eo -k data/kafka/q5-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q5-boki-180s-0swarm-100ms-src100ms --output distributions/q5-eo-16000.png --include 16000

# ./target/release/latency compare -t "Q6 Kafka vs. Sys" -d eo -k data/kafka/q6-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms --output distributions/q6-eo-375.png --include 375
# ./target/release/latency compare -t "Q6 Kafka vs. Sys" -d eo -k data/kafka/q6-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms --output distributions/q6-eo-625.png --include 625
# ./target/release/latency compare -t "Q6 Kafka vs. Sys" -d eo -k data/kafka/q6-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q6-boki-180s-0swarm-100ms-src100ms --output distributions/q6-eo-750.png --include 750

# ./target/release/latency compare -t "Q7 Kafka vs. Sys" -d eo -k data/kafka/q7-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms --output distributions/q7-eo.png
# ./target/release/latency compare -t "Q7 Kafka vs. Sys" -d eo -k data/kafka/q7-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms --output distributions/q7-eo-250.png --include 250
# ./target/release/latency compare -t "Q7 Kafka vs. Sys" -d eo -k data/kafka/q7-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms --output distributions/q7-eo-1000.png --include 1000
# ./target/release/latency compare -t "Q7 Kafka vs. Sys" -d eo -k data/kafka/q7-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q7-boki-180s-0swarm-100ms-src100ms --output distributions/q7-eo-4000.png --include 4000

./target/release/latency compare -t "Q8 Kafka vs. Sys" -d eo -k data/kafka/q8-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms --output distributions/q8-eo.png
# ./target/release/latency compare -t "Q8 Kafka vs. Sys" -d eo -k data/kafka/q8-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms --output distributions/q8-eo-8000.png --include=8000
# ./target/release/latency compare -t "Q8 Kafka vs. Sys" -d eo -k data/kafka/q8-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms --output distributions/q8-eo-12000.png --include=12000
# ./target/release/latency compare -t "Q8 Kafka vs. Sys" -d eo -k data/kafka/q8-kafka-180s-0swarm-100ms-src100ms -s data/sys-boki/q8-boki-180s-0swarm-100ms-src100ms --output distributions/q8-eo-16000.png --include=16000
