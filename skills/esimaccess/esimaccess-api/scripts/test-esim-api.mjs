#!/usr/bin/env node
/**
 * eSIM Access API Test Script
 * Tests all core functions of the eSIM Access API.
 *
 * Usage: node test-esim-api.mjs <accessCode>
 *
 * Get your accessCode from https://console.esimaccess.com/developer/index
 */

import crypto from 'crypto';

const BASE_URL = 'https://api.esimaccess.com/api/v1/open';

// ─── Auth ──────────────────────────────────────────────────────────────────

function generateHeaders(accessCode, secretKey, body) {
  const timestamp = Date.now().toString();
  const requestId = crypto.randomUUID();
  const signStr = timestamp + requestId + accessCode + body;
  const signature = crypto
    .createHmac('sha256', secretKey)
    .update(signStr)
    .digest('hex')
    .toLowerCase();

  return {
    'Content-Type': 'application/json',
    'RT-AccessCode': accessCode,
    'RT-Timestamp': timestamp,
    'RT-RequestID': requestId,
    'RT-Signature': signature,
  };
}

async function apiCall(accessCode, secretKey, endpoint, body = {}) {
  const bodyStr = JSON.stringify(body);
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: generateHeaders(accessCode, secretKey, bodyStr),
    body: bodyStr,
  });

  const data = await response.json();
  return data;
}

