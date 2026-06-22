# Blog de Gatos 🐱

Blog informativo sobre gatos con arquitectura de dos servicios containerizados, integrado con tres pipelines de CI/CD: **Jenkins**, **Travis CI** y **Codeship Pro**.

---

## Arquitectura del proyecto

| Componente | Tecnología          | Puerto | Descripción                                     |
|------------|---------------------|--------|-------------------------------------------------|
| Backend    | Python 3.11 + Flask | 5000   | API REST con endpoint `/getCatsInfo`            |
| Frontend   | Nginx + HTML/CSS/JS | 8080   | Blog estático que consume el API vía proxy      |

Los dos servicios corren en la red interna `red-gatos`. El frontend hace proxy de `/getCatsInfo` → `http://backend:5000` directamente desde Nginx, evitando problemas de CORS.

```
Navegador → localhost:8080 → Nginx (frontend)
                                  ↓ proxy /getCatsInfo
                             Flask (backend) :5000
```

---

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o Docker Engine en Linux)
- WSL con distribución Linux (solo en Windows)
- Git

---

## Correr la aplicación

### Con Docker Compose (recomendado)

Desde la raíz del proyecto:

```bash
docker compose up -d --build
```

Abre [http://localhost:8080](http://localhost:8080).

Para detener y limpiar:

```bash
docker compose down
```

### Manual paso a paso

```bash
# Construir imágenes
cd backend && docker build -t backend:latest . && cd ..
cd frontend && docker build -t website:latest . && cd ..

# Crear red y levantar contenedores
docker network create red-gatos
docker run -d --name back -p 5000:5000 --network red-gatos backend:latest
docker run -d --name web  -p 8080:80  --network red-gatos website:latest
```

---

## CI/CD — Integración Continua

---

### Jenkins

Jenkins corre en un contenedor propio con acceso al socket Docker del host (Docker-in-Docker vía socket mount). El `Jenkinsfile` en la raíz define cuatro stages:

| Stage              | Qué hace                                                                 |
|--------------------|--------------------------------------------------------------------------|
| Checkout           | Clona el repositorio desde GitHub                                        |
| Build images       | Construye las imágenes del backend y frontend                            |
| Run tests          | Ejecuta pytest sobre el backend en un contenedor efímero `python:3.11-slim` |
| Integration test   | Levanta el stack completo y verifica con curl que ambos servicios respondan |

#### Paso 1 — Levantar Jenkins

```bash
docker compose -f jenkins/docker-compose.jenkins.yml up -d
```

Espera ~30 segundos y abre [http://localhost:8081](http://localhost:8081).

#### Paso 2 — Configuración inicial

Obtén la contraseña de admin:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

En el navegador:

1. Pega la contraseña en el campo que aparece
2. Selecciona **Install suggested plugins** y espera que termine
3. Crea tu usuario administrador y guarda

#### Paso 3 — Crear el pipeline

1. Dashboard → **New Item**
2. Nombre: `cat-blog-pipeline`, tipo: **Pipeline** → OK
3. Sección **Pipeline**, configura:
   - **Definition:** `Pipeline script from SCM`
   - **SCM:** `Git`
   - **Repository URL:** `https://github.com/AndruTRADX/docker_cat_blog.git`
   - **Branch Specifier:** `*/master`
   - **Script Path:** `Jenkinsfile`
4. Clic en **Save**

#### Paso 4 — Ejecutar el pipeline

Clic en **Build Now**. Si todos los stages quedan en verde, el blog estará corriendo en [http://localhost:8080](http://localhost:8080).

#### Paso 5 — Webhook para CI automático (opcional)

Expón Jenkins con ngrok:

```bash
ngrok http 8081
```

En GitHub → Settings → Webhooks → Add webhook:
- **Payload URL:** `https://<tu-url-ngrok>/github-webhook/`
- **Content type:** `application/json`
- **Events:** `Just the push event`

En Jenkins → job `cat-blog-pipeline` → Configure → **Build Triggers** → activa **GitHub hook trigger for GITScm polling** → Save.

---

### Travis CI

Travis CI se conecta directamente al repositorio de GitHub y detecta el archivo `.travis.yml` de la raíz automáticamente. El pipeline ejecuta:

| Fase             | Qué hace                                                              |
|------------------|-----------------------------------------------------------------------|
| `before_install` | Verifica la versión de Docker y docker compose disponible en el agente |
| `install`        | Construye las imágenes del backend y frontend                         |
| `script`         | Levanta el stack con `docker compose up -d`, espera 8 segundos y hace smoke tests en `:8080` y `:5000` |
| `after_failure`  | Imprime los logs de todos los contenedores para facilitar el debug    |
| `after_script`   | Baja el stack siempre, independientemente del resultado               |

> El archivo `.travis.yml` ya está en el repositorio. No se requiere ningún cambio de código.

#### Activar Travis CI

1. Ve a [https://travis-ci.com](https://travis-ci.com)
2. Inicia sesión con tu cuenta de GitHub (botón **Sign in with GitHub**)
3. En la esquina superior derecha clic en tu avatar → **Settings**
4. Sección **Repositories** → clic en **Manage repositories on GitHub**
5. Selecciona el repositorio `docker_cat_blog` y otorga acceso
6. De vuelta en Travis CI, busca `docker_cat_blog` en el dashboard y activa el toggle
7. Haz cualquier `git push` a `master` — Travis disparará el build automáticamente

---

### Codeship Pro

Codeship Pro usa los archivos `codeship-services.yml` y `codeship-steps.yml` de la raíz del proyecto. Los steps son:

| Step                  | Qué hace                                             |
|-----------------------|------------------------------------------------------|
| `run_tests`           | Instala pytest y ejecuta las pruebas del backend     |
| `build_check_backend` | Verifica que la imagen del backend se construyó OK   |
| `build_check_frontend`| Verifica que la imagen del frontend se construyó OK  |

> Los archivos `codeship-services.yml` y `codeship-steps.yml` ya están en el repositorio.

#### ⚠️ Paso previo obligatorio — Renombrar los Dockerfiles

Los Dockerfiles del proyecto están nombrados en minúscula (`dockerfile`) pero `codeship-services.yml` los referencia como `Dockerfile` (D mayúscula). En Linux —donde corre Codeship— el sistema de archivos distingue mayúsculas, por lo que el build fallará si no se corrige esto.

Ejecuta desde la raíz del proyecto:

```bash
# Renombrar los archivos
mv backend/dockerfile backend/Dockerfile
mv frontend/dockerfile frontend/Dockerfile

# Registrar el cambio en git
git add backend/Dockerfile frontend/Dockerfile
git commit -m "fix: rename dockerfile -> Dockerfile for Linux CI compatibility"
git push
```

#### Conectar el proyecto en Codeship

1. Ve a [https://app.codeship.com](https://app.codeship.com) y crea una cuenta o inicia sesión
2. Clic en **New Project**
3. Selecciona **GitHub** como SCM y autoriza el acceso
4. Busca y selecciona el repositorio `docker_cat_blog`
5. En la pantalla de tipo de proyecto, selecciona **Codeship Pro** (⚠️ no Basic)
6. Codeship detectará automáticamente los archivos `codeship-services.yml` y `codeship-steps.yml`
7. Haz un `git push` — Codeship disparará el primer build

> Si creaste el proyecto como **Basic** por error, debes eliminarlo y recrearlo como **Pro**. Los archivos yml de Codeship son exclusivos del modo Pro; en Basic serán ignorados.

---

## Flujo CI completo

```
git push ──→ GitHub
               ├──→ Travis CI   (automático vía integración GitHub)
               ├──→ Codeship    (automático vía integración GitHub)
               └──→ Jenkins     (manual con Build Now, o automático con webhook ngrok)

Cada pipeline:
  Build imágenes Docker
       ↓
  Run tests (pytest en backend)
       ↓
  Smoke / integration tests
       ↓
  ✅ Verde  o  ❌ Rojo + logs
```

---

## Historial de cambios

| Cambio                                                           | Notas                                                    |
|------------------------------------------------------------------|----------------------------------------------------------|
| Estructura inicial del proyecto (backend + frontend + Dockerfiles) | Estado base del repositorio                             |
| Agregado `docker-compose.yml` con red `red-gatos`                | Permite levantar todo con un solo comando                |
| Creado `backend/tests/test_app.py` con pytest                    | Tests de build e integración del contenedor             |
| Creado `backend/pyproject.toml` para configuración de pytest     | Centraliza la configuración de pytest                   |
| Creado `Jenkinsfile` en la raíz                                  | Pipeline: checkout → build → tests → integration test   |
| Creado `jenkins/Dockerfile` y `docker-compose.jenkins.yml`       | Jenkins con Docker CLI, docker-compose y socket mount   |
| Creado `.travis.yml` en la raíz                                  | CI en Travis CI: build + smoke tests al stack completo  |
| Creados `codeship-services.yml` y `codeship-steps.yml`           | CI con Codeship Pro: tests + build checks               |
| Fix: renombrado `dockerfile` → `Dockerfile`                      | Compatibilidad con sistemas Linux (case-sensitive)      |

---

## Problemas encontrados y soluciones

### Backend binding a 127.0.0.1 en lugar de 0.0.0.0

**Problema:** Flask escuchaba solo en `127.0.0.1` dentro del contenedor, haciendo que el health check de Jenkins y el proxy de Nginx no pudieran alcanzar el servicio.  
**Causa:** Flask usa `127.0.0.1` por defecto si no se especifica el host.  
**Solución:** `app.run(host='0.0.0.0', port=5000)` en `app.py` para que Flask acepte conexiones desde fuera del contenedor.

---

### Comunicación entre contenedores

**Problema:** El frontend no podía llamar al backend usando `localhost`.  
**Causa:** Cada contenedor tiene su propio namespace de red; `localhost` dentro de un contenedor solo apunta a ese contenedor.  
**Solución:** Red Docker compartida (`red-gatos`) y el `default.conf` de Nginx hace proxy de `/getCatsInfo` → `http://backend:5000` usando el nombre del servicio Docker como hostname.

---

### Jenkins — Docker-in-Docker

**Problema:** Jenkins intentaba correr `docker build` pero no tenía acceso al daemon Docker.  
**Causa:** El contenedor de Jenkins no tenía el socket Docker del host montado.  
**Solución:** `docker-compose.jenkins.yml` monta `/var/run/docker.sock:/var/run/docker.sock` y el `jenkins/Dockerfile` instala Docker CLI y docker-compose dentro de la imagen de Jenkins.

---

### Travis CI — `docker compose` vs `docker-compose`

**Problema:** En algunas imágenes de Travis el subcomando `docker compose` (sin guión, Plugin V2) no está disponible.  
**Causa:** Diferencia entre Docker Compose V1 (binario separado `docker-compose`) y V2 (plugin integrado `docker compose`).  
**Solución:** El `.travis.yml` detecta la versión con `docker compose version || (instalación manual del binario)` antes de usarlo.

---

### Codeship Pro vs Basic

**Problema:** El build en Codeship fallaba silenciosamente sin ejecutar ningún paso.  
**Causa:** El proyecto fue creado como **Codeship Basic**, que no soporta `codeship-services.yml` ni `codeship-steps.yml`.  
**Solución:** Eliminar el proyecto y recrearlo seleccionando explícitamente **Codeship Pro**.

---

### Codeship — nombres de Dockerfile en minúscula

**Problema:** `codeship-services.yml` referencia `Dockerfile` (D mayúscula) pero los archivos en el repo estaban en minúscula `dockerfile`.  
**Causa:** Windows usa un sistema de archivos case-insensitive; localmente funciona, pero Codeship y Travis corren en Linux (case-sensitive).  
**Solución:** Renombrar los archivos a `Dockerfile` y hacer commit (ver sección Codeship arriba).

---

## Opiniones sobre las herramientas

### Jenkins

**Pros:** Muy flexible, self-hosted, gratuito, ecosistema de plugins enorme, control total sobre el pipeline.  
**Contras:** La configuración inicial es compleja (contenedor, socket mount, plugins, usuarios). Requiere infraestructura propia corriendo localmente o en servidor.  
**Veredicto:** La herramienta más potente de las tres pero también la que más overhead de setup tiene. Ideal para entornos productivos o equipos con servidor dedicado. Para un proyecto universitario, el tiempo de configuración es considerable comparado con las alternativas cloud.

---

### Travis CI

**Pros:** Integración nativa con GitHub activable con un solo toggle, configuración en un único `.travis.yml`, gratuito para repositorios públicos, sin infraestructura propia.  
**Contras:** Desde 2021 el plan gratuito tiene créditos limitados (10,000 por organización). Para repositorios privados requiere plan de pago.  
**Veredicto:** La opción más rápida y simple para un proyecto público en GitHub. Casi cero configuración: subes el `.travis.yml` y ya funciona. Ideal como punto de entrada a CI/CD.

---

### Codeship Pro

**Pros:** Interfaz limpia, soporte nativo de Docker con sus archivos yml propios, soporte para steps paralelos, buena integración con GitHub.  
**Contras:** La distinción Basic/Pro confunde al principio y puede hacer perder tiempo. La documentación es menos extensa que la de Travis o Jenkins. Los archivos de configuración tienen una sintaxis propia que hay que aprender.  
**Veredicto:** Buena opción intermedia. Una vez entendido el modelo Pro/Basic y la sintaxis de `codeship-services.yml`, la configuración es intuitiva y el soporte Docker es sólido. Recomendado para quien ya conoce Travis y quiere explorar una alternativa con más control sobre los servicios Docker.

---

## Referencias

- Docker Compose: https://docs.docker.com/compose/
- Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/
- Travis CI: https://docs.travis-ci.com/
- Codeship Pro: https://docs.cloudbees.com/docs/cloudbees-codeship/latest/pro-builds-and-configuration/
- Flask: https://flask.palletsprojects.com/
- Nginx: https://nginx.org/en/docs/