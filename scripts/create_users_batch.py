import httpx

# URL da sua API
base_url = "http://127.0.0.1:8000"

# Lista de usuários para serem criados
users = [
    {"name": "Alice", "username": "alice", "email": "alice@example.com", "password": "alice123"},
    {"name": "Bob", "username": "bob", "email": "bob@example.com", "password": "bob456"},
    {"name": "Charlie", "username": "charlie", "email": "charlie@example.com", "password": "charlie789"},
    {"name": "David", "username": "david", "email": "david@example.com", "password": "david101"},
    {"name": "Eve", "username": "eve", "email": "eve@example.com", "password": "eve202"},
    {"name": "Frank", "username": "frank", "email": "frank@example.com", "password": "frank303"},
    {"name": "Grace", "username": "grace", "email": "grace@example.com", "password": "grace404"},
    {"name": "Hank", "username": "hank", "email": "hank@example.com", "password": "hank505"},
    {"name": "Ivy", "username": "ivy", "email": "ivy@example.com", "password": "ivy606"},
    {"name": "Jack", "username": "jack", "email": "jack@example.com", "password": "jack707"},
    {"name": "Karen", "username": "karen", "email": "karen@example.com", "password": "karen808"},
    {"name": "Leo", "username": "leo", "email": "leo@example.com", "password": "leo909"},
    {"name": "Mia", "username": "mia", "email": "mia@example.com", "password": "mia010"},
    {"name": "Nina", "username": "nina", "email": "nina@example.com", "password": "nina111"},
    {"name": "Oscar", "username": "oscar", "email": "oscar@example.com", "password": "oscar121"}
]



def create_users_batch():
    with httpx.Client() as client:
        for user in users:
            response = client.post(f"{base_url}/user/", json=user)
            if response.status_code == 200:
                print(f"Usuário {user['name']} criado com sucesso: {response.json()}")
            else:
                print(f"Falha ao criar o usuário {user['name']}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    create_users_batch()
