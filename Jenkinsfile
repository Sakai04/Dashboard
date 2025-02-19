pipeline {
    agent any

    environment {
        // AWS ECR 설정
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        PROJECT_DIR    = "/home/ec2-user/project"

        // Jenkins Credentials 주입
        DB_USER        = credentials('DB_USER')
        DB_PASSWORD    = credentials('DB_PASSWORD')
        DB_NAME        = credentials('DB_NAME')
        PGADMIN_EMAIL  = credentials('PGADMIN_EMAIL')
        PGADMIN_PASS   = credentials('PGADMIN_PASSWORD')
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    dockerImage = docker.build(
                        "${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}",
                        "--platform=linux/amd64 --build-arg DB_USER=\${DB_USER} --build-arg DB_PASSWORD=\${DB_PASSWORD} ."
                    )
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}"
                        dockerImage.push()
                    }
                }
            }
        }

        stage('Prepare Config Files') {
            steps {
                sh '''
                    # docker-compose.yml 생성
                    cat <<EOD > docker-compose-prod.yml
                    version: '3.8'

                    services:
                      db:
                        image: postgres:15
                        container_name: prod-db
                        env_file: .env
                        volumes:
                          - pg_data:/var/lib/postgresql/data
                        networks:
                          - app-net
                        healthcheck:
                          test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
                          interval: 10s
                          timeout: 5s
                          retries: 5

                      app:
                        image: ${ECR_URL}/dashback:latest
                        container_name: prod-app
                        env_file: .env
                        depends_on:
                          db:
                            condition: service_healthy
                        networks:
                          - app-net
                        ports:
                          - "8000:8000"

                      pgadmin:
                        image: dpage/pgadmin4:latest
                        container_name: prod-pgadmin
                        env_file: .env
                        depends_on:
                          - db
                        ports:
                          - "8080:80"

                    networks:
                      app-net:
                        driver: bridge

                    volumes:
                      pg_data:
                    EOD

                    # .env 파일 생성
                    cat <<EOF > .env
                    POSTGRES_USER=${DB_USER}
                    POSTGRES_PASSWORD=${DB_PASSWORD}
                    POSTGRES_DB=${DB_NAME}
                    PGADMIN_DEFAULT_EMAIL=${PGADMIN_EMAIL}
                    PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASS}
                    DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}?ssl=require
                    ECR_URL=${ECR_URL}
                    EOF
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshPublisher(
                    publishers: [
                        sshPublisherDesc(
                            configName: 'EC2_Instance',
                            transfers: [
                                sshTransfer(
                                    sourceFiles: 'docker-compose-prod.yml, .env',
                                    removePrefix: '',
                                    remoteDirectory: PROJECT_DIR,
                                    execCommand: """
                                        cd ${PROJECT_DIR}
                                        export COMPOSE_PROJECT_NAME=dashboard_prod
                                        docker-compose -f docker-compose-prod.yml down --remove-orphans
                                        docker-compose -f docker-compose-prod.yml pull
                                        docker-compose -f docker-compose-prod.yml up -d
                                        docker ps -a
                                    """
                                )
                            ],
                            verbose: true
                        )
                    ]
                )
            }
        }
    }

    post {
        always {
            sh 'rm -f docker-compose-prod.yml .env'
        }
    }
}
