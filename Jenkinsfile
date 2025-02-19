pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        PROJECT_DIR    = "/home/ec2-user/project"  // EC2에 프로젝트 저장할 경로
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
                    // t2.micro(x86_64)에 맞춰 빌드
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

        // 1) EC2에 소스(특히 docker-compose.yml) 전송
        stage('Transfer Files to EC2') {
            steps {
                script {
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance',  // Publish Over SSH 설정에 등록된 이름
                                transfers: [
                                    sshTransfer(
                                        // 현재 Jenkins 워크스페이스의 모든 파일(서브디렉토리 포함)
                                        sourceFiles: '**',
                                        // removePrefix를 비워두면 폴더 구조가 그대로 복사됨
                                        removePrefix: '',
                                        // EC2에 복사할 경로
                                        remoteDirectory: "${PROJECT_DIR}",
                                        // 날짜/시간 기반 폴더 생성 방지
                                        remoteDirectorySDF: false
                                    )
                                ],
                                verbose: true
                            )
                        ]
                    )
                }
            }
        }

        // 2) 배포 명령 (docker-compose) 실행
        stage('Deploy via Docker Compose on EC2') {
            steps {
                script {
                    def deployCommand = """
                        cd ${PROJECT_DIR}
                        echo "=== Debug: List files in ${PROJECT_DIR} ==="
                        ls -l

                        echo "=== Show docker-compose.yml content ==="
                        cat docker-compose.yml

                        echo "=== Pulling latest images ==="
                        docker-compose pull

                        echo "=== Starting containers ==="
                        docker-compose up -d --remove-orphans
                    """.stripIndent()

                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance',
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
            echo "Deployment completed successfully."
        }
        failure {
            echo "Deployment failed."
        }
    }
}
