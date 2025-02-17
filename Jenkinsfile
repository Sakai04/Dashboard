pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dashback"
        IMAGE_TAG = "latest"
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        BACKEND_DIR = "app"  // 백엔드 코드가 위치한 폴더 (프로젝트 구조에 맞게 조정)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                dir("${BACKEND_DIR}") {
                    script {
                        dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
                // 인스턴스 역할을 사용하는 경우 자격증명 없이 동작할 수 있으나, 필요 시 withCredentials 블록 사용
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                '''
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
                // ECS 업데이트: 클러스터와 서비스 이름은 실제 환경에 맞게 수정하세요.
                sh '''
                  aws ecs update-service --cluster devcluster --service dash/back --force-new-deployment --region ${AWS_REGION}
                '''
            }
        }
    }
    post {
        success {
            echo "Backend deployment completed successfully."
        }
        failure {
            echo "Backend deployment failed."
        }
    }
}
