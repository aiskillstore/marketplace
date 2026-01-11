---
name: deployment-checker
description: Pre-deployment validation checklist and automated readiness assessment.
---

# Deployment Checker Skill

Pre-deployment validation checklist and automated readiness assessment.

## Instructions

You are a deployment readiness expert. When invoked:

1. **Pre-Deployment Validation**:
   - Code quality checks passed
   - All tests passing
   - Build successful
   - Dependencies updated and secure
   - Environment variables configured
   - Database migrations ready

2. **Security Checks**:
   - No secrets in code
   - Security headers configured
   - Authentication/authorization tested
   - Input validation implemented
   - HTTPS enabled
   - Rate limiting configured

3. **Performance Validation**:
   - Load testing completed
   - Resource limits configured
   - Caching strategies implemented
   - Database indexes optimized
   - CDN configured (if applicable)

4. **Infrastructure Checks**:
   - Health checks configured
   - Monitoring and alerting set up
   - Logging configured
   - Backup strategy in place
   - Rollback plan documented
   - DNS and SSL configured

5. **Generate Checklist**: Create deployment-ready report with go/no-go decision

## Deployment Checklist

### Pre-Deployment (Before Release)

#### Code Quality
- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed and approved
- [ ] Linting passed (no warnings)
- [ ] Code coverage meets threshold (>80%)
- [ ] No known critical bugs
- [ ] Breaking changes documented
- [ ] API contracts validated

#### Build & Dependencies
- [ ] Build successful in CI/CD
- [ ] Dependencies updated
- [ ] Security vulnerabilities resolved
- [ ] Bundle size within acceptable limits
- [ ] Source maps generated (if applicable)
- [ ] Docker images built and pushed

#### Database
- [ ] Migrations tested in staging
- [ ] Migration rollback plan ready
- [ ] Backup created before migration
- [ ] Database indexes optimized
- [ ] Data validation scripts run
- [ ] Connection pool configured

#### Environment Configuration
- [ ] Environment variables documented
- [ ] Secrets stored securely (not in code)
- [ ] Feature flags configured
- [ ] CORS settings verified
- [ ] API keys rotated (if needed)
- [ ] Third-party services configured

#### Security
- [ ] Authentication tested
- [ ] Authorization rules verified
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS prevention implemented
- [ ] CSRF tokens configured
- [ ] Security headers set
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Secrets manager configured

#### Performance
- [ ] Load testing completed
- [ ] Performance benchmarks met
- [ ] Database query optimization done
- [ ] Caching strategy implemented
- [ ] CDN configured (if applicable)
- [ ] Resource limits set
- [ ] Auto-scaling configured

### Deployment (During Release)

#### Infrastructure
- [ ] Health check endpoints working
- [ ] Monitoring dashboards ready
- [ ] Alerting configured
- [ ] Logging centralized
- [ ] Error tracking enabled (Sentry, etc.)
- [ ] Backup strategy verified
- [ ] SSL certificates valid
- [ ] DNS records updated
- [ ] Load balancer configured

#### Deployment Strategy
- [ ] Deployment method chosen (blue-green, canary, rolling)
- [ ] Rollback plan documented
- [ ] Database migration strategy defined
- [ ] Downtime window communicated (if any)
- [ ] Deployment runbook prepared
- [ ] Staging deployment successful

#### Communication
- [ ] Stakeholders notified
- [ ] Change log prepared
- [ ] Documentation updated
- [ ] Support team briefed
- [ ] Maintenance window scheduled (if needed)
- [ ] Status page updated

### Post-Deployment (After Release)

#### Validation
- [ ] Smoke tests passed
- [ ] Health checks green
- [ ] Error rates normal
- [ ] Response times acceptable
- [ ] Database migrations completed
- [ ] Feature flags validated

#### Monitoring
- [ ] Application logs reviewed
- [ ] Error tracking checked
- [ ] Performance metrics reviewed
- [ ] User feedback monitored
- [ ] Resource usage normal
- [ ] Alerts configured and tested

#### Documentation
- [ ] Release notes published
- [ ] API documentation updated
- [ ] Known issues documented
- [ ] Rollback procedure tested
- [ ] Incident response plan ready

## Usage Examples

```
@deployment-checker
@deployment-checker --environment production
@deployment-checker --checklist
@deployment-checker --automated
@deployment-checker --report
```

## Automated Checks Script

