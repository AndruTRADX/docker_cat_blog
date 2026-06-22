import subprocess
import time
import urllib.request
import urllib.error


def test_backend_builds():
    """Verifica que la imagen Docker del backend se construye sin errores."""
    result = subprocess.run(
        ["docker", "build", "-t", "backend:test", "."],
        cwd=".",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"docker build falló:\n{result.stderr}"


def test_backend_starts_and_responds():
    """Levanta el contenedor del backend y verifica que responde en /."""
    subprocess.run(
        ["docker", "run", "-d", "--rm", "--name", "back_test", "-p", "5001:5000", "backend:test"],
        check=True,
    )
    time.sleep(3)

    try:
        with urllib.request.urlopen("http://localhost:5001", timeout=5) as resp:
            assert resp.status == 200, f"Se esperaba 200, se obtuvo {resp.status}"
    except urllib.error.HTTPError as e:
        # 4xx también significa que el server está vivo
        assert e.code < 500, f"El servidor respondió con error {e.code}"
    finally:
        subprocess.run(["docker", "stop", "back_test"], check=False)


def test_backend_image_exists_after_build():
    """Confirma que la imagen queda registrada en Docker después del build."""
    result = subprocess.run(
        ["docker", "image", "inspect", "backend:test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "La imagen backend:test no existe en Docker"