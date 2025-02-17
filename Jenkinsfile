pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dash/back"
        // Dockerfile이 프로젝트 루트에 있으므로 빌드 컨텍스트는 "."
        BACKEND_DIR = "."
        IMAGE_TAG = "latest"
        // ECR URL 형식: AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com
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
                echo "Building Docker image using Dockerfile from project root..."
                script {
                    dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}", "--platform linux/amd64 .")
                    echo "Docker image built with ID: ${dockerImage.id}"
                }
            }
        }

        stage('Docker Login to ECR') {
            steps {
                echo "Logging in to AWS ECR..."
                script {
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-credentials', // Jenkins에 등록된 AWS 자격 증명 ID
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]]) {
                        sh '''
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                        '''
                    }
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
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-credentials',
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]]) {
                        sh '''
                          aws ecs update-service \
                            --cluster devcluster \
                            --service dashback \
                            --force-new-deployment \
                            --region ${AWS_REGION}
                        '''
                    }
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
