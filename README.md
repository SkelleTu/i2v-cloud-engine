# I2V Cloud Engine

Backend de Image-to-Video para executar modelos I2V em nuvem e ser consumido pelo LibertyAI.

## Objetivo

O repositório é independente do `LibertyAI`. Ele será importado/deployado na Replit e expõe uma API HTTP para geração de vídeo.

Modelo principal configurado: `Wan-AI/Wan2.2-I2V-A14B-Diffusers`.

## Arquitetura

`LibertyAI (PC) -> HTTPS API -> I2V Cloud Engine (Replit) -> backend de inferência -> MP4`

O cliente local nunca precisa carregar o modelo pesado.

## Configuração

Variáveis de ambiente:

- `HF_TOKEN`: token Hugging Face, somente como Secret da Replit.
- `I2V_MODEL`: modelo a usar. Padrão Wan 2.2 I2V A14B.
- `I2V_BACKEND`: `auto`, `diffusers` ou `huggingface`.
- `MAX_FILE_MB`: limite de upload, padrão 20.

Em `auto`, o serviço tenta inferência local via Diffusers quando CUDA está disponível; sem CUDA, usa o endpoint da Hugging Face como fallback.

## API

- `GET /` informações básicas
- `GET /health` diagnóstico
- `GET /api/models` modelos configurados/disponíveis
- `POST /api/generate` multipart com `image`, `prompt`, `negative_prompt`, `num_frames`, `num_inference_steps`, `guidance_scale`

A resposta de `/api/generate` é um MP4 diretamente.

## Replit

Importe este repositório como um projeto Python. O processo web deve escutar em `0.0.0.0` e usar a porta fornecida por `PORT`.

Nunca coloque `HF_TOKEN` no código ou em arquivos versionados.
