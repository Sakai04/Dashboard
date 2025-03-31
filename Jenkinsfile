pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = ""
        AWS_REGION     = "
        ECR_REPO       = "
        IMAGE_TAG      = "
        ECR_URL        = "
        // EC2 접속 정보는 Jenkins의 Publish Over SSH 설정에 등록된 'EC2_Instance'를 사용합니다.
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
                    // t2.micro (x86_64) 인스턴스에 맞게 --platform 옵션 추가
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
                    // 프로젝트 전체가 배포된 경로를 지정합니다.
                    def composeDirectory = "/home/ec2-user/project"

                    def deployCommand = """
                        cd ${composeDirectory}
                        docker-compose pull
                        docker-compose up -d --remove-orphans
                    """.stripIndent()

                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance',  // Jenkins에 등록된 EC2 접속 설정 이름
                                transfers: [
                                    sshTransfer(
                                        sourceFiles: '',  // 파일 전송은 필요 없음
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
