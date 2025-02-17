pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dashback"             // ECR 리포지토리 이름
        IMAGE_TAG = "latest"
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        BACKEND_DIR = "app"               // 백엔드 코드가 위치한 폴더 (프로젝트 구조에 맞게 조정)
    }

    stages {
        stage('Checkout') {
            steps {
                // 저장소에서 코드를 체크아웃합니다.
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                // 백엔드 폴더로 이동하여 Dockerfile을 기반으로 도커 이미지를 빌드합니다.
                dir("${BACKEND_DIR}") {
                    script {
                        dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
                // AWS 자격증명을 사용하여 ECR에 로그인합니다.
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-credentials'
                ]]) {
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                    '''
                }
            }
        }
        stage('Docker Push') {
            steps {
                script {
                    // 빌드된 도커 이미지를 ECR에 푸시합니다.
                    dockerImage.push()
                }
            }
        }
        stage('Deploy to ECS') {
            steps {
                // AWS 자격증명을 사용하여 ECS 서비스 업데이트(롤링 업데이트)를 수행합니다.
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-credentials'
                ]]) {
                    sh '''
                        aws ecs update-service --cluster devcluster --service dash/back --force-new-deployment --region ${AWS_REGION}
                    '''
                }
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