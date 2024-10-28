from locust import HttpUser, task, between
import random
from faker import Faker

fake = Faker()


class FastAPITestUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def on_start(self):
        self.email = f"{fake.email().split(
            '@')[0]}_{random.randint(1, 100000)}@test.com"
        self.password = "testpassword"
        self.sign_up()
        self.login()

    def sign_up(self):
        self.client.post("/api/v1/test", json={
            "name": fake.name(),
            "email": self.email,
            "password": self.password
        })

    def login(self):
        response = self.client.post("/api/v1/test/login", json={
            "email": self.email,
            "password": self.password
        })

        if response.status_code == 200:
            self.access_token = response.json()["access_token"]

    @task
    def test_authenticated_endpoint(self):
        if hasattr(self, "access_token"):
            headers = {"Authorization": f"Bearer {self.access_token}"}
            self.client.get("/api/v1/test/protected-endpoint", headers=headers)
