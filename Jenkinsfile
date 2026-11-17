pipeline {
    agent { label 'docker-slave-staging' }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    parameters {
        booleanParam(name: 'PUBLISH_IMAGE', defaultValue: false, description: 'Publish an image from master to Docker Hub')
        string(name: 'IMAGE_TAG', defaultValue: '', description: 'Versioned Docker image tag to publish (required when publishing)')
    }

    environment {
        IMAGE = 'lightspeedcommerceinc/shpkpr'
    }

    stages {
        stage('Validate release') {
            when { expression { params.PUBLISH_IMAGE } }
            steps {
                script {
                    if (env.BRANCH_NAME != 'master') {
                        error('Images can only be published from the master branch')
                    }
                    if (!(params.IMAGE_TAG ==~ /[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}/) || params.IMAGE_TAG == 'latest') {
                        error('Provide a valid, versioned IMAGE_TAG other than latest')
                    }
                }
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build --platform linux/amd64 -t "$IMAGE:$GIT_COMMIT" .'
            }
        }

        stage('Check Docker API negotiation') {
            steps {
                sh '''
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        --entrypoint python "$IMAGE:$GIT_COMMIT" \
                        -c 'import docker; print("Docker API:", docker.from_env(version="auto").version()["ApiVersion"])'
                '''
            }
        }

        stage('Publish image') {
            when { expression { params.PUBLISH_IMAGE && env.BRANCH_NAME == 'master' } }
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub_roboshopkeep') {
                        sh '''
                            docker tag "$IMAGE:$GIT_COMMIT" "$IMAGE:$IMAGE_TAG"
                            docker push "$IMAGE:$IMAGE_TAG"
                        '''
                    }
                }
            }
        }
    }
}
