pipeline {
    agent any

    stages {
        stage('E2E Tests') {
            steps {
                withCredentials([
                    string(credentialsId: 'api_dev_key', variable: 'api_dev_key'),
                    usernamePassword(credentialsId: 'pastebin-creds', usernameVariable: 'api_user_name', passwordVariable: 'api_user_password')
                ]) {
                    sh 'pipx install uv'
                    sh '~/.local/bin/uv venv -p 3.10'
                    sh '~/.local/bin/uv pip sync requirements.txt'
                    sh '~/.local/bin/uv pip install behave yt-dlp'
                    sh '''
                        . .venv/bin/activate
                        behave e2e/ --no-capture
                    '''
                }
            }
        }
    }
}
