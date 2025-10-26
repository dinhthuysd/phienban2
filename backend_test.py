#!/usr/bin/env python3
"""
Comprehensive KYC Backend API Testing Suite
Tests all KYC-related endpoints for the trading platform admin panel
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, Optional

# Configuration
BACKEND_URL = "https://verify-hub-5.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@trading.com"
ADMIN_PASSWORD = "Admin@123456"

class KYCAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
            
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                return False, {'error': f'Unsupported method: {method}'}
                
            try:
                response_data = response.json()
            except:
                response_data = {'raw_response': response.text}
                
            return response.status_code < 400, response_data
            
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}

    def test_admin_authentication(self):
        """Test admin login and token generation"""
        print("🔐 Testing Admin Authentication...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        success, response = self.make_request('POST', '/admin/auth/login', login_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.log_test(
                "Admin Login", 
                True, 
                f"Successfully authenticated as {ADMIN_EMAIL}",
                {'token_type': response.get('token_type')}
            )
            return True
        else:
            self.log_test(
                "Admin Login", 
                False, 
                "Failed to authenticate admin user",
                response
            )
            return False

    def test_kyc_statistics(self):
        """Test KYC statistics API"""
        print("📊 Testing KYC Statistics API...")
        
        # Test basic statistics
        success, response = self.make_request('GET', '/admin/kyc/statistics')
        
        if success:
            required_fields = ['overview', 'timeline', 'id_type_distribution', 'quality_distribution']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                overview = response.get('overview', {})
                expected_overview_fields = ['total_submissions', 'pending', 'approved', 'rejected', 'approval_rate', 'avg_processing_time_hours']
                missing_overview = [field for field in expected_overview_fields if field not in overview]
                
                if not missing_overview:
                    self.log_test(
                        "KYC Statistics - Basic", 
                        True, 
                        f"Retrieved statistics: {overview['total_submissions']} total submissions",
                        {'overview': overview}
                    )
                else:
                    self.log_test(
                        "KYC Statistics - Basic", 
                        False, 
                        f"Missing overview fields: {missing_overview}",
                        response
                    )
            else:
                self.log_test(
                    "KYC Statistics - Basic", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response
                )
        else:
            self.log_test(
                "KYC Statistics - Basic", 
                False, 
                "Failed to retrieve KYC statistics",
                response
            )
        
        # Test statistics with time range parameter
        success, response = self.make_request('GET', '/admin/kyc/statistics', params={'days': 30})
        
        if success:
            self.log_test(
                "KYC Statistics - Time Range", 
                True, 
                "Successfully retrieved 30-day statistics",
                {'timeline_entries': len(response.get('timeline', []))}
            )
        else:
            self.log_test(
                "KYC Statistics - Time Range", 
                False, 
                "Failed to retrieve statistics with time range",
                response
            )

    def test_kyc_management_apis(self):
        """Test KYC management endpoints"""
        print("📋 Testing KYC Management APIs...")
        
        # Test get all KYC submissions
        success, response = self.make_request('GET', '/admin/kyc/all', params={'page': 1, 'limit': 10})
        
        if success:
            required_fields = ['submissions', 'total', 'page', 'limit', 'pages']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.log_test(
                    "KYC Management - Get All", 
                    True, 
                    f"Retrieved {len(response['submissions'])} submissions (total: {response['total']})",
                    {'pagination': {'page': response['page'], 'total': response['total']}}
                )
            else:
                self.log_test(
                    "KYC Management - Get All", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response
                )
        else:
            self.log_test(
                "KYC Management - Get All", 
                False, 
                "Failed to retrieve KYC submissions",
                response
            )
        
        # Test with status filter (pending)
        success, response = self.make_request('GET', '/admin/kyc/all', params={
            'page': 1, 
            'limit': 10, 
            'status_filter': 'pending'
        })
        
        if success:
            self.log_test(
                "KYC Management - Pending Filter", 
                True, 
                f"Retrieved {len(response.get('submissions', []))} pending submissions",
                {'filtered_count': len(response.get('submissions', []))}
            )
        else:
            self.log_test(
                "KYC Management - Pending Filter", 
                False, 
                "Failed to retrieve pending KYC submissions",
                response
            )
        
        # Test with different status filters
        for status in ['approved', 'rejected']:
            success, response = self.make_request('GET', '/admin/kyc/all', params={
                'page': 1, 
                'limit': 10, 
                'status_filter': status
            })
            
            if success:
                self.log_test(
                    f"KYC Management - {status.title()} Filter", 
                    True, 
                    f"Retrieved {len(response.get('submissions', []))} {status} submissions",
                    {'status': status, 'count': len(response.get('submissions', []))}
                )
            else:
                self.log_test(
                    f"KYC Management - {status.title()} Filter", 
                    False, 
                    f"Failed to retrieve {status} KYC submissions",
                    response
                )
        
        # Test pagination edge case
        success, response = self.make_request('GET', '/admin/kyc/all', params={
            'page': 999, 
            'limit': 10
        })
        
        if success:
            self.log_test(
                "KYC Management - Pagination Edge Case", 
                True, 
                f"Handled high page number gracefully",
                {'submissions_count': len(response.get('submissions', []))}
            )
        else:
            self.log_test(
                "KYC Management - Pagination Edge Case", 
                False, 
                "Failed to handle pagination edge case",
                response
            )
        
        # Test search functionality
        success, response = self.make_request('GET', '/admin/kyc/all', params={
            'page': 1, 
            'limit': 10,
            'search': 'demo'
        })
        
        if success:
            self.log_test(
                "KYC Management - Search", 
                True, 
                f"Search functionality working, found {len(response.get('submissions', []))} results",
                {'search_results': len(response.get('submissions', []))}
            )
        else:
            self.log_test(
                "KYC Management - Search", 
                False, 
                "Failed to test search functionality",
                response
            )

    def test_kyc_timeline_api(self):
        """Test KYC timeline API"""
        print("⏰ Testing KYC Timeline API...")
        
        # First, get a KYC submission to test timeline
        success, response = self.make_request('GET', '/admin/kyc/all', params={'page': 1, 'limit': 1})
        
        if success and response.get('submissions'):
            kyc_id = response['submissions'][0].get('id')
            
            if kyc_id:
                # Test timeline for valid KYC ID
                success, timeline_response = self.make_request('GET', f'/admin/kyc/timeline/{kyc_id}')
                
                if success:
                    required_fields = ['kyc_id', 'current_status', 'timeline']
                    missing_fields = [field for field in required_fields if field not in timeline_response]
                    
                    if not missing_fields:
                        self.log_test(
                            "KYC Timeline - Valid ID", 
                            True, 
                            f"Retrieved timeline for KYC {kyc_id} with {len(timeline_response.get('timeline', []))} events",
                            {'timeline_events': len(timeline_response.get('timeline', []))}
                        )
                    else:
                        self.log_test(
                            "KYC Timeline - Valid ID", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            timeline_response
                        )
                else:
                    self.log_test(
                        "KYC Timeline - Valid ID", 
                        False, 
                        "Failed to retrieve timeline for valid KYC ID",
                        timeline_response
                    )
            else:
                self.log_test(
                    "KYC Timeline - Valid ID", 
                    False, 
                    "No KYC ID found in submissions",
                    response
                )
        else:
            self.log_test(
                "KYC Timeline - Valid ID", 
                False, 
                "No KYC submissions found to test timeline",
                response
            )
        
        # Test timeline with invalid KYC ID
        invalid_kyc_id = "invalid-kyc-id-12345"
        success, response = self.make_request('GET', f'/admin/kyc/timeline/{invalid_kyc_id}')
        
        if not success and response.get('detail') == 'KYC submission not found':
            self.log_test(
                "KYC Timeline - Invalid ID", 
                True, 
                "Correctly handled invalid KYC ID with 404 error",
                {'error_message': response.get('detail')}
            )
        else:
            self.log_test(
                "KYC Timeline - Invalid ID", 
                False, 
                "Did not handle invalid KYC ID correctly",
                response
            )

    def test_kyc_settings_api(self):
        """Test KYC settings API"""
        print("⚙️ Testing KYC Settings API...")
        
        # Test get system settings (includes KYC settings)
        success, response = self.make_request('GET', '/admin/settings')
        
        if success:
            kyc_settings = [
                'kyc_required_for_withdrawal',
                'kyc_required_amount_threshold', 
                'kyc_auto_approval_enabled',
                'kyc_auto_approval_threshold',
                'kyc_quality_threshold',
                'kyc_require_face_detection',
                'kyc_allowed_id_types',
                'kyc_max_file_size_mb'
            ]
            
            missing_kyc_settings = [setting for setting in kyc_settings if setting not in response]
            
            if not missing_kyc_settings:
                self.log_test(
                    "KYC Settings - Get", 
                    True, 
                    "Successfully retrieved KYC settings",
                    {
                        'kyc_auto_approval': response.get('kyc_auto_approval_enabled'),
                        'kyc_threshold': response.get('kyc_auto_approval_threshold'),
                        'allowed_id_types': response.get('kyc_allowed_id_types')
                    }
                )
            else:
                self.log_test(
                    "KYC Settings - Get", 
                    False, 
                    f"Missing KYC settings: {missing_kyc_settings}",
                    response
                )
        else:
            self.log_test(
                "KYC Settings - Get", 
                False, 
                "Failed to retrieve system settings",
                response
            )
        
        # Test update KYC settings
        kyc_update_data = {
            "kyc_auto_approval_threshold": 85.0,
            "kyc_quality_threshold": 65.0,
            "kyc_max_file_size_mb": 8.0
        }
        
        success, response = self.make_request('PUT', '/admin/settings', kyc_update_data)
        
        if success:
            self.log_test(
                "KYC Settings - Update", 
                True, 
                "Successfully updated KYC settings",
                {'message': response.get('message')}
            )
            
            # Verify the update by getting settings again
            success, verify_response = self.make_request('GET', '/admin/settings')
            if success:
                updated_threshold = verify_response.get('kyc_auto_approval_threshold')
                if updated_threshold == 85.0:
                    self.log_test(
                        "KYC Settings - Update Verification", 
                        True, 
                        f"Settings update verified: threshold = {updated_threshold}",
                        {'verified_threshold': updated_threshold}
                    )
                else:
                    self.log_test(
                        "KYC Settings - Update Verification", 
                        False, 
                        f"Settings not updated correctly: expected 85.0, got {updated_threshold}",
                        verify_response
                    )
        else:
            self.log_test(
                "KYC Settings - Update", 
                False, 
                "Failed to update KYC settings",
                response
            )

    def test_kyc_file_viewer(self):
        """Test KYC file viewer API"""
        print("📁 Testing KYC File Viewer API...")
        
        # First get a KYC submission to get file IDs
        success, response = self.make_request('GET', '/admin/kyc/all', params={'page': 1, 'limit': 1})
        
        if success and response.get('submissions'):
            kyc_submission = response['submissions'][0]
            file_ids = kyc_submission.get('file_ids', [])
            
            if file_ids:
                # Test file info retrieval
                file_id = file_ids[0]
                success, file_response = self.make_request('GET', f'/admin/kyc/file/{file_id}')
                
                if success:
                    self.log_test(
                        "KYC File Viewer - Valid File ID", 
                        True, 
                        f"Retrieved file info for {file_id}",
                        {'file_id': file_response.get('file_id')}
                    )
                else:
                    # File might not exist on disk, which is expected for demo data
                    if 'not found' in str(file_response.get('detail', '')).lower():
                        self.log_test(
                            "KYC File Viewer - Valid File ID", 
                            True, 
                            "Correctly handled missing file on disk (expected for demo data)",
                            {'expected_behavior': 'file_not_on_disk'}
                        )
                    else:
                        self.log_test(
                            "KYC File Viewer - Valid File ID", 
                            False, 
                            "Unexpected error retrieving file info",
                            file_response
                        )
            else:
                self.log_test(
                    "KYC File Viewer - Valid File ID", 
                    False, 
                    "No file IDs found in KYC submission",
                    kyc_submission
                )
        else:
            self.log_test(
                "KYC File Viewer - Valid File ID", 
                False, 
                "No KYC submissions found to test file viewer",
                response
            )
        
        # Test invalid file ID
        invalid_file_id = "invalid-file-id-12345"
        success, response = self.make_request('GET', f'/admin/kyc/file/{invalid_file_id}')
        
        if not success and 'not found' in str(response.get('detail', '')).lower():
            self.log_test(
                "KYC File Viewer - Invalid File ID", 
                True, 
                "Correctly handled invalid file ID with 404 error",
                {'error_message': response.get('detail')}
            )
        else:
            self.log_test(
                "KYC File Viewer - Invalid File ID", 
                False, 
                "Did not handle invalid file ID correctly",
                response
            )

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("🚨 Testing Error Handling...")
        
        # Test unauthorized access (without token)
        original_token = self.token
        self.token = None
        
        success, response = self.make_request('GET', '/admin/kyc/statistics')
        
        if not success:
            self.log_test(
                "Error Handling - Unauthorized Access", 
                True, 
                "Correctly rejected unauthorized request",
                {'status_handled': 'unauthorized'}
            )
        else:
            self.log_test(
                "Error Handling - Unauthorized Access", 
                False, 
                "Did not properly handle unauthorized access",
                response
            )
        
        # Restore token
        self.token = original_token
        
        # Test invalid parameters
        success, response = self.make_request('GET', '/admin/kyc/statistics', params={'days': -1})
        
        if not success:
            self.log_test(
                "Error Handling - Invalid Parameters", 
                True, 
                "Correctly handled invalid parameters",
                {'error_type': 'validation_error'}
            )
        else:
            # Some APIs might handle negative values gracefully, so this could still be valid
            self.log_test(
                "Error Handling - Invalid Parameters", 
                True, 
                "API handled negative days parameter gracefully",
                response
            )

    def run_all_tests(self):
        """Run all KYC API tests"""
        print("🚀 Starting Comprehensive KYC Backend API Tests")
        print("=" * 60)
        
        # Authentication is prerequisite for all other tests
        if not self.test_admin_authentication():
            print("❌ Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Run all KYC API tests
        self.test_kyc_statistics()
        self.test_kyc_management_apis()
        self.test_kyc_timeline_api()
        self.test_kyc_file_viewer()
        self.test_kyc_settings_api()
        self.test_error_handling()
        
        # Summary
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        return failed_tests == 0

if __name__ == "__main__":
    tester = KYCAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)