### Node.js Example
```javascript
// deployment-check.js
const chalk = require('chalk');

class DeploymentChecker {
  constructor() {
    this.checks = [];
    this.passed = 0;
    this.failed = 0;
  }

  async runChecks() {
    console.log(chalk.bold('\n🚀 Deployment Readiness Check\n'));

    await this.checkTests();
    await this.checkBuild();
    await this.checkDependencies();
    await this.checkEnvironment();
    await this.checkSecurity();
    await this.checkDatabase();

    this.printSummary();
    return this.failed === 0;
  }

  async checkTests() {
    console.log(chalk.blue('📋 Running Tests...'));
    try {
      await this.exec('npm test');
      this.pass('All tests passing');
    } catch (error) {
      this.fail('Tests failed', error.message);
    }
  }

  async checkBuild() {
    console.log(chalk.blue('\n🔨 Building Application...'));
    try {
      await this.exec('npm run build');
      this.pass('Build successful');
    } catch (error) {
      this.fail('Build failed', error.message);
    }
  }

  async checkDependencies() {
    console.log(chalk.blue('\n📦 Checking Dependencies...'));
    try {
      const result = await this.exec('npm audit --audit-level=high');
      if (result.includes('0 vulnerabilities')) {
        this.pass('No high/critical vulnerabilities');
      } else {
        this.fail('Security vulnerabilities found');
      }
    } catch (error) {
      this.fail('Dependency check failed', error.message);
    }
  }

  async checkEnvironment() {
    console.log(chalk.blue('\n🌍 Checking Environment...'));

    const required = [
      'DATABASE_URL',
      'JWT_SECRET',
      'API_KEY',
      'REDIS_URL'
    ];

    for (const envVar of required) {
      if (process.env[envVar]) {
        this.pass(`${envVar} is set`);
      } else {
        this.fail(`${envVar} is missing`);
      }
    }
  }

  async checkSecurity() {
    console.log(chalk.blue('\n🔒 Security Checks...'));

    // Check for secrets in code
    try {
      const result = await this.exec('git secrets --scan');
      this.pass('No secrets found in code');
    } catch (error) {
      this.fail('Secrets detected in code');
    }

    // Check HTTPS
    if (process.env.FORCE_HTTPS === 'true') {
      this.pass('HTTPS enforced');
    } else {
      this.fail('HTTPS not enforced');
    }
  }

  async checkDatabase() {
    console.log(chalk.blue('\n💾 Database Checks...'));

    // Check migrations are up to date
    try {
      await this.exec('npm run db:check-migrations');
      this.pass('Database migrations ready');
    } catch (error) {
      this.fail('Database migration issues');
    }
  }

  pass(message) {
    console.log(chalk.green(`  ✓ ${message}`));
    this.passed++;
  }

  fail(message, details = '') {
    console.log(chalk.red(`  ✗ ${message}`));
    if (details) {
      console.log(chalk.gray(`    ${details}`));
    }
    this.failed++;
  }

  printSummary() {
    console.log(chalk.bold('\n📊 Summary\n'));
    console.log(chalk.green(`  Passed: ${this.passed}`));
    console.log(chalk.red(`  Failed: ${this.failed}`));

    if (this.failed === 0) {
      console.log(chalk.green.bold('\n✅ READY FOR DEPLOYMENT\n'));
    } else {
      console.log(chalk.red.bold('\n❌ NOT READY FOR DEPLOYMENT\n'));
      process.exit(1);
    }
  }

  async exec(command) {
    const { execSync } = require('child_process');
    return execSync(command, { encoding: 'utf8' });
  }
}

// Run checks
const checker = new DeploymentChecker();
checker.runChecks();
```

## Deployment Report Template

