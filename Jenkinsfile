pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO    = "dashback"
        IMAGE_TAG   = "latest"
        ECR_URL     = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // EC2 관련 설정
        EC2_HOST    = "3.34.44.0"   // 실제 EC2 인스턴스의 퍼블릭 IP 또는 DNS
        EC2_USER    = "ec2-user"    // Amazon Linux 2의 기본 사용자
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
                    // Dockerfile을 이용해 이미지를 빌드하고 dockerImage 변수에 저장
                    dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}", "-f Dockerfile .")
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
                // AWS 자격증명은 Jenkins에 미리 등록된 aws-credentials ID 사용
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
                    // 빌드한 이미지를 ECR에 푸시
                    dockerImage.push()
                }
            }
        }
        stage('Deploy to EC2') {
            steps {
                // EC2에 SSH로 접속하여 새로운 이미지로 컨테이너 실행
                sshCommand remote: [
                    name: "EC2_Instance",
                    host: "${EC2_HOST}",
                    port: 22,
                    user: "${EC2_USER}",
                    credentialsId: "dash_key",  // EC2용 SSH 자격증명 ID (authorized_keys에 공개키 등록 필요)
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
