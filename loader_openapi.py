from pathlib import Path
from typing import List, Dict, Any
import json
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader

def load_spec(api_path: Path) -> Dict[str, Any]:
    """Load and resolve an OpenAPI/Swagger spec using prance.

    Requires prance to be installed. All $ref references will be resolved.
    """
    from prance import ResolvingParser  # type: ignore

    parser = ResolvingParser(str(api_path))
    # prance exposes the resolved spec via `specification`
    return parser.specification  # type: ignore[return-value]


def format_schema(schema: Dict[str, Any], schema_name: str | None = None) -> str:
    """Convert a JSON schema to readable text."""
    lines = [f"Schema: {schema_name}"] if schema_name else []
    
    if "type" in schema:
        lines.append(f"Type: {schema['type']}")
    
    if "description" in schema:
        lines.append(f"Description: {schema['description']}")
    
    if "required" in schema:
        lines.append(f"Required fields: {', '.join(schema['required'])}")
    
    if "properties" in schema:
        lines.append("\nProperties:")
        for prop_name, prop_def in schema["properties"].items():
            prop_type = prop_def.get("type", "unknown")
            prop_desc = prop_def.get("description", "")
            required_mark = " (required)" if prop_name in schema.get("required", []) else ""
            lines.append(f"  - {prop_name} ({prop_type}){required_mark}: {prop_desc}")
            
            if "enum" in prop_def:
                lines.append(f"    Allowed values: {', '.join(map(str, prop_def['enum']))}")
            if "format" in prop_def:
                lines.append(f"    Format: {prop_def['format']}")
    
    return "\n".join(lines)


def format_endpoint(path: str, method: str, operation: Dict[str, Any], spec: Dict[str, Any]) -> str:
    """Convert an API endpoint to readable text."""
    lines = [
        f"Endpoint: {method.upper()} {path}",
        f"Operation ID: {operation.get('operationId', 'N/A')}",
    ]
    
    if "summary" in operation:
        lines.append(f"Summary: {operation['summary']}")
    
    if "description" in operation:
        lines.append(f"Description: {operation['description']}")
    
    if "tags" in operation:
        lines.append(f"Tags: {', '.join(operation['tags'])}")
    
    # Security
    if "security" in operation:
        lines.append("\nSecurity:")
        for sec in operation["security"]:
            for scheme_name in sec.keys():
                lines.append(f"  - {scheme_name}")

        # Inline security scheme details (explicit enrichment)
        if "components" in spec and "securitySchemes" in spec["components"]:
            all_schemes = spec["components"]["securitySchemes"]
            # Collect unique scheme names referenced by this operation
            referenced = []
            for sec in operation["security"]:
                for scheme_name in sec.keys():
                    if scheme_name in all_schemes and scheme_name not in referenced:
                        referenced.append(scheme_name)

            if referenced:
                lines.append("\nSecurity Scheme Details:")
                for scheme_name in referenced:
                    scheme_def = all_schemes[scheme_name]
                    scheme_text = format_security_scheme(scheme_name, scheme_def)
                    lines.append(_indent(scheme_text, 2))
    
    # Request body
    if "requestBody" in operation:
        req_body = operation["requestBody"]
        lines.append("\nRequest Body:")
        if req_body.get("required"):
            lines.append("  Required: Yes")
        
        if "content" in req_body:
            for content_type, content_def in req_body["content"].items():
                lines.append(f"  Content-Type: {content_type}")
                
                if "schema" in content_def:
                    schema_obj = content_def["schema"]
                    # With prance enforced, schema is expected to be fully resolved here.
                    if isinstance(schema_obj, dict):
                        schema_text = format_schema(schema_obj)
                        lines.append(f"  Schema: \n{_indent(schema_text, 4)}")
                
                if "examples" in content_def:
                    lines.append("  Examples:")
                    for ex_name, ex_def in content_def["examples"].items():
                        lines.append(f"    - {ex_name}: {ex_def.get('summary', '')}")
                        if "value" in ex_def:
                            ex_value = json.dumps(ex_def["value"], indent=2, ensure_ascii=False)
                            lines.append(_indent(ex_value, 6))
    
    # Responses
    if "responses" in operation:
        lines.append("\nResponses:")
        for status_code, response_def in operation["responses"].items():
            lines.append(f"  {status_code}: {response_def.get('description', 'N/A')}")
            
            if "content" in response_def:
                for content_type, content_spec in response_def["content"].items():
                    lines.append(f"    Content-Type: {content_type}")
                    if "schema" in content_spec:
                        schema = content_spec["schema"]
                        if "type" in schema:
                            lines.append(f"    Type: {schema['type']}")
                        if "format" in schema:
                            lines.append(f"    Format: {schema['format']}")
    
    return "\n".join(lines)


def _indent(text: str, spaces: int) -> str:
    """Indent each line of text by the specified number of spaces."""
    indent_str = " " * spaces
    return "\n".join(indent_str + line for line in text.split("\n"))


