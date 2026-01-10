// Jenkins Declarative Pipeline for Black Duck SCA Scanning
//
// Prerequisites:
// 1. Install "Synopsys Detect" plugin in Jenkins
// 2. Configure Black Duck server in Jenkins Global Configuration
// 3. Add credentials: BLACKDUCK_URL and BLACKDUCK_API_TOKEN

pipeline {
    agent any

    parameters {
        choice(
            name: 'SCAN_TYPE',
            choices: ['RAPID', 'INTELLIGENT', 'FULL'],
            description: 'Type of Black Duck scan to perform'
        )
        booleanParam(
            name: 'FAIL_ON_POLICY_VIOLATION',
            defaultValue: true,
            description: 'Fail build on policy violations'
        )
        booleanParam(
            name: 'GENERATE_SBOM',
            defaultValue: false,
            description: 'Generate Software Bill of Materials'
        )
    }

    environment {
        BLACKDUCK_URL = credentials('blackduck-url')
        BLACKDUCK_TOKEN = credentials('blackduck-api-token')
        PROJECT_NAME = "${env.JOB_NAME}"
        PROJECT_VERSION = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
        DETECT_JAR_DOWNLOAD_DIR = "${WORKSPACE}/.blackduck"
    }

    options {
        timestamps()
        timeout(time: 2, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '10'))
    }

    stages {
        stage('Preparation') {
            steps {
                script {
                    echo "=========================================="
                    echo "Black Duck SCA Scan"
                    echo "=========================================="
                    echo "Project: ${PROJECT_NAME}"
                    echo "Version: ${PROJECT_VERSION}"
                    echo "Scan Type: ${params.SCAN_TYPE}"
                    echo "=========================================="
                }

                // Clean previous scan results
                sh 'rm -rf blackduck-output || true'
                sh 'mkdir -p blackduck-output'
            }
        }

        stage('Dependency Installation') {
            steps {
                script {
                    // Install dependencies based on project type
                    if (fileExists('package.json')) {
                        echo 'Node.js project detected'
                        sh 'npm ci || npm install'
                    }
                    else if (fileExists('requirements.txt')) {
                        echo 'Python project detected'
                        sh 'pip install -r requirements.txt'
                    }
                    else if (fileExists('pom.xml')) {
                        echo 'Maven project detected'
                        sh 'mvn dependency:resolve'
                    }
                    else if (fileExists('build.gradle')) {
                        echo 'Gradle project detected'
                        sh './gradlew dependencies'
                    }
                }
            }
        }

        stage('Black Duck Scan') {
            steps {
                script {
                    def detectCommand = """
                        bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
                            --blackduck.url=${BLACKDUCK_URL} \
                            --blackduck.api.token=${BLACKDUCK_TOKEN} \
                            --detect.project.name="${PROJECT_NAME}" \
                            --detect.project.version.name="${PROJECT_VERSION}" \
                            --detect.output.path=${WORKSPACE}/blackduck-output \
                            --detect.cleanup=false \
                            --detect.risk.report.pdf=true \
                            --detect.notices.report=true
                    """

                    // Add scan type configuration
                    switch(params.SCAN_TYPE) {
                        case 'RAPID':
                            detectCommand += " --detect.detector.search.depth=0"
                            detectCommand += " --detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING"
                            break
                        case 'INTELLIGENT':
                            detectCommand += " --detect.detector.search.depth=3"
                            break
                        case 'FULL':
                            detectCommand += " --detect.tools=DETECTOR,SIGNATURE_SCAN,BINARY_SCAN"
                            detectCommand += " --detect.detector.search.depth=10"
                            break
                    }

                    // Add policy check if enabled
                    if (params.FAIL_ON_POLICY_VIOLATION) {
                        detectCommand += " --detect.policy.check.fail.on.severities=BLOCKER,CRITICAL"
                        detectCommand += " --detect.wait.for.results=true"
                    }

                    // Execute scan
                    try {
                        sh detectCommand
                    } catch (Exception e) {
                        if (params.FAIL_ON_POLICY_VIOLATION) {
                            error("Black Duck policy violations detected!")
                        } else {
                            unstable("Black Duck scan completed with violations")
                        }
                    }
                }
            }
        }

        stage('Generate SBOM') {
            when {
                expression { params.GENERATE_SBOM == true }
            }
            steps {
                script {
                    sh """
                        bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
                            --blackduck.url=${BLACKDUCK_URL} \
                            --blackduck.api.token=${BLACKDUCK_TOKEN} \
                            --detect.project.name="${PROJECT_NAME}" \
                            --detect.project.version.name="${PROJECT_VERSION}" \
                            --detect.tools=DETECTOR \
                            --detect.bom.aggregate.name=sbom-cyclonedx.json \
                            --detect.output.path=${WORKSPACE}/sbom-output
                    """
                }
            }
        }

        stage('Parse Results') {
            steps {
                script {
                    // Parse Black Duck results
                    def statusFile = sh(
                        script: 'find blackduck-output -name "status.json" -type f | head -n 1',
                        returnStdout: true
                    ).trim()

                    if (statusFile) {
                        def status = readJSON file: statusFile
                        echo "Policy Status: ${status.policyStatus?.overallStatus}"
                        echo "Component Count: ${status.componentStatus?.componentCount}"

                        // Set build description
                        currentBuild.description = """
                            Black Duck Scan Results
                            Policy: ${status.policyStatus?.overallStatus}
                            Components: ${status.componentStatus?.componentCount}
                        """.stripIndent()
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                // Archive reports
                archiveArtifacts(
                    artifacts: 'blackduck-output/**/BlackDuck_RiskReport_*.pdf,blackduck-output/**/BlackDuck_Notices_*.txt',
                    allowEmptyArchive: true,
                    fingerprint: true
                )

                // Archive SBOM if generated
                archiveArtifacts(
                    artifacts: 'sbom-output/**/sbom-cyclonedx.json',
                    allowEmptyArchive: true,
                    fingerprint: true
                )

                // Publish HTML reports
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'blackduck-output',
                    reportFiles: '**/*.html',
                    reportName: 'Black Duck Security Report'
                ])
            }
        }

        stage('Quality Gate') {
            when {
                expression { params.FAIL_ON_POLICY_VIOLATION == true }
            }
            steps {
                script {
                    // Check for policy violations
                    def statusFile = sh(
                        script: 'find blackduck-output -name "status.json" -type f | head -n 1',
                        returnStdout: true
                    ).trim()

                    if (statusFile) {
                        def status = readJSON file: statusFile

                        if (status.policyStatus?.overallStatus == 'IN_VIOLATION') {
                            error("Build failed: Black Duck policy violations detected")
                        } else {
                            echo "✅ No policy violations detected"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: '.blackduck', type: 'INCLUDE'],
                    [pattern: 'blackduck-output/runs', type: 'INCLUDE']
                ]
            )
        }

        success {
            echo '✅ Black Duck scan completed successfully'

            // Send notification (configure as needed)
            // emailext(
            //     subject: "Black Duck Scan Success: ${PROJECT_NAME}",
            //     body: "Black Duck scan completed with no policy violations",
            //     to: "${env.CHANGE_AUTHOR_EMAIL}"
            // )
        }

        failure {
            echo '❌ Black Duck scan failed or policy violations detected'

            // Send notification
            // emailext(
            //     subject: "Black Duck Scan Failed: ${PROJECT_NAME}",
            //     body: "Black Duck scan detected policy violations. Review the report for details.",
            //     to: "${env.CHANGE_AUTHOR_EMAIL}"
            // )
        }

        unstable {
            echo '⚠️  Black Duck scan completed with warnings'
        }
    }
}

// Shared library functions (optional)

def getProjectType() {
    if (fileExists('package.json')) return 'nodejs'
    if (fileExists('requirements.txt')) return 'python'
    if (fileExists('pom.xml')) return 'maven'
    if (fileExists('build.gradle')) return 'gradle'
    if (fileExists('Gemfile')) return 'ruby'
    if (fileExists('go.mod')) return 'golang'
    return 'unknown'
}

def installDependencies(projectType) {
    switch(projectType) {
        case 'nodejs':
            sh 'npm ci || npm install'
            break
        case 'python':
            sh 'pip install -r requirements.txt'
            break
        case 'maven':
            sh 'mvn dependency:resolve'
            break
        case 'gradle':
            sh './gradlew dependencies'
            break
        case 'ruby':
            sh 'bundle install'
            break
        case 'golang':
            sh 'go mod download'
            break
        default:
            echo "Unknown project type, skipping dependency installation"
    }
}
