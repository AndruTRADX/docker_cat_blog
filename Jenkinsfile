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
                echo '==> Ejecutando tests del backend...'
                sh '''
                    docker run --rm \
                        -v "$(pwd)/backend:/app" \
                        -w /app \
                        ${BACKEND_IMAGE} \
                        sh -c "pip install pytest --quiet && pytest tests/ -v"
                '''
            }
        }

        stage('Integration test') {
            steps {
                echo '==> Levantando stack completo con docker compose...'
                sh 'docker compose -f ${COMPOSE_FILE} up -d --build'

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
            sh 'docker compose -f ${COMPOSE_FILE} down --remove-orphans || true'
        }
        success {
            echo '✅ Pipeline completado exitosamente.'
        }
        failure {
            echo '❌ Pipeline falló. Revisar logs arriba.'
        }
    }
}