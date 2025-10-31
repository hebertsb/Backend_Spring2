import os
import sys
import zipfile
import shutil
from pathlib import Path
import subprocess
from urllib.parse import urlparse
from condominio.backups.utils import BACKUP_DIR  # Usa la ruta centralizada

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def restore_backup(backup_zip_path: Path, restore_code=True, restore_db=True):
    """
    Restaura un backup .zip (creado por backup_full.py o por la API).
    Compatible con SQLite, PostgreSQL y fixtures JSON.
    """
    if not backup_zip_path.exists():
        msg = f"❌ No se encontró el backup: {backup_zip_path}"
        print(msg)
        return {"error": msg}

    # Carpeta temporal para descomprimir
    temp_dir = BACKUP_DIR / "restore_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    print(f"📦 Descomprimiendo backup {backup_zip_path.name} en {temp_dir}")
    with zipfile.ZipFile(backup_zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # ------------------------------------
    # DETECTAR TIPO DE BACKUP (NUEVO)
    # ------------------------------------
    backup_type = detect_backup_type(temp_dir)
    print(f"🔍 Tipo de backup detectado: {backup_type}")

    # ------------------------------------
    # Restaurar código backend
    # ------------------------------------
    if restore_code:
        # Buscar backend_code en diferentes ubicaciones posibles
        backend_code_dirs = [
            temp_dir / "backend_code",  # Backups manuales
            next(temp_dir.glob("backend_code_*"), None),  # Backups automáticos
        ]
        
        backend_code_dir = None
        for possible_dir in backend_code_dirs:
            if possible_dir and possible_dir.exists():
                backend_code_dir = possible_dir
                break

        if backend_code_dir:
            print("📝 Restaurando código backend completo...")

            include_dirs = ["condominio", "core", "authz", "config", "scripts"]
            for folder in include_dirs:
                src = backend_code_dir / folder
                dst = BASE_DIR / folder

                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"✅ Carpeta restaurada: {folder}")
        else:
            print("⚠️ No se encontró carpeta de código backend en el backup.")

    # ------------------------------------
    # Restaurar base de datos
    # ------------------------------------
    if restore_db:
        print("🗄️ Restaurando base de datos...")

        # Buscar archivo de base de datos dentro del backup
        sqlite_file = temp_dir / "db.sqlite3"
        postgres_dump = next(temp_dir.glob("*.sql"), None)
        json_files = list(temp_dir.glob("*.json"))

        # Obtener configuración de Postgres
        DATABASE_URL = get_database_url()
        
        # ------------------- SQLite -------------------
        if sqlite_file.exists():
            dst_db = BASE_DIR / "db.sqlite3"
            if dst_db.exists():
                # Hacer backup de la BD actual antes de reemplazar
                backup_current_db(dst_db)
                dst_db.unlink()
            shutil.copy2(sqlite_file, dst_db)
            print(f"✅ Base de datos SQLite restaurada: {dst_db}")

        # ------------------- PostgreSQL -------------------
        elif postgres_dump:
            print(f"🔄 Restaurando dump PostgreSQL: {postgres_dump.name}")
            restore_postgresql(DATABASE_URL, postgres_dump)

        # ------------------- JSON Fixtures -------------------
        elif json_files:
            restore_json_fixtures(json_files)
        else:
            print("⚠️ No se encontró base de datos, dump o fixture JSON.")

    # ------------------------------------
    # Ejecutar migraciones (NUEVO)
    # ------------------------------------
    if restore_db:
        print("🔄 Ejecutando migraciones de Django...")
        run_django_migrations()

    # ------------------------------------
    # Limpieza final
    # ------------------------------------
    try:
        shutil.rmtree(temp_dir)
        print("🧹 Carpeta temporal eliminada. Restore finalizado con éxito.")
    except Exception as e:
        print(f"⚠️ No se pudo eliminar carpeta temporal: {e}")

    return {"message": f"Backup {backup_zip_path.name} restaurado correctamente"}


# ====================================================
#   FUNCIONES AUXILIARES (NUEVAS)
# ====================================================

def detect_backup_type(temp_dir: Path) -> str:
    """Detecta si el backup es manual o automático"""
    if (temp_dir / "backend_code").exists():
        return "manual"
    elif any(temp_dir.glob("backend_code_*")):
        return "automatic"
    else:
        return "unknown"

