from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "deploy" / "webhook-deployment.yaml",
    ROOT / "deploy" / "telegram-webhook-deploy.yaml",
]


def test_ingress_rewrite_target_uses_first_capture_group():
    for file_path in FILES:
        text = file_path.read_text(encoding="utf-8")
        assert "path: /webhook/(.*)" in text
        assert "nginx.ingress.kubernetes.io/rewrite-target: /$2" not in text
        assert "nginx.ingress.kubernetes.io/rewrite-target: /$1" in text

