pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "296062584049"
        AWS_REGION = "ap-northeast-2"
        ECR_REPO = "dashback"
        IMAGE_TAG = "latest"
        // ECR URL 형식: {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com
        ECR_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // Dockerfile은 프로젝트 루트에 있으므로 BACKEND_DIR는 "." 입니다.
        BACKEND_DIR = "."
        // ECS 클러스터와 서비스 이름 (실제 AWS 콘솔에서 확인 후 수정)
        ECS_CLUSTER = "devcluster"         // 예: "devcluster" 또는 "arn:aws:ecs:ap-northeast-2:296062584049:cluster/devcluster"
        ECS_SERVICE = "dash2"            // 예: 실제 서비스 이름
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Build') {
            steps {
                dir("${BACKEND_DIR}") {
                    script {
                        dockerImage = docker.build("${ECR_URL}/${ECR_REPO}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Docker Login to ECR') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                        sh '''
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                        '''
                    }
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
        stage('Deploy to ECS') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                        sh '''
                           aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --force-new-deployment --region ${AWS_REGION}
                        '''
                    }
                }
            }
        }
    }
    post {
        success {
            echo "Backend deployment succeeded."
        }
        failure {
            echo "Backend deployment failed."
        }
    }
}
