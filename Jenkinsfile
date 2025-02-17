pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dashback"
        IMAGE_TAG = "latest"
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // EC2 인스턴스 접속 관련 환경 변수 (Jenkins Credentials에서 사용)
        EC2_HOST = "your.ec2.public.ip.or.dns"  // 실제 EC2 인스턴스의 퍼블릭 IP 또는 DNS
        EC2_USER = "ec2-user"  // 예시: Amazon Linux의 기본 사용자 (OS에 따라 변경)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                script {
                    // 프로젝트 루트의 Dockerfile을 사용하여 도커 이미지를 빌드합니다.
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
        stage('Deploy to EC2') {
            steps {
                // SSH 플러그인을 사용하여 EC2 인스턴스에 접속한 후 명령어를 실행합니다.
                // Jenkins의 SSH Pipeline Steps Plugin을 사용해야 합니다.
                sshCommand remote: [
                    name: 'EC2_Instance',
                    host: "${EC2_HOST}",
                    port: 22,
                    user: "${EC2_USER}",
                    credentialsId: "ec2-ssh"  // Jenkins에 등록한 SSH 자격증명 ID
                ], command: '''
                    echo "Pulling the latest image..."
                    docker pull ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}

                    echo "Stopping existing container if exists..."
                    docker stop my_app_container || true
                    docker rm my_app_container || true

                    echo "Running new container..."
                    docker run -d --name my_app_container -p 80:8000 ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}
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