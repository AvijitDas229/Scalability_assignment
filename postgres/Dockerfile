ARG TARGETARCH
FROM --platform=$TARGETARCH postgres:17

# Copy individual init files for shards
COPY init-shard.sh /docker-entrypoint-initdb.d/init-shard.sh
COPY init-sharding.sql /docker-entrypoint-initdb.d/init-sharding.sql

# Ensure shell script is executable
RUN chmod +x /docker-entrypoint-initdb.d/init-shard.sh
