import json
import os
import boto3

client = boto3.client("bedrock-agent-runtime")
KB_ID = os.environ["KNOWLEDGE_BASE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "https://praschess.github.io")

PROMPT_TEMPLATE = """You are the 64 Squares Strategy assistant for Prasanna Rao's corporate speaking and workshop business.

Your job is to help a visitor:
1. understand the decision frameworks in the retrieved material,
2. identify the most relevant session for their team,
3. understand what a workshop or keynote would look like,
4. learn about Prasanna's chess and business background,
5. move toward a speaking inquiry when there is a clear fit.

Rules:
- Ground factual claims in the retrieved sources.
- Never invent clients, testimonials, prices, employers, achievements, or chess games.
- If the retrieved material does not support a factual answer, say that the site does not have that information yet.
- Keep most answers concise: 2-5 short paragraphs or a compact set of bullets.
- If the visitor appears to be evaluating an event, ask at most ONE useful follow-up question at a time.
- Recommend sessions based on the visitor's business problem, not merely their job title.
- Do not claim the Risk Lab is a validated scientific, financial, or investment model.
- Do not provide investment, legal, or medical advice.
- When appropriate, end with one concrete next action.

Retrieved source material:
$search_results$

$output_format_instructions$
"""

def response(status, body):
    return {"statusCode": status, "headers": {"content-type": "application/json", "cache-control": "no-store", "access-control-allow-origin": ALLOWED_ORIGIN, "access-control-allow-headers": "content-type", "access-control-allow-methods": "POST,OPTIONS"}, "body": json.dumps(body)}

def handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return response(204, {})
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON."})
    message = str(payload.get("message", "")).strip()
    session_id = payload.get("sessionId")
    if not message:
        return response(400, {"error": "Message is required."})
    if len(message) > 1200:
        return response(400, {"error": "Please keep the question under 1,200 characters."})
    request = {"input": {"text": message}, "retrieveAndGenerateConfiguration": {"type": "KNOWLEDGE_BASE", "knowledgeBaseConfiguration": {"knowledgeBaseId": KB_ID, "modelArn": MODEL_ARN, "retrievalConfiguration": {"vectorSearchConfiguration": {"numberOfResults": 5}}, "generationConfiguration": {"promptTemplate": {"textPromptTemplate": PROMPT_TEMPLATE}, "inferenceConfig": {"textInferenceConfig": {"maxTokens": 550, "temperature": 0.2, "topP": 0.9}}}}}}
    if session_id:
        request["sessionId"] = session_id
    try:
        result = client.retrieve_and_generate(**request)
    except Exception as exc:
        print("Bedrock error:", repr(exc))
        return response(500, {"error": "The advisor is temporarily unavailable."})
    citations = []
    for citation in result.get("citations", []):
        for ref in citation.get("retrievedReferences", []):
            uri = ref.get("location", {}).get("s3Location", {}).get("uri")
            if uri and uri not in citations:
                citations.append(uri)
    return response(200, {"answer": result.get("output", {}).get("text", ""), "sessionId": result.get("sessionId"), "sources": citations[:5]})
