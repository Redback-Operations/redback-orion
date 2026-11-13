"""Force ONNX Runtime onto the DirectML execution provider.

Ultralytics' ONNXBackend (8.4.x) only ever selects CUDA, CoreML or CPU
execution providers - it has no DirectML path. To run the ONNX people model on
a DX12 GPU (AMD / Intel) we wrap onnxruntime.InferenceSession so every session
Ultralytics builds is pinned to DmlExecutionProvider, with CPU as the per-op
fallback DirectML requires. Call enable_dml() once before YOLO() loads the model.
"""

from __future__ import annotations

_patched = False


def enable_dml() -> None:
    """Repin onnxruntime.InferenceSession to DirectML. Idempotent; raises with a
    fix hint if the DirectML build of onnxruntime is not the one installed."""
    global _patched
    if _patched:
        return

    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError(
            "CROWD_DEVICE=dml needs the DirectML build of onnxruntime:\n"
            "  pip install onnxruntime-directml"
        ) from exc

    if "DmlExecutionProvider" not in ort.get_available_providers():
        raise RuntimeError(
            "CROWD_DEVICE=dml but DmlExecutionProvider is unavailable "
            f"(providers: {ort.get_available_providers()}).\n"
            "Only the DirectML build may be installed - plain onnxruntime and "
            "onnxruntime-gpu share the same folder and shadow it:\n"
            "  pip uninstall -y onnxruntime onnxruntime-gpu onnxruntime-directml\n"
            "  pip install onnxruntime-directml"
        )

    _orig = ort.InferenceSession

    def _session(*args, **kwargs):
        kwargs["providers"] = ["DmlExecutionProvider", "CPUExecutionProvider"]
        kwargs.pop("provider_options", None)
        return _orig(*args, **kwargs)

    ort.InferenceSession = _session
    _patched = True
    print("[INFO] ONNX Runtime pinned to DmlExecutionProvider (DirectML GPU)")
