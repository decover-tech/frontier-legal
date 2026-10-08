"""Small REST adapters. No SDK required; no tool execution or implicit retries."""
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request

KEYS = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}


class ProviderError(RuntimeError):
    """Safe diagnostic without request headers, keys, or provider error body."""


def tls_context():
    if os.environ.get("SSL_CERT_FILE"):
        return ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def request_spec(provider, model, messages, max_tokens):
    if provider == "openai":
        return "https://api.openai.com/v1/responses", {
            "model": model, "input": messages, "max_output_tokens": max_tokens,
            "store": False,
        }
    if provider == "anthropic":
        return "https://api.anthropic.com/v1/messages", {
            "model": model, "messages": messages, "max_tokens": max_tokens,
        }
    if provider == "gemini":
        return "https://generativelanguage.googleapis.com/v1beta/models/" + urllib.parse.quote(model, safe="") + ":generateContent", {
            "contents": [{"role": "user", "parts": [{"text": m["content"]}]} for m in messages],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
    raise ValueError("Unsupported provider")


def normalize(provider, response, requested_model):
    if provider == "openai":
        text = "".join(part.get("text", "") for item in response.get("output", [])
                       if item.get("type") == "message"
                       for part in item.get("content", []) if part.get("type") == "output_text")
        usage = response.get("usage", {})
        tokens = {"input": usage.get("input_tokens"), "output": usage.get("output_tokens")}
        stop = response.get("status")
    elif provider == "anthropic":
        text = "".join(p.get("text", "") for p in response.get("content", []) if p.get("type") == "text")
        usage = response.get("usage", {})
        input_count = usage.get("input_tokens")
        if input_count is not None:
            input_count += usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
        tokens = {"input": input_count, "output": usage.get("output_tokens")}
        stop = response.get("stop_reason")
    else:
        candidates = response.get("candidates", [])
        first = candidates[0] if candidates else {}
        text = "".join(p.get("text", "") for p in first.get("content", {}).get("parts", []) if not p.get("thought"))
        usage = response.get("usageMetadata", {})
        out = usage.get("candidatesTokenCount")
        if out is not None:
            out += usage.get("thoughtsTokenCount", 0)
        tokens = {"input": usage.get("promptTokenCount"), "output": out}
        stop = first.get("finishReason", response.get("promptFeedback", {}).get("blockReason"))
    return {"completion": text, "resolved_model": response.get("model", response.get("modelVersion", requested_model)),
            "usage": usage, "tokens": tokens, "stop_reason": stop,
            "response_id": response.get("id", response.get("responseId"))}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def generate(provider, model, messages, max_tokens=1024, timeout=45):
    key = os.environ.get(KEYS[provider])
    if provider == "gemini":
        key = key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ProviderError("MISSING_CREDENTIAL:" + KEYS[provider])
    url, body = request_spec(provider, model, messages, max_tokens)
    headers = {"Content-Type": "application/json"}
    if provider == "openai":
        headers["Authorization"] = "Bearer " + key
    elif provider == "anthropic":
        headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
    else:
        headers["x-goog-api-key"] = key
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=tls_context()))
        with opener.open(req, timeout=timeout) as result:
            data = json.load(result)
        if not isinstance(data, dict) or data.get("error") is not None:
            raise ProviderError("INVALID_PROVIDER_RESPONSE")
        return normalize(provider, data, model)
    except urllib.error.HTTPError as error:
        raise ProviderError("HTTP_" + str(error.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ProviderError("NETWORK_OR_TLS_ERROR") from None
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ProviderError("INVALID_PROVIDER_RESPONSE") from None
