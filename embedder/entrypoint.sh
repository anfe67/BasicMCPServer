#!/usr/bin/env bash
set -euo pipefail

# --- locate llama-server (path varies between image tags) ---
LLAMA_BIN="$(command -v llama-server || true)"
if [[ -z "${LLAMA_BIN}" ]]; then
  for cand in /usr/local/bin/llama-server /usr/bin/llama-server \
              /app/llama-server /build/bin/llama-server \
              /usr/src/app/build/bin/llama-server; do
    [[ -x "${cand}" ]] && LLAMA_BIN="${cand}" && break
  done
fi
if [[ -z "${LLAMA_BIN}" ]]; then
  LLAMA_BIN="$(find / -xdev -type f -name 'llama-server' 2>/dev/null | head -n1 || true)"
fi
if [[ -z "${LLAMA_BIN}" || ! -x "${LLAMA_BIN}" ]]; then
  echo "[embedder] ERROR: llama-server binary not found in this image" >&2
  exit 1
fi
echo "[embedder] Using: ${LLAMA_BIN}"

# --- model download (first start only) ---
MODEL_DIR="/models"
MODEL_FILE="${MODEL_DIR}/${EMBED_MODEL_FILE}"

if [[ ! -f "${MODEL_FILE}" ]]; then
  echo "[embedder] Downloading ${EMBED_HF_URL} ..."
  mkdir -p "${MODEL_DIR}"
  tmp="${MODEL_FILE}.part"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 --retry-delay 5 -o "$tmp" "$EMBED_HF_URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$tmp" "$EMBED_HF_URL"
  else
    echo "[embedder] ERROR: neither curl nor wget available in image" >&2
    exit 1
  fi
  mv "$tmp" "$MODEL_FILE"
  echo "[embedder] Model ready: ${MODEL_FILE}"
fi

exec "${LLAMA_BIN}" \
  --host 0.0.0.0 \
  --port 8080 \
  --model "${MODEL_FILE}" \
  --embedding \
  --ctx-size "${EMBED_CTX_SIZE:-8192}" \
  --threads "${THREADS:-0}"
