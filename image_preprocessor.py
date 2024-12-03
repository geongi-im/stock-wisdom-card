import os
import cv2
import numpy as np

def get_edge_color(image):
    # 이미지 가장자리 픽셀 추출
    edges = np.concatenate([
        image[0, :],  # 상단 가장자리
        image[-1, :],  # 하단 가장자리
        image[:, 0],  # 왼쪽 가장자리
        image[:, -1]  # 오른쪽 가장자리
    ])
    
    # 가장자리 픽셀들의 평균 색상 계산
    average_color = np.mean(edges, axis=0).astype(np.uint8)
    
    # 색상을 약간 어둡게 조정 (더 나은 대비를 위해)
    darkened_color = (average_color * 0.7).astype(np.uint8)
    
    return darkened_color

def maintain_aspect_ratio_resize(image, target_size):
    height, width = image.shape[:2]
    
    # 가로, 세로 중 긴 쪽을 target_size에 맞춤
    if height > width:
        # 세로가 더 길 경우
        new_height = target_size
        new_width = int(width * (target_size / height))
    else:
        # 가로가 더 길 경우
        new_width = target_size
        new_height = int(height * (target_size / width))
    
    # 리사이징
    resized = cv2.resize(image, (new_width, new_height))
    
    # 이미지 가장자리의 평균 색상 계산
    background_color = get_edge_color(resized)
    
    # target_size x target_size 배경 이미지 생성
    square_img = np.full((target_size, target_size, 3), background_color, dtype=np.uint8)
    
    # 리사이즈된 이미지를 중앙에 배치
    x_offset = (target_size - new_width) // 2
    y_offset = (target_size - new_height) // 2
    square_img[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
    
    return square_img

def process_images():
    # 이미지 디렉토리 경로 설정
    img_dir = 'img'
    source_dir = os.path.join(img_dir, 'source')
    
    # 처리할 인물 목록
    target_names = ["Warren Buffett", "Andre Kostolany", "Peter Lynch", "Ken Fisher", "Benjamin Graham", "John Templeton", "Seth Klarman", "William O'Neil", "Charlie Munger"]
    
    # img 디렉토리가 없으면 생성
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        print(f"'{img_dir}' 디렉토리가 생성되었습니다.")
    
    # source 디렉토리가 없으면 생성
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"'{source_dir}' 디렉토리가 생성되었습니다.")
        return
    
    # 각 인물별로 처리
    for name in target_names:
        # source 디렉토리에서 해당 인물의 이미지 찾기
        for filename in os.listdir(source_dir):
            if filename.startswith(name) and any(filename.endswith(f"{num:02d}.jpg") or filename.endswith(f"{num:02d}.png") for num in range(1, 4)):
                # 이미지 파일 경로
                img_path = os.path.join(source_dir, filename)
                
                # 이미지 읽기
                img = cv2.imread(img_path)
                if img is None:
                    print(f"'{filename}' 파일을 읽을 수 없습니다.")
                    continue
                
                # 비율 유지하면서 리사이징 (긴 쪽을 600px에 맞춤)
                resized_img = maintain_aspect_ratio_resize(img, 600)
                
                # 흑백 변환
                gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
                
                # 3채널로 다시 변환
                gray_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
                
                # 파일 번호 추출 (01, 02, 03)
                file_num = filename[-6:-4]  # 확장자 제외하고 마지막 두 자리
                
                # 인물명으로 된 폴더에 저장
                output_path = os.path.join(img_dir, name, f"{file_num}.jpg")
                
                # 처리된 이미지 저장
                cv2.imwrite(output_path, gray_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
                print(f"'{filename}' 처리 완료 -> {output_path}")

if __name__ == '__main__':
    process_images()
    print("모든 이미지 처리가 완료되었습니다.")