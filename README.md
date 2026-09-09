# 64 Squares Strategy

Corporate speaking website + AWS-native RAG advisor for Prasanna Rao.

## Architecture

Frontend:
- GitHub Pages
- plain HTML/CSS/JavaScript

RAG backend:
- AWS Lambda Function URL
- Amazon Bedrock Knowledge Bases
- Amazon S3 source documents
- Amazon S3 Vectors vector store
- Amazon Titan Text Embeddings V2
- Amazon Nova Lite for response generation

## Why this architecture

It avoids an always-on OpenSearch or Aurora vector database. The corpus is intentionally curated around speaker credibility, session IP, decision frameworks, formats, FAQs, and discovery questions.

## Repository structure

- `index.html` — landing page
- `css/chatbot.css` — chatbot UI
- `js/chatbot.js` — browser chat logic
- `backend/app.py` — Lambda RAG endpoint
- `knowledge/` — source-of-truth Markdown used by Bedrock
- `template.yaml` — AWS SAM / CloudFormation infrastructure
- `scripts/deploy.sh` — deploy stack, upload knowledge, start ingestion
- `scripts/configure-frontend.sh` — insert the deployed Lambda URL

## AWS deployment

Requirements:
- AWS CLI authenticated to the target account
- AWS SAM CLI
- permission to create IAM, Lambda, S3, S3 Vectors, and Bedrock resources
- Bedrock model access for Titan Text Embeddings V2 and Amazon Nova Lite in the selected Region

Default Region: `us-west-2`.

```bash
./scripts/deploy.sh
```

The script prints the Lambda Function URL. Then run:

```bash
./scripts/configure-frontend.sh "https://YOUR_FUNCTION_URL.lambda-url.us-west-2.on.aws/"
git add .
git commit -m "Connect AWS RAG advisor"
git push
```

## Updating knowledge

Edit files under `knowledge/`, sync them to the knowledge bucket, and start a new Bedrock ingestion job.

## Guardrails already in the code

- factual claims should come from retrieved sources
- no invented clients, testimonials, prices, or chess games
- one discovery question at a time
- max 1,200-character visitor prompt
- Lambda reserved concurrency capped at 2
- no conversation database
- CORS restricted to the configured website origin
- Risk Lab explicitly treated as an illustrative teaching tool

## Cost note

Lambda and the public Function URL are serverless. Bedrock embeddings and generation are usage-priced, and S3/S3 Vectors are usage-priced. This architecture is designed to be inexpensive at small traffic, not to promise permanent $0 AWS spend.
