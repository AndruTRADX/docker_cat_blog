pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "cat_blog"
    }

    stages {
        stage('Clonar repositorio') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        stage('Limpieza previa') {
            steps {
                echo 'Bajando contenedores anteriores si existen...'
                sh 'docker-compose down --remove-orphans || true'
            }
        }

        stage('Construir imágenes') {
            steps {
                echo 'Construyendo imágenes Docker...'
                sh 'docker-compose build --no-cache'
            }
        }

        stage('Levantar contenedores') {
            steps {
                echo 'Levantando los servicios...'
                sh 'docker-compose up -d'
            }
        }

        stage('Verificar servicios') {
            steps {
                echo 'Verificando que los contenedores estén corriendo...'
                sh 'docker-compose ps'
                sh '''
                    sleep 5
                    docker exec web curl -f http://localhost:80 || exit 1
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline ejecutado exitosamente. Blog corriendo en puerto 8080.'
        }
        failure {
            echo '❌ Pipeline falló. Bajando contenedores...'
            sh 'docker-compose logs || true'
            sh 'docker-compose down || true'
        }
        always {
            echo 'Pipeline finalizado.'
        }
    }
}