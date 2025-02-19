pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dashback"
        IMAGE_TAG = "latest"
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // EC2 관련 설정
        EC2_HOST = "3.34.44.0"  // 실제 EC2 인스턴스의 퍼블릭 IP 또는 DNS
        EC2_USER = "ec2-user"   // 예: Amazon Linux 2의 기본 사용자
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                // 프로젝트 루트에 있는 Dockerfile 사용 (필요에 따라 BACKEND_DIR 조정)
                script {
                    dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}", "-f Dockerfile .")
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
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
                    dockerImage.push()
                }
            }
        }
        stage('Test SSH Connection') {
            steps {
                // 간단한 SSH 연결 테스트 (명령어: echo "SSH 연결 테스트 완료")
                sshCommand remote: [
                    name: "EC2_Test",
                    host: "${EC2_HOST}",
                    port: 22,
                    user: "${EC2_USER}",
                    credentialsId: "dashkey",  // Jenkins에 등록한 SSH 자격증명 ID
                    allowAnyHosts: true
                ], command: "echo 'SSH 연결 테스트 완료'"
            }
        }
        stage('Deploy to EC2') {
            steps {
                // EC2 인스턴스에 SSH로 접속하여 도커 배포 명령어 실행
                sshCommand remote: [
                    name: "EC2_Instance",
                    host: "${EC2_HOST}",
                    port: 22,
                    user: "${EC2_USER}",
                    credentialsId: "dashkey",
                    allowAnyHosts: true
                ], command: '''
                    echo "Pulling the latest image..."
                    sudo docker pull ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}

                    echo "Stopping existing container if exists..."
                    sudo docker stop my_app_container || true
                    sudo docker rm my_app_container || true

                    echo "Running new container..."
                    sudo docker run -d --name my_app_container -p 80:8000 ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}
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
