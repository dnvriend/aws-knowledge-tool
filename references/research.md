# AWS Knowledge MCP Server Research

**Date**: 2025-11-20
**Researcher**: Dennis Vriend
**Purpose**: Investigate AWS Knowledge MCP Server API capabilities for CLI tool development

---

## Executive Summary

The AWS Knowledge MCP Server is a **remote MCP server** that provides programmatic access to AWS documentation, regional availability data, and service information. It **only supports MCP protocol** (JSON-RPC 2.0 over HTTP) and does **not expose a traditional REST API**.

**Key Facts**:
- **Endpoint**: `https://knowledge-mcp.global.api.aws`
- **Protocol**: MCP (Model Context Protocol) via JSON-RPC 2.0
- **Authentication**: None required (public, rate-limited)
- **Transport**: HTTP
- **No Traditional REST API**: Requires MCP client implementation

---

## MCP Server Details

### Connection Information

| Property | Value |
|----------|-------|
| **Server URL** | `https://knowledge-mcp.global.api.aws` |
| **Protocol** | Model Context Protocol (MCP) |
| **Transport** | HTTP (JSON-RPC 2.0) |
| **Authentication** | None (public access) |
| **Rate Limiting** | Yes (AWS-managed) |
| **Framework** | FastMCP (Python) |
| **Hosting** | AWS-managed (likely Lambda + API Gateway) |

### Architecture

```
┌─────────────┐         MCP Protocol          ┌──────────────────────┐
│             │   (JSON-RPC 2.0 over HTTP)   │                      │
│  CLI Tool   │ ────────────────────────────> │  AWS Knowledge MCP   │
│  (Python)   │                               │  Server (Remote)     │
│             │ <──────────────────────────── │                      │
└─────────────┘                               └──────────────────────┘
                                                        │
                                                        │ Indexes
                                                        ▼
                                              ┌──────────────────────┐
                                              │  AWS Documentation   │
                                              │  AWS Services Data   │
                                              │  Regional Info       │
                                              │  CloudFormation      │
                                              └──────────────────────┘
```

---

## Available Tools (MCP Commands)

The AWS Knowledge MCP Server exposes **5 tools** that can be called via MCP protocol:

### 1. `aws___list_regions`

**Purpose**: Retrieve a list of all AWS regions with their identifiers and names.

**Parameters**: None

**Returns**: List of regions with:
- `region_id`: Region code (e.g., 'us-east-1')
- `region_long_name`: Human-friendly name (e.g., 'US East (N. Virginia)')

**Use Cases**:
- Infrastructure planning for global deployments
- Region validation before API calls
- Complete AWS regional inventory

---

### 2. `aws___get_regional_availability`

**Purpose**: Check availability of AWS products, APIs, and CloudFormation resources across regions.

**Parameters**:
- `region` (required): Target AWS region code (e.g., 'us-east-1', 'eu-west-1')
- `resource_type` (required): Type of resource
  - `'product'`: AWS products (services and features)
  - `'api'`: SDK service APIs
  - `'cfn'`: CloudFormation resources
- `filters` (optional): List of specific resources to check
- `next_token` (optional): Pagination token (when no filters specified)

**Filter Formats**:
- **Products**: `['AWS Lambda', 'Amazon S3', 'Latency-Based Routing']`
- **APIs** (API level): `['Athena+UpdateNamedQuery', 'IAM+GetSSHPublicKey']`
- **APIs** (Service level): `['EC2', 'ACM PCA']`
- **CloudFormation**: `['AWS::EC2::Instance', 'AWS::Lambda::Function']`

**Returns**: List of resources with availability status:
- `'isAvailableIn'`: Resource is available
- `'isNotAvailableIn'`: Resource is not available
- `'isPlannedIn'`: Resource is planned
- `'Not Found'`: Invalid resource identifier

**Use Cases**:
- Pre-deployment validation
- Architecture planning for multi-region deployments
- Regional capability comparison

---

### 3. `aws___search_documentation`

**Purpose**: Search AWS documentation using the official AWS Documentation Search API.

**Parameters**:
- `search_phrase` (required): Search query string
- `limit` (optional): Maximum number of results to return

