import exifread

with open("WA_example.jpeg", "rb") as archivo:
    tags = exifread.process_file(archivo)

for nombre, valor in tags.items():
    print(nombre, valor)