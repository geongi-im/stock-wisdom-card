import requests
from typing import List, Optional
import os
from PIL import Image
import io
from utils.logger_util import LoggerUtil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ApiError(Exception):
    """API 호출 관련 커스텀 예외"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error (Status: {status_code}): {message}")

class ApiUtil:
    def __init__(self):
        base_url = os.getenv("BASE_URL")
        if not base_url:
            raise EnvironmentError("환경 변수 'BASE_URL'가 설정되어 있지 않습니다.")

        base_url = base_url.rstrip("/")
        self.api_base_url = f"{base_url}/api"
        self.headers = {
            "Accept": "application/json"
        }
        self.max_file_size = 1 * 1024 * 1024  # 1MB
        self.max_width = 800  # 최대 너비
        self.logger = LoggerUtil().get_logger()

    def _compress_image(self, image_path: str):
        """이미지 압축"""
        try:
            with Image.open(image_path) as img:
                # 이미지 크기 조정
                if img.width > self.max_width:
                    ratio = self.max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
                
                # 이미지 품질 조정
                buffer = io.BytesIO()
                format = img.format if img.format else 'PNG'
                
                if format == 'PNG':
                    img.save(buffer, format=format, optimize=True)
                else:
                    img.save(buffer, format=format, quality=85, optimize=True)
                
                compressed_image = buffer.getvalue()
                
                # 압축 후에도 크기가 큰 경우 추가 압축
                quality = 85
                while len(compressed_image) > self.max_file_size and quality > 30:
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    compressed_image = buffer.getvalue()
                    quality -= 10
                
                self.logger.info(f"이미지 압축 완료: {image_path} (크기: {len(compressed_image)/1024:.1f}KB)")
                return compressed_image, format.lower()
        except Exception as e:
            self.logger.error(f"이미지 압축 실패: {image_path} - {str(e)}")
            raise

    def create_post(self, title: str, content: str, category: str, writer: str, image_paths: Optional[List[str]] = None):
        """게시글 생성 API 호출"""
        url = f"{self.api_base_url}/board-content"
        
        try:
            if image_paths:
                self.logger.info(f"게시글 생성 시작 (이미지 포함) - 제목: {title}")
                # 이미지와 함께 게시글 등록
                files = {}
                for i, image_path in enumerate(image_paths):
                    if os.path.exists(image_path):
                        try:
                            compressed_image, format = self._compress_image(image_path)
                            # 원본 파일명 사용
                            original_filename = os.path.basename(image_path)
                            # 각 이미지를 배열로 전송
                            files[f'image[{i}]'] = (original_filename, compressed_image, f'image/{format}')
                            self.logger.debug(f"이미지 {i+1} 추가: {original_filename}")
                        except Exception as e:
                            self.logger.error(f"이미지 처리 실패: {image_path} - {str(e)}")
                            continue
                
                if not files:
                    error_msg = "처리 가능한 이미지가 없습니다."
                    self.logger.error(error_msg)
                    raise ApiError(400, error_msg)
                
                data = {
                    "title": title,
                    "content": content,
                    "category": category,
                    "writer": writer
                }
                
                try:
                    # 요청 데이터 로깅 추가
                    self.logger.debug(f"API 요청 데이터: {data}")
                    self.logger.debug(f"파일 데이터: {[f'{k}: {v[0]}' for k, v in files.items()]}")
                    
                    # multipart/form-data로 전송 시에는 Content-Type 헤더를 제거 (requests가 자동으로 설정)
                    headers = self.headers.copy()
                    
                    # form-data 형식으로 전송
                    form_data = {}
                    for key, value in data.items():
                        # Laravel 필드명에 맞게 수정
                        form_data[key] = (None, str(value))
                    
                    # 이미지 파일 추가
                    form_data.update(files)
                    
                    # 디버그 로그 추가
                    self.logger.debug(f"최종 전송 데이터: {[(k, v[0] if isinstance(v, tuple) else v) for k, v in form_data.items()]}")
                    
                    response = requests.post(
                        url, 
                        headers=headers,
                        files=form_data,
                        timeout=30
                    )
                    
                    # 응답 상태 코드 로깅
                    self.logger.debug(f"응답 상태 코드: {response.status_code}")
                    self.logger.debug(f"응답 헤더: {dict(response.headers)}")
                finally:
                    files.clear()
            else:
                self.logger.info(f"게시글 생성 시작 (이미지 없음) - 제목: {title}")
                payload = {
                    "title": title,
                    "content": content,
                    "category": category,
                    "writer": writer
                }
                response = requests.post(url, headers=self.headers, json=payload)

            # 응답 확인 및 한글 디코딩
            try:
                response.encoding = 'utf-8'  # 응답 인코딩을 UTF-8로 설정
                response_data = response.json()
                
                # 응답 로깅 (디버깅용)
                self.logger.debug(f"API 응답: {response_data}")
                
                if not response_data.get('success', False):
                    error_msg = f"게시글 생성 실패\n제목: {title}\n카테고리: {category}\n응답: {response.text}"
                    self.logger.error(error_msg)
                    raise ApiError(response.status_code, error_msg)

                self.logger.info(f"게시글 생성 성공 - 제목: {title}")
                
                # 이미지 URL 확인 로직 수정
                if image_paths and not response_data.get('data', {}).get('image_urls'):
                    self.logger.warning(f"이미지가 포함된 게시글이지만 image_urls가 비어있습니다. - 제목: {title}")
                elif image_paths:
                    self.logger.info(f"이미지 URL: {response_data.get('data', {}).get('image_urls')}")
                
                return response_data
                
            except ValueError as e:
                error_msg = f"JSON 응답 파싱 실패\n제목: {title}\n카테고리: {category}\n응답: {response.text}"
                self.logger.error(error_msg)
                raise ApiError(response.status_code, error_msg)

        except requests.RequestException as e:
            error_msg = f"API 요청 중 오류 발생\n제목: {title}\n카테고리: {category}\n오류: {str(e)}"
            self.logger.error(error_msg)
            raise ApiError(500, error_msg)

    def upload_wisdom_card(self, image_path: str, author: str, wisdom_kr: str, wisdom_en: str, name_kr: str, name_en: str):
        """
        명언 카드 이미지를 API 서버에 업로드
        
        Args:
            image_path (str): 업로드할 이미지 파일 경로
            author (str): 저자 정보
            wisdom_kr (str): 명언 한글 텍스트
            wisdom_en (str): 명언 영문 텍스트
            name_kr (str): 저자 한글 이름
            name_en (str): 저자 영문 이름
            
        Returns:
            dict: 성공 시 {"success": True, "image_url": "..."}, 실패 시 {"success": False, "error": "에러 메시지"}
        """
        url = f"{self.api_base_url}/board-content"
        
        try:
            self.logger.info(f"명언 카드 업로드 시작 - 저자: {author}")
            
            # 이미지 처리
            files = {}
            thumbnail_image = {}
            if os.path.exists(image_path):
                try:
                    compressed_image, format = self._compress_image(image_path)
                    original_filename = os.path.basename(image_path)
                    files['image[0]'] = (original_filename, compressed_image, f'image/{format}')
                    thumbnail_image['thumbnail_image'] = (original_filename, compressed_image, f'image/{format}')
                    self.logger.debug(f"이미지 추가: {original_filename}")
                except Exception as e:
                    error_msg = f"이미지 처리 실패: {image_path} - {str(e)}"
                    self.logger.error(error_msg)
                    raise ApiError(400, error_msg)
            else:
                error_msg = f"이미지 파일을 찾을 수 없습니다: {image_path}"
                self.logger.error(error_msg)
                raise ApiError(400, error_msg)

            # 현재 날짜 가져오기
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 게시글 제목 생성
            title = f"{current_date} {name_kr}의 투자 명언"

            # 게시글 내용 생성
            content = f"""<strong><h3>[{name_kr} ({name_en})의 투자 명언]</h3></strong><br>
            <p class="quote">{wisdom_kr}</p><br>
            <p class="quote">{wisdom_en}</p><br>
            <p>
                <a href="#">#{name_kr}</a> 
                <a href="#">#{name_en}</a> 
                <a href="#">#투자명언</a> 
                <a href="#">#주식명언</a> 
                <a href="#">#투자대가</a> 
                <a href="#">#재테크</a> 
                <a href="#">#경제공부</a>
            </p>"""

            # 데이터 구성
            data = {
                "title": title,
                "content": content,
                "category": "투자명언",
                "writer": "admin"
            }

            try:
                # 요청 데이터 로깅
                self.logger.debug(f"API 요청 데이터: {data}")
                self.logger.debug(f"파일 데이터: {[f'{k}: {v[0]}' for k, v in files.items()]}")
                
                # form-data 형식으로 전송
                form_data = {}
                for key, value in data.items():
                    form_data[key] = (None, str(value))
                
                # 이미지 파일 추가
                form_data.update(files)
                form_data.update(thumbnail_image)
                
                # 디버그 로그 추가
                self.logger.debug(f"최종 전송 데이터: {[(k, v[0] if isinstance(v, tuple) else v) for k, v in form_data.items()]}")
                
                # API 요청
                response = requests.post(
                    url,
                    headers=self.headers,
                    files=form_data,
                    timeout=30
                )
                
                # 응답 상태 코드 로깅
                self.logger.debug(f"응답 상태 코드: {response.status_code}")
                self.logger.debug(f"응답 헤더: {dict(response.headers)}")

                # 응답 처리
                response.encoding = 'utf-8'
                response_data = response.json()
                
                # 응답 로깅
                self.logger.debug(f"API 응답: {response_data}")
                
                if not response_data.get('success', False):
                    error_msg = f"명언 카드 업로드 실패\n제목: {title}\n응답: {response.text}"
                    self.logger.error(error_msg)
                    raise ApiError(response.status_code, error_msg)

                self.logger.info(f"명언 카드 업로드 성공 - 제목: {title}")
                
                # 이미지 URL 확인
                image_urls = response_data.get('data', {}).get('image_urls', [])
                if not image_urls:
                    self.logger.warning("응답에 이미지 URL이 없습니다.")
                else:
                    self.logger.info(f"이미지 URL: {image_urls[0]}")
                
                return {
                    "success": True,
                    "image_url": image_urls[0] if image_urls else None,
                    "message": "이미지가 성공적으로 업로드되었습니다."
                }

            except ValueError as e:
                error_msg = f"JSON 응답 파싱 실패\n제목: {title}\n응답: {response.text}"
                self.logger.error(error_msg)
                raise ApiError(response.status_code, error_msg)

        except requests.RequestException as e:
            error_msg = f"API 요청 중 오류 발생\n저자: {author}\n오류: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except ApiError as e:
            return {"success": False, "error": str(e)}
        finally:
            if 'files' in locals():
                files.clear()

if __name__ == "__main__":
    # API 테스트
    api = ApiUtil()
    logger = LoggerUtil().get_logger()
    
    # 테스트 데이터
    test_data = {
        "image_path": "output/20240101.jpeg",
        "author": "워렌 버핏 Warren Buffett",
        "wisdom_text": "주식시장에서 성공하는 방법은 다른 사람들이 두려워할 때 욕심을 내고, 다른 사람들이 욕심낼 때 두려워하는 것이다.",
        "name_kr": "워렌 버핏",
        "name_en": "Warren Buffett"
    }
    
    try:
        # API 호출 테스트
        result = api.upload_wisdom_card(
            image_path=test_data["image_path"],
            author=test_data["author"],
            wisdom_text=test_data["wisdom_text"],
            name_kr=test_data["name_kr"],
            name_en=test_data["name_en"]
        )
        logger.info(f"API 호출 결과: {result}")
        
    except ApiError as e:
        logger.error(f"API 에러 발생: {e}")
    except Exception as e:
        logger.error(f"예상치 못한 에러 발생: {e}") 