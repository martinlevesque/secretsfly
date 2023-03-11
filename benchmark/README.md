# Benchmark

## Requirements

- ab (sudo apt install apache2-utils)

## Results

We use ab benchmark tool to test the API secrets performance, using the following command:

`ab -H "Authorization: $SECRETSFLY_TOKEN" -c 10 -n 10000 $SECRETSFLY_API_BASE_URL/secrets/`

The following results are obtained on a local laptop machine 4.2 GHz i5-1135G7 (8MB Cache – 4 Cores – 8 Threads), 16 GB RAM, 1 TB PCIe Gen3 Seq Read.

### with concurrency = 10

| # secrets | Requests per second | Latency (ms) |
|:----------|:-------------------:|-------------:|
| 0         |       386.00        |       25.906 |
| 25        |        88.20        |      113.384 |
| 50        |        52.59        |      190.145 |
