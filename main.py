import os
import random
from datetime import datetime
from image_processor import ImageProcessor
from database_manager import DatabaseManager
from instagram_post import InstagramAPI  # InstagramAPI 클래스 import
from dotenv import load_dotenv  # .env 파일 로드를 위해 추가

# 환경 변수 로드
load_dotenv()

class WisdomCardGenerator:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        self.image_processor = ImageProcessor()
        self.db_manager = DatabaseManager()
        self.instagram_api = InstagramAPI()
        self.domain_url = os.getenv("DOMAIN_URL")
        
        if not self.domain_url:
            raise ValueError("DOMAIN_URL이 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # output 디렉토리 생성 및 권한 설정
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.chmod(output_dir, 0o777)  # 폴더 권한을 777로 설정
            print(f"'{output_dir}' 디렉토리가 생성되었습니다.")
        else:
            # 기존 폴더의 권한 확인 및 설정
            current_mode = os.stat(output_dir).st_mode & 0o777
            if current_mode != 0o777:
                os.chmod(output_dir, 0o777)
                print(f"'{output_dir}' 디렉토리 권한을 777로 변경했습니다.")

        # img 디렉토리 체크 및 권한 설정
        img_dir = 'img'
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            os.chmod(img_dir, 0o777)
            print(f"'{img_dir}' 디렉토리가 생성되었습니다.")
        else:
            # 기존 img 폴더의 권한 확인 및 설정
            current_mode = os.stat(img_dir).st_mode & 0o777
            if current_mode != 0o777:
                os.chmod(img_dir, 0o777)
                print(f"'{img_dir}' 디렉토리 권한을 777로 변경했습니다.")

    def generate_and_post(self):
        """명언 카드를 생성하고 인스타그램에 포스팅"""
        # 명언 데이터 가져오기
        self.wisdom_data = self.db_manager.get_random_wisdom()
        if not self.wisdom_data:
            return False

        # 데이터 출력
        print("\n=== 조회된 데이터 ===")
        print(f"idx: {self.wisdom_data['idx']}")
        print(f"영문 이름: {self.wisdom_data['name_en']}")
        print(f"한글 이름: {self.wisdom_data['name_kr']}")
        print(f"명언(한글): {self.wisdom_data['wisdom_kr']}")
        print("==================\n")

        # 이미지 선택 및 생성
        image_path = self._get_random_image(self.wisdom_data['name_en'])
        if not image_path:
            return False
        print(f"선택된 이미지: {image_path}")

        # 저자 정보 포매팅
        author = f"{self.wisdom_data['name_kr']} {self.wisdom_data['name_en']}"

        # 카드 생성
        print("\n이미지 생성 중...")
        img = self.image_processor.create_card(
            image_path, 
            self.wisdom_data['wisdom_kr'],
            author
        )

        # 파일 저장
        output_filename = self._save_image(img)
        if not output_filename:
            return False

        output_path = os.path.join(self.output_dir, output_filename)
        print(f"이미지 저장 완료: {output_path}")

        # 이미지 URL 생성
        image_url = f"{self.domain_url}/stock-wisdom-card/{output_path}"
        print(f"이미지 URL: {image_url}")

        # 인스타그램에 포스팅
        try:
            caption = f"""{self.wisdom_data['name_kr']}의 투자 명언

#MQ #MoneyQuotient #{self.wisdom_data['name_kr'].replace(" ", "")} #{self.wisdom_data['name_en'].replace(" ", "")} #투자명언 #주식명언 #투자대가 #재테크 #경제공부 #주식 #투자"""

            print("\n인스타그램 포스팅 시도 중...")
            result = self.instagram_api.post_image(image_url, caption)
            
            if result["success"]:
                print(f"✨ 인스타그램 포스팅 완료! (Post ID: {result['post_id']})")
                # DB 업데이트
                if self.db_manager.update_wisdom_file(self.wisdom_data['idx'], output_filename):
                    print("DB 업데이트 완료")
                    return True
            else:
                print(f"❌ 인스타그램 포스팅 실패: {result['error']}")
                return False

        except Exception as e:
            print(f"❌ 인스타그램 포스팅 중 오류 발생: {e}")
            return False

    def _get_random_image(self, name_en):
        image_folder = f'img/{name_en}'
        try:
            image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
            if not image_files:
                print(f"이미지를 찾을 수 없습니다: {image_folder}")
                return None
            return os.path.join(image_folder, random.choice(image_files))
        except Exception as e:
            print(f"이미지 선택 중 오류 발생: {e}")
            return None

    def _save_image(self, img):
        try:
            current_date = datetime.now().strftime('%Y%m%d')
            output_path = os.path.join(self.output_dir, f"{current_date}.jpeg")
            
            # 중복 파일명 처리
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(
                    self.output_dir, 
                    f"{current_date}_{counter}.jpeg"
                )
                counter += 1

            img.save(output_path, 'JPEG', quality=95)
            return os.path.basename(output_path)
        except Exception as e:
            print(f"이미지 저장 중 오류 발생: {e}")
            return None

def main():
    print("=== 명언 카드 생성기 시작 ===")
    generator = WisdomCardGenerator()
    
    try:
        if generator.generate_and_post():
            print("\n✨ 명언 카드 생성 및 포스팅이 완료되었습니다!")
        else:
            print("\n❌ 명언 카드 생성 또는 포스팅 중 오류가 발생했습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
    
    print("\n=== 프로그램 종료 ===")

if __name__ == '__main__':
    main()