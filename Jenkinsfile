pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dash/back"
        // Dockerfile이 프로젝트 루트에 있으므로 BACKEND_DIR을 "."로 설정
        BACKEND_DIR = "."
        IMAGE_TAG = "latest"
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image from project root..."
                // 프로젝트 루트에서 Dockerfile을 빌드
                dir("${BACKEND_DIR}") {
                    script {
                        dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}", ".")
                        echo "Docker image built: ${dockerImage.id}"
                    }
                }
            }
        }

        stage('Docker Login to ECR') {
            steps {
                echo "Logging in to AWS ECR..."
                script {
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                echo "Pushing Docker image to ECR..."
                script {
                    dockerImage.push()
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                echo "Deploying to ECS service..."
                script {
                    sh '''
                      aws ecs update-service \
                        --cluster devcluster \
                        --service dash/back \
                        --force-new-deployment \
                        --region ${AWS_REGION}
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Backend deployment succeeded!"
        }
        failure {
            echo "Backend deployment failed!"
        }
    }
}