```markdown
# Deployment Readiness Report

**Environment**: Production
**Date**: 2024-01-15
**Version**: v2.3.0
**Release Manager**: @username

---

## Overall Status

🟢 **READY FOR DEPLOYMENT**

**Score**: 95/100
- ✅ Critical checks: 10/10
- ✅ High priority: 18/20
- ⚠️  Medium priority: 28/30
- ✅ Low priority: 39/40

---

## Critical Checks (10/10) ✅

- ✅ All tests passing (1,234 tests, 0 failures)
- ✅ Build successful
- ✅ No critical vulnerabilities
- ✅ Database migrations tested
- ✅ Environment variables configured
- ✅ HTTPS enabled
- ✅ Health checks working
- ✅ Rollback plan documented
- ✅ Monitoring configured
- ✅ Staging deployment successful

---

## High Priority (18/20) ✅

- ✅ Code review approved
- ✅ Security scan passed
- ✅ Performance benchmarks met
- ✅ Load testing completed
- ✅ Error tracking enabled
- ✅ Rate limiting configured
- ✅ Backup strategy verified
- ✅ SSL certificates valid
- ⚠️  API documentation needs update (2 endpoints)
- ⚠️  Cache warming script not tested

---

## Medium Priority (28/30) ⚠️

- ✅ Linting passed
- ✅ Code coverage: 87% (target: 80%)
- ✅ Bundle size: 245KB (within limit)
- ⚠️  Minor performance issue in search endpoint
- ⚠️  1 TODO comment in critical path

---

## Test Results

**Unit Tests**: ✅ 856 passed, 0 failed
**Integration Tests**: ✅ 234 passed, 0 failed
**E2E Tests**: ✅ 144 passed, 0 failed
**Total**: 1,234 tests in 2m 34s

**Coverage**:
- Statements: 87.4%
- Branches: 82.1%
- Functions: 89.3%
- Lines: 86.8%

---

## Security Scan Results

**Dependencies**: ✅ No critical/high vulnerabilities
**Secrets Scan**: ✅ No secrets detected
**HTTPS**: ✅ Enforced
**Security Headers**: ✅ Configured
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security: max-age=31536000

**Authentication**: ✅ Tested
**Rate Limiting**: ✅ 100 req/15min per IP

---

## Performance Metrics

**Load Test Results** (10,000 concurrent users):
- Average Response Time: 234ms ✅ (target: <500ms)
- P95 Response Time: 456ms ✅ (target: <1s)
- P99 Response Time: 789ms ✅ (target: <2s)
- Error Rate: 0.02% ✅ (target: <0.1%)
- Throughput: 12,345 req/s ✅

**Database**:
- Query Response Time: <50ms ✅
- Connection Pool: Configured (min: 5, max: 50) ✅
- Indexes: Optimized ✅

---

## Infrastructure Status

**Health Checks**: ✅ All passing
- /health: 200 OK (5ms)
- /ready: 200 OK (8ms)
- Database: Connected
- Redis: Connected
- External APIs: Reachable

**Monitoring**: ✅ Configured
- Application metrics: Datadog
- Error tracking: Sentry
- Logging: CloudWatch
- Uptime monitoring: Pingdom

**Alerts Configured**:
- Error rate > 1%
- Response time P95 > 1s
- CPU > 80%
- Memory > 85%
- Database connections > 45

---

## Database Migrations

**Status**: ✅ Ready

Migrations to apply:
1. `20240115_add_user_preferences` - Tested ✅
2. `20240115_create_notifications_table` - Tested ✅

**Rollback Plan**: ✅ Documented
**Backup**: ✅ Created (15GB, 2024-01-15 10:00 UTC)

---

## Deployment Plan

**Strategy**: Blue-Green Deployment
**Estimated Duration**: 15 minutes
**Downtime**: None
**Rollback Time**: 2 minutes

**Steps**:
1. Deploy to green environment
2. Run smoke tests
3. Switch 10% traffic to green
4. Monitor for 10 minutes
5. Switch 50% traffic to green
6. Monitor for 10 minutes
7. Switch 100% traffic to green
8. Keep blue environment for 24h (quick rollback)

---

## Action Items Before Deployment

### Must Fix (Blockers)
- None ✅

### Should Fix (Recommended)
- ⚠️  Update API documentation for new endpoints
- ⚠️  Test cache warming script

### Nice to Have
- Consider adding more E2E tests for edge cases
- Update changelog with latest changes

---

## Risk Assessment

**Overall Risk**: 🟢 Low

**Identified Risks**:
1. **Database Migration** (Low Risk)
   - Mitigation: Tested in staging, rollback plan ready

2. **Traffic Spike** (Low Risk)
   - Mitigation: Load tested, auto-scaling configured

3. **Third-Party API** (Medium Risk)
   - Mitigation: Circuit breaker implemented, fallback configured

---

## Rollback Plan

**Trigger Conditions**:
- Error rate > 5%
- Response time P95 > 2s
- Critical functionality broken

**Rollback Steps**:
1. Switch traffic back to blue environment (30 seconds)
2. Investigate issue
3. Fix and redeploy

**Data Rollback**:
- Database backup available (15 minutes to restore)
- Migration rollback scripts tested

---

## Communication Plan

**Notifications Sent**:
- ✅ Engineering team
- ✅ Product team
- ✅ Support team
- ✅ Stakeholders

**Status Page**: Updated
**Changelog**: Ready to publish
**Documentation**: Updated

---

## Sign-Off

**Technical Lead**: ✅ Approved - @tech-lead
**QA**: ✅ Approved - @qa-lead
**DevOps**: ✅ Approved - @devops-lead
**Product**: ✅ Approved - @product-manager

---

## Final Recommendation

🟢 **APPROVED FOR DEPLOYMENT**

All critical checks passed. Minor issues identified do not block deployment.
Recommend proceeding with deployment as scheduled.

**Scheduled Deployment**: 2024-01-15 14:00 UTC
**Deployment Window**: 14:00 - 14:30 UTC
```

## Best Practices

### Blue-Green Deployment
- Zero downtime
- Instant rollback
- Full testing before switch
- Keep old environment for quick revert

### Canary Deployment
- Gradual rollout (1% → 10% → 50% → 100%)
- Monitor metrics at each stage
- Automatic rollback on errors
- Low risk

### Rolling Deployment
- Update instances one by one
- No downtime
- Automatic health checks
- Slower than blue-green

### Database Migrations
- Always test in staging first
- Create rollback scripts
- Backup before migration
- Avoid breaking changes when possible
- Use feature flags for schema changes

## Notes

- Never deploy on Fridays (unless critical)
- Always have a rollback plan
- Monitor closely for first hour after deployment
- Document everything
- Automate as much as possible
- Test in production-like environment
- Use feature flags for gradual rollout
- Keep deployments small and frequent
- Have team available during deployment
- Celebrate successful deployments!
