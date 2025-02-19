pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        EC2_HOST       = "3.34.44.0"   // 실제 EC2 인스턴스의 퍼블릭 IP 또는 DNS
        // EC2_USER는 자격 증명 "dash_key"에 이미 포함되어 있다고 가정
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
                        aws ecr get-login-password --region ${AWS_REGION} \
                          | docker login --username AWS --password-stdin ${ECR_URL}
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
        stage('Configure sudo on EC2') {
            steps {
                sshCommand remote: [
                    name: "EC2_Instance",
                    host: "${EC2_HOST}",
                    port: 22,
                    credentialsId: "dash_key",  // "dash_key" 자격 증명에 ec2-user와 PEM 키가 설정되어 있어야 함
                    allowAnyHosts: true
                ], command: '''
                    # 비밀번호 없이 sudo를 사용하도록 설정 (이미 등록된 내용이 중복되지 않도록 주의)
                    sudo su -c "echo 'ec2-user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"
                    sudo sed -i 's/^Defaults.*requiretty/# &/' /etc/sudoers
                    echo "sudoers 설정 완료"
                '''
            }
        }
        stage('Deploy to EC2') {
            steps {
                sshCommand remote: [
                    name: "EC2_Instance",
                    host: "${EC2_HOST}",
                    port: 22,
                    credentialsId: "dash_key",
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
