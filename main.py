import os
import random
from datetime import datetime
from image_processor import ImageProcessor
from database_manager import DatabaseManager

class WisdomCardGenerator:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        self.image_processor = ImageProcessor()
        self.db_manager = DatabaseManager()
        
        # output 디렉토리 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"'{output_dir}' 디렉토리가 생성되었습니다.")

    def generate_card(self):
        # 명언 데이터 가져오기
        wisdom_data = self.db_manager.get_random_wisdom()
        if not wisdom_data:
            return False

        # 데이터 출력
        print("\n=== 조회된 데이터 ===")
        print(f"idx: {wisdom_data['idx']}")
        print(f"영문 이름: {wisdom_data['name_en']}")
        print(f"한글 이름: {wisdom_data['name_kr']}")
        print(f"명언(한글): {wisdom_data['wisdom_kr']}")
        print("==================\n")

        # 이미지 선택
        image_path = self._get_random_image(wisdom_data['name_en'])
        if not image_path:
            return False
        print(f"선택된 이미지: {image_path}")

        # 저자 정보 포매팅
        author = f"{wisdom_data['name_kr']} {wisdom_data['name_en']}"

        # 카드 생성
        print("\n이미지 생성 중...")
        img = self.image_processor.create_card(
            image_path, 
            wisdom_data['wisdom_kr'],
            author
        )

        # 파일 저장
        output_filename = self._save_image(img)
        if not output_filename:
            return False
        print(f"이미지 저장 완료: {output_filename}")

        # DB 업데이트
        print("\nDB 업데이트 중...")
        if self.db_manager.update_wisdom_file(wisdom_data['idx'], output_filename):
            print("DB 업데이트 완료")
            return True
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
        if generator.generate_card():
            print("\n✨ 명언 카드가 성공적으로 생성되었습니다!")
        else:
            print("\n❌ 명언 카드 생성 중 오류가 발생했습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
    
    print("\n=== 프로그램 종료 ===")

if __name__ == '__main__':
    main()