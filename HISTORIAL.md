# Historial de cambios y documentación del proyecto

**Proyecto:** docker_cat_blog  
**Repositorio:** https://github.com/AndruTRADX/docker_cat_blog  
**Asignatura:** Infraestructura de software / DevOps  

---

## 1. Descripción general del proyecto

Blog de gatos con arquitectura de dos servicios containerizados:

| Servicio | Tecnología | Puerto |
|----------|-----------|--------|
| Backend  | Python (Flask / FastAPI) | 5000 |
| Frontend | HTML + CSS + JS (Nginx) | 8080 |

Los contenedores se comunican dentro de la red `red-gatos` definida en `docker-compose.yml`. El frontend llama al backend en `http://back:5000` usando el nombre del servicio como hostname.

---

## 2. Historial de cambios

| Fecha | Cambio | Responsable | Notas |
|-------|--------|-------------|-------|
| — | Estructura inicial del proyecto (backend + frontend + Dockerfiles) | — | Estado base del repo |
| — | Agregado `docker-compose.yml` con red `red-gatos` | — | Permite levantar todo con un solo comando |
| — | Creado `backend/tests/test_app.py` con pytest | — | Pre-requisito para pipelines de CI |
| — | Creado `backend/pyproject.toml` para configuración de pytest | — | — |
| — | Creado `Jenkinsfile` en la raíz | — | Pipeline: build → tests → integration → cleanup |
| — | Creado `.travis.yml` en la raíz | — | CI en Travis CI con smoke tests |
| — | Creados `codeship-services.yml` y `codeship-steps.yml` | — | CI con Codeship Pro |
| — | Creado `docs/historial.md` | — | Este documento |

> Completar las fechas y responsables con los datos reales del equipo.

---

## 3. Problemas encontrados y soluciones

### 3.1 Comunicación entre contenedores

**Problema:** El frontend no podía llamar al backend usando `localhost`.  
**Causa:** Cada contenedor tiene su propio namespace de red; `localhost` dentro de un contenedor solo apunta a ese contenedor.  
**Solución:** Crear una red Docker compartida (`red-gatos`) y usar el nombre del servicio (`back`) como hostname. Con `docker-compose.yml`, esto es automático.

---

### 3.2 Travis CI — `docker compose` vs `docker-compose`

**Problema:** En ambientes de Travis antiguos el comando es `docker-compose` (guión), en los modernos es `docker compose` (subcomando).  
**Solución:** Usar `docker compose version` en `before_install` para detectar la versión. Si falla, agregar la instalación manual del plugin:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

### 3.3 Codeship Pro — diferencia con Codeship Basic

**Problema:** Codeship tiene dos variantes: Basic (sin Docker nativo) y Pro (con Docker nativo).  
**Causa:** Los archivos `codeship-services.yml` y `codeship-steps.yml` son exclusivos de **Codeship Pro**.  
**Solución:** Al crear el proyecto en codeship.com, seleccionar **Pro** (no Basic). Si ya existe como Basic, hay que recrearlo.

---

### 3.4 Jenkins — Docker-in-Docker

**Problema:** Jenkins intenta correr `docker build` pero el agente no tiene acceso al daemon de Docker.  
**Causa:** El contenedor de Jenkins no tiene montado el socket de Docker del host.  
**Solución:** Correr Jenkins con:
```bash
docker run -d \
  -p 8081:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```
Y dentro del contenedor instalar Docker CLI:
```bash
docker exec -it -u root <container_id> bash
apt-get update && apt-get install -y docker.io
```

---

## 4. Responsabilidades del equipo

| Integrante | Responsabilidad |
|------------|----------------|
| — | Estructura del proyecto (backend + frontend + Docker) |
| — | Configuración de Jenkins (Jenkinsfile) |
| — | Configuración de Travis CI (.travis.yml) |
| — | Configuración de Codeship Pro |
| — | Tests y documento final |

> Completar con los nombres reales del equipo.

---

## 5. Opiniones sobre las herramientas

### Jenkins
**Pros:** Muy flexible, self-hosted, plugins para todo, gratis.  
**Contras:** Requiere infraestructura propia (un servidor o contenedor corriendo), configuración inicial más compleja, UI desactualizada.  
**Veredicto:** Ideal para equipos con servidor propio o en producción real. Para un trabajo universitario, la complejidad de setup es alta.

### Travis CI
**Pros:** Se conecta directo a GitHub con un solo toggle, configuración en un solo archivo `.travis.yml`, gratuito para repositorios públicos.  
**Contras:** El plan gratuito tiene créditos limitados desde 2021; para repositorios privados requiere pago.  
**Veredicto:** La opción más sencilla y rápida para un proyecto académico público en GitHub.

### Codeship
**Pros:** Interfaz limpia, Codeship Pro soporta Docker nativo con sus archivos yml propios, buen soporte para pipelines paralelos.  
**Contras:** La distinción entre Basic y Pro confunde al principio; documentación menos extensa que Travis o Jenkins.  
**Veredicto:** Buena opción intermedia. Pro con Docker es potente pero requiere entender bien la diferencia entre los dos modos.

---

## 6. Capturas de pipelines exitosos

> Adjuntar capturas de pantalla de cada pipeline en estado verde:
> - Jenkins: captura del Blue Ocean o la vista clásica de stages
> - Travis CI: captura del build en travis-ci.com
> - Codeship: captura del build en codeship.com

---

## 7. Referencias

- Documentación Docker Compose: https://docs.docker.com/compose/
- Documentación Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/
- Documentación Travis CI: https://docs.travis-ci.com/
- Documentación Codeship Pro: https://docs.cloudbees.com/docs/cloudbees-codeship/latest/pro-builds-and-configuration/
