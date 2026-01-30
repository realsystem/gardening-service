#!/bin/bash
# Database backup script
# Creates a SQL dump of the PostgreSQL database

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/gardening_db_${TIMESTAMP}.sql"

# Create backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Creating database backup..."
docker-compose exec -T db pg_dump -U gardener gardening_db > "$BACKUP_FILE"

echo "✓ Backup created: $BACKUP_FILE"
echo ""
echo "To restore this backup:"
echo "  cat $BACKUP_FILE | docker-compose exec -T db psql -U gardener gardening_db"
