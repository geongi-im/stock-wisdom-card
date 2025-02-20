import sqlite3
import csv
import os
from datetime import datetime
from utils.logger_util import LoggerUtil

class DatabaseManager:
    def __init__(self, db_path='sqlite.db'):
        self.db_path = db_path
        self.logger = LoggerUtil().get_logger()
        self._initialize_database()

    def _initialize_database(self):
        """데이터베이스와 테이블 초기화"""
        db_exists = os.path.exists(self.db_path)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if not db_exists:
                    self.logger.info(f"새로운 데이터베이스 파일 생성: {self.db_path}")
                
                # 테이블 존재 여부 확인
                cursor.execute("""
                    SELECT count(name) FROM sqlite_master 
                    WHERE type='table' AND name='wisdom_list'
                """)
                
                if cursor.fetchone()[0] == 0:
                    self.logger.info("wisdom_list 테이블 생성 중...")
                    self._create_wisdom_table(cursor)
                    self._import_csv_data(cursor)
                    conn.commit()
                    self.logger.info("테이블 생성 및 데이터 임포트 완료")
        
        except sqlite3.Error as e:
            self.logger.error(f"데이터베이스 초기화 중 오류 발생: {e}")
            raise

    def _create_wisdom_table(self, cursor):
        """wisdom_list 테이블 생성"""
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS wisdom_list (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT,
            name_kr TEXT,
            wisdom_en TEXT,
            wisdom_kr TEXT,
            file_name TEXT,
            open_yn INTEGER DEFAULT 1,
            reg_date TEXT
        )
        ''')

    def _import_csv_data(self, cursor):
        """CSV 파일에서 데이터 임포트"""
        csv_path = 'wisdom.csv'
        if not os.path.exists(csv_path):
            self.logger.warning(f"경고: {csv_path} 파일을 찾을 수 없습니다.")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
                next(csv_reader)  # 헤더 건너뛰기
                
                insert_count = 0
                for row in csv_reader:
                    if len(row) == 4:  # 모든 필드가 있는 경우에만 삽입
                        cursor.execute('''
                        INSERT INTO wisdom_list (name_en, name_kr, wisdom_en, wisdom_kr)
                        VALUES (?, ?, ?, ?)
                        ''', (row[0], row[1], row[2], row[3]))
                        insert_count += 1
                
                self.logger.info(f"{insert_count}개의 데이터가 임포트되었습니다.")
        
        except Exception as e:
            self.logger.error(f"CSV 데이터 임포트 중 오류 발생: {e}")
            raise

    def get_random_wisdom(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT idx, name_en, name_kr, wisdom_kr 
                    FROM wisdom_list 
                    WHERE open_yn = 1 AND file_name IS NULL 
                    ORDER BY RANDOM() 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    return {
                        'idx': result[0],
                        'name_en': result[1],
                        'name_kr': result[2],
                        'wisdom_kr': result[3]
                    }
                self.logger.warning("조건에 맞는 데이터가 없습니다.")
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"데이터베이스 오류: {e}")
            return None

    def update_wisdom_file(self, idx, filename):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE wisdom_list SET file_name = ?, reg_date = ? WHERE idx = ?",
                    (filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), idx)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"데이터베이스 업데이트 오류: {e}")
            return False 