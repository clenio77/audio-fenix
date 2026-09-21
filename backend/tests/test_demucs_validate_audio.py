"""
Tests for DemucsEngine.validate_audio format allowlist.

Upload/AudioValidator advertise AAC; Demucs must accept the same extensions
or every .aac upload fails after enqueueing.
"""
import pytest

from model.demucs_engine import DemucsEngine


@pytest.fixture
def engine():
    return DemucsEngine()


class TestDemucsValidateAudioAllowlist:
    def test_aac_is_accepted(self, engine, temp_dir):
        """Regression: .aac passed upload then was rejected by Demucs."""
        path = temp_dir / "song.aac"
        path.write_bytes(b"fake-aac-content")

        ok, err = engine.validate_audio(path)

        assert ok is True
        assert err == ""

    def test_m4a_and_mp3_still_accepted(self, engine, temp_dir):
        for name in ("track.m4a", "track.mp3", "track.wav", "track.flac", "track.ogg"):
            path = temp_dir / name
            path.write_bytes(b"x")
            ok, err = engine.validate_audio(path)
            assert ok is True, f"{name} should be accepted: {err}"

    def test_unsupported_extension_rejected(self, engine, temp_dir):
        path = temp_dir / "notes.mid"
        path.write_bytes(b"x")

        ok, err = engine.validate_audio(path)

        assert ok is False
        assert "Formato não suportado" in err

    def test_missing_file_rejected(self, engine, temp_dir):
        path = temp_dir / "missing.aac"

        ok, err = engine.validate_audio(path)

        assert ok is False
        assert "não encontrado" in err.lower()

    def test_empty_file_rejected(self, engine, temp_dir):
        path = temp_dir / "empty.aac"
        path.write_bytes(b"")

        ok, err = engine.validate_audio(path)

        assert ok is False
        assert "vazio" in err.lower()
