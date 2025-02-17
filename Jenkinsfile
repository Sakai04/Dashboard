pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dash/back"
        IMAGE_TAG = "latest"
        // ECR URL 형식: {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // Dockerfile이 프로젝트 루트에 있으므로 BACKEND_DIR는 "." 입니다.
        BACKEND_DIR = "."
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                // 프로젝트 루트에서 도커 이미지를 빌드합니다.
                dir("${BACKEND_DIR}") {
                    script {
                        dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                        sh '''
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                        '''
                    }
                }
            }
        }
        stage('Docker Push') {
            steps {
                script {
                    dockerImage.push()
                }
            }
        }
        stage('Deploy to ECS') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                        sh '''
                           aws ecs update-service --cluster devcluster --service dash/back --force-new-deployment --region ${AWS_REGION}
                        '''
                    }
                }
            }
        }
    }
    post {
        success {
            echo "Backend deployment succeeded."
        }
        failure {
            echo "Backend deployment failed."
        }
    }
}
