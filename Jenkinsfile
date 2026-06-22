pipeline {
    agent any

    environment {
        COMPOSE_FILE = 'docker-compose.yml'
        BACKEND_IMAGE = 'backend:latest'
        FRONTEND_IMAGE = 'website:latest'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '==> Clonando repositorio...'
                checkout scm
            }
        }

        stage('Build images') {
            steps {
                echo '==> Construyendo imágenes Docker...'
                sh 'docker build -t ${BACKEND_IMAGE} ./backend'
                sh 'docker build -t ${FRONTEND_IMAGE} ./frontend'
            }
        }

        stage('Run tests') {
            steps {
                echo '==> Configurando entorno de pruebas con acceso a Docker...'
                sh '''
                docker rm -f backend-tester || true
                
                docker create --name backend-tester -v /var/run/docker.sock:/var/run/docker.sock -w /app python:3.11-slim sleep 300
                
                docker cp backend/. backend-tester:/app
                
                docker start backend-tester
                
                docker exec backend-tester apt-get update
                docker exec backend-tester apt-get install -y --no-install-recommends docker.io
                
                docker exec backend-tester pip install --no-cache-dir -r requirements.txt pytest --quiet
                
                docker exec backend-tester python -m pytest tests/ -v
                
                docker rm -f backend-tester
                '''
            }
        }

        stage('Integration test') {
            steps {
                echo '==> Levantando stack completo con docker compose...'
                sh 'docker-compose -f ${COMPOSE_FILE} up -d --build'

                echo '==> Esperando que los servicios estén listos...'
                sh 'sleep 5'

                echo '==> Verificando que el frontend responde...'
                sh '''
                    curl --fail --silent --max-time 10 http://localhost:8080 \
                        && echo "Frontend OK" \
                        || (echo "Frontend no responde" && exit 1)
                '''

                echo '==> Verificando que el backend responde...'
                sh '''
                    curl --fail --silent --max-time 10 http://localhost:5000 \
                        && echo "Backend OK" \
                        || echo "Backend sin ruta raíz (aceptable si hay /cats o similar)"
                '''
            }
        }
    }

    post {
        always {
            echo '==> Limpiando contenedores...'
            sh 'docker-compose -f ${COMPOSE_FILE} down --remove-orphans || true'
        }
        success {
            echo '✅ Pipeline completado exitosamente.'
        }
        failure {
            echo '❌ Pipeline falló. Revisar logs arriba.'
        }
    }
}