import os
from datetime import datetime

# ==========================
# CONFIGURACIÓN
# ==========================

ARCHIVO_SALIDA = "compilacion.txt"

CARPETAS_EXCLUIDAS = {
    "__pycache__",
    "venv",
    ".venv",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "migrations",
    "dist",
    "bootstrap",
    "build"
}

ARCHIVOS_EXCLUIDOS = {
    ".env",
    ".gitignore",
    "compilacion.txt"
}

EXTENSIONES_VALIDAS = {
    ".py", ".html", ".css", ".js",
    ".md", ".txt", ".json", ".toml", ".yaml", ".yml"
}

# ==========================
# FUNCIONES
# ==========================

def es_archivo_valido(nombre_archivo):
    extension = os.path.splitext(nombre_archivo)[1].lower()
    return (
        extension in EXTENSIONES_VALIDAS and
        nombre_archivo not in ARCHIVOS_EXCLUIDOS
    )


def compilar_proyecto():
    ruta_base = os.getcwd()
    ruta_salida = os.path.join(ruta_base, ARCHIVO_SALIDA)

    with open(ruta_salida, "w", encoding="utf-8") as salida:
        
        # Encabezado general
        salida.write("COMPILACIÓN DEL PROYECTO\n")
        salida.write(f"Ruta base: {ruta_base}\n")
        salida.write(f"Fecha: {datetime.now()}\n")
        salida.write("=" * 80 + "\n\n")

        for root, dirs, files in os.walk(ruta_base):

            # Filtrar carpetas irrelevantes
            dirs[:] = [d for d in dirs if d not in CARPETAS_EXCLUIDAS]

            for archivo in files:

                if es_archivo_valido(archivo):

                    ruta_completa = os.path.join(root, archivo)
                    ruta_relativa = os.path.relpath(ruta_completa, ruta_base)

                    salida.write("\n" + "=" * 80 + "\n")
                    salida.write(f"ARCHIVO: {ruta_relativa}\n")
                    salida.write("=" * 80 + "\n\n")

                    try:
                        with open(ruta_completa, "r", encoding="utf-8") as f:
                            contenido = f.read()
                        salida.write(contenido)
                        salida.write("\n\n")
                    except Exception as e:
                        salida.write(f"[ERROR AL LEER EL ARCHIVO: {e}]\n\n")

    print(f"\n✅ Compilación completada.")
    print(f"📄 Archivo generado en: {ruta_salida}")


# ==========================
# EJECUCIÓN
# ==========================

if __name__ == "__main__":
    compilar_proyecto()