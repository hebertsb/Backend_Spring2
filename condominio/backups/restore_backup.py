import os
import sys
import zipfile
import shutil
from pathlib import Path
import subprocess
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
    # Restaurar código backend
    # ------------------------------------
    if restore_code:
        backend_code_dir = temp_dir / "backend_code"
        if backend_code_dir.exists():
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
            print("⚠️ No se encontró carpeta 'backend_code' en el backup.")

    # ------------------------------------
    # Restaurar base de datos
    # ------------------------------------
    if restore_db:
        print("🗄️ Restaurando base de datos...")

        from urllib.parse import urlparse
        DATABASE_URL = os.getenv("DATABASE_URL")

        sqlite_file = temp_dir / "db.sqlite3"
        postgres_dump = next(temp_dir.glob("*.sql"), None)
        json_files = list(temp_dir.glob("*.json"))

        # ------------------- SQLite -------------------
        if sqlite_file.exists():
            dst_db = BASE_DIR / "db.sqlite3"
            if dst_db.exists():
                dst_db.unlink()
            shutil.copy2(sqlite_file, dst_db)
            print(f"✅ Base de datos SQLite restaurada: {dst_db}")

        # ------------------- PostgreSQL -------------------
        elif postgres_dump:
            print(f"🔄 Restaurando dump PostgreSQL: {postgres_dump.name}")

            if DATABASE_URL:
                parsed = urlparse(DATABASE_URL)
                pg_user = parsed.username
                pg_password = parsed.password
                pg_host = parsed.hostname
                pg_port = parsed.port or "5432"
                pg_db = parsed.path.lstrip("/")
            else:
                pg_user = os.getenv("POSTGRES_USER", "postgres")
                pg_password = os.getenv("POSTGRES_PASSWORD", "")
                pg_host = os.getenv("POSTGRES_HOST", "localhost")
                pg_port = os.getenv("POSTGRES_PORT", "5432")
                pg_db = os.getenv("POSTGRES_DB", "mydatabase")

            os.environ["PGPASSWORD"] = pg_password or ""

            result = subprocess.run([
                "pg_restore",
                "-U", pg_user,
                "-h", pg_host,
                "-p", str(pg_port),
                "-d", pg_db,
                str(postgres_dump)
            ])

            if result.returncode == 0:
                print("✅ Base de datos PostgreSQL restaurada correctamente.")
            else:
                print("❌ Error al restaurar la base de datos PostgreSQL.")

        # ------------------- JSON Fixtures -------------------
        elif json_files:
            for json_file in json_files:
                print(f"🔄 Restaurando fixture JSON: {json_file.name}")
                subprocess.run([
                    sys.executable, str(BASE_DIR / "manage.py"),
                    "loaddata", str(json_file)
                ])
            print("✅ Fixtures restaurados.")
        else:
            print("⚠️ No se encontró base de datos, dump o fixture JSON.")

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
#   CLI (para uso directo desde terminal)
# ====================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Restore backup Django")
    parser.add_argument("--select", action="store_true", help="Seleccionar backup a restaurar")
    parser.add_argument("--no-code", action="store_true", help="No restaurar código")
    parser.add_argument("--no-db", action="store_true", help="No restaurar base de datos")
    args = parser.parse_args()

    backup_files = sorted(BACKUP_DIR.glob("*.zip"), reverse=True)
    if not backup_files:
        print(f"❌ No se encontraron backups en {BACKUP_DIR}")
        sys.exit(1)

    if args.select:
        print("📋 Backups disponibles:")
        for idx, f in enumerate(backup_files, 1):
            print(f"{idx}. {f.name}")
        choice = input("Selecciona el backup a restaurar (número): ")
        try:
            idx = int(choice) - 1
            backup_to_restore = backup_files[idx]
        except:
            print("❌ Selección inválida")
            sys.exit(1)
    else:
        backup_to_restore = backup_files[0]

    restore_backup(
        backup_to_restore,
        restore_code=not args.no_code,
        restore_db=not args.no_db,
    )
