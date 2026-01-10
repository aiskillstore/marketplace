#!/usr/bin/env node

/**
 * API测试工具
 * 用于测试RESTful API端点，支持多种请求方式和断言
 */

const fetch = require('node-fetch');
const chalk = require('chalk');
const Table = require('cli-table3');

class APITester {
  constructor(baseURL = 'http://localhost:3000') {
    this.baseURL = baseURL;
    this.results = [];
    this.passed = 0;
    this.failed = 0;
  }

  /**
   * 发送HTTP请求
   */
  async request(method, endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const startTime = Date.now();

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
        timeout: options.timeout || 5000,
      });

      const duration = Date.now() - startTime;
      const responseBody = await response.text();

      let parsedBody;
      try {
        parsedBody = JSON.parse(responseBody);
      } catch {
        parsedBody = responseBody;
      }

      return {
        success: true,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers.raw(),
        body: parsedBody,
        rawBody: responseBody,
        duration,
        url,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        duration: Date.now() - startTime,
        url,
      };
    }
  }

  /**
   * 发送GET请求
   */
  async get(endpoint, options = {}) {
    return this.request('GET', endpoint, options);
  }

  /**
   * 发送POST请求
   */
  async post(endpoint, body, options = {}) {
    return this.request('POST', endpoint, { body, ...options });
  }

  /**
   * 发送PUT请求
   */
  async put(endpoint, body, options = {}) {
    return this.request('PUT', endpoint, { body, ...options });
  }

  /**
   * 发送DELETE请求
   */
  async delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, options);
  }

  /**
   * 运行测试用例
   */
  async runTest(name, testFn) {
    console.log(`\n${chalk.blue('▶')} Running: ${chalk.bold(name)}`);

    try {
      const result = await testFn();
      this.passed++;
      this.results.push({ name, status: 'PASS', ...result });
      console.log(`  ${chalk.green('✓')} PASS`);
      return result;
    } catch (error) {
      this.failed++;
      this.results.push({ name, status: 'FAIL', error: error.message });
      console.log(`  ${chalk.red('✗')} FAIL`);
      console.log(`  ${chalk.gray('Error:')} ${error.message}`);
      throw error;
    }
  }

  /**
   * 断言状态码
   */
  assertStatus(response, expectedStatus) {
    if (!response.success) {
      throw new Error(`请求失败: ${response.error}`);
    }

    if (response.status !== expectedStatus) {
      throw new Error(`状态码不匹配: 期望 ${expectedStatus}, 实际 ${response.status}`);
    }

    return true;
  }

  /**
   * 断言响应包含某个字段
   */
  assertHas(response, path) {
    if (!response.success) {
      throw new Error(`请求失败: ${response.error}`);
    }

    const keys = path.split('.');
    let current = response.body;

    for (const key of keys) {
      if (current === null || current === undefined || !(key in current)) {
        throw new Error(`响应中缺少字段: ${path}`);
      }
      current = current[key];
    }

    return current;
  }

  /**
   * 断言响应时间
   */
  assertDuration(response, maxMs) {
    if (response.duration > maxMs) {
      throw new Error(`响应时间超时: ${response.duration}ms > ${maxMs}ms`);
    }
    return true;
  }

  /**
   * 打印测试总结
   */
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log(chalk.bold('📊 测试总结'));
    console.log('='.repeat(60));

    const total = this.passed + this.failed;
    const passRate = total > 0 ? (this.passed / total * 100).toFixed(1) : 0;

    // 结果概览
    console.log(`\n总测试数: ${total}`);
    console.log(chalk.green(`  ✓ 通过: ${this.passed}`));
    console.log(chalk.red(`  ✗ 失败: ${this.failed}`));
    console.log(`  通过率: ${passRate}%`);

    // 详细结果表格
    if (this.results.length > 0) {
      console.log('\n详细结果:');
      const table = new Table({
        head: ['Test Name', 'Status', 'Duration', 'Status Code'],
        style: { head: ['cyan'] },
      });

      this.results.forEach((result) => {
        const statusColor = result.status === 'PASS' ? chalk.green : chalk.red;
        const duration = result.duration ? `${result.duration}ms` : '-';
        const statusCode = result.statusCode || '-';

        table.push([
          result.name,
          statusColor(result.status),
          duration,
          statusCode,
        ]);
      });

      console.log(table.toString());
    }

    // 建议
    if (this.failed > 0) {
      console.log(chalk.yellow('\n💡 建议:'));
      console.log('  - 检查API服务是否运行');
      console.log('  - 验证测试数据和配置');
      console.log('  - 查看详细的错误日志');
    }

    console.log('\n' + '='.repeat(60));
  }

  /**
   * 导出JSON报告
   */
  exportReport(filename = 'api-test-report.json') {
    const report = {
      summary: {
        total: this.passed + this.failed,
        passed: this.passed,
        failed: this.failed,
        timestamp: new Date().toISOString(),
      },
      results: this.results,
    };

    const fs = require('fs');
    fs.writeFileSync(filename, JSON.stringify(report, null, 2));
    console.log(`\n💾 报告已导出: ${filename}`);
  }
}

// CLI 接口
async function main() {
  const args = process.argv.slice(2);
  const baseURL = args[0] || process.env.API_BASE_URL || 'http://localhost:3000';

  console.log(chalk.bold.blue('🚀 API测试工具'));
  console.log(`Base URL: ${chalk.gray(baseURL)}`);
  console.log('='.repeat(60));

  const tester = new APITester(baseURL);

  // 示例测试套件
  try {
    // 测试1: 健康检查
    await tester.runTest('健康检查端点', async () => {
      const response = await tester.get('/health');
      tester.assertStatus(response, 200);
      tester.assertDuration(response, 1000);
    });

    // 测试2: 用户注册
    await tester.runTest('用户注册', async () => {
      const response = await tester.post('/api/auth/register', {
        email: 'test@example.com',
        password: 'Test@123',
      });
      tester.assertStatus(response, 201);
      tester.assertHas(response, 'user.id');
      tester.assertHas(response, 'token.accessToken');
    });

    // 测试3: 用户登录
    await tester.runTest('用户登录', async () => {
      const response = await tester.post('/api/auth/login', {
        email: 'test@example.com',
        password: 'Test@123',
      });
      tester.assertStatus(response, 200);
      const token = tester.assertHas(response, 'token.accessToken');
      return { token };
    });

    // 测试4: 访问受保护资源
    await tester.runTest('访问受保护资源', async () => {
      // 先登录获取token（这里简化，实际应该传递）
      const loginRes = await tester.post('/api/auth/login', {
        email: 'test@example.com',
        password: 'Test@123',
      });
      const token = loginRes.body.token.accessToken;

      const response = await tester.get('/api/user/profile', {
        headers: { Authorization: `Bearer ${token}` },
      });
      tester.assertStatus(response, 200);
      tester.assertHas(response, 'user.email');
    });

  } catch (error) {
    console.error(chalk.red('\n测试执行中断:'), error.message);
  }

  // 打印总结
  tester.printSummary();

  // 导出报告
  tester.exportReport();
}

// 运行
if (require.main === module) {
  main().catch((error) => {
    console.error(chalk.red('致命错误:'), error);
    process.exit(1);
  });
}

module.exports = { APITester };
