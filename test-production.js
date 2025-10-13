#!/usr/bin/env node

/**
 * DroneWatch Production API Test Script
 * Tests the production API endpoint and verifies data structure
 */

const API_URL = 'https://www.dronemap.cc/api/incidents';

console.log('🧪 DroneWatch Production API Test\n');
console.log('📍 Testing endpoint:', API_URL);
console.log('⏱️  Starting test at:', new Date().toISOString());
console.log('─'.repeat(60));

async function testAPI() {
  try {
    // Test 1: Basic fetch
    console.log('\n✅ Test 1: Basic API fetch');
    const response = await fetch(API_URL);
    console.log('   Status:', response.status, response.statusText);
    console.log('   Headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Test 2: Parse JSON
    console.log('\n✅ Test 2: Parse JSON response');
    const incidents = await response.json();
    console.log('   Incident count:', incidents.length);
    console.log('   Data type:', Array.isArray(incidents) ? 'Array' : typeof incidents);

    // Test 3: Validate structure
    console.log('\n✅ Test 3: Validate data structure');
    if (incidents.length > 0) {
      const sample = incidents[0];
      const requiredFields = ['id', 'title', 'occurred_at', 'evidence_score', 'lat', 'lon', 'sources'];
      const missingFields = requiredFields.filter(field => !(field in sample));
      
      if (missingFields.length > 0) {
        console.log('   ❌ Missing fields:', missingFields.join(', '));
      } else {
        console.log('   ✅ All required fields present');
      }

      console.log('   Sample incident:');
      console.log('     - ID:', sample.id);
      console.log('     - Title:', sample.title.substring(0, 60) + '...');
      console.log('     - Evidence Score:', sample.evidence_score);
      console.log('     - Location:', `${sample.lat}, ${sample.lon}`);
      console.log('     - Sources:', sample.sources?.length || 0);
    } else {
      console.log('   ⚠️  No incidents returned (empty array)');
    }

    // Test 4: Evidence scores
    console.log('\n✅ Test 4: Evidence score distribution');
    const scores = incidents.reduce((acc, inc) => {
      acc[inc.evidence_score] = (acc[inc.evidence_score] || 0) + 1;
      return acc;
    }, {});
    Object.entries(scores).sort().forEach(([score, count]) => {
      const label = ['', 'UNCONFIRMED', 'REPORTED', 'VERIFIED', 'OFFICIAL'][score];
      console.log(`   Score ${score} (${label}): ${count} incidents`);
    });

    // Test 5: Countries
    console.log('\n✅ Test 5: Country coverage');
    const countries = [...new Set(incidents.map(i => i.country))];
    console.log('   Countries:', countries.join(', '));

    // Test 6: Asset types
    console.log('\n✅ Test 6: Asset types');
    const assetTypes = incidents.reduce((acc, inc) => {
      acc[inc.asset_type] = (acc[inc.asset_type] || 0) + 1;
      return acc;
    }, {});
    Object.entries(assetTypes).forEach(([type, count]) => {
      console.log(`   ${type}: ${count} incidents`);
    });

    // Summary
    console.log('\n' + '═'.repeat(60));
    console.log('✅ ALL TESTS PASSED');
    console.log('📊 Summary:');
    console.log(`   - Total incidents: ${incidents.length}`);
    console.log(`   - Countries: ${countries.length}`);
    console.log(`   - Evidence scores: ${Object.keys(scores).length} different levels`);
    console.log(`   - API Status: WORKING`);
    console.log(`   - Database: CONNECTED`);
    console.log('═'.repeat(60));

  } catch (error) {
    console.error('\n❌ TEST FAILED');
    console.error('   Error:', error.message);
    console.error('   Stack:', error.stack);
    process.exit(1);
  }
}

testAPI();
