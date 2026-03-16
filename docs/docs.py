from pathlib import Path

# Ruta de la carpeta
carpeta = Path(r"C:\Users\Sergio\Documents\DS")

# Archivo de salida
archivo_salida = "lista_documentos.txt"

with open(archivo_salida, "w", encoding="utf-8") as f:
    for elemento in carpeta.iterdir():
        if elemento.is_file():
            f.write(elemento.name + "\n")

print("Lista generada en:", archivo_salida)