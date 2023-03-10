
export SECRETSFLY_TOKEN="" # Your token here
export SECRETSFLY_API_BASE_URL="http://localhost:4430/api"
export SECRETSFLY_UNSAFE_SSL_CERT=true

# Run the benchmark

ab -H "Authorization: $SECRETSFLY_TOKEN" -c 500 -n 1000 $SECRETSFLY_API_BASE_URL/secrets/