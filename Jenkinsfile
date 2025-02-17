pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "das/back"
        IMAGE_TAG = "latest"
        // ECR URL 형식: {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // 백엔드 소스 코드가 위치한 디렉토리 (예: app)
        BACKEND_DIR = "app"
    }

    stages {
        stage('Checkout') {
            steps {
                // Git 저장소에서 소스코드를 체크아웃합니다.
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                // BACKEND_DIR 디렉토리 내에서 도커 이미지를 빌드합니다.
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
                    // AWS 자격증명은 Jenkins Credentials에 "aws-credentials" ID로 등록되어 있어야 합니다.
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
                    // 빌드된 이미지를 ECR로 푸시합니다.
                    dockerImage.push()
                }
            }
        }
        stage('Deploy to ECS') {
            steps {
                script {
                    // ECS 업데이트 명령어 실행 전 AWS 자격증명을 withCredentials로 주입합니다.
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
