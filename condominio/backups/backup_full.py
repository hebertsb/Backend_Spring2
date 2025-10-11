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

# Carpeta de backups (única, dentro de condominio/backups)
BACKUP_ROOT = PROJECT_ROOT / "condominio" / "backups"

# Base de datos SQLite
SQLITE_FILE = PROJECT_ROOT / "db.sqlite3"

# Archivo manage.py
MANAGE_PY = PROJECT_ROOT / "manage.py"

# ---------------------------
# Función de backup
# ---------------------------

def run_backup(include_backend=True, include_db=True, include_frontend=True, db_type="sqlite"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_backup_dir = BACKUP_ROOT / f"backup_temp_{timestamp}"
    os.makedirs(temp_backup_dir, exist_ok=True)

    print(f"📦 Creando backup temporal en: {temp_backup_dir}")

    # -------------------
    # Backup de base de datos
    # -------------------
    if include_db:
        if db_type.lower() == "sqlite":
            if SQLITE_FILE.exists():
                shutil.copy(SQLITE_FILE, temp_backup_dir / SQLITE_FILE.name)
                print(f"🗄️ Base de datos SQLite copiada: {SQLITE_FILE.name}")
            else:
                print("⚠️ No se encontró archivo de base de datos SQLite.")
        elif db_type.lower() == "postgres":
            pg_dump_file = temp_backup_dir / f"postgres_dump_{timestamp}.sql"
            print("💾 Realizando backup de Postgres...")
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
                print(f"✅ Dump de Postgres generado: {pg_dump_file.name}")
            else:
                print("❌ Error al realizar backup de Postgres.")

    # -------------------
    # Backup de backend
    # -------------------
    if include_backend:
        include_dirs = ["condominio", "core", "authz", "config", "scripts"]
        exclude_patterns = ['venv', '__pycache__', 'backups', 'node_modules']

        backend_backup_dir = temp_backup_dir / "backend_code"
        os.makedirs(backend_backup_dir, exist_ok=True)

        print("📝 Copiando código backend completo...")
        for include_dir in include_dirs:
            src = PROJECT_ROOT / include_dir
            if not src.exists():
                continue
            dst = backend_backup_dir / include_dir
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*exclude_patterns))
        print("✅ Código backend copiado correctamente.")

    # -------------------
    # Backup de datos JSON (fixtures)
    # -------------------
    if include_db and db_type.lower() == "sqlite":
        if MANAGE_PY.exists():
            json_backup_file = temp_backup_dir / f"dump_{timestamp}.json"
            subprocess.run([
                sys.executable, str(MANAGE_PY), "dumpdata",
                "--exclude", "auth.permission",
                "--exclude", "contenttypes",
                "--indent", "2",
                "--output", str(json_backup_file)
            ])
            print(f"🧾 Fixture JSON generada: {json_backup_file.name}")
        else:
            print("⚠️ No se encontró manage.py, no se pudo generar fixture JSON.")

    # -------------------
    # Comprimir todo en ZIP
    # -------------------
    zip_file = BACKUP_ROOT / f"full_backup_{timestamp}.zip"
    print(f"📁 Comprimiendo backup final en: {zip_file}")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_backup_dir):
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, file_path.relative_to(temp_backup_dir))
    print(f"✅ Backup completo comprimido en: {zip_file}")

    # Limpiar carpeta temporal
    shutil.rmtree(temp_backup_dir)
    print("🧹 Carpeta temporal eliminada. Backup finalizado con éxito.")

# ---------------------------
# Ejecución desde CLI
# ---------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup Django completo")
    parser.add_argument("--no-backend", action="store_true", help="No incluir código backend")
    parser.add_argument("--no-db", action="store_true", help="No incluir base de datos")
    parser.add_argument("--no-frontend", action="store_true", help="No incluir frontend (solo si existe)")
    parser.add_argument("--db-type", choices=["sqlite", "postgres"], default="sqlite", help="Tipo de base de datos")
    args = parser.parse_args()

    run_backup(
        include_backend=not args.no_backend,
        include_db=not args.no_db,
        include_frontend=not args.no_frontend,
        db_type=args.db_type
    )
