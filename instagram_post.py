import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import time  # 상단에 time 모듈 import 추가

# 환경 변수 로드
load_dotenv()

class InstagramAPI:
    def __init__(self):
        """Initialize Instagram API with credentials from environment variables"""
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        
        if not self.access_token or not self.account_id:
            raise ValueError("Instagram 자격 증명이 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def _test_image_url(self, image_url, max_retries=5, delay=2):
        """
        이미지 URL 접근성 테스트를 재시도하는 헬퍼 함수
        
        Args:
            image_url (str): 테스트할 이미지 URL
            max_retries (int): 최대 재시도 횟수
            delay (int): 재시도 간 대기 시간(초)
            
        Returns:
            bool: 접근 가능하면 True, 아니면 False
        """
        for attempt in range(max_retries):
            try:
                test_response = requests.head(image_url)
                print(f"시도 {attempt + 1}/{max_retries} - HTTP 상태: {test_response.status_code}")
                print(f"Content-Type: {test_response.headers.get('content-type', 'unknown')}")
                
                if test_response.status_code == 200:
                    return True
                    
                if attempt < max_retries - 1:  # 마지막 시도가 아니면 대기
                    print(f"{delay}초 후 재시도...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"시도 {attempt + 1}/{max_retries} - 실패: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"{delay}초 후 재시도...")
                    time.sleep(delay)
        
        return False

    def _create_single_media(self, image_url, caption=""):
        """
        단일 이미지 미디어 컨테이너 생성
        
        Args:
            image_url (str): 이미지 URL
            caption (str): 이미지 설명
            
        Returns:
            dict: API 응답 데이터
        """
        print(f"\n이미지 URL 확인: {image_url}")
        
        # 이미지 URL 접근성 테스트 (재시도 로직 적용)
        if not self._test_image_url(image_url):
            raise Exception("이미지 URL에 접근할 수 없습니다.")
        
        container_url = f"{self.base_url}/{self.account_id}/media"
        container_params = {
            "access_token": self.access_token,
            "image_url": image_url,
            "caption": caption
        }
        
        print("\nInstagram API 요청:")
        print(f"URL: {container_url}")
        print("Parameters:", {k: v if k != 'access_token' else '****' for k, v in container_params.items()})
        
        try:
            response = requests.post(container_url, params=container_params)
            print(f"\nAPI 응답 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                print("에러 응답:", response.text)
            else:
                print("성공 응답:", response.json())
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\nAPI 요청 실패: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print("에러 응답:", e.response.text)
            raise

    def _create_carousel_item(self, image_url):
        """
        캐러셀 아이템 생성
        
        Args:
            image_url (str): 이미지 URL
            
        Returns:
            dict: API 응답 데이터
        """
        print(f"\n이미지 URL 확인: {image_url}")
        
        # 이미지 URL 접근성 테스트 (재시도 로직 적용)
        if not self._test_image_url(image_url):
            raise Exception("이미지 URL에 접근할 수 없습니다.")
        
        container_url = f"{self.base_url}/{self.account_id}/media"
        container_params = {
            "access_token": self.access_token,
            "image_url": image_url,
            "is_carousel_item": True
        }
        
        print("\nInstagram API 요청:")
        print(f"URL: {container_url}")
        print("Parameters:", {k: v if k != 'access_token' else '****' for k, v in container_params.items()})
        
        try:
            response = requests.post(container_url, params=container_params)
            print(f"\nAPI 응답 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                print("에러 응답:", response.text)
            else:
                print("성공 응답:", response.json())
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\nAPI 요청 실패: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print("에러 응답:", e.response.text)
            raise

    def _create_carousel_container(self, children_ids, caption=""):
        """
        캐러셀 컨테이너 생성
        
        Args:
            children_ids (list): 캐러셀 아이템 ID 리스트
            caption (str): 캐러셀 설명
            
        Returns:
            dict: API 응답 데이터
        """
        container_url = f"{self.base_url}/{self.account_id}/media"
        container_params = {
            "access_token": self.access_token,
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption
        }
        
        print("\nInstagram API 요청:")
        print(f"URL: {container_url}")
        print("Parameters:", {k: v if k != 'access_token' else '****' for k, v in container_params.items()})
        
        try:
            response = requests.post(container_url, params=container_params)
            print(f"\nAPI 응답 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                print("에러 응답:", response.text)
            else:
                print("성공 응답:", response.json())
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\nAPI 요청 실패: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print("에러 응답:", e.response.text)
            raise

    def _publish_media(self, creation_id):
        """
        미디어 게시
        
        Args:
            creation_id (str): 생성된 미디어 ID
            
        Returns:
            dict: API 응답 데이터
        """
        publish_url = f"{self.base_url}/{self.account_id}/media_publish"
        publish_params = {
            "access_token": self.access_token,
            "creation_id": creation_id
        }
        
        print("\nInstagram API 요청:")
        print(f"URL: {publish_url}")
        print("Parameters:", {k: v if k != 'access_token' else '****' for k, v in publish_params.items()})
        
        try:
            response = requests.post(publish_url, params=publish_params)
            print(f"\nAPI 응답 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                print("에러 응답:", response.text)
            else:
                print("성공 응답:", response.json())
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\nAPI 요청 실패: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print("에러 응답:", e.response.text)
            raise
        
    def post_image(self, image_paths, caption=None):
        """
        Instagram에 이미지를 포스팅합니다.
        
        Args:
            image_paths (str or list): 업로드할 이미지 URL 또는 URL 리스트
            caption (str, optional): 포스트에 포함될 캡션 텍스트. None이면 자동 생성됨.
            
        Returns:
            dict: 성공 시 {"success": True, "post_id": "..."}, 실패 시 {"success": False, "error": "에러 메시지"}
        """
        try:            
            # 단일 이미지인 경우 리스트로 변환
            if isinstance(image_paths, str):
                image_paths = [image_paths]

            # 이미지가 여러 장인 경우 캐러슬로 처리
            if len(image_paths) > 1:
                print(f"캐러셀 이미지 업로드 중... (총 {len(image_paths)}장)")
                
                # 각 이미지를 캐러셀 아이템으로 생성
                children_ids = []
                for i, image_url in enumerate(image_paths, 1):
                    print(f"이미지 {i}/{len(image_paths)} 처리 중...")
                    response = self._create_carousel_item(image_url)
                    if "id" not in response:
                        return {"success": False, "error": f"캐러셀 아이템 {i} 생성 실패"}
                    children_ids.append(response["id"])
                
                # 캐러셀 컨테이너 생성
                print("캐러셀 컨테이너 생성 중...")
                container = self._create_carousel_container(children_ids, caption)
                
            else:  # 단일 이미지 처리
                print("단일 이미지 업로드 중...")
                container = self._create_single_media(image_paths[0], caption)

            if "id" not in container:
                return {"success": False, "error": "미디어 컨테이너 ID를 받지 못했습니다"}
            
            # 미디어 게시
            print("Instagram에 게시물 발행 중...")
            publish_data = self._publish_media(container["id"])
            
            if "id" not in publish_data:
                return {"success": False, "error": "게시물 ID를 받지 못했습니다"}
            
            print("게시물 발행 완료!")
            return {
                "success": True, 
                "post_id": publish_data["id"],
                "status": "이미지가 성공적으로 Instagram에 업로드되었습니다. 원본 파일은 이제 삭제해도 됩니다."
            }
            
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_message = f"{error_data['error'].get('message', str(e))}"
                except ValueError:
                    pass
            return {"success": False, "error": f"Instagram 포스팅 중 오류 발생: {error_message}"}


if __name__ == "__main__":
    api = InstagramAPI()
    
    # 테스트 이미지 URL
    single_image = "https://petapixel.com/assets/uploads/2022/06/what-is-a-jpeg-featured-800x420.jpg"
    multiple_images = [
        "https://petapixel.com/assets/uploads/2022/06/what-is-a-jpeg-featured-800x420.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
    ]
    
    # 단일 이미지 테스트
    print("\n=== 단일 이미지 테스트 ===")
    result = api.post_image(single_image)
    if result["success"]:
        print(f"포스팅 성공! 게시물 ID: {result['post_id']}")
        print(result["status"])
    else:
        print(f"포스팅 실패: {result['error']}")
    
    # 다중 이미지 테스트
    print("\n=== 다중 이미지 테스트 ===")
    result = api.post_image(multiple_images)
    if result["success"]:
        print(f"포스팅 성공! 게시물 ID: {result['post_id']}")
        print(result["status"])
    else:
        print(f"포스팅 실패: {result['error']}")