function formatPrice(apiPrice) {
  return (apiPrice / 10000).toFixed(2);
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ─── Tests ─────────────────────────────────────────────────────────────────

const results = {};

async function test(name, fn) {
  process.stdout.write(`\n${'─'.repeat(60)}\n`);
  process.stdout.write(`TEST: ${name}\n`);
  process.stdout.write(`${'─'.repeat(60)}\n`);
  try {
    const result = await fn();
    results[name] = { success: true, result };
    console.log('✅ PASS');
    return result;
  } catch (err) {
    results[name] = { success: false, error: err.message };
    console.log(`❌ FAIL: ${err.message}`);
    return null;
  }
}

async function main() {
  const accessCode = process.argv[2];
  const secretKey = process.argv[3] || accessCode;

  if (!accessCode) {
    console.error('Usage: node test-esim-api.mjs <accessCode>');
    console.error('');
    console.error('The accessCode is the API key from https://console.esimaccess.com/developer/index');
    console.error('It is used for both authentication and HMAC signing.');
    process.exit(1);
  }

  console.log('🔑 eSIM Access API Test Suite');
  console.log(`   Access Code: ${accessCode.substring(0, 8)}...`);
  console.log(`   Base URL: ${BASE_URL}`);
  console.log(`   Time: ${new Date().toISOString()}`);

  // ─── 1. Check Balance ────────────────────────────────────────────────

  let balanceBefore = 0;
  await test('1. Check Balance', async () => {
    const data = await apiCall(accessCode, secretKey, '/balance/query');
    console.log('   Response:', JSON.stringify(data, null, 2));

    if (data.success) {
      balanceBefore = data.obj.balance;
      console.log(`   Balance: $${formatPrice(data.obj.balance)} USD`);
    } else {
      throw new Error(data.errorMsg || `Error code: ${data.errorCode}`);
    }
    return data;
  });

  // ─── 2. Check Supported Regions ──────────────────────────────────────

  let regions = [];
  await test('2. Check Supported Regions', async () => {
    const data = await apiCall(accessCode, secretKey, '/package/list', {
      locationCode: '', type: '', slug: '', packageCode: '', iccid: ''
    });

    if (!data.success) throw new Error(data.errorMsg || `Error code: ${data.errorCode}`);

    const packageList = data.obj?.packageList || [];
    const regionSet = new Set();
    const packageCodes = new Set();

    for (const pkg of packageList) {
      regionSet.add(pkg.location);
      packageCodes.add(pkg.packageCode);
    }

    regions = Array.from(regionSet).sort();
    console.log(`   Total packages: ${packageList.length}`);
    console.log(`   Total regions: ${regions.length}`);
    console.log(`   Sample regions: ${regions.slice(0, 20).join(', ')}...`);
    return { totalPackages: packageList.length, totalRegions: regions.length, regions };
  });

  // ─── 3. Check Products by Country ────────────────────────────────────

  let samplePackage = null;
  await test('3. Check Products by Country (US)', async () => {
    const data = await apiCall(accessCode, secretKey, '/package/list', {
      locationCode: 'US', type: '', slug: '', packageCode: '', iccid: ''
    });

    if (!data.success) throw new Error(data.errorMsg || `Error code: ${data.errorCode}`);

    const packages = data.obj?.packageList || [];
    console.log(`   US packages: ${packages.length}`);

    // Find the cheapest non-daily package for testing
    const sorted = [...packages]
      .filter(p => !p.packageCode.includes('DAILY'))
      .sort((a, b) => a.price - b.price);

    if (sorted.length > 0) {
      samplePackage = sorted[0];
      console.log(`   Cheapest package: ${samplePackage.name}`);
      console.log(`     Code: ${samplePackage.packageCode}`);
      console.log(`     Cost: $${formatPrice(samplePackage.price)} USD`);
      console.log(`     Retail: $${formatPrice(samplePackage.retailPrice)} USD`);
      console.log(`     Data: ${formatBytes(samplePackage.volume)}`);
      console.log(`     Duration: ${samplePackage.duration} ${samplePackage.durationUnit}`);
      console.log(`     TopUp: ${samplePackage.supportTopUpType === 2 ? 'Yes' : 'No'}`);
    }

    // Show first 5 packages
    for (const pkg of packages.slice(0, 5)) {
      console.log(`   - ${pkg.name}: $${formatPrice(pkg.price)} (${formatBytes(pkg.volume)}, ${pkg.duration} ${pkg.durationUnit})`);
    }

    return { packages: packages.length, cheapest: samplePackage };
  });

  // ─── 4. Check Available Top-up Packages ──────────────────────────────

  await test('4. Check Available Top-up Packages (US)', async () => {
    const data = await apiCall(accessCode, secretKey, '/package/list', {
      locationCode: 'US', type: '', slug: '', packageCode: '', iccid: ''
    });

    if (!data.success) throw new Error(data.errorMsg || `Error code: ${data.errorCode}`);

    const topupPackages = (data.obj?.packageList || []).filter(p => p.supportTopUpType === 2);
    console.log(`   Top-up capable packages: ${topupPackages.length}`);

    for (const pkg of topupPackages.slice(0, 5)) {
      console.log(`   - ${pkg.name}: $${formatPrice(pkg.price)} (${formatBytes(pkg.volume)})`);
    }

    return { topupPackages: topupPackages.length };
  });

  // ─── 5. Make an eSIM Order ───────────────────────────────────────────

  let orderNo = null;
  let esimTranNo = null;
  let iccid = null;

  if (samplePackage && balanceBefore > samplePackage.price) {
    await test('5. Make an eSIM Order', async () => {
      const transactionId = `mcp_test_${Date.now()}`;
      console.log(`   Package: ${samplePackage.packageCode}`);
      console.log(`   Transaction ID: ${transactionId}`);

      const data = await apiCall(accessCode, secretKey, '/esim/order', {
        transactionId,
        packageInfoList: [{
          packageCode: samplePackage.packageCode,
          count: 1,
        }],
      });

      console.log('   Response:', JSON.stringify(data, null, 2));

      if (!data.success) throw new Error(data.errorMsg || `Error code: ${data.errorCode}`);

      orderNo = data.obj.orderNo;
      console.log(`   Order No: ${orderNo}`);
      return data;
    });
  } else {
    console.log('\n⏭️  SKIP: 5. Make an eSIM Order (insufficient balance or no package found)');
    results['5. Make an eSIM Order'] = { success: false, error: 'Skipped - insufficient balance or no package' };
  }

  // ─── 6. Check Order Status (Poll for ICCID) ─────────────────────────

  if (orderNo) {
    await test('6. Check Order Status & Poll for ICCID', async () => {
      for (let attempt = 1; attempt <= 5; attempt++) {
        console.log(`   Poll attempt ${attempt}/5...`);
        await new Promise(r => setTimeout(r, 3000));

        const data = await apiCall(accessCode, secretKey, '/esim/query', {
          orderNo,
          pager: { pageNum: 1, pageSize: 20 },
        });

        if (data.success && data.obj?.esimList?.length > 0) {
          const esim = data.obj.esimList[0];
          esimTranNo = esim.esimTranNo;
          iccid = esim.iccid;

          console.log(`   eSIM Tran No: ${esimTranNo}`);
          console.log(`   ICCID: ${iccid || 'pending'}`);
          console.log(`   SMDP Status: ${esim.smdpStatus}`);
          console.log(`   eSIM Status: ${esim.esimStatus}`);
          console.log(`   QR Code: ${esim.qrCodeUrl || 'N/A'}`);
          console.log(`   Short URL: ${esim.shortUrl || 'N/A'}`);
          console.log(`   Total Volume: ${formatBytes(esim.totalVolume)}`);
          console.log(`   Duration: ${esim.totalDuration} ${esim.durationUnit}`);

          if (iccid) {
            console.log('   ✅ ICCID obtained successfully');
            return esim;
          }
        }
      }

      console.log('   ⚠️ ICCID not yet available (webhook will complete later)');
      return { orderNo, status: 'polling_timeout' };
    });
  } else {
    console.log('\n⏭️  SKIP: 6. Check Order Status (no order created)');
    results['6. Check Order Status & Poll for ICCID'] = { success: false, error: 'Skipped - no order' };
  }

  // ─── 7. Check Data Usage ─────────────────────────────────────────────

  if (iccid) {
    await test('7. Check Data Usage', async () => {
      // Usage query requires esimTranNo, not ICCID
      const data = await apiCall(accessCode, secretKey, '/esim/usage/query', { esimTranNoList: [esimTranNo] });
      console.log('   Response:', JSON.stringify(data, null, 2));

      if (data.success && data.obj) {
        const usageList = Array.isArray(data.obj) ? data.obj : [data.obj];
        for (const u of usageList) {
          console.log(`   Total Volume: ${formatBytes(u.totalVolume || 0)}`);
          console.log(`   Used: ${formatBytes(u.orderUsage || 0)}`);
          console.log(`   Remaining: ${formatBytes(u.remain || 0)}`);
        }
      }
      return data;
    });
  } else {
    console.log('\n⏭️  SKIP: 7. Check Data Usage (no ICCID)');
    results['7. Check Data Usage'] = { success: false, error: 'Skipped - no ICCID' };
  }

  // ─── 8. Check Full eSIM Status ───────────────────────────────────────

  if (iccid) {
    await test('8. Check Full eSIM Status', async () => {
      const data = await apiCall(accessCode, secretKey, '/esim/query', {
        iccid,
        pager: { pageNum: 1, pageSize: 20 },
      });

      if (data.success && data.obj?.esimList?.length > 0) {
        const esim = data.obj.esimList[0];
        console.log('   Full eSIM Details:');
        console.log(`     ICCID: ${esim.iccid}`);
        console.log(`     eSIM Tran No: ${esim.esimTranNo}`);
        console.log(`     Order No: ${esim.orderNo}`);
        console.log(`     IMSI: ${esim.imsi}`);
        console.log(`     SMDP Status: ${esim.smdpStatus}`);
        console.log(`     eSIM Status: ${esim.esimStatus}`);
        console.log(`     EID: ${esim.eid || 'none'}`);
        console.log(`     Active Type: ${esim.activeType}`);
        console.log(`     Activate Time: ${esim.activateTime || 'not activated'}`);
        console.log(`     Expired Time: ${esim.expiredTime}`);
        console.log(`     Total Volume: ${formatBytes(esim.totalVolume)}`);
        console.log(`     Used: ${formatBytes(esim.orderUsage)}`);
        console.log(`     Duration: ${esim.totalDuration} ${esim.durationUnit}`);
        console.log(`     QR Code URL: ${esim.qrCodeUrl}`);
        console.log(`     Short URL: ${esim.shortUrl}`);
        console.log(`     Packages: ${esim.packageList?.length || 0}`);
        for (const pkg of (esim.packageList || [])) {
          console.log(`       - ${pkg.packageName} (${pkg.packageCode})`);
        }
      }
      return data;
    });
  } else {
    console.log('\n⏭️  SKIP: 8. Check Full eSIM Status (no ICCID)');
    results['8. Check Full eSIM Status'] = { success: false, error: 'Skipped - no ICCID' };
  }

  // ─── 9. Check Top-up Packages for eSIM ──────────────────────────────

  if (iccid) {
    await test('9. Check Top-up Packages for eSIM', async () => {
      const data = await apiCall(accessCode, secretKey, '/package/list', {
        locationCode: '', type: '', slug: '', packageCode: '', iccid,
      });

      if (data.success) {
        const topups = (data.obj?.packageList || []).filter(p => p.supportTopUpType === 2);
        console.log(`   Available top-up packages: ${topups.length}`);
        for (const pkg of topups.slice(0, 5)) {
          console.log(`   - ${pkg.name}: $${formatPrice(pkg.price)} (${formatBytes(pkg.volume)})`);
        }
      }
      return data;
    });
  } else {
    console.log('\n⏭️  SKIP: 9. Check Top-up Packages for eSIM (no ICCID)');
    results['9. Check Top-up Packages for eSIM'] = { success: false, error: 'Skipped - no ICCID' };
  }

  // ─── 10. Query Webhook Settings ──────────────────────────────────────

  await test('10. Query Webhook Settings', async () => {
    const data = await apiCall(accessCode, secretKey, '/webhook/query');
    console.log('   Response:', JSON.stringify(data, null, 2));
    return data;
  });

  // ─── 11. Suspend Profile (if we have an esimTranNo) ──────────────────

  if (esimTranNo) {
    await test('11. Suspend Profile', async () => {
      const data = await apiCall(accessCode, secretKey, '/esim/suspend', { esimTranNo });
      console.log('   Response:', JSON.stringify(data, null, 2));
      return data;
    });

    // ─── 12. Unsuspend Profile ──────────────────────────────────────────

    await test('12. Unsuspend Profile', async () => {
      const data = await apiCall(accessCode, secretKey, '/esim/unsuspend', { esimTranNo });
      console.log('   Response:', JSON.stringify(data, null, 2));
      return data;
    });
  } else {
    console.log('\n⏭️  SKIP: 11-12. Suspend/Unsuspend Profile (no esimTranNo)');
  }

  // ─── 13. Send SMS (if supported) ─────────────────────────────────────

  if (iccid) {
    await test('13. Send SMS (test)', async () => {
      const data = await apiCall(accessCode, secretKey, '/esim/sendSms', {
        iccid,
        message: 'Test SMS from eSIM MCP skill',
      });
      console.log('   Response:', JSON.stringify(data, null, 2));
      return data;
    });
  } else {
    console.log('\n⏭️  SKIP: 13. Send SMS (no ICCID)');
  }

  // ─── 14. Cancel eSIM (if unused) ─────────────────────────────────────

  if (esimTranNo) {
    await test('14. Cancel eSIM (refund test)', async () => {
      // Check balance before
      const beforeData = await apiCall(accessCode, secretKey, '/balance/query');
      const beforeBalance = beforeData.success ? beforeData.obj.balance : 0;
      console.log(`   Balance before cancel: $${formatPrice(beforeBalance)}`);

      // Cancel
      const cancelData = await apiCall(accessCode, secretKey, '/esim/cancel', { esimTranNo });
      console.log('   Cancel response:', JSON.stringify(cancelData, null, 2));

      if (cancelData.success) {
        // Wait and check balance after
        await new Promise(r => setTimeout(r, 2000));
        const afterData = await apiCall(accessCode, secretKey, '/balance/query');
        const afterBalance = afterData.success ? afterData.obj.balance : 0;
        console.log(`   Balance after cancel: $${formatPrice(afterBalance)}`);
        console.log(`   Refund amount: $${formatPrice(afterBalance - beforeBalance)}`);
      }

      return cancelData;
    });
  } else {
    console.log('\n⏭️  SKIP: 14. Cancel eSIM (no esimTranNo)');
  }

  // ─── 15. Check Balance After ─────────────────────────────────────────

  await test('15. Check Balance After Tests', async () => {
    const data = await apiCall(accessCode, secretKey, '/balance/query');
    if (data.success) {
      const balanceAfter = data.obj.balance;
      console.log(`   Balance: $${formatPrice(balanceAfter)} USD`);
      console.log(`   Net change: $${formatPrice(balanceAfter - balanceBefore)} USD`);
    }
    return data;
  });

  // ─── Summary ─────────────────────────────────────────────────────────

  console.log('\n' + '═'.repeat(60));
  console.log('TEST SUMMARY');
  console.log('═'.repeat(60));

  let passed = 0;
  let failed = 0;
  let skipped = 0;

  for (const [name, result] of Object.entries(results)) {
    const icon = result.success ? '✅' : (result.error?.startsWith('Skipped') ? '⏭️ ' : '❌');
    if (result.success) passed++;
    else if (result.error?.startsWith('Skipped')) skipped++;
    else failed++;
    console.log(`  ${icon} ${name}`);
  }

  console.log('');
  console.log(`  Passed: ${passed}  Failed: ${failed}  Skipped: ${skipped}`);
  console.log('═'.repeat(60));
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
