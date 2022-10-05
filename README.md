Tabla de Contenido
==================
- [Tabla de contenido](#tabla-de-contenido)
  - [Acerca del proyecto](#acerca-del-proyecto)
  - [Requisitos](#requisitos)
  - [Instalación](#instalacion)
  - [Estructura del proyecto](#estructura-del-proyecto)
  - [Agradecimientos](#agradecimientos)

Acerca del proyecto
------

bpy-web es un fork de [guweb](https://github.com/varkaria/guweb), que es el front-end del protocolo de servidores de osu, [bancho.py](https://github.com/osuperu/gulag).
Este fork contiene cambios y adiciones hechas para nuestro servidor privado [Hoshizada](https://osu.hoshizada.ga/), hosteado para la comunidad de [osu!Perú](https://osuperu.ga).

Mediante el uso de la sintaxis nativa async/await, desarrollada a base de [Quart](https://github.com/pgjones/quart) y la [librería multipropósitos de cmyui](https://github.com/cmyui/cmyui_pkg), bpy-web logra una flexibilidad, limpieza y eficiencia que no se ve en otras implementaciones de front-end, conservando a la vez la simplicidad de Python.

Requisitos
------

- Algunos conocimientos de Linux (Testeado en Ubuntu 22.04), Python y conocimientos de programación en general.
- MySQL
- Nginx

Instalacion
------

La instalación es relativamente simple: los siguientes comandos te ayudarán con el proceso.

Notas:

- Ubuntu 20.04 tiene problemas con Nginx y osu! por razones desconocidas.

```sh
# Instala Python >=3.9 y la última versión de PIP
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9 python3.9-dev python3.9-distutils
wget https://bootstrap.pypa.io/get-pip.py
python3.9 get-pip.py && rm get-pip.py

# Instala MySQL and NGINX
sudo apt install mysql-server nginx

# Clona el repositorio desde Github
git clone https://github.com/osuperu/bpy-web.git
cd bpy-web

# Inicializa y actualiza los submodulos
git submodule init && git submodule update

# Instala los requisitos desde pip
python3.9 -m pip install -r ext/requirements.txt

# Añade y modifica la configuración de NGINX de bpy-web en nginx/sites-enabled
sudo ln -r -s ext/nginx.conf /etc/nginx/sites-enabled/guweb.conf
sudo nano ext/nginx.conf
sudo nginx -s reload

# Configura el proyecto
cp ext/config.sample.py config.py
nano config.py

# Ejecuta el proyecto (on port 8000).
python3.9 main.py # Ejecuta directamente para acceder a las funciones de depuración para el desarrollo
hypercorn main.py # Ejecute guweb con hypercorn cuando esté en producción. Mejorará el rendimiento drásticamente al desactivar todas las funciones de depuración que un desarrollador necesitaría
```

Estructura del proyecto
------

    .
    ├── blueprints   # Rutas modulares como la API, el Frontend o el Panel de Administración
    ├── ext          # Archivos externos de la función principal de bpy-web
    ├── objects      # Código para representar privilegios, objetos globales, etc
    ├── static       # Código o contenido que no es modificado o procesado por el propia guweb
    ├── templates    # HTML que contiene contenido que se renderiza después de que la página se haya cargado
        ├── admin    # Contenido de plantillas para el panel de administración (/admin)
        ├── settings # Contenido de plantillas para los ajustes (/settings)
        └ ...         # Contenido de plantillas para todo guweb (/)


Agradecimientos
------
- [Varkaria](https://github.com/Varkaria) | Frontend y Backend [Autor del proyecto en el que se basa este fork]
- [Yoru](https://github.com/Yo-ru) | Backend [Deprecado]
- [midoripeach](https://twitter.com/midoripeachy) | Artista que dibujó la osu!Perú chan<3~