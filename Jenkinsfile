pipeline {
    agent any

    environment {
        // AWS 계정 및 리포지토리 관련 변수 (Jenkins 환경 변수로 안전하게 관리)
        AWS_ACCOUNT_ID = "296062584049"   // 본인 AWS 계정 ID
        AWS_REGION = "ap-northeast-2"           // 본인 리전
        ECR_REPO = "dash/back"       // ECR 리포지토리 이름
        BACKEND_DIR = "app"            // 백엔드 코드가 위치한 폴더
        IMAGE_TAG = "latest"
        // ECR URL: 예) 123456789012.dkr.ecr.us-east-1.amazonaws.com
        ECR_URL = "296062584049dkr.ecr.ap-northeast-2.amazonaws.com"
        // API_BASE_URL 등 추가 환경변수는 필요에 따라 추가합니다.
    }

    stages {
        stage('Checkout') {
            steps {
                // Git 저장소에서 코드를 체크아웃합니다.
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                dir(app) {
                    script {
                        dockerImage = docker.build("296062584049.dkr.ecr.ap-northeast-2.amazonaws.com/dash/back/dash/back:latest")
                    }
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
                script {
                    sh '''
                        aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 296062584049.dkr.ecr.ap-northeast-2.amazonaws.com/dash/back
                    '''
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
                    // ECS 업데이트 명령을 실행합니다.
                    // 아래 예시는 ECS 서비스 업데이트 예시입니다.
                    // 실제 클러스터 및 서비스 이름에 맞게 수정해야 합니다.
                    sh '''
                      aws ecs update-service \
                        --cluster devcluster \
                        --service dash/back \
                        --force-new-deployment \
                        --region ap-northeast-2
                    '''
                }
            }
        }
    }
    post {
        success {
            echo "Backend 배포 완료"
        }
        failure {
            echo "Backend 배포 실패"
        }
    }
}
