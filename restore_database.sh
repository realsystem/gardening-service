#!/bin/bash
# Database restore script
# Restores a SQL dump to the PostgreSQL database

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore_database.sh <backup_file.sql>"
    echo ""
    echo "Available backups:"
    ls -1t backups/*.sql 2>/dev/null | head -5 || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring database from: $BACKUP_FILE"
echo "WARNING: This will overwrite existing data!"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Drop and recreate database
docker-compose exec -T db psql -U gardener -d postgres <<EOF
DROP DATABASE IF EXISTS gardening_db;
CREATE DATABASE gardening_db;
EOF

# Restore backup
cat "$BACKUP_FILE" | docker-compose exec -T db psql -U gardener gardening_db

echo "✓ Database restored successfully"
