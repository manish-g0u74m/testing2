pipeline{
    agent any
    triggers {
    githubPush()
    }
    stages{
        stage("Code Clone"){
            steps{
                echo "Code Clone Stage"
                git url: "https://github.com/manish-g0u74m/testing.git", branch: "master"
            }
        }
        stage("Code Build & Test"){
            steps{
                echo "Code Build Stage"
                sh "docker build -t restaurent-g0u74m ."
            }
        }
        stage("Push To DockerHub"){
            steps{
                withCredentials([usernamePassword(
                    credentialsId:"dockerHubCreds",
                    usernameVariable:"dockerHubUser", 
                    passwordVariable:"dockerHubPass")]){
                sh 'echo $dockerHubPass | docker login -u $dockerHubUser --password-stdin'
                sh "docker image tag restaurent-g0u74m:latest ${env.dockerHubUser}/restaurent-g0u74m:latest"
                sh "docker push ${env.dockerHubUser}/restaurent-g0u74m:latest"
                }
            }
        }
        stage("Deploy"){
            steps{
                sh "docker-compose down && docker-compose up -d --build"
            }
        }
    }
}
