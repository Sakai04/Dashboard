pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dashback"
        IMAGE_TAG = "latest"
        // ECR URL은 AWS 계정과 리전을 조합하여 만듭니다.
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // EC2 설정 – 실제 EC2 인스턴스의 퍼블릭 IP 또는 DNS로 변경하세요.
        EC2_HOST = "3.34.44.0"
        EC2_USER = "ec2-user"
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
                    // Dockerfile이 프로젝트 루트에 있다고 가정합니다.
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
                // SSH Steps 플러그인을 사용하여 원격 EC2에 접속 후 명령어 실행
                sshCommand remote: [
                    name: "EC2_Instance",
                    host: "${EC2_HOST}",
                    port: 22,
                    user: "${EC2_USER}",
                    credentialsId: "dashkey",  // Jenkins에 등록한 SSH 자격증명 ID (예: dashkey)
                    allowAnyHosts: true
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
