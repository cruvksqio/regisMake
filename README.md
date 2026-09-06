
```text
                                                  __                
                    __          /'\_/`\          /\ \               
 _ __    __     __ /\_\    ____/\      \     __  \ \ \/'\      __   
/\`'__\/'__`\ /'_ `\/\ \  /',__\ \ \__\ \  /'__`\ \ \ , <    /'__`\ 
\ \ \//\  __//\ \L\ \ \ \/\__, `\ \ \_/\ \/\ \L\.\_\ \ \\`\ /\  __/ 
 \ \_\\ \____\ \____ \ \_\/\____/\ \_\\ \_\ \__/.\_\\ \_\ \_\ \____\
  \/_/ \/____/\/___L\ \/_/\/___/  \/_/ \/_/\/__/\/_/ \/_/\/_/\/____/
                /\____/                                             
                \_/__/                                              
```


regisMakin es una aplicación que tiene la utilidad de convertir, esos registros que mas te gustan, en álbumes MP3 con sus temas ordenados y con portada para su uso en aplicaciones de reproducción de musica que utilicen archivos locales. Esta aplicación fue creada a partir de la librería  de interfaz gráfica tkinter de Python, junto a otras mas para poder realizar el procesado de audio de la descarga, como el recorte y ordenamiento de los audios.

***
## **Uso de aplicación:**

1.  Ingresa el link de Youtube en la barra de arriba
2.  En la ventana central de la derecha, ingresa el texto con las timestamps del video y haz click el botón Check para verificar si la información es correcta
3.  Si la informacion es correcta se habilitaran las opciones para editar la portada, el nombre de las canciones, mover o borrar alguna, etc.
4.  Haz click en convertir para crear tu album, este sera enviado a la carpeta downloads

## **Instalación:**

Asegúrate de tener instalado Python 3.10+ y Git en tu sistema antes de comenzar.

# 1. Clonar el repositorio

Abre tu terminal o PowerShell y descarga el código fuente:

```bash
git clone https://github.com/cruvksqio/regisMakin.git
cd regisMakin
```
# 2. Crear y activar el Entorno Virtual (venv)

Es una buena práctica aislar las librerías del proyecto. Dependiendo de tu sistema operativo, ejecuta:

Para Windows (PowerShell):
PowerShell

```bash
python -m venv venv
.\venv\Scripts\activate
```

> Nota para usuarios de Windows: Si PowerShell te arroja un error de permisos en rojo al intentar activar el entorno, ejecuta este comando primero para habilitar los scripts y vuelve a intentar:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```
Para Linux / Mac (Terminal):
Bash
```bash
python3 -m venv venv
source venv/bin/activate
```
Sabrás que funcionó porque verás un (venv) al inicio de la línea en tu consola.
# 3. Instalar las dependencias

Con el entorno virtual activado, instala todas las librerías necesarias ejecutando:
Bash
```bash
pip install -r requirements.txt
```
# 4. Requisito necesario: FFmpeg

Este programa utiliza pydub y yt-dlp, los cuales requieren el motor de FFmpeg para procesar y exportar los audios a MP3.

En Windows: Descarga los binarios de [FFmpeg](https://github.com/GyanD/codexffmpeg/releases/tag/2026-08-20-git-7d77562d2a), extrae los archivos ffmpeg.exe y ffprobe.exe de la carpeta bin, y pégalos directamente en la carpeta raíz de este proyecto (al lado de main.py).

En Linux: Simplemente instálalo en tu sistema con: 
```bash
sudo apt install ffmpeg
```
# 5. Ejecutar la aplicación

Una vez que todo esté instalado, simplemente corre el programa con:
Bash
```bash
python main.py
```
