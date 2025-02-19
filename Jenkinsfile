pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION     = "ap-northeast-2"
        ECR_REPO       = "dashback"
        IMAGE_TAG      = "latest"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        PROJECT_DIR    = "/home/ec2-user/project"

        // Credentials 주입
        DB_USER        = credentials('DB_USER')
        DB_PASSWORD    = credentials('DB_PASSWORD')
        DB_NAME        = credentials('DB_NAME')
        PGADMIN_EMAIL  = credentials('PGADMIN_EMAIL')
        PGADMIN_PASSWORD = credentials('PGADMIN_PASSWORD')
    }

    stages {
        // [기존 stage 생략...]

        stage('Prepare Env File') {
            steps {
                sh '''
                    cat <<EOF > .env
                    DB_USER=${DB_USER}
                    DB_PASSWORD=${DB_PASSWORD}
                    DB_NAME=${DB_NAME}
                    PGADMIN_EMAIL=${PGADMIN_EMAIL}
                    PGADMIN_PASSWORD=${PGADMIN_PASSWORD}
                    ECR_URL=${ECR_URL}
                    EOF
                '''
            }
        }

        stage('Transfer Files to EC2') {
            steps {
                sshPublisher(
                    publishers: [
                        sshPublisherDesc(
                            configName: 'EC2_Instance',
                            transfers: [
                                sshTransfer(
                                    sourceFiles: '**/*',
                                    removePrefix: '',
                                    remoteDirectory: PROJECT_DIR,
                                    remoteDirectorySDF: false,
                                    execTimeout: 1200000
                                )
                            ],
                            verbose: true
                        )
                    ]
                )
            }
        }

        stage('Deploy via Docker Compose on EC2') {
            steps {
                script {
                    def deployCommand = """
                        cd ${PROJECT_DIR}
                        export \$(grep -v '^#' .env | xargs)  # 환경 변수 로드

                        # ECR 이미지 풀
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}

                        # 기존 컨테이너 정리
                        docker-compose down --remove-orphans

                        # 새 컨테이너 실행
                        docker-compose up -d --force-recreate

                        # 상태 확인
                        sleep 10
                        docker ps -a
                        docker logs fastapi_app
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
}
