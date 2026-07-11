import requests
from requests import Response
from requests.exceptions import (
    ConnectionError,
    JSONDecodeError,
    RequestException,
    Timeout,
)

from app.exceptions import LLMGenerationError
from app.llm.base_llm import BaseLLM


class OllamaLLM(BaseLLM):
    """LLM provider backed by a local Ollama server."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        """Generate a response using Ollama."""

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=self._timeout,
            )

            self._raise_for_http_error(response)

            response_json = response.json()

            generated_text = response_json.get("response")

            if not isinstance(generated_text, str):
                raise LLMGenerationError(
                    "Ollama response does not contain a valid " "'response' field."
                )

            return generated_text

        except Timeout as exc:
            raise LLMGenerationError("The Ollama request timed out.") from exc

        except ConnectionError as exc:
            raise LLMGenerationError("Could not connect to the Ollama server.") from exc

        except JSONDecodeError as exc:
            raise LLMGenerationError("Ollama returned invalid JSON.") from exc

        except RequestException as exc:
            raise LLMGenerationError(
                "Unexpected HTTP error while contacting Ollama."
            ) from exc

    @staticmethod
    def _raise_for_http_error(response: Response) -> None:
        """Translate HTTP status codes into application errors."""

        if response.status_code == 404:
            raise LLMGenerationError("Requested Ollama model was not found.")

        if response.status_code >= 400:
            raise LLMGenerationError(f"Ollama returned HTTP {response.status_code}.")
