import os
import shutil
from datetime import datetime
from pathlib import Path
import subprocess
import zipfile
import argparse
import sys

# ---------------------------
# Configuración de rutas
# ---------------------------

# Raíz del proyecto (donde está manage.py y db.sqlite3)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Carpeta backend
BACKEND_DIR = PROJECT_ROOT / "condominio"

# Carpeta backups
BACKUP_ROOT = BACKEND_DIR / "backups"

# Carpeta frontend (opcional)
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Base de datos SQLite (puede estar fuera de condominio)
SQLITE_FILE = PROJECT_ROOT / "db.sqlite3"

# Archivo manage.py
MANAGE_PY = PROJECT_ROOT / "manage.py"

# ---------------------------
# Función de backup
# ---------------------------

def run_backup(include_backend=True, include_db=True, include_frontend=True, db_type="sqlite"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / f"backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)

    print(f"Creando backup en: {backup_dir}")

    # -------------------
    # Backup de base de datos
    # -------------------
    if include_db:
        if db_type.lower() == "sqlite":
            if SQLITE_FILE.exists():
                shutil.copy(SQLITE_FILE, backup_dir / SQLITE_FILE.name)
                print(f"Base de datos SQLite copiada: {SQLITE_FILE.name}")
            else:
                print("No se encontró archivo de base de datos SQLite.")
        elif db_type.lower() == "postgres":
            # Dump de postgres usando pg_dump (requiere que esté en PATH)
            pg_dump_file = backup_dir / f"postgres_dump_{timestamp}.sql"
            print("Realizando backup de Postgres...")
            result = subprocess.run([
                "pg_dump",
                "-U", os.getenv("POSTGRES_USER", "postgres"),
                "-h", os.getenv("POSTGRES_HOST", "localhost"),
                "-p", os.getenv("POSTGRES_PORT", "5432"),
                "-F", "c",
                "-f", str(pg_dump_file),
                os.getenv("POSTGRES_DB", "mydatabase")
            ])
            if result.returncode == 0:
                print(f"Dump de Postgres generado: {pg_dump_file.name}")
            else:
                print("Error al realizar backup de Postgres.")

    # -------------------
    # Backup de backend
    # -------------------
    if include_backend:
        # Copiar migraciones
        migrations_dir = BACKEND_DIR / "core" / "migrations"
        if migrations_dir.exists():
            shutil.copytree(migrations_dir, backup_dir / "migrations")
            print("Migraciones copiadas.")
        else:
            print("No se encontraron migraciones.")

        # Copiar todo el backend sin duplicar la carpeta condominio
        backend_backup_dir = backup_dir / "backend_code"
        shutil.copytree(BACKEND_DIR, backend_backup_dir, ignore=shutil.ignore_patterns('venv', '__pycache__', 'backups'))
        print("Código backend copiado.")

    # -------------------
    # Backup de frontend
    # -------------------
    if include_frontend:
        if FRONTEND_DIR.exists():
            frontend_backup_dir = backup_dir / "frontend_code"
            shutil.copytree(FRONTEND_DIR, frontend_backup_dir, ignore=shutil.ignore_patterns('node_modules', '.next', 'build'))
            print("Código frontend copiado.")
        else:
            print("No se encontró carpeta frontend.")

    # -------------------
    # Backup de datos de la base de datos en JSON (fixture)
    # Solo para SQLite / Django ORM
    # -------------------
    if include_db and db_type.lower() == "sqlite":
        if MANAGE_PY.exists():
            json_backup_file = backup_dir / f"dump_{timestamp}.json"
            subprocess.run([
                sys.executable, str(MANAGE_PY), "dumpdata",
                "--exclude", "auth.permission",
                "--exclude", "contenttypes",
                "--indent", "2",
                "--output", str(json_backup_file)
            ])
            print(f"Fixture JSON generada: {json_backup_file.name}")
        else:
            print("No se encontró manage.py, no se pudo generar fixture JSON.")

    # -------------------
    # Comprimir todo en ZIP
    # -------------------
    zip_file = BACKUP_ROOT / f"full_backup_{timestamp}.zip"
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, file_path.relative_to(backup_dir))
    print(f"Backup completo comprimido en: {zip_file}")
    print("✅ Backup finalizado con éxito.")

# ---------------------------
# Ejecución desde CLI
# ---------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup Django")
    parser.add_argument("--no-backend", action="store_true", help="No incluir código backend")
    parser.add_argument("--no-db", action="store_true", help="No incluir base de datos")
    parser.add_argument("--no-frontend", action="store_true", help="No incluir frontend")
    parser.add_argument("--db-type", choices=["sqlite", "postgres"], default="sqlite", help="Tipo de base de datos")
    args = parser.parse_args()

    run_backup(
        include_backend=not args.no_backend,
        include_db=not args.no_db,
        include_frontend=not args.no_frontend,
        db_type=args.db_type
    )
