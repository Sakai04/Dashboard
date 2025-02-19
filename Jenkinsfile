pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        PROJECT_DIR    = "/home/ec2-user/project"  // EC2에서 프로젝트를 저장할 경로
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
                    def deployCommand = """
                        mkdir -p ${PROJECT_DIR}  # 디렉토리가 없으면 생성
                        cd ${PROJECT_DIR}
                        ls -l  # 파일 목록 확인 (디버깅용)
                        cat docker-compose.yml  # 파일 내용 확인 (디버깅용)
                        docker-compose pull
                        docker-compose up -d --remove-orphans
                    """.stripIndent()

                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance',
                                transfers: [
                                    // 🔹 **프로젝트 전체 전송**
                                    sshTransfer(
                                        sourceFiles: '**',
                                        removePrefix: '',
                                        remoteDirectory: PROJECT_DIR
                                    ),
                                    // 🔹 **배포 명령 실행**
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
            echo "Deployment via Docker Compose completed successfully."
        }
        failure {
            echo "Deployment failed."
        }
    }
}
