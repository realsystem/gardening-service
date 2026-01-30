# Data Persistence Guide

This guide explains how data is stored persistently and how to backup/restore your gardening database.

## Local Persistent Storage

All database data is stored in the local `.data/postgres/` directory. This means:

✅ **Data survives container recreation** - You can safely run `docker-compose down` and `docker-compose up` without losing data
✅ **Easy backups** - Simply copy the `.data/` directory
✅ **Version control safe** - `.data/` is in `.gitignore` so sensitive data isn't committed
✅ **Portable** - Move the entire project folder and data moves with it

### Storage Location

```
gardening-service/
├── .data/
│   └── postgres/          # PostgreSQL data files (gitignored)
├── backups/               # SQL backups (gitignored)
├── backup_database.sh     # Backup script
└── restore_database.sh    # Restore script
```

## Safe Container Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services (KEEPS DATA)
```bash
docker-compose down
```
**Note:** This stops containers but preserves all data in `.data/postgres/`

### Rebuild Containers (KEEPS DATA)
```bash
docker-compose down
docker-compose up -d --build
```
**Note:** Rebuilds images but keeps all database data

### Full Reset (DELETES ALL DATA)
```bash
docker-compose down
rm -rf .data/postgres/
docker-compose up -d
# Run migrations: docker-compose exec api alembic upgrade head
```
**Warning:** Only do this if you want to start fresh!

## Backup & Restore

### Create a Backup

```bash
./backup_database.sh
```

This creates a timestamped SQL dump in `backups/`:
```
backups/gardening_db_20260129_221500.sql
```

### Restore from Backup

```bash
./restore_database.sh backups/gardening_db_20260129_221500.sql
```

**Warning:** This will overwrite your current database!

### Manual Backup (Alternative)

```bash
# Export database to SQL file
docker-compose exec -T db pg_dump -U gardener gardening_db > my_backup.sql

# Restore from SQL file
cat my_backup.sql | docker-compose exec -T db psql -U gardener gardening_db
```

## Migrating Data to New Machine

### Option 1: Copy Entire Directory
```bash
# On old machine
cd /path/to/gardening-service
docker-compose down
tar czf gardening-service-backup.tar.gz .data/

# On new machine
tar xzf gardening-service-backup.tar.gz
docker-compose up -d
```

### Option 2: Use SQL Backup
```bash
# On old machine
./backup_database.sh
# Copy backups/gardening_db_*.sql to new machine

# On new machine
docker-compose up -d
docker-compose exec api alembic upgrade head
./restore_database.sh backups/gardening_db_*.sql
```

## Database Maintenance

### View Database Size
```bash
docker-compose exec db psql -U gardener -d gardening_db -c "
SELECT
  pg_size_pretty(pg_database_size('gardening_db')) AS size;
"
```

### Vacuum Database (Clean Up)
```bash
docker-compose exec db psql -U gardener -d gardening_db -c "VACUUM ANALYZE;"
```

### Connect to Database
```bash
docker-compose exec db psql -U gardener -d gardening_db
```

## Troubleshooting

### Issue: Permission Errors

If you get permission errors with `.data/postgres/`:

```bash
# Fix ownership (macOS/Linux)
sudo chown -R $(id -u):$(id -g) .data/
```

### Issue: Database Won't Start

```bash
# Check logs
docker-compose logs db

# If corrupted, restore from backup
docker-compose down
rm -rf .data/postgres/
docker-compose up -d
./restore_database.sh backups/your_backup.sql
```

### Issue: Lost Data After Rebuild

If you lost data after rebuilding containers, check:
1. Did you run `docker volume rm`? (This deletes data)
2. Is `.data/postgres/` empty? (Should contain database files)
3. Check docker-compose.yml has: `- ./.data/postgres:/var/lib/postgresql/data`

## Best Practices

1. **Regular Backups**: Run `./backup_database.sh` before major changes
2. **Keep Multiple Backups**: Don't delete old backups immediately
3. **Test Restores**: Occasionally test that restores work
4. **Never Commit .data/**: It's in .gitignore for security
5. **Use Backups for Production**: Before deploying, create a backup

## Production Considerations

For production deployments:
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
- Set up automated backups
- Use environment-specific credentials
- Enable SSL/TLS for database connections
- Implement point-in-time recovery

## Summary

**Your data is safe as long as `.data/postgres/` exists.**

- ✅ Stop/start containers: **Data persists**
- ✅ Rebuild containers: **Data persists**
- ✅ Update code: **Data persists**
- ❌ Delete `.data/`: **Data lost** (use backups!)
- ❌ Run `docker volume rm`: **Data lost** (but we use bind mounts now, so this doesn't apply)
