# Blog de gatos

Este es un blog sencillo de gatos que te muestra información interesante sobre felinos. Tiene un backend (API) y un frontend (sitio web) que se comunican entre sí dentro de contenedores Docker.

Para ejecutar el proyecto necesitas tener Docker Desktop instalado, junto con WSL y la distribución de Linux que prefieras.

## **Construcción de las imágenes**

Primero debes crear las imágenes de Docker para el backend y el frontend. Cada imagen empaqueta el código y sus dependencias.

Abre una terminal en la raíz del proyecto y ejecuta los comandos en orden:

```bash
cd backend
docker build -t backend:latest .
```

- `cd backend` te mueve a la carpeta que contiene el Dockerfile y el código del backend.
- `docker build -t backend:latest .` construye la imagen usando el Dockerfile de ese directorio (el punto `.` indica el contexto de construcción). El flag `t` le asigna un nombre y etiqueta (`backend:latest`) para poder referenciarla después.

Luego construye el frontend:

```bash
cd ../frontend
docker build -t website:latest .
```

- `cd ../frontend` te lleva a la carpeta del frontend.
- `docker build -t website:latest .` crea la imagen del sitio web con la etiqueta `website:latest`.

## **Crear red y levantar los contenedores**

Para que los contenedores se comuniquen entre sí (el frontend necesita llamar al backend), debes crear una red de Docker y después iniciar ambos contenedores dentro de esa misma red.

Ejecuta los siguientes comandos:

```bash
docker network create red-gatos
```

- `docker network create red-gatos` crea una red virtual llamada `red-gatos`. Todos los contenedores que se conecten a ella podrán verse entre sí usando sus nombres como nombres de host.

Ahora inicia el backend:

```bash
cd ../backend
docker run -it --rm -d -p 5000:5000 --name back --network red-gatos backend:latest
```

- `cd ../backend` te ubica en la carpeta del backend (puedes omitirlo si ya estás allí, pero se incluye por claridad).
- `docker run` crea y arranca un contenedor a partir de la imagen `backend:latest`.
- `it` asigna una terminal interactiva (útil si necesitas ver logs en tiempo real; no es estrictamente necesario pero se mantiene como en tu comando original).
- `-rm` elimina automáticamente el contenedor cuando se detenga, evitando acumular contenedores parados.
- `d` ejecuta el contenedor en segundo plano (modo detached), liberando la terminal.
- `p 5000:5000` mapea el puerto 5000 de tu máquina al puerto 5000 del contenedor, permitiendo acceder a la API desde `localhost:5000`.
- `-name back` asigna el nombre `back` al contenedor. Este nombre será usado por el frontend para comunicarse con el backend dentro de la red `red-gatos`.
- `-network red-gatos` conecta el contenedor a la red que creaste.

Después levanta el frontend:

```bash
cd ../frontend
docker run -it --rm -d -p 8080:80 --name web --network red-gatos website:latest
```

- `cd ../frontend` te mueve a la carpeta del frontend.
- `docker run` arranca el contenedor del sitio web.
- Los flags `it`, `-rm` y `d` cumplen la misma función que antes.
- `p 8080:80` mapea el puerto 8080 de tu máquina al puerto 80 del contenedor (el puerto por defecto del servidor web). Así accedes al blog desde `http://localhost:8080`.
- `-name web` asigna el nombre `web` al contenedor.
- `-network red-gatos` conecta el contenedor a la misma red, permitiendo que el frontend haga peticiones al backend usando `http://back:5000`.

Por último, abre en tu navegador:

[http://localhost:8080](http://localhost:8080/)

¡Y listo! Lograste comunicar el backend y el frontend de la aplicación usando contenedores aislados pero conectados.

## **Docker compose**

El repositorio ya incluye un archivo `docker-compose.yml` que automatiza todos los pasos anteriores: construye las imágenes, crea la red y levanta ambos contenedores con un solo comando.

Solo necesitas ejecutar esto en la raíz del proyecto:

```bash
docker compose up -d --build
```

- `up` levanta los servicios definidos en el archivo `docker-compose.yml`.
- `d` ejecuta todo en segundo plano (modo detached), igual que con `docker run`.
- `-build` fuerza la reconstrucción de las imágenes antes de iniciar los contenedores, asegurando que cualquier cambio en el código se refleje.

Después, abre [http://localhost:8080](http://localhost:8080/) y verás el blog funcionando.

Cuando quieras detener y eliminar los contenedores junto con la red, usa:

```bash
docker compose down
```

Así mantienes limpio tu entorno sin esfuerzo manual.
