import secrets
import string
import uuid
import base64
import argparse
import os
from datetime import datetime


def generate_random_key(length=32):
    """
    지정된 길이의 안전한 랜덤 문자열을 생성합니다.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_uuid_key():
    """
    UUID 기반 키를 생성합니다.
    """
    return str(uuid.uuid4())


def generate_timestamp_key(prefix=""):
    """
    타임스탬프가 포함된 키를 생성합니다.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(8)
    return f"{prefix}{timestamp}_{random_part}"


def generate_base64_key(length=32):
    """
    Base64로 인코딩된 키를 생성합니다.
    """
    random_bytes = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8')


def save_key_to_file(key, filename="api_key.txt"):
    """
    생성된 키를 파일에 저장합니다.
    """
    with open(filename, 'w') as f:
        f.write(key)
    print(f"키가 '{filename}' 파일에 저장되었습니다.")


def main():
    parser = argparse.ArgumentParser(description='안전한 API 키 생성기')
    parser.add_argument('--type', choices=['random', 'uuid', 'timestamp', 'base64'], 
                        default='random', help='생성할 키의 유형 (기본값: random)')
    parser.add_argument('--length', type=int, default=32, 
                        help='키의 길이 (random 및 base64 유형용, 기본값: 32)')
    parser.add_argument('--prefix', type=str, default='key_', 
                        help='타임스탬프 키의 접두사 (기본값: key_)')
    parser.add_argument('--save', action='store_true', 
                        help='키를 파일에 저장할지 여부')
    parser.add_argument('--file', type=str, default='api_key.txt', 
                        help='키를 저장할 파일 이름 (기본값: api_key.txt)')
    parser.add_argument('--count', type=int, default=1, 
                        help='생성할 키의 개수 (기본값: 1)')
    
    args = parser.parse_args()
    
    print(f"{args.count}개의 '{args.type}' 타입 키를 생성합니다...\n")
    
    keys = []
    for i in range(args.count):
        if args.type == 'random':
            key = generate_random_key(args.length)
        elif args.type == 'uuid':
            key = generate_uuid_key()
        elif args.type == 'timestamp':
            key = generate_timestamp_key(args.prefix)
        elif args.type == 'base64':
            key = generate_base64_key(args.length)
        
        keys.append(key)
        print(f"키 #{i+1}: {key}")
    
    if args.save and keys:
        if args.count == 1:
            save_key_to_file(keys[0], args.file)
        else:
            for i, key in enumerate(keys):
                filename = f"{os.path.splitext(args.file)[0]}_{i+1}{os.path.splitext(args.file)[1]}"
                save_key_to_file(key, filename)


if __name__ == "__main__":
    main()