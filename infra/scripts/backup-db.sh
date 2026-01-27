#!/bin/bash

# Database backup script
# Creates a timestamped backup of the PostgreSQL database

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting database backup..."
docker-compose exec -T postgres pg_dump -U postgres phd_timeline_db > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "Backup completed: ${BACKUP_FILE}.gz"

# Optional: Delete backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Old backups cleaned up"
