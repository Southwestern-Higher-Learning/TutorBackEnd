#!/bin/sh

echo "Running migrations..."

aerich upgrade

echo "Migrations finished"

exec "$@"