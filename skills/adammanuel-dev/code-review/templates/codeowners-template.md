# CODEOWNERS - Code Ownership and Review Assignment
# Documentation: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners

# ============================================================================
# OVERVIEW
# ============================================================================
# This file defines code ownership for automatic review assignment.
# When a PR modifies files matching a pattern, owners are auto-assigned.
#
# Syntax:
#   pattern   @owner1 @owner2 @team-name
#
# Patterns are matched from top to bottom. Later matches override earlier ones.
# ============================================================================

# ============================================================================
# DEFAULT OWNERS
# ============================================================================
# Catch-all for files without specific owners
# Remove or adjust based on your team structure

* @team-leads


# ============================================================================
# FRONTEND CODE
# ============================================================================

# React components
/src/components/            @frontend-team
/src/pages/                 @frontend-team

# Styles and assets
/src/styles/                @frontend-team @design-team
/public/assets/             @frontend-team @design-team

# Frontend utilities
/src/utils/client/          @frontend-team


# ============================================================================
# BACKEND CODE
# ============================================================================

# API endpoints
/src/api/                   @backend-team
/src/routes/                @backend-team

# Services and business logic
/src/services/              @backend-team

# Database code
/src/database/              @backend-team @database-experts
/src/migrations/            @backend-team @database-experts

# Backend utilities
/src/utils/server/          @backend-team


# ============================================================================
# SECURITY-CRITICAL PATHS
# ============================================================================
# Require security team approval for sensitive areas

/src/auth/                  @backend-team @security-team
/src/encryption/            @security-team
/src/permissions/           @backend-team @security-team


# ============================================================================
# INFRASTRUCTURE & DEVOPS
# ============================================================================

# CI/CD configuration
/.github/                   @devops-team
/.gitlab/                   @devops-team

# Docker and containerization
/docker/                    @devops-team
/Dockerfile                 @devops-team
/docker-compose*.yml        @devops-team

# Infrastructure as Code
/terraform/                 @devops-team @infrastructure-team
/kubernetes/                @devops-team
/helm/                      @devops-team

# Build configuration
/webpack.config.js          @frontend-team @devops-team
/vite.config.ts             @frontend-team @devops-team
/rollup.config.js           @frontend-team @devops-team


# ============================================================================
# TESTING
# ============================================================================

# Test files (broad ownership encourages test writing)
/tests/                     @frontend-team @backend-team
**/*.test.ts                @frontend-team @backend-team
**/*.test.js                @frontend-team @backend-team
**/*.spec.ts                @frontend-team @backend-team

# E2E tests
/e2e/                       @qa-team
/playwright/                @qa-team


# ============================================================================
# DOCUMENTATION
# ============================================================================

/docs/                      @tech-writers @team-leads
README.md                   @tech-writers @team-leads
/CONTRIBUTING.md            @team-leads
/CODE_OF_CONDUCT.md         @team-leads


# ============================================================================
# CONFIGURATION FILES
# ============================================================================
# Require broader approval for config that affects entire system

package.json                @team-leads @devops-team
package-lock.json           @team-leads @devops-team
yarn.lock                   @team-leads @devops-team
pnpm-lock.yaml              @team-leads @devops-team

.eslintrc*                  @frontend-team @backend-team
.prettierrc*                @frontend-team @backend-team
tsconfig.json               @frontend-team @backend-team

.env.example                @devops-team @team-leads
.env.template               @devops-team @team-leads


# ============================================================================
# DOMAIN-SPECIFIC OWNERSHIP
# ============================================================================
# Add custom paths for your application domains

# Example: Payment processing
# /src/payments/            @payments-team @security-team

# Example: Analytics
# /src/analytics/           @analytics-team @data-team

# Example: Notifications
# /src/notifications/       @backend-team @frontend-team


# ============================================================================
# INDIVIDUAL EXPERT OWNERSHIP
# ============================================================================
# Use sparingly - prefer team ownership

# Example: Specific expert for complex subsystem
# /src/ml-pipeline/         @ml-expert @data-team


# ============================================================================
# NOTES
# ============================================================================
#
# Best Practices:
# 1. Prefer team ownership over individual ownership
# 2. Use 1-2 owners per file for fast reviews
# 3. Avoid assigning entire organization (causes bystander effect)
# 4. Review and update quarterly as team structure changes
# 5. New team members should be added to team groups, not individual entries
#
# Troubleshooting:
# - If reviews are too slow: Check for over-assignment (too many required reviewers)
# - If wrong people assigned: Check pattern specificity (more specific patterns override)
# - If no one assigned: Add catch-all pattern (*)
#
# GitHub Teams:
# - Create teams in GitHub org settings
# - Use @org/team-name syntax
# - Manage membership in GitHub, not in CODEOWNERS file
#
# ============================================================================
