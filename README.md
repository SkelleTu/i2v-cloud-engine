# I2V Cloud Engine

Backend e interface leves de Image-to-Video para rodar em nuvem e ser consumidos pelo LibertyAI.

## Importação direta na Replit

Este repositório foi preparado para ser importado como projeto Python **sem precisar do Replit Agent para montar a aplicação**.

O arquivo `.replit` já aponta para o launcher. As dependências ficam em `requirements.txt`.

Depois da importação, configure somente as variáveis de ambiente/Secrets:

- `HF_TOKEN`: seu token da Hugging Face.
- `I2V_API_KEY`: chave privada que o LibertyAI usará para chamar esta Engine. Pode ser qualquer segredo forte criado por você.
- `I2V_MODEL`: opcional. Padrão `Wan-AI/Wan2.2-I2V-A14B-Diffusers`.
- `I2V_BACKEND`: opcional. Padrão `huggingface`. Outros valores: `auto` ou `diffusers`.
- `MAX_FILE_MB`: opcional. Padrão 20 MB.

## O que já vem pronto

- interface web leve para testar Image-to-Video;
- upload de PNG/JPEG/WebP;
- prompt e negative prompt;
- seleção de modelo;
- frames, steps e guidance;
- geração e reprodução do MP4;
- download do resultado;
- endpoint de saúde com diagnóstico de CUDA/GPU;
- API HTTP para o LibertyAI;
- autenticação opcional por `x-i2v-api-key`;
- CORS para integração com cliente local.

## Endpoints

- `/` interface da Engine
- `/api` informações do serviço
- `/health` diagnóstico do runtime
- `/api/models` catálogo de modelos
- `/api/generate` geração multipart com imagem e parâmetros
- `/docs` documentação automática do FastAPI

## Arquitetura

`LibertyAI no PC -> HTTPS -> I2V Cloud Engine -> backend de inferência -> MP4`

O cliente local não precisa carregar o modelo pesado.

## Modelo

O modelo principal configurado é o Wan 2.2 I2V A14B do Hugging Face. Os pesos não são versionados neste GitHub porque são grandes demais para um repositório Git comum. Quando o backend usa Hugging Face, o modelo é executado pelo provedor de inferência configurado pelo `HF_TOKEN`.

O modo `diffusers` fica disponível para um runtime com GPU/CUDA compatível e armazenamento suficiente, sem exigir alterações no projeto.

## Segurança

Nunca coloque tokens no código. No deployment da Replit, use Secrets/Environment Variables.

A `I2V_API_KEY` é a credencial usada futuramente pelo `LibertyAI` para acessar a Engine. O token `HF_TOKEN` permanece somente no servidor.
