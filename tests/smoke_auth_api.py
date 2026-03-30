from datetime import datetime
import argparse

import httpx


def run(base_url: str, password: str) -> int:
    email = f"smoke_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    signup_payload = {
        "name": "Smoke Test",
        "email": email,
        "password": password,
        "confirm_password": password,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            health = client.get(f"{base_url}/health")
            print(f"[health] status={health.status_code} body={health.text}")
            if health.status_code != 200:
                return 1

            signup = client.post(f"{base_url}/api/v1/auth/signup", json=signup_payload)
            print(f"[signup] status={signup.status_code} body={signup.text}")
            if signup.status_code != 201:
                return 1

            login = client.post(
                f"{base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
            )
            print(f"[login] status={login.status_code} body={login.text}")
            if login.status_code != 200:
                return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {exc}")
        return 1

    print("[ok] smoke auth test passed")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test for signup/login endpoints.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8001", help="Backend base URL.")
    parser.add_argument("--password", default="Secret123", help="Password used by the smoke user.")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(run(arguments.base_url, arguments.password))
