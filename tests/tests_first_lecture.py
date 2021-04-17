from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timedelta
from ..main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_post_method():
    response = client.get(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}


@pytest.mark.parametrize("password, password_hash, status_code",
                         [('haslo',
                           ('013c6889f799cd986a735118e1888727d1435f7f623d05d58'
                            'c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316'
                            'b2d13b36804080c44aa6198c533215'),
                           204), ('', '', 401),
                          ('haslo', 'asdasda', 401)])
def test_auth_method(password, password_hash, status_code):
    response = client.get(
        f"/auth?password={password}&password_hash={password_hash}")
    assert response.status_code == status_code


def test_register():
    params = {
        "name": "Jan",
        "surname": "Nowak"
    }
    response = client.post(f"/register", json=params)
    assert response.status_code == 201
    print(response.json())
    today = datetime.now()
    name_len = len(params['name'])
    surname_len = len(params['surname'])
    vaccination_date = today + timedelta(days=surname_len + name_len)
    assert response.json() == {
        "id": 1,
        "name": "Jan",
        "surname": "Nowak",
        "register_date": f"{today.strftime('%Y-%m-%d')}",
        "vaccination_date": f"{vaccination_date.strftime('%Y-%m-%d')}"
    }


@pytest.mark.parametrize("id, status_code",
                         [('1', 200), ('-1', 400), ('921834981274', 404)])
def test_get_patient_by_id(id, status_code):
    response = client.get(f"/patient/{id}")
    assert response.status_code == status_code
