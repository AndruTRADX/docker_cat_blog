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

        stage('Construir imágenes') {
            steps {
                echo 'Construyendo imágenes Docker...'
                sh 'docker-compose build'
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
                    curl -f http://localhost:8080 || exit 1
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline ejecutado exitosamente. Blog corriendo en puerto 8080.'
        }
        failure {
            echo '❌ Pipeline falló. Revisando logs...'
            sh 'docker-compose logs'
            sh 'docker-compose down'
        }
    }
}