pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        PROJECT_DIR    = "/home/ec2-user/project"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // (디버그) Jenkins 작업공간 파일 확인
        stage('Debug Workspace') {
            steps {
                sh 'pwd'
                sh 'ls -alR'
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}",
                                               "--platform=linux/amd64 -f Dockerfile .")
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

        stage('Transfer Files to EC2') {
            steps {
                script {
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'EC2_Instance', // Publish Over SSH 설정
                                transfers: [
                                    sshTransfer(
                                        sourceFiles: '**',         // 모든 파일
                                        removePrefix: '',          // 폴더 구조 유지
                                        remoteDirectory: PROJECT_DIR,
                                        remoteDirectorySDF: false  // 날짜 폴더 생성 방지
                                    )
                                ],
                                verbose: true
                            )
                        ]
                    )
                }
            }
        }

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
                                    // 여기서는 파일을 전송하지 않고, 명령만 실행
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
