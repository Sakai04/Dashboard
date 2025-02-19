pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // EC2 접속 정보는 Publish Over SSH 설정(예: 'EC2_Instance')에서 관리합니다.
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
                sshPublisher(
                    publishers: [
                        sshPublisherDesc(
                            configName: 'EC2_Instance', // Jenkins에 미리 설정한 Publish Over SSH 서버 이름
                            transfers: [
                                sshTransfer(
                                    sourceFiles: '',
                                    execCommand: '''
                                        # ec2-user에 대해 비밀번호 없이 sudo 허용
                                        sudo su -c "echo 'ec2-user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"
                                        # requiretty가 활성화되어 있다면 주석 처리
                                        sudo sed -i 's/^Defaults.*requiretty/# &/' /etc/sudoers
                                        echo "sudoers 설정 완료"
                                    '''
                                )
                            ],
                            verbose: true
                        )
                    ]
                )
            }
        }
        stage('Deploy to EC2') {
            steps {
                script {
                    // 환경 변수를 미리 확장한 명령어 문자열 생성
                    def deployCommand = """
                        echo "Pulling the latest image..."
                        sudo docker pull ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}
                        echo "Stopping existing container if exists..."
                        sudo docker stop my_app_container || true
                        sudo docker rm my_app_container || true
                        echo "Running new container..."
                        sudo docker run -d --name my_app_container -p 80:8000 ${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}
                    """.stripIndent()

                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance', // Publish Over SSH에 등록된 서버 설정 이름
                                transfers: [
                                    sshTransfer(
                                        sourceFiles: '',
                                        execCommand: deployCommand
                                    )
                                ],
                                verbose: true
                            )
                        ]
                    )
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
