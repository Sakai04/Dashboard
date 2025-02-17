pipeline {
    agent any

    environment {
        // AWS 및 ECR 관련 환경변수 (실제 값으로 대체)
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        // ECR 리포지토리 이름: ECR 콘솔에서 dash/back 리포지토리를 생성했다고 가정
        ECR_REPO = "dash/back"
        // 백엔드 코드가 위치한 폴더: 'app' 폴더 안에 Dockerfile이 있음
        BACKEND_DIR = "app"
        IMAGE_TAG = "latest"
        // ECR URL 구성: 예) 296062584049.dkr.ecr.ap-northeast-2.amazonaws.com
        ECR_URL = "296062584049.dkr.ecr.ap-northeast-2.amazonaws.com"
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
                echo "Building Docker image from ${BACKEND_DIR} directory..."
                // BACKEND_DIR 폴더로 이동하여 Dockerfile을 사용해 이미지 빌드
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
                    // 레포지토리 이름 없이 ECR URL(도메인)만 사용합니다.
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
                    // ECS 클러스터 이름과 서비스 이름은 실제 환경에 맞게 수정합니다.
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
