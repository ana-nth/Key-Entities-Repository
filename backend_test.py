import requests
import sys
import json
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image

class VirtualTryOnAPITester:
    def __init__(self, base_url="https://b8b304e5-ad9a-4af8-bcc1-8ab654b09579.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def create_sample_image_base64(self, color="red", size=(200, 200)):
        """Create a sample image and return as base64"""
        try:
            # Create a simple colored image
            img = Image.new('RGB', size, color=color)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"Error creating sample image: {e}")
            return None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=60)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        success, response = self.run_test(
            "Basic API Connectivity",
            "GET",
            "api/",
            200
        )
        return success

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Test creating a status check
        status_data = {
            "client_name": f"test_client_{datetime.now().strftime('%H%M%S')}"
        }
        
        success1, response1 = self.run_test(
            "Create Status Check",
            "POST",
            "api/status",
            200,
            data=status_data
        )
        
        # Test getting status checks
        success2, response2 = self.run_test(
            "Get Status Checks",
            "GET",
            "api/status",
            200
        )
        
        return success1 and success2

    def test_tryon_generation(self):
        """Test the main try-on generation endpoint"""
        # Create sample images
        user_image = self.create_sample_image_base64("blue", (300, 400))
        clothing_image = self.create_sample_image_base64("green", (200, 300))
        
        if not user_image or not clothing_image:
            print("❌ Failed to create sample images for testing")
            return False
        
        tryon_data = {
            "name": "Test User",
            "user_image": user_image,
            "clothing_image": clothing_image,
            "measurements": {
                "height": "170",
                "weight": "65",
                "chest": "90",
                "waist": "75",
                "hips": "95"
            },
            "style": "casual"
        }
        
        success, response = self.run_test(
            "Virtual Try-On Generation",
            "POST",
            "api/tryon/generate",
            200,
            data=tryon_data
        )
        
        if success and isinstance(response, dict):
            tryon_id = response.get('id')
            if tryon_id:
                # Test getting the specific try-on result
                success2, response2 = self.run_test(
                    "Get Try-On Result",
                    "GET",
                    f"api/tryon/{tryon_id}",
                    200
                )
                
                # Test getting try-on image as base64
                success3, response3 = self.run_test(
                    "Get Try-On Image Base64",
                    "GET",
                    f"api/tryon/{tryon_id}/base64",
                    200
                )
                
                return success and success2 and success3
        
        return success

    def test_tryon_validation(self):
        """Test try-on endpoint validation"""
        # Test with missing user image
        invalid_data1 = {
            "name": "Test User",
            "clothing_image": self.create_sample_image_base64("green"),
            "measurements": {
                "height": "170",
                "weight": "65",
                "chest": "90",
                "waist": "75",
                "hips": "95"
            },
            "style": "casual"
        }
        
        success1, _ = self.run_test(
            "Validation - Missing User Image",
            "POST",
            "api/tryon/generate",
            400,
            data=invalid_data1
        )
        
        # Test with missing name
        invalid_data2 = {
            "name": "",
            "user_image": self.create_sample_image_base64("blue"),
            "clothing_image": self.create_sample_image_base64("green"),
            "measurements": {
                "height": "170",
                "weight": "65",
                "chest": "90",
                "waist": "75",
                "hips": "95"
            },
            "style": "casual"
        }
        
        success2, _ = self.run_test(
            "Validation - Empty Name",
            "POST",
            "api/tryon/generate",
            400,
            data=invalid_data2
        )
        
        return success1 and success2

    def test_get_all_tryons(self):
        """Test getting all try-on results"""
        success, response = self.run_test(
            "Get All Try-On Results",
            "GET",
            "api/tryons",
            200
        )
        return success

    def test_nonexistent_tryon(self):
        """Test getting a non-existent try-on result"""
        success, response = self.run_test(
            "Get Non-existent Try-On",
            "GET",
            "api/tryon/nonexistent-id",
            404
        )
        return success

def main():
    print("🚀 Starting Virtual Try-On API Tests")
    print("=" * 50)
    
    # Setup
    tester = VirtualTryOnAPITester()
    
    # Run tests in order
    tests = [
        ("Basic Connectivity", tester.test_basic_connectivity),
        ("Status Endpoints", tester.test_status_endpoints),
        ("Try-On Generation", tester.test_tryon_generation),
        ("Try-On Validation", tester.test_tryon_validation),
        ("Get All Try-Ons", tester.test_get_all_tryons),
        ("Non-existent Try-On", tester.test_nonexistent_tryon),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            failed_tests.append(test_name)
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed test categories:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n✅ All test categories passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())