def format_security_scheme(name: str, scheme: Dict[str, Any]) -> str:
    """Format a single security scheme definition into readable text.

    Supports common OpenAPI security scheme fields: type, description, in, name,
    scheme (for http), bearerFormat (for http bearer), and oauth2 flows.
    """
    lines: List[str] = [f"Scheme: {name}"]
    lines.append(f"Type: {scheme.get('type', 'N/A')}")

    if scheme.get("description"):
        lines.append(f"Description: {scheme['description']}")
    if scheme.get("in"):
        lines.append(f"In: {scheme['in']}")
    if scheme.get("name"):
        lines.append(f"Name: {scheme['name']}")
    if scheme.get("scheme"):
        lines.append(f"HTTP Scheme: {scheme['scheme']}")
    if scheme.get("bearerFormat"):
        lines.append(f"Bearer Format: {scheme['bearerFormat']}")

    # OAuth2 flows
    flows = scheme.get("flows")
    if isinstance(flows, dict):
        lines.append("OAuth2 Flows:")
        for flow_name, flow_def in flows.items():
            lines.append(f"  - {flow_name}:")
            auth_url = flow_def.get("authorizationUrl")
            token_url = flow_def.get("tokenUrl")
            refresh_url = flow_def.get("refreshUrl")
            if auth_url:
                lines.append(f"      authorizationUrl: {auth_url}")
            if token_url:
                lines.append(f"      tokenUrl: {token_url}")
            if refresh_url:
                lines.append(f"      refreshUrl: {refresh_url}")
            scopes = flow_def.get("scopes")
            if isinstance(scopes, dict) and scopes:
                lines.append("      scopes:")
                for scope, desc in scopes.items():
                    lines.append(f"        - {scope}: {desc}")

    return "\n".join(lines)


class OpenAPIDocumentLoader(BaseLoader):
    """Loader for OpenAPI/Swagger specifications that produces structured documents.
    
    This loader parses OpenAPI specs using prance (for $ref resolution) and generates
    separate documents for API info, endpoints, schemas, and security schemes. It
    enriches endpoint documents with inline security scheme details for better RAG
    retrieval.
    
    Args:
        file_path: Path to the OpenAPI/Swagger JSON file.
    
    Example:
        ```python
        from pathlib import Path
        from openapi_loader import OpenAPIDocumentLoader
        
        loader = OpenAPIDocumentLoader(Path("api-doc/my-api.json"))
        documents = loader.load()
        ```
    """
    
    def __init__(self, file_path: Path):
        """Initialize the OpenAPI document loader.
        
        Args:
            file_path: Path to the OpenAPI/Swagger JSON file.
        """
        self.file_path = file_path
    
    def load(self) -> List[Document]:
        """Load and parse OpenAPI spec into structured documents.
        
        Returns:
            List of Document objects representing different parts of the API spec.
        """
        spec = load_spec(self.file_path)
        
        documents = []
        
        # 1. API Info
        if "info" in spec:
            info = spec["info"]
            info_text = f"API Title: {info.get('title', 'N/A')}\n"
            info_text += f"Version: {info.get('version', 'N/A')}\n"
            if "description" in info:
                info_text += f"Description: {info['description']}\n"
            
            if "servers" in spec:
                info_text += "\nServers:\n"
                for server in spec["servers"]:
                    info_text += f"  - {server.get('url', 'N/A')}\n"
            
            documents.append(
                Document(
                    page_content=info_text,
                    metadata={
                        "source": str(self.file_path),
                        "chunk_type": "info",
                        "path": "N/A",
                        "method": "N/A",
                    }
                )
            )
        
        # 2. Endpoints (paths)
        if "paths" in spec:
            for path, methods in spec["paths"].items():
                for method, operation in methods.items():
                    if not isinstance(operation, dict):
                        continue
                    
                    endpoint_text = format_endpoint(path, method, operation, spec)
                    documents.append(
                        Document(
                            page_content=endpoint_text,
                            metadata={
                                "source": str(self.file_path),
                                "chunk_type": "endpoint",
                                "path": path,
                                "method": method.upper(),
                                "operation_id": operation.get("operationId", "N/A"),
                            }
                        )
                    )
        
        # 3. Schemas/Components
        if "components" in spec and "schemas" in spec["components"]:
            for schema_name, schema_def in spec["components"]["schemas"].items():
                schema_text = format_schema(schema_def, schema_name)
                documents.append(
                    Document(
                        page_content=schema_text,
                        metadata={
                            "source": str(self.file_path),
                            "chunk_type": "schema",
                            "schema_name": schema_name,
                            "path": "N/A",
                            "method": "N/A",
                        }
                    )
                )
        
        # 4. Security schemes
        if "components" in spec and "securitySchemes" in spec["components"]:
            sec_text = "Security Schemes:\n"
            for scheme_name, scheme_def in spec["components"]["securitySchemes"].items():
                sec_text += f"\n{scheme_name}:\n"
                sec_text += f"  Type: {scheme_def.get('type', 'N/A')}\n"
                if "description" in scheme_def:
                    sec_text += f"  Description: {scheme_def['description']}\n"
                if "in" in scheme_def:
                    sec_text += f"  Location: {scheme_def['in']}\n"
                if "name" in scheme_def:
                    sec_text += f"  Name: {scheme_def['name']}\n"
            
            documents.append(
                Document(
                    page_content=sec_text,
                    metadata={
                        "source": str(self.file_path),
                        "chunk_type": "security",
                        "path": "N/A",
                        "method": "N/A",
                    }
                )
            )
        return documents

if __name__ == "__main__":
    loader = OpenAPIDocumentLoader(Path(__file__).parent.joinpath("specs", "thoughtworks-api.json"))
    docs = loader.load()
    for doc in docs:
        print(f"--- Document Chunk ({doc.metadata['chunk_type']}) ---\n{doc.page_content}\n")