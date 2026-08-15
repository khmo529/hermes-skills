# -*- coding: utf-8 -*-
"""
wp-publisher 인증 테스트
- 인증 확인 → Draft 생성 → 삭제
- Secret 값은 출력 시 마스킹
"""
from __future__ import annotations
import os
import sys

# 스킬 디렉토리에서 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wp_publisher import WPPublisher


def mask(value: str) -> str:
    if not value:
        return "(미설정)"
    return value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"


def main() -> int:
    wp = WPPublisher()

    print("=" * 50)
    print("[wp-publisher] 인증 테스트 시작")
    print("=" * 50)

    # 1. 환경 설정 확인
    print("\n[1/3] 환경 설정 확인")
    print(f"  WP_URL      : {mask(wp.url)}")
    print(f"  WP_USER     : {mask(wp.user)}")
    print(f"  APP_PASSWORD: {'설정됨' if wp.password else '(미설정)'}")

    if not wp.password:
        print("\n❌ WP_APP_PASSWORD가 설정되지 않았습니다.")
        print("   .env 파일을 확인하세요.")
        return 1

    # 2. 헬스체크
    print("\n[2/3] 헬스체크 실행")
    health = wp.health_check()
    print(f"  API 접근    : {'✅' if health['api_ok'] else '❌'} {health['api_ok']}")
    print(f"  인증        : {'✅' if health['auth_ok'] else '❌'} {health['auth_ok']}")
    if health["user"]:
        print(f"  사용자      : {health['user']}")
    if health["error"]:
        print(f"  오류        : {health['error']}")

    if not health["auth_ok"]:
        print("\n❌ 인증에 실패했습니다.")
        print("   WP_USER / WP_APP_PASSWORD를 확인하세요.")
        return 1

    # 3. Draft 생성 테스트
    print("\n[3/3] Draft 생성 테스트")
    try:
        post_id = wp.create_draft(
            title="[wp-publisher] 인증 테스트",
            content="<p>이 게시글은 wp-publisher 인증 테스트용입니다. 삭제 예정입니다.</p>",
            category="general",
            tags=[],
        )
    except Exception as e:
        print(f"❌ Draft 생성 실패: {e}")
        return 1

    # 4. 생성된 게시글 확인
    try:
        post = wp.get_post(post_id)
        title = post.get("title", {}).get("rendered", "(제목 없음)")
        status = post.get("status", "unknown")
        print(f"  생성된 게시글: ID {post_id}, 상태={status}, 제목={title}")
    except Exception as e:
        print(f"⚠️ 게시글 조회 실패: {e}")

    # 5. 삭제
    print("\n[정리] 테스트 게시글 삭제")
    try:
        ok = wp.delete(post_id)
        if ok:
            print(f"  ✅ ID {post_id} 삭제 완료")
        else:
            print(f"  ⚠️ ID {post_id} 삭제 실패 (HTTP 코드 확인 필요)")
    except Exception as e:
        print(f"  ❌ 삭제 중 오류: {e}")

    print("\n" + "=" * 50)
    print("✅ 인증 테스트 완료")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
