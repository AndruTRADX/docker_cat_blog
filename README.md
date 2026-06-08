# Blog de gatos 🐱

Este es un blog sencillo de gatos que te muestra información interesante sobre felinos. Tiene un backend (API) y un frontend (sitio web) que se comunican entre sí dentro de contenedores Docker.

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- WSL con una distribución de Linux (si usas Windows)
- Git

---

## Ejecución del proyecto

### Opción A — Docker Compose (recomendado)

Desde la raíz del proyecto ejecuta:

```bash
docker compose up -d --build
```

Luego abre [http://localhost:8080](http://localhost:8080) y verás el blog funcionando.

Para detener y eliminar los contenedores:

```bash
docker compose down
```

### Opción B — Paso a paso manual

Construye las imágenes:

```bash
cd backend
docker build -t backend:latest .
cd ../frontend
docker build -t website:latest .
```

Crea la red y levanta los contenedores:

```bash
docker network create red-gatos
docker run -it --rm -d -p 5000:5000 --name back --network red-gatos backend:latest
docker run -it --rm -d -p 8080:80 --name web --network red-gatos website:latest
```

Abre [http://localhost:8080](http://localhost:8080).

---

## Integración Continua con Jenkins

Este proyecto incluye un pipeline de CI con Jenkins que automatiza el build, despliegue y verificación de la aplicación en cada cambio.

### Paso 1 — Levantar Jenkins

Desde la raíz del proyecto ejecuta:

```bash
docker compose -f jenkins/docker-compose.jenkins.yml build --no-cache
docker compose -f jenkins/docker-compose.jenkins.yml up -d
```

Espera unos 30 segundos y abre Jenkins en [http://localhost:8081](http://localhost:8081).

### Paso 2 — Configuración inicial de Jenkins

**2.1 Obtener la contraseña inicial:**

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**2.2 En el navegador:**

1. Pega la contraseña en el campo que aparece
2. Selecciona **"Install suggested plugins"** y espera a que termine
3. Crea tu usuario administrador y guarda

### Paso 3 — Crear el pipeline

1. En el dashboard haz clic en **"New Item"**
2. Escribe el nombre `cat-blog-pipeline`, selecciona **"Pipeline"** y haz clic en **OK**
3. En la sección **"Pipeline"** configura:
   - **Definition:** `Pipeline script from SCM`
   - **SCM:** `Git`
   - **Repository URL:** `https://github.com/AndruTRADX/docker_cat_blog.git`
   - **Branch Specifier:** `*/master`
   - **Script Path:** `Jenkinsfile`
4. Haz clic en **"Save"**

### Paso 4 — Ejecutar el pipeline

Haz clic en **"Build Now"**. El pipeline correrá los siguientes stages:

```text
Clonar repositorio   → clona el código desde GitHub
Limpieza previa      → baja contenedores anteriores si existen
Construir imágenes   → ejecuta docker-compose build
Levantar contenedores → ejecuta docker-compose up -d
Verificar servicios  → confirma que nginx responde correctamente
```

Si todos los stages están en verde, el blog estará corriendo en [http://localhost:8080](http://localhost:8080).

### Paso 5 — Webhook para CI automático (opcional)

Para que Jenkins se dispare automáticamente en cada `git push`:

**5.1 Expón Jenkins con ngrok:**

```bash
ngrok http 8081
```

Copia la URL generada, por ejemplo: `https://abc123.ngrok-free.app`

**5.2 Configura el webhook en GitHub:**

Ve a tu repositorio → `Settings` → `Webhooks` → `Add webhook`:
- **Payload URL:** `https://abc123.ngrok-free.app/github-webhook/`
- **Content type:** `application/json`
- **Events:** `Just the push event`
- Haz clic en **"Add webhook"**

**5.3 Activa el trigger en Jenkins:**

Ve al job `cat-blog-pipeline` → `Configure` → sección **"Build Triggers"** → activa **"GitHub hook trigger for GITScm polling"** → guarda.

A partir de ese momento cada `git push` a `master` disparará el pipeline automáticamente.

---

## Flujo CI completo

```text
git push → GitHub Webhook → Jenkins → Limpieza → Build → Deploy → Verificación
```