**Returns**: Search results with:
- `rank_order`: Relevance ranking (lower = more relevant)
- `url`: Documentation page URL
- `title`: Page title
- `context`: Brief excerpt or summary

**Search Tips**:
- Use specific technical terms (e.g., "S3 bucket versioning")
- Include service names to narrow results
- Use quotes for exact phrase matching (e.g., "AWS Lambda function URLs")
- Include abbreviations and alternative terms

**Sources Searched**:
- AWS Documentation
- AWS Blog
- AWS Solutions Library
- Getting Started with AWS
- AWS Architecture Center
- AWS Prescriptive Guidance

---

### 4. `aws___read_documentation`

**Purpose**: Fetch and convert an AWS documentation page to markdown format.

**Parameters**:
- `url` (required): URL of AWS documentation page
- `start_index` (optional): Starting character index for pagination
- `max_length` (optional): Maximum characters to return

**URL Requirements**:
- Must be from `docs.aws.amazon.com` or `aws.amazon.com` domain

**Example URLs**:
- `https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html`
- `https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html`
- `https://aws.amazon.com/about-aws/whats-new/2023/02/aws-telco-network-builder/`
- `https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/`
- `https://aws.amazon.com/blogs/developer/make-the-most-of-community-resources-for-aws-sdks-and-tools/`

**Returns**: Markdown-formatted content with:
- Preserved headings and structure
- Code blocks for examples
- Lists and tables in markdown format

**Pagination**: For long documents, make multiple calls with different `start_index` values.

---

### 5. `aws___recommend`

**Purpose**: Get content recommendations for related AWS documentation pages.

**Parameters**:
- `url` (required): URL of AWS documentation page (must be from `docs.aws.amazon.com`)

**Returns**: Four recommendation categories:
1. **Highly Rated**: Popular pages within the same AWS service
2. **New**: Recently added pages (useful for finding new features)
3. **Similar**: Pages covering similar topics
4. **Journey**: Pages commonly viewed next by other users

**Each recommendation includes**:
- `url`: Documentation page URL
- `title`: Page title
- `context`: Brief description (if available)

**Use Cases**:
- Finding related content after reading a page
- Exploring a new AWS service
- Discovering popular/important pages
- Finding newly released features (check **New** recommendations from service welcome page)

---

## Python MCP Client Library

### Installation

```bash
# Using uv (recommended)
uv pip install mcp anthropic-mcp-client

# Using pip
pip install mcp anthropic-mcp-client
```

### Dependencies

```python
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "click",
#     "httpx",
# ]
# ///
```

---

## Example Code

### Basic Connection Example

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
# ]
# ///
"""
Basic example of connecting to AWS Knowledge MCP Server.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic


async def connect_to_aws_knowledge():
    """Connect to AWS Knowledge MCP Server via HTTP transport."""
    server_url = "https://knowledge-mcp.global.api.aws"

    # Create HTTP client for MCP server
    async with ClientSession(
        server_url=server_url,
        transport="http"
    ) as session:
        # Initialize the session
        await session.initialize()

        # List available tools
        tools = await session.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        return session


if __name__ == "__main__":
    asyncio.run(connect_to_aws_knowledge())
```

---

### Example: List All AWS Regions

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
#     "click",
# ]
# ///
"""
Example: List all AWS regions using aws___list_regions tool.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
import json
from typing import List, Dict
from mcp import ClientSession


async def list_aws_regions() -> List[Dict[str, str]]:
    """
    Retrieve list of all AWS regions.

    Returns:
        List of dicts with region_id and region_long_name
    """
    server_url = "https://knowledge-mcp.global.api.aws"

    async with ClientSession(
        server_url=server_url,
        transport="http"
    ) as session:
        await session.initialize()

        # Call the aws___list_regions tool
        result = await session.call_tool(
            name="aws___list_regions",
            arguments={}
        )

        return json.loads(result.content[0].text)


