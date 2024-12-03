from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

class ImageProcessor:
    def __init__(self, font_dir='fonts'):
        self.font_dir = font_dir
        self.quote_font_path = os.path.join(font_dir, 'NanumGothicBold.ttf')
        self.author_font_path = os.path.join(font_dir, 'MaruBuri-Bold.ttf')

    def get_optimal_font_size(self, text, max_width, max_height, font_path=None, initial_size=60):
        # 시작 폰트 크기
        font_size = initial_size
        
        while font_size > 10:  # 최소 폰트 크기는 10
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
                    return font
                    
                # 텍스트를 여러 줄로 나눔 (한 줄당 약 15-20자)
                wrapped_text = textwrap.fill(text, width=20)
                lines = wrapped_text.split('\n')
                
                # 모든 줄의 최대 너비와 총 높이 계산
                max_line_width = 0
                total_height = 0
                line_spacing = font_size * 0.3
                
                for line in lines:
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                    line_height = bbox[3] - bbox[1]
                    max_line_width = max(max_line_width, line_width)
                    total_height += line_height
                
                if len(lines) > 1:
                    total_height += line_spacing * (len(lines) - 1)
                
                if max_line_width <= max_width and total_height <= max_height:
                    return font, wrapped_text
                
            except Exception as e:
                print(f"폰트 크기 조정 중 오류 발생: {e}")
                font = ImageFont.load_default()
                return font, text
                
            font_size -= 2
        
        return ImageFont.load_default(), text

    def create_card(self, image_path, wisdom_quote, author):
        # 이미지 열기 및 기본 설정
        img = Image.open(image_path)
        filename = os.path.basename(image_path)
        
        # 반투명 레이어 생성 및 합성
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 128))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        draw = ImageDraw.Draw(img)
        max_text_width = int(img.size[0] * 0.8)
        max_text_height = int(img.size[1] * 0.5)
        
        # 폰트 설정
        try:
            formatted_quote = f'"{wisdom_quote}"'
            quote_font, wrapped_quote = self.get_optimal_font_size(
                formatted_quote, max_text_width, max_text_height, 
                self.quote_font_path, 60
            )
            author_font, _ = self.get_optimal_font_size(
                author, max_text_width, max_text_height, 
                self.author_font_path, 20
            )
        except Exception as e:
            print(f"폰트 로드 중 오류 발생: {e}")
            quote_font, wrapped_quote = self.get_optimal_font_size(
                formatted_quote, max_text_width, max_text_height, initial_size=60
            )
            author_font, _ = self.get_optimal_font_size(
                author, max_text_width, max_text_height, initial_size=20
            )

        # 텍스트 위치 계산 및 그리기
        img_width, img_height = img.size
        quote_lines = wrapped_quote.split('\n')
        line_spacing = quote_font.size * 0.3
        
        # 전체 인용구 높이 계산
        total_quote_height = self._calculate_total_height(quote_font, quote_lines, line_spacing)
        
        # 텍스트 위치 결정
        quote_y = self._determine_text_position(filename, img_height, total_quote_height)
        
        # 텍스트 그리기
        quote_y = self._draw_quote(draw, quote_lines, quote_font, img_width, quote_y, line_spacing)
        self._draw_author(draw, author, author_font, img_width, quote_y)
        
        return img.convert('RGB')

    def _calculate_total_height(self, font, lines, line_spacing):
        total_height = 0
        for line in lines:
            bbox = font.getbbox(line)
            total_height += (bbox[3] - bbox[1])
        total_height += line_spacing * (len(lines) - 1)
        return total_height

    def _determine_text_position(self, filename, img_height, total_quote_height):
        position = filename.split('_')[1][0]
        if position == 't':
            return img_height - int(img_height * 0.8) - total_quote_height
        elif position == 'b':
            return img_height - int(img_height * 0.25) - total_quote_height
        return (img_height - total_quote_height) // 2 - 30

    def _draw_quote(self, draw, lines, font, img_width, y_pos, line_spacing):
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            line_x = (img_width - line_width) // 2
            
            # 그림자 및 메인 텍스트
            draw.text((line_x + 2, y_pos + 2), line, fill=(0, 0, 0, 180), font=font)
            draw.text((line_x, y_pos), line, fill=(255, 255, 255, 255), font=font)
            y_pos += line_height + line_spacing
        return y_pos

    def _draw_author(self, draw, author, font, img_width, quote_y):
        formatted_author = f"- {author} -"
        bbox = draw.textbbox((0, 0), formatted_author, font=font)
        author_width = bbox[2] - bbox[0]
        author_x = (img_width - author_width) // 2
        author_y = quote_y + 20
        
        # 그림자 및 메인 텍스트
        draw.text((author_x + 2, author_y + 2), formatted_author, fill=(0, 0, 0, 180), font=font)
        draw.text((author_x, author_y), formatted_author, fill=(255, 255, 255, 255), font=font) 