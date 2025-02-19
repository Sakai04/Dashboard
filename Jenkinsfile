pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // EC2 접속 정보는 Jenkins Publish Over SSH 설정에서 관리 (예: 'EC2_Instance')
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
                    // x86_64 (t2.micro)에 맞게 빌드합니다.
                    dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}", "--platform=linux/amd64 -f Dockerfile .")
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
        stage('Deploy via Docker Compose on EC2') {
            steps {
                script {
                    // docker-compose 파일이 위치한 디렉터리 경로 (예: /home/ec2-user/app)
                    def composeDirectory = "/home/ec2-user/app"

                    // docker-compose 명령어로 이미지를 풀하고, 컨테이너를 업데이트 합니다.
                    def deployCommand = """
                        cd ${composeDirectory}
                        docker-compose pull
                        docker-compose up -d
                    """.stripIndent()

                    // Publish Over SSH 플러그인을 사용해 EC2에서 위 명령어 실행
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance',  // Jenkins에 미리 설정한 Publish Over SSH 서버 이름
                                transfers: [
                                    sshTransfer(
                                        sourceFiles: '', // 파일 전송이 필요하지 않으므로 비워둡니다.
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
            echo "Deployment via Docker Compose completed successfully."
        }
        failure {
            echo "Deployment failed."
        }
    }
}
