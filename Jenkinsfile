pipeline {
    agent any

    environment {
        // AWS 및 ECR 관련 환경변수 (실제 값으로 대체)
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        // ECR 리포지토리 이름 (ECR 콘솔에서 dash/back 리포지토리를 생성했다고 가정)
        ECR_REPO = "dash/back"
        IMAGE_TAG = "latest"
        // ECR URL: "296062584049.dkr.ecr.ap-northeast-2.amazonaws.com"
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
                    // 프로젝트 루트에 Dockerfile이 있으므로 빌드 컨텍스트는 "."
                    dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}", ".")
                    echo "Docker image built with ID: ${dockerImage.id}"
                }
            }
        }

        stage('Docker Login to ECR') {
            steps {
                echo "Logging in to AWS ECR..."
                script {
                    // Docker 로그인할 때는 전체 리포지토리 이름 없이 ECR URL만 사용
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
                    // ECS 클러스터와 서비스 이름은 실제 환경에 맞게 수정하세요.
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
