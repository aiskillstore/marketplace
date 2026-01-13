// Jenkinsfile - Semgrep Security Scanning
// Basic pipeline with Semgrep security gate

pipeline {
    agent any

    environment {
        SEMGREP_VERSION = '1.50.0'  // Pin to specific version
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    // Install Semgrep
                    sh 'pip3 install semgrep==${SEMGREP_VERSION}'

                    // Run Semgrep scan
                    sh '''
                        semgrep --config="p/security-audit" \
                                --config="p/owasp-top-ten" \
                                --json \
                                --output=semgrep-results.json \
                                --severity=ERROR \
                                --severity=WARNING
                    '''
                }
            }
        }

        stage('Process Results') {
            steps {
                script {
                    // Parse results
                    def results = readJSON file: 'semgrep-results.json'
                    def findings = results.results.size()
                    def critical = results.results.findAll {
                        it.extra.severity == 'ERROR'
                    }.size()

                    echo "Total findings: ${findings}"
                    echo "Critical findings: ${critical}"

                    // Fail build if critical findings
                    if (critical > 0) {
                        error("❌ Critical security vulnerabilities detected!")
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive scan results
            archiveArtifacts artifacts: 'semgrep-results.json',
                           fingerprint: true

            // Publish results (if using warnings-ng plugin)
            // recordIssues(
            //     tools: [semgrep(pattern: 'semgrep-results.json')],
            //     qualityGates: [[threshold: 1, type: 'TOTAL', unstable: false]]
            // )
        }
        failure {
            echo '❌ Security scan failed - review findings'
        }
        success {
            echo '✅ No critical security issues detected'
        }
    }
}

// Advanced: Differential scanning for PRs
pipeline {
    agent any

    environment {
        TARGET_BRANCH = env.CHANGE_TARGET ?: 'main'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm

                script {
                    // Fetch target branch for comparison
                    sh """
                        git fetch origin ${TARGET_BRANCH}:${TARGET_BRANCH}
                    """
                }
            }
        }

        stage('Differential Scan') {
            when {
                changeRequest()  // Only for pull requests
            }
            steps {
                sh """
                    pip3 install semgrep

                    semgrep --config="p/security-audit" \
                            --baseline-commit="${TARGET_BRANCH}" \
                            --json \
                            --output=semgrep-diff.json
                """

                script {
                    def results = readJSON file: 'semgrep-diff.json'
                    def newFindings = results.results.size()

                    if (newFindings > 0) {
                        echo "❌ ${newFindings} new security issues introduced"
                        error("Fix security issues before merging")
                    } else {
                        echo "✅ No new security issues"
                    }
                }
            }
        }

        stage('Full Scan') {
            when {
                branch 'main'  // Full scan on main branch
            }
            steps {
                sh """
                    semgrep --config="p/security-audit" \
                            --config="p/owasp-top-ten" \
                            --config="p/cwe-top-25" \
                            --json \
                            --output=semgrep-full.json
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'semgrep-*.json',
                           allowEmptyArchive: true
        }
    }
}

// With custom rules
pipeline {
    agent any

    stages {
        stage('Security Scan with Custom Rules') {
            steps {
                sh """
                    pip3 install semgrep

                    # Run with both official and custom rules
                    semgrep --config="p/owasp-top-ten" \
                            --config="custom-rules/" \
                            --json \
                            --output=results.json
                """

                script {
                    // Generate HTML report (requires additional tooling)
                    sh """
                        python3 -c "
import json
with open('semgrep-results.json') as f:
    results = json.load(f)
    findings = results['results']
    print(f'Security Scan Complete:')
    print(f'  Total Findings: {len(findings)}')
    for severity in ['ERROR', 'WARNING', 'INFO']:
        count = len([f for f in findings if f.get('extra', {}).get('severity') == severity])
        print(f'  {severity}: {count}')
"
                    """
                }
            }
        }
    }
}
