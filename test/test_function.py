from fastapi.testclient import TestClient
from main import app
import pytest


@pytest.fixture
def server():
    # TestClient'i bir fixture olarak döndürüyoruz
    return TestClient(app)

class TestAuth:
    def test_sign_up_succes(self,server):
        response =server.post("/user/sign/",json={"username":"Cihat","password":"DormLifeSever"})
        assert response.status_code == 201
        assert response.json() == {"message": "Login successful"}

    def test_sign_up_already_exists(self,server):
        response = server.post("/user/sign/",json={"username":"Cihat","password":"DormLifeSever"})
        assert response.status_code == 201
        print(response.json())
        assert response.json() == {"status_code": 400,"detail": "user name already exists","headers": "Not"
}

    def test_sign_up_least_characters_username(self,server):
        response = server.post("/user/sign/", json={"username": "ber", "password": "Abc.1234"})
        assert response.status_code == 201
        assert response.json() == {"status_code": 405,"detail": "Kullanıcı Adı Veya Şifresi 3 Karakterden Az Olamaz","headers": "Not"}

    def test_sign_up_least_characters_password(self, server):
        response = server.post("/user/sign/", json={"username": "berkehan", "password": "A"})
        assert response.status_code == 201
        assert response.json() == {"status_code": 405,"detail": "Kullanıcı Adı Veya Şifresi 3 Karakterden Az Olamaz","headers": "Not"}

    def test_login_success(self,server):
        response = server.post("/user/login/", json={"username": "Cihat", "password": "DormLifeSever"})
        status_code = response.json()
        assert status_code["status_code"] == 200

    def test_login_least_characters_username(self,server):
        response = server.post("/user/login/", json={"username": "Cih", "password": "DormLifeSever"})
        assert response.json() == {"status_code": 405,"detail": "Kullanıcı Adı Veya Şifresi 3 Karakterden Az Olamaz","headers": "Not"}

    def test_login_least_characters_password(self, server):
        response = server.post("/user/login/", json={"username": "Cihat", "password": "Do"})
        assert response.json() == {"status_code": 405, "detail": "Kullanıcı Adı Veya Şifresi 3 Karakterden Az Olamaz",
                                   "headers": "Not"}