async def main():
    regions = await list_aws_regions()

    print(f"Total AWS Regions: {len(regions)}\n")
    for region in regions:
        print(f"{region['region_id']:20} {region['region_long_name']}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Example: Check Regional Availability

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
#     "click",
# ]
# ///
"""
Example: Check if AWS services are available in a specific region.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
import json
from typing import List, Dict
from mcp import ClientSession


async def check_regional_availability(
    region: str,
    resource_type: str,
    filters: List[str] = None
) -> List[Dict]:
    """
    Check availability of AWS resources in a region.

    Args:
        region: AWS region code (e.g., 'us-east-1')
        resource_type: 'product', 'api', or 'cfn'
        filters: Optional list of specific resources to check

    Returns:
        List of resources with availability status
    """
    server_url = "https://knowledge-mcp.global.api.aws"

    async with ClientSession(
        server_url=server_url,
        transport="http"
    ) as session:
        await session.initialize()

        arguments = {
            "region": region,
            "resource_type": resource_type
        }

        if filters:
            arguments["filters"] = filters

        result = await session.call_tool(
            name="aws___get_regional_availability",
            arguments=arguments
        )

        return json.loads(result.content[0].text)


async def main():
    # Check if Lambda and S3 are available in eu-west-1
    results = await check_regional_availability(
        region="eu-west-1",
        resource_type="product",
        filters=["AWS Lambda", "Amazon S3"]
    )

    print("Regional Availability Check:")
    for result in results:
        print(f"  {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Example: Search AWS Documentation

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
#     "click",
# ]
# ///
"""
Example: Search AWS documentation.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
import json
from typing import List, Dict
from mcp import ClientSession


async def search_aws_docs(
    search_phrase: str,
    limit: int = 10
) -> List[Dict]:
    """
    Search AWS documentation.

    Args:
        search_phrase: Search query
        limit: Maximum number of results

    Returns:
        List of search results with url, title, context, rank_order
    """
    server_url = "https://knowledge-mcp.global.api.aws"

    async with ClientSession(
        server_url=server_url,
        transport="http"
    ) as session:
        await session.initialize()

        result = await session.call_tool(
            name="aws___search_documentation",
            arguments={
                "search_phrase": search_phrase,
                "limit": limit
            }
        )

        return json.loads(result.content[0].text)


async def main():
    results = await search_aws_docs(
        search_phrase="Lambda function URLs",
        limit=5
    )

    print(f"Search Results ({len(results)} found):\n")
    for result in results:
        print(f"[{result['rank_order']}] {result['title']}")
        print(f"    URL: {result['url']}")
        if 'context' in result:
            print(f"    Context: {result['context'][:100]}...")
        print()


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Example: Read AWS Documentation

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
#     "click",
# ]
# ///
"""
Example: Read and convert AWS documentation to markdown.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
import json
from mcp import ClientSession


async def read_aws_docs(
    url: str,
    start_index: int = 0,
    max_length: int = None
) -> str:
    """
    Read AWS documentation page and convert to markdown.

    Args:
        url: AWS documentation URL
        start_index: Starting character index for pagination
        max_length: Maximum characters to return

    Returns:
        Markdown-formatted documentation content
    """
    server_url = "https://knowledge-mcp.global.api.aws"

    async with ClientSession(
        server_url=server_url,
        transport="http"
    ) as session:
        await session.initialize()

        arguments = {"url": url}
        if start_index:
            arguments["start_index"] = start_index
        if max_length:
            arguments["max_length"] = max_length

        result = await session.call_tool(
            name="aws___read_documentation",
            arguments=arguments
        )

        return result.content[0].text


async def main():
    url = "https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html"

    content = await read_aws_docs(url, max_length=2000)

    print(f"Documentation from: {url}\n")
    print(content)


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Example: Get Documentation Recommendations

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
#     "click",
# ]
# ///
"""
Example: Get related documentation recommendations.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
import json
from typing import Dict, List
from mcp import ClientSession


async def get_recommendations(url: str) -> Dict[str, List[Dict]]:
    """
    Get documentation recommendations for a page.

    Args:
        url: AWS documentation URL

    Returns:
        Dict with categories: highly_rated, new, similar, journey
    """
    server_url = "https://knowledge-mcp.global.api.aws"

    async with ClientSession(
        server_url=server_url,
        transport="http"
    ) as session:
        await session.initialize()

        result = await session.call_tool(
            name="aws___recommend",
            arguments={"url": url}
        )

        return json.loads(result.content[0].text)


async def main():
    url = "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html"

    recommendations = await get_recommendations(url)

    for category, pages in recommendations.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        for page in pages[:3]:  # Show top 3
            print(f"  - {page['title']}")
            print(f"    {page['url']}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Complete CLI Example with Click

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mcp",
#     "anthropic-mcp-client",
#     "httpx",
#     "click",
# ]
# ///
"""
Complete CLI tool for querying AWS Knowledge MCP Server.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import asyncio
import json
from typing import List, Optional
import click
from mcp import ClientSession


SERVER_URL = "https://knowledge-mcp.global.api.aws"


async def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Generic function to call any MCP tool."""
    async with ClientSession(
        server_url=SERVER_URL,
        transport="http"
    ) as session:
        await session.initialize()
        result = await session.call_tool(name=tool_name, arguments=arguments)
        return json.loads(result.content[0].text)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AWS Knowledge CLI - Query AWS documentation and service information."""
    pass


@cli.command()
def regions():
    """List all AWS regions.

    Examples:

    \b
        # List all regions
        aws-knowledge regions
    """
    async def _list_regions():
        results = await call_mcp_tool("aws___list_regions", {})
        for region in results:
            click.echo(f"{region['region_id']:20} {region['region_long_name']}")

    asyncio.run(_list_regions())


@cli.command()
@click.argument("region")
@click.option("--type", "-t", "resource_type",
              type=click.Choice(["product", "api", "cfn"]),
              default="product", help="Resource type to check")
@click.option("--filter", "-f", "filters", multiple=True,
              help="Filter specific resources")
def availability(region: str, resource_type: str, filters: tuple):
    """Check regional availability of AWS resources.

    Examples:

    \b
        # Check Lambda availability in us-east-1
        aws-knowledge availability us-east-1 --filter "AWS Lambda"

    \b
        # Check multiple CloudFormation resources
        aws-knowledge availability eu-west-1 \\
            --type cfn \\
            --filter "AWS::Lambda::Function" \\
            --filter "AWS::EC2::Instance"
    """
    async def _check_availability():
        arguments = {
            "region": region,
            "resource_type": resource_type
        }
        if filters:
            arguments["filters"] = list(filters)

        results = await call_mcp_tool("aws___get_regional_availability", arguments)
        click.echo(json.dumps(results, indent=2))

    asyncio.run(_check_availability())


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Maximum number of results")
def search(query: str, limit: int):
    """Search AWS documentation.

    Examples:

    \b
        # Search for Lambda documentation
        aws-knowledge search "Lambda function URLs"

    \b
        # Search with limit
        aws-knowledge search "S3 bucket versioning" --limit 5
    """
    async def _search():
        results = await call_mcp_tool(
            "aws___search_documentation",
            {"search_phrase": query, "limit": limit}
        )

        click.echo(f"\nFound {len(results)} results:\n")
        for result in results:
            click.echo(f"[{result['rank_order']}] {result['title']}")
            click.echo(f"    {result['url']}")
            if 'context' in result:
                click.echo(f"    {result['context'][:100]}...")
            click.echo()

    asyncio.run(_search())


@cli.command()
@click.argument("url")
@click.option("--output", "-o", help="Output file (default: stdout)")
def read(url: str, output: Optional[str]):
    """Read AWS documentation page as markdown.

    Examples:

    \b
        # Read documentation to stdout
        aws-knowledge read https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html

    \b
        # Save to file
        aws-knowledge read https://docs.aws.amazon.com/lambda/latest/dg/welcome.html \\
            --output lambda-docs.md
    """
    async def _read():
        result = await call_mcp_tool(
            "aws___read_documentation",
            {"url": url}
        )
        content = result if isinstance(result, str) else json.dumps(result, indent=2)

        if output:
            with open(output, "w") as f:
                f.write(content)
            click.echo(f"Documentation saved to: {output}")
        else:
            click.echo(content)

    asyncio.run(_read())


@cli.command()
@click.argument("url")
def recommend(url: str):
    """Get related documentation recommendations.

    Examples:

    \b
        # Get recommendations for Lambda docs
        aws-knowledge recommend https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
    """
    async def _recommend():
        results = await call_mcp_tool("aws___recommend", {"url": url})

        for category, pages in results.items():
            click.echo(f"\n{category.upper().replace('_', ' ')}:")
            for page in pages[:5]:
                click.echo(f"  - {page['title']}")
                click.echo(f"    {page['url']}")

    asyncio.run(_recommend())


if __name__ == "__main__":
    cli()
```

---

## Alternative: Direct AWS SDK Approach

If you want to bypass MCP entirely and use AWS Bedrock directly:

### Using boto3 (Python)

```python
import boto3

# Create Bedrock Agent Runtime client
client = boto3.client(
    'bedrock-agent-runtime',
    region_name='us-east-1'
)

# Query knowledge base
response = client.retrieve(
    knowledgeBaseId='YOUR_KB_ID',
    retrievalQuery={
        'text': 'How do I configure Lambda function URLs?'
    },
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 5
        }
    }
)

# Process results
for result in response['retrievalResults']:
    print(f"Content: {result['content']['text']}")
    print(f"Source: {result['location']['s3Location']['uri']}")
    print(f"Score: {result['score']}")
```

**Note**: This requires:
- AWS credentials configured
- A Knowledge Base created in AWS Bedrock
- Knowledge Base populated with AWS documentation

---

## Sources and References

### Official Documentation

1. **AWS Knowledge MCP Server**
   - GitHub (Archived): https://github.com/modelcontextprotocol/servers-archived/tree/main/src/aws-kb-retrieval-server
   - NPM Package: `@modelcontextprotocol/server-aws-kb-retrieval` (v0.6.2)

2. **Model Context Protocol (MCP)**
   - Specification: https://modelcontextprotocol.io
   - MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
   - MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

3. **AWS Bedrock Agent Runtime**
   - API Reference: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html
   - Service Documentation: https://docs.aws.amazon.com/bedrock/

4. **AWS SDK Documentation**
   - boto3 (Python): https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
   - AWS SDK for JavaScript v3: https://github.com/aws/aws-sdk-js-v3

### Research Reports

5. **Context7 Research Report**
   - Location: `/Users/dennisvriend/research-reports/aws-knowledge-mcp-research.md`
   - Date: 2025-11-20
   - Key Finding: MCP-only protocol, no REST API

6. **Z.AI Web Search Results**
   - aws-kb-retrieval-server GitHub repository
   - Bedrock Agent Runtime API documentation
   - Community MCP implementations

### Community Resources

7. **Community MCP Servers**
   - AWS MCP Server (General): https://github.com/rishikavikondala/mcp-server-aws
   - Fastify MCP Server: https://github.com/flaviodelgrosso/fastify-mcp-server

8. **Alternative Documentation Access**
   - AWS Documentation Scraper: https://github.com/scalastic/aws-documentation-scraper
   - AWS SDK Service Models: https://github.com/aws/aws-sdk-js-v3/tree/main/codegen/sdk-codegen/aws-models

---

## Key Takeaways

1. **No REST API Available**: AWS Knowledge MCP Server only supports MCP protocol
2. **Python MCP Client**: Use `mcp` and `anthropic-mcp-client` packages for Python integration
3. **Five Main Tools**: regions, availability, search, read, recommend
4. **No Authentication**: Public endpoint, but rate-limited
5. **Alternative**: Use AWS Bedrock Agent Runtime SDK directly (requires AWS credentials and Knowledge Base setup)

---

## Next Steps

For building the CLI tool:

1. **Install Dependencies**:
   ```bash
   uv pip install mcp anthropic-mcp-client httpx click
   ```

2. **Test Connection**:
   - Run basic connection example to verify MCP server access
   - Test each tool individually

3. **Build CLI Structure**:
   - Use Click for command-line interface
   - Implement async/await for MCP calls
   - Add error handling and retries
   - Implement pagination for large results

4. **Add Features**:
   - Output formatting (JSON, table, markdown)
   - Caching for repeated queries
   - Configuration file support
   - Verbose/debug logging

---

**End of Research Document**
