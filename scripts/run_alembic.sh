#!/bin/bash
set -e

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Set the DATABASE_URL for alembic
export DATABASE_URL=$POSTGRES_URI

# Run alembic with the provided arguments
alembic "$@"
