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
