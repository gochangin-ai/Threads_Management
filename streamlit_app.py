import streamlit as st
import requests
import json
from datetime import datetime


class ThreadsFollowManager:
    def __init__(self, access_token):
        self.access_token = access_token
        self.api_base_url = "https://www.threads.net/api/v1"
        self.following_list = set()
        self.load_following_list()

    def load_following_list(self):
        try:
            with open('following_list.json', 'r') as f:
                self.following_list = set(json.load(f))
        except FileNotFoundError:
            st.warning("팔로잉 목록 파일이 없습니다. 새로운 목록을 생성합니다.")

    def save_following_list(self):
        with open('following_list.json', 'w') as f:
            json.dump(list(self.following_list), f)

    def get_following(self):
        url = f"{self.api_base_url}/users/following"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return set(user['id'] for user in response.json()['data'])
        else:
            st.error(f"팔로잉 목록을 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return set()

    def check_unfollowed_users(self):
        current_following = self.get_following()
        unfollowed_users = self.following_list - current_following

        if unfollowed_users:
            st.write("언팔로우한 사용자:")
            for user_id in unfollowed_users:
                st.write(f"- {user_id}")
            return unfollowed_users
        else:
            st.info("언팔로우한 사용자가 없습니다.")
            return set()

    def unfollow_users(self, user_ids):
        for user_id in user_ids:
            url = f"{self.api_base_url}/friendships/destroy/{user_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                st.success(f"{user_id} 사용자 언팔로우 성공")
                self.following_list.remove(user_id)
            else:
                st.error(f"{user_id} 사용자 언팔로우 실패. 상태 코드: {response.status_code}")

    def update_following_list(self):
        self.following_list = self.get_following()
        self.save_following_list()
        st.success("팔로잉 목록이 업데이트되었습니다.")


def main():
    st.title("Threads 팔로우 관리자")

    access_token = st.text_input("Threads API 액세스 토큰을 입력하세요:", type="password")

    if access_token:
        manager = ThreadsFollowManager(access_token)

        option = st.selectbox(
            "작업을 선택하세요:",
            ("언팔로우한 사용자 확인", "언팔로우한 사용자 자동 언팔로우", "팔로잉 목록 업데이트")
        )

        if st.button("실행"):
            if option == "언팔로우한 사용자 확인":
                manager.check_unfollowed_users()
            elif option == "언팔로우한 사용자 자동 언팔로우":
                unfollowed_users = manager.check_unfollowed_users()
                if unfollowed_users:
                    if st.button("이 사용자들을 언팔로우하시겠습니까?"):
                        manager.unfollow_users(unfollowed_users)
            elif option == "팔로잉 목록 업데이트":
                manager.update_following_list()
    else:
        st.warning("액세스 토큰을 입력해주세요.")


if __name__ == "__main__":
    main()