def get_database_url() -> str:
    """Obtiene la URL de la base de datos (compartida con backup_full.py)"""
    DATABASE_URL = (
        os.getenv("DATABASE_URL")
        or os.getenv("PG_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("RAILWAY_DATABASE_URL")
    )

    if not DATABASE_URL or "${" in DATABASE_URL:
        pg_user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
        pg_password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
        pg_host = os.getenv("RAILWAY_PRIVATE_DOMAIN") or os.getenv("RAILWAY_TCP_PROXY_DOMAIN") or "localhost"
        pg_port = os.getenv("PGPORT") or os.getenv("RAILWAY_TCP_PROXY_PORT") or "5432"
        pg_db = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "railway"

        DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    
    return DATABASE_URL

def backup_current_db(db_path: Path):
    """Crea un backup de la base de datos actual antes de restaurar"""
    backup_path = BACKUP_DIR / f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
    shutil.copy2(db_path, backup_path)
    print(f"📋 Backup de BD actual creado: {backup_path.name}")

def restore_postgresql(database_url: str, postgres_dump: Path):
    """Restaura un dump de PostgreSQL"""
    try:
        parsed = urlparse(database_url)
        pg_user = parsed.username
        pg_password = parsed.password
        pg_host = parsed.hostname
        pg_port = parsed.port or "5432"
        pg_db = parsed.path.lstrip("/")
        
        os.environ["PGPASSWORD"] = pg_password or ""

        # Primero dropear y recrear la base de datos para limpieza completa
        print("🧹 Limpiando base de datos existente...")
        subprocess.run([
            "psql",
            "-U", pg_user,
            "-h", pg_host,
            "-p", str(pg_port),
            "-d", "postgres",  # Conectarse a postgres para poder dropear la BD
            "-c", f"DROP DATABASE IF EXISTS {pg_db}; CREATE DATABASE {pg_db};"
        ], check=False)  # No fallar si no puede dropear

        # Restaurar el dump
        print("🔄 Restaurando datos...")
        result = subprocess.run([
            "psql",
            "-U", pg_user,
            "-h", pg_host,
            "-p", str(pg_port),
            "-d", pg_db,
            "-f", str(postgres_dump)
        ])

        if result.returncode == 0:
            print("✅ Base de datos PostgreSQL restaurada correctamente.")
        else:
            print("❌ Error al restaurar PostgreSQL")

    except Exception as e:
        print(f"❌ Error al restaurar PostgreSQL: {e}")

def restore_json_fixtures(json_files: list):
    """Restaura fixtures JSON de Django"""
    for json_file in json_files:
        print(f"🔄 Restaurando fixture JSON: {json_file.name}")
        result = subprocess.run([
            sys.executable, str(BASE_DIR / "manage.py"),
            "loaddata", str(json_file)
        ])
        if result.returncode == 0:
            print(f"✅ Fixture {json_file.name} restaurado.")
        else:
            print(f"⚠️ Error restaurando fixture {json_file.name}")

def run_django_migrations():
    """Ejecuta las migraciones de Django después de restaurar"""
    try:
        # Aplicar migraciones
        subprocess.run([
            sys.executable, str(BASE_DIR / "manage.py"),
            "migrate"
        ], check=True)
        print("✅ Migraciones aplicadas correctamente.")
        
        # Recolectar archivos estáticos (opcional)
        subprocess.run([
            sys.executable, str(BASE_DIR / "manage.py"),
            "collectstatic", "--noinput"
        ], check=False)
        print("✅ Archivos estáticos actualizados.")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error ejecutando migraciones: {e}")


# ====================================================
#   CLI (MEJORADA)
# ====================================================
if __name__ == "__main__":
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Restore backup Django (SQLite, PostgreSQL o fixtures)")
    parser.add_argument("--select", action="store_true", help="Seleccionar backup a restaurar")
    parser.add_argument("--no-code", action="store_true", help="No restaurar código")
    parser.add_argument("--no-db", action="store_true", help="No restaurar base de datos")
    parser.add_argument("--file", type=str, help="Ruta específica del archivo backup a restaurar")
    parser.add_argument("--list", action="store_true", help="Listar backups disponibles y salir")
    args = parser.parse_args()

    backup_files = sorted(BACKUP_DIR.glob("*.zip"), key=os.path.getmtime, reverse=True)
    
    if args.list:
        print("📋 Backups disponibles:")
        for idx, f in enumerate(backup_files, 1):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"{idx}. {f.name} ({size_mb:.1f} MB)")
        sys.exit(0)

    if not backup_files:
        print(f"❌ No se encontraron backups en {BACKUP_DIR}")
        sys.exit(1)

    if args.file:
        # Restaurar archivo específico
        backup_to_restore = BACKUP_DIR / args.file
        if not backup_to_restore.exists():
            print(f"❌ No se encontró el backup: {args.file}")
            sys.exit(1)
    elif args.select:
        # Selección interactiva
        print("📋 Backups disponibles:")
        for idx, f in enumerate(backup_files, 1):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"{idx}. {f.name} ({size_mb:.1f} MB)")
        
        try:
            choice = input("Selecciona el backup a restaurar (número): ")
            idx = int(choice) - 1
            backup_to_restore = backup_files[idx]
        except (ValueError, IndexError):
            print("❌ Selección inválida")
            sys.exit(1)
    else:
        # Usar el backup más reciente
        backup_to_restore = backup_files[0]

    print(f"🎯 Restaurando backup: {backup_to_restore.name}")
    
    restore_backup(
        backup_to_restore,
        restore_code=not args.no_code,
        restore_db=not args.no_db,
    )