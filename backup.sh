#!/bin/bash
DATA=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/www/truffle-finder/backups"
tar -czf "$BACKUP_DIR/truffle_backup_$DATA.tar.gz" --exclude="backups" --exclude="__pycache__" --exclude=".git" .
echo "✅ [SUCESSO] Backup seguro gerado: truffle_backup_$DATA.tar.gz na pasta backups/"
