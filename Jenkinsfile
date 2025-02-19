pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        EC2_HOST       = "3.34.44.0"   // 실제 EC2 인스턴스의 퍼블릭 IP 또는 DNS
        EC2_USER       = "ec2-user"     // EC2 인스턴스의 사용자 이름
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
                    user: "${EC2_USER}",          // 반드시 명시적으로 사용자 지정
                    credentialsId: "dash_key",      // 자격 증명 ID
                    allowAnyHosts: true
                ], command: '''
                    # 1) ec2-user에 대해 비밀번호 없이 sudo 허용
                    sudo su -c "echo 'ec2-user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"
                    # 2) requiretty가 활성화되어 있다면 주석 처리
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
                    user: "${EC2_USER}",          // 반드시 명시적으로 사용자 지정
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
