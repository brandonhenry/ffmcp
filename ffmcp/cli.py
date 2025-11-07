"""Main CLI entry point for ffmcp"""
import click
import sys
import json
import os
import io
import logging
from typing import Any, Dict, List, Optional

from ffmcp.providers import get_provider
from ffmcp.config import Config
from ffmcp.brain import ZepBrainClient, BrainInfo, ZepSDKNotInstalledError
from ffmcp.agents import Agent

# Ensure UTF-8 encoding for stdin/stdout as early as possible
# Environment hint for Python and downstream libs
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
os.environ.setdefault('PYTHONUTF8', '1')

# Reconfigure stdio to UTF-8 with replacement-on-error to avoid crashes on exotic glyphs
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    # If the environment forbids reconfiguration, continue with defaults
    pass

# Ensure proper encoding for Click output
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass  # Use system default


# Patch Click's echo to ensure UTF-8 encoding
_original_echo = click.echo

def safe_echo(message=None, file=None, nl=True, err=False, color=None):
    """Wrapper for click.echo that ensures UTF-8 encoding"""
    try:
        if message is not None:
            if isinstance(message, bytes):
                message = message.decode('utf-8', errors='replace')
            elif not isinstance(message, str):
                message = str(message)
        return _original_echo(message, file=file, nl=nl, err=err, color=color)
    except UnicodeEncodeError:
        # Fallback: write directly to buffer
        target = sys.stderr.buffer if err else sys.stdout.buffer
        if message:
            target.write(str(message).encode('utf-8', errors='replace'))
        if nl:
            target.write(b'\n')
        target.flush()

click.echo = safe_echo

# ---------------- Logging Setup ----------------
# Configure logging early; default WARNING to avoid polluting normal output.
# Enable DEBUG by setting FFMCP_DEBUG=1 or set explicit FFMCP_LOGLEVEL (e.g., INFO/DEBUG).
_env_level = os.getenv('FFMCP_LOGLEVEL')
if _env_level is None and os.getenv('FFMCP_DEBUG') in {'1', 'true', 'True'}:
    _env_level = 'DEBUG'
_level = getattr(logging, (_env_level or 'WARNING').upper(), logging.WARNING)
logging.basicConfig(level=_level, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger('ffmcp.cli')


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ffmcp - AI command-line tool for accessing AI services"""
    logger.debug('CLI invoked')
    pass


@cli.command()
@click.argument('prompt', required=False)
@click.option('--provider', '-p', default='openai', help='AI provider to use (openai, anthropic, gemini, groq, deepseek, mistral, together, cohere, perplexity)')
@click.option('--model', '-m', help='Model to use (overrides default)')
@click.option('--temperature', '-t', type=float, help='Temperature for generation')
@click.option('--max-tokens', type=int, help='Maximum tokens to generate')
@click.option('--stream', '-s', is_flag=True, help='Stream the response')
@click.option('--input', '-i', type=click.File('r', encoding='utf-8'), help='Read prompt from file')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
def generate(prompt: Optional[str], provider: str, model: Optional[str], 
             temperature: Optional[float], max_tokens: Optional[int], 
             stream: bool, input: Optional, output: Optional):
    """Generate text using AI"""
    config = Config()
    
    # Get prompt from argument, file, or stdin
    input_source = 'stdin'
    if input:
        input_source = 'file'
        prompt_text = input.read()
    elif prompt:
        input_source = 'arg'
        prompt_text = prompt
    else:
        prompt_text = sys.stdin.read()
    
    logger.info(
        "generate start provider=%s model=%s temperature=%s max_tokens=%s stream=%s input_source=%s output=%s",
        provider,
        model or '(default)',
        temperature,
        max_tokens,
        stream,
        input_source,
        bool(output),
    )
    logger.debug("prompt length=%d", len(prompt_text or ''))

    if not (prompt_text or '').strip():
        click.echo("Error: No prompt provided", err=True)
        sys.exit(1)
    
    # Get provider instance
    try:
        provider_instance = get_provider(provider, config)
        try:
            default_model = provider_instance.get_default_model()
        except Exception:
            default_model = None
        logger.info(
            "provider initialized name=%s class=%s default_model=%s",
            provider,
            provider_instance.__class__.__name__,
            default_model,
        )
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        logger.exception("failed to initialize provider: %s", provider)
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)
    
    # Prepare parameters
    params = {}
    if model:
        params['model'] = model
    if temperature is not None:
        params['temperature'] = temperature
    if max_tokens:
        params['max_tokens'] = max_tokens
    
    # Generate
    try:
        if stream:
            logger.info("streaming generation started")
            _chunk_count = 0
            for chunk in provider_instance.generate_stream(prompt_text, **params):
                _chunk_count += 1
                click.echo(chunk, nl=False)
                if output:
                    output.write(chunk)
            click.echo()  # Newline after streaming
            logger.info("streaming generation finished chunks=%d", _chunk_count)
        else:
            logger.debug("calling provider.generate with params=%s", params)
            result = provider_instance.generate(prompt_text, **params)
            click.echo(result)
            if output:
                output.write(result)
            logger.info("generation finished result_length=%d", len(result or ''))
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        logger.exception("generation failed")
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('prompt')
@click.option('--provider', '-p', default='openai', help='AI provider to use (openai, anthropic, gemini, groq, deepseek, mistral, together, cohere, perplexity)')
@click.option('--model', '-m', help='Model to use')
@click.option('--system', '-s', help='System message')
def chat(prompt: str, provider: str, model: Optional[str], system: Optional[str]):
    """Chat with AI (conversational context)"""
    config = Config()
    
    try:
        provider_instance = get_provider(provider, config)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        params = {}
        if model:
            params['model'] = model
        
        result = provider_instance.chat(messages, **params)
        click.echo(result)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@cli.command()
def providers():
    """List available AI providers"""
    from ffmcp.providers import AVAILABLE_PROVIDERS
    click.echo("Available providers:")
    for name, provider_class in AVAILABLE_PROVIDERS.items():
        click.echo(f"  - {name}: {provider_class.__doc__ or 'No description'}")


@cli.command()
@click.option('--provider', '-p', help='Filter by provider (e.g., openai, anthropic, gemini, groq, deepseek, mistral, together, cohere, perplexity)')
@click.option('--date', '-d', help='UTC date YYYY-MM-DD (default: today)')
def tokens(provider: Optional[str], date: Optional[str]):
    """Show cumulative token usage for the given UTC day (integer)."""
    config = Config()
    try:
        count = config.get_token_usage(date_str=date, provider=provider)
        click.echo(str(int(count)))
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--provider', '-p', required=True, help='Provider name')
@click.option('--key', '-k', help='API key')
def config(provider: str, key: Optional[str]):
    """Configure API keys for providers"""
    config = Config()
    if key:
        config.set_api_key(provider, key)
        click.echo(f"API key configured for {provider}")
    else:
        current_key = config.get_api_key(provider)
        if current_key:
            masked = current_key[:4] + "..." + current_key[-4:] if len(current_key) > 8 else "***"
            click.echo(f"{provider}: {masked}")
        else:
            click.echo(f"No API key configured for {provider}")


# ========== OpenAI-specific commands ==========

@cli.group()
def openai():
    """OpenAI-specific commands"""
    pass


@openai.command()
@click.argument('prompt')
@click.argument('images', nargs=-1, required=True)
@click.option('--model', '-m', default='gpt-4o', help='Vision model to use')
@click.option('--temperature', '-t', type=float, help='Temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
def vision(prompt: str, images: tuple, model: str, temperature: Optional[float], 
           max_tokens: Optional[int], output: Optional):
    """Analyze images with vision models"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        if not hasattr(provider, 'vision'):
            click.echo("Error: Vision not supported by this provider", err=True)
            sys.exit(1)
        
        params = {'model': model}
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens:
            params['max_tokens'] = max_tokens
        
        result = provider.vision(prompt, list(images), **params)
        click.echo(result)
        if output:
            output.write(result)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


# ========== Zep / Brain commands ==========

@cli.group()
def brain():
    """Manage brains (Zep memory, collections, graph)."""
    pass


def _load_brain_and_client(config: Config, brain_name: str = None) -> tuple:
    zep_settings = config.get_zep_settings()
    try:
        client = ZepBrainClient(
            api_key=zep_settings.get('api_key'),
            base_url=zep_settings.get('base_url'),
            env=zep_settings.get('env'),
        )
    except ZepSDKNotInstalledError as e:
        click.echo(str(e), err=True)
        sys.exit(1)

    if not brain_name:
        brain_name = config.get_active_brain()
        if not brain_name:
            click.echo("Error: No brain specified and no active brain set. Use 'ffmcp brain create <name>' or 'ffmcp brain use <name>'.", err=True)
            sys.exit(1)
    brain_cfg = config.get_brain(brain_name)
    if not brain_cfg:
        click.echo(f"Error: Unknown brain '{brain_name}'. Create it with 'ffmcp brain create {brain_name}'.", err=True)
        sys.exit(1)
    brain_info = BrainInfo(name=brain_name, default_session_id=brain_cfg.get('default_session_id'))
    return client, brain_info


@brain.command('create')
@click.argument('name')
@click.option('--session-id', help='Default session id for this brain (optional)')
def brain_create(name: str, session_id: str):
    """Create a new brain and set it active."""
    config = Config()
    try:
        config.create_brain(name, default_session_id=session_id)
        click.echo(f"Brain created: {name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@brain.command('list')
def brain_list():
    """List brains."""
    config = Config()
    brains = config.list_brains()
    active = config.get_active_brain()
    for b in brains:
        marker = ' *' if b.get('name') == active else ''
        click.echo(f"{b.get('name')}{marker}")


@brain.command('use')
@click.argument('name')
def brain_use(name: str):
    """Set active brain."""
    config = Config()
    try:
        config.set_active_brain(name)
        click.echo(f"Active brain: {name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@brain.command('current')
def brain_current():
    """Show active brain."""
    config = Config()
    curr = config.get_active_brain()
    if curr:
        click.echo(curr)
    else:
        click.echo("No active brain")


@brain.command('delete')
@click.argument('name')
def brain_delete(name: str):
    """Delete a brain from local registry (does not delete Zep data)."""
    config = Config()
    config.delete_brain(name)
    click.echo(f"Deleted brain: {name}")


@brain.group()
def memory():
    """Chat memory operations."""
    pass


@memory.command('add')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--session', 'session_id', help='Session id. Defaults to brain default or name.')
@click.option('--role', default='user', help='Speaker name (e.g., user name).')
@click.option('--role-type', default='user', type=click.Choice(['user', 'assistant', 'system']), help='Message role type.')
@click.option('--content', help='Message content text.')
@click.option('--json', 'json_file', type=click.File('r', encoding='utf-8'), help='JSON array of messages to add.')
def memory_add(brain_name: Optional[str], session_id: Optional[str], role: str, role_type: str, content: Optional[str], json_file):
    """Add messages to memory. Provide --content or --json with messages array."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)

    messages: List[Dict[str, Any]] = []
    if json_file:
        try:
            messages = json.load(json_file)
        except Exception as e:
            click.echo(f"Error reading JSON: {e}", err=True)
            sys.exit(1)
    elif content:
        messages = [{"role": role, "role_type": role_type, "content": content}]
    else:
        click.echo("Error: Provide --content or --json", err=True)
        sys.exit(1)

    res = client.memory_add_messages(brain=brain_info, session_id=session_id, messages=messages)
    if not res.get('ok'):
        click.echo(f"Error: {res.get('error')}", err=True)
        sys.exit(1)
    click.echo("OK")


@memory.command('get')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--session', 'session_id', help='Session id. Defaults to brain default or name.')
def memory_get(brain_name: Optional[str], session_id: Optional[str]):
    """Get memory context for a session."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    res = client.memory_get(brain=brain_info, session_id=session_id)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@memory.command('search')
@click.argument('query')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--session', 'session_id', help='Session id. Defaults to brain default or name.')
@click.option('--limit', type=int, default=5)
@click.option('--min-score', type=float)
def memory_search(query: str, brain_name: Optional[str], session_id: Optional[str], limit: int, min_score: Optional[float]):
    """Semantic search over session memory."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    res = client.memory_search(brain=brain_info, session_id=session_id, query=query, limit=limit, min_score=min_score)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@memory.command('clear')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--session', 'session_id', help='Session id. Defaults to brain default or name.')
def memory_clear(brain_name: Optional[str], session_id: Optional[str]):
    """Clear memory for a session."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    res = client.memory_clear(brain=brain_info, session_id=session_id)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@brain.group()
def collection():
    """Collection operations (document store)."""
    pass


@collection.command('create')
@click.argument('name')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--description')
@click.option('--metadata', type=click.File('r', encoding='utf-8'), help='JSON file with metadata.')
def collection_create(name: str, brain_name: Optional[str], description: Optional[str], metadata):
    """Create a namespaced collection."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    meta = None
    if metadata:
        try:
            meta = json.load(metadata)
        except Exception as e:
            click.echo(f"Error reading metadata JSON: {e}", err=True)
            sys.exit(1)
    res = client.collection_create(brain=brain_info, name=name, description=description, metadata=meta)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@collection.command('list')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
def collection_list(brain_name: Optional[str]):
    """List collections for a brain."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    res = client.collection_list(brain=brain_info)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@brain.group()
def document():
    """Document operations in collections."""
    pass


@document.command('add')
@click.argument('collection')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--id', 'doc_id')
@click.option('--text')
@click.option('--input', 'input_file', type=click.File('r', encoding='utf-8'), help='Read text from file')
@click.option('--metadata', type=click.File('r', encoding='utf-8'), help='JSON file with metadata')
def document_add(collection: str, brain_name: Optional[str], doc_id: Optional[str], text: Optional[str], input_file, metadata):
    """Add a text document to a collection."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    if input_file and text:
        click.echo("Error: Provide either --text or --input, not both", err=True)
        sys.exit(1)
    if input_file:
        text = input_file.read()
    meta = None
    if metadata:
        try:
            meta = json.load(metadata)
        except Exception as e:
            click.echo(f"Error reading metadata JSON: {e}", err=True)
            sys.exit(1)
    res = client.document_add(brain=brain_info, collection=collection, document_id=doc_id, text=text, metadata=meta)
    if not res.get('ok'):
        click.echo(f"Error: {res.get('error')}", err=True)
        sys.exit(1)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@document.command('search')
@click.argument('collection')
@click.argument('query')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--limit', type=int, default=5)
@click.option('--min-score', type=float)
def document_search(collection: str, query: str, brain_name: Optional[str], limit: int, min_score: Optional[float]):
    """Semantic search over documents in a collection."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    res = client.document_search(brain=brain_info, collection=collection, query=query, limit=limit, min_score=min_score)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@document.command('delete')
@click.argument('collection')
@click.option('--brain', 'brain_name', help='Brain name. Defaults to active brain.')
@click.option('--id', 'doc_id', required=True)
def document_delete(collection: str, brain_name: Optional[str], doc_id: str):
    """Delete a document by id from a collection."""
    config = Config()
    client, brain_info = _load_brain_and_client(config, brain_name)
    res = client.document_delete(brain=brain_info, collection=collection, document_id=doc_id)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@brain.group()
def graph():
    """Low-level Graph API (zep-cloud)."""
    pass


@graph.command('add')
@click.argument('user_id')
@click.option('--type', 'data_type', required=True, help='Data type, e.g., json')
@click.option('--data', 'data_str', help='Inline JSON string')
@click.option('--input', 'input_file', type=click.File('r', encoding='utf-8'), help='JSON file input')
def graph_add(user_id: str, data_type: str, data_str: Optional[str], input_file):
    """Add graph data (cloud only)."""
    config = Config()
    zep_settings = config.get_zep_settings()
    try:
        client = ZepBrainClient(api_key=zep_settings.get('api_key'), base_url=zep_settings.get('base_url'), env=zep_settings.get('env'))
    except ZepSDKNotInstalledError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    data_obj: Any = data_str
    if input_file:
        data_obj = input_file.read()
    if not data_obj:
        click.echo("Error: Provide --data or --input", err=True)
        sys.exit(1)
    res = client.graph_add(user_id=user_id, data_type=data_type, data=data_obj)
    if not res.get('ok'):
        click.echo(f"Error: {res.get('error')}", err=True)
        sys.exit(1)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))


@graph.command('get')
@click.argument('user_id')
def graph_get(user_id: str):
    """Get graph data (cloud only)."""
    config = Config()
    zep_settings = config.get_zep_settings()
    try:
        client = ZepBrainClient(api_key=zep_settings.get('api_key'), base_url=zep_settings.get('base_url'), env=zep_settings.get('env'))
    except ZepSDKNotInstalledError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    res = client.graph_get(user_id=user_id)
    if not res.get('ok'):
        click.echo(f"Error: {res.get('error')}", err=True)
        sys.exit(1)
    click.echo(json.dumps(res.get('result'), indent=2, default=str))
@openai.command()
@click.argument('prompt')
@click.option('--model', '-m', default='dall-e-3', help='Model (dall-e-2 or dall-e-3)')
@click.option('--size', default='1024x1024', help='Image size')
@click.option('--quality', default='standard', help='Quality (standard or hd for dall-e-3)')
@click.option('--style', default='vivid', help='Style (vivid or natural for dall-e-3)')
@click.option('--output', '-o', help='Save image URL to file')
def image(prompt: str, model: str, size: str, quality: str, style: str, output: Optional[str]):
    """Generate image using DALL·E"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        result = provider.generate_image(
            prompt,
            model=model,
            size=size,
            quality=quality,
            style=style
        )
        click.echo(f"Image URL: {result['url']}")
        if 'revised_prompt' in result and result['revised_prompt']:
            click.echo(f"Revised prompt: {result['revised_prompt']}")
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result['url'])
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--model', '-m', default='whisper-1', help='Model to use')
@click.option('--language', '-l', help='Language code (optional)')
@click.option('--prompt', '-p', help='Prompt to guide transcription')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def transcribe(audio_file: str, model: str, language: Optional[str], prompt: Optional[str],
               output: Optional, json_output: bool):
    """Transcribe audio to text using Whisper"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        params = {'model': model}
        if language:
            params['language'] = language
        if prompt:
            params['prompt'] = prompt
        if json_output:
            params['response_format'] = 'json'
        
        result = provider.transcribe(audio_file, **params)
        
        if json_output:
            output_text = json.dumps(result, indent=2)
        else:
            output_text = result.get('text', str(result))
        
        click.echo(output_text)
        if output:
            output.write(output_text)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--model', '-m', default='whisper-1', help='Model to use')
@click.option('--prompt', '-p', help='Prompt to guide translation')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def translate(audio_file: str, model: str, prompt: Optional[str], output: Optional, json_output: bool):
    """Translate audio to English using Whisper"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        params = {'model': model}
        if prompt:
            params['prompt'] = prompt
        if json_output:
            params['response_format'] = 'json'
        
        result = provider.translate(audio_file, **params)
        
        if json_output:
            output_text = json.dumps(result, indent=2)
        else:
            output_text = result.get('text', str(result))
        
        click.echo(output_text)
        if output:
            output.write(output_text)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('text')
@click.argument('output_file', type=click.Path())
@click.option('--model', '-m', default='tts-1', help='Model (tts-1 or tts-1-hd)')
@click.option('--voice', '-v', default='alloy', 
              type=click.Choice(['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']),
              help='Voice to use')
@click.option('--speed', '-s', type=float, default=1.0, help='Speed (0.25 to 4.0)')
def tts(text: str, output_file: str, model: str, voice: str, speed: float):
    """Convert text to speech"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        result = provider.text_to_speech(text, output_file, model=model, voice=voice, speed=speed)
        click.echo(f"Audio saved to: {result}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('text')
@click.option('--model', '-m', default='text-embedding-3-small', help='Embedding model')
@click.option('--dimensions', '-d', type=int, help='Number of dimensions')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
@click.option('--json', 'json_output', is_flag=True, help='Output full JSON')
def embed(text: str, model: str, dimensions: Optional[int], output: Optional, json_output: bool):
    """Create embeddings for text"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        params = {'model': model}
        if dimensions:
            params['dimensions'] = dimensions
        
        result = provider.create_embedding(text, **params)
        
        if json_output:
            output_text = json.dumps(result, indent=2)
        else:
            # Output just the embedding vector
            embedding = result.get('embedding') or result.get('embeddings', [])[0]
            output_text = json.dumps(embedding)
        
        click.echo(output_text)
        if output:
            output.write(output_text)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('prompt')
@click.option('--tools', '-t', type=click.File('r', encoding='utf-8'), help='Tools JSON file')
@click.option('--model', '-m', help='Model to use')
@click.option('--temperature', type=float, help='Temperature')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
def tools(prompt: str, tools: Optional, model: Optional[str], temperature: Optional[float], output: Optional):
    """Chat with function calling support"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        
        messages = [{"role": "user", "content": prompt}]
        tools_list = []
        
        if tools:
            tools_list = json.load(tools)
        
        params = {}
        if model:
            params['model'] = model
        if temperature is not None:
            params['temperature'] = temperature
        
        result = provider.chat_with_tools(messages, tools_list, **params)
        
        output_text = json.dumps(result, indent=2)
        click.echo(output_text)
        if output:
            output.write(output_text)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@openai.group()
def assistant():
    """Manage OpenAI Assistants"""
    pass


@assistant.command()
@click.argument('name')
@click.argument('instructions')
@click.option('--model', '-m', default='gpt-4o-mini', help='Model to use')
@click.option('--tools', '-t', type=click.File('r', encoding='utf-8'), help='Tools JSON file')
@click.option('--temperature', type=float, help='Temperature')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Save assistant ID to file')
def create(name: str, instructions: str, model: str, tools: Optional, temperature: Optional[float], output: Optional):
    """Create a new assistant"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        
        params = {'model': model}
        if tools:
            params['tools'] = json.load(tools)
        if temperature is not None:
            params['temperature'] = temperature
        
        result = provider.create_assistant(name, instructions, **params)
        
        click.echo(f"Assistant created: {result['id']}")
        click.echo(json.dumps(result, indent=2))
        if output:
            output.write(result['id'])
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


# ========== Anthropic/Claude-specific commands ==========

@cli.group()
def claude():
    """Anthropic Claude-specific commands"""
    pass


@claude.command()
@click.argument('prompt')
@click.argument('images', nargs=-1, required=True)
@click.option('--model', '-m', default='claude-3-5-sonnet-20241022', help='Vision model to use')
@click.option('--temperature', '-t', type=float, help='Temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
def vision(prompt: str, images: tuple, model: str, temperature: Optional[float], 
           max_tokens: Optional[int], output: Optional):
    """Analyze images with Claude vision models"""
    config = Config()
    try:
        provider = get_provider('anthropic', config)
        if not hasattr(provider, 'vision'):
            click.echo("Error: Vision not supported by this provider", err=True)
            sys.exit(1)
        
        params = {'model': model}
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens:
            params['max_tokens'] = max_tokens
        
        result = provider.vision(prompt, list(images), **params)
        click.echo(result)
        if output:
            output.write(result)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@claude.command()
@click.argument('prompt')
@click.argument('urls', nargs=-1, required=True)
@click.option('--model', '-m', default='claude-3-5-sonnet-20241022', help='Vision model to use')
@click.option('--temperature', '-t', type=float, help='Temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
def vision_urls(prompt: str, urls: tuple, model: str, temperature: Optional[float], 
                max_tokens: Optional[int], output: Optional):
    """Analyze images from URLs with Claude vision models"""
    config = Config()
    try:
        provider = get_provider('anthropic', config)
        if not hasattr(provider, 'vision_urls'):
            click.echo("Error: Vision URLs not supported by this provider", err=True)
            sys.exit(1)
        
        params = {'model': model}
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens:
            params['max_tokens'] = max_tokens
        
        result = provider.vision_urls(prompt, list(urls), **params)
        click.echo(result)
        if output:
            output.write(result)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@claude.command()
@click.argument('prompt')
@click.option('--tools', '-t', type=click.File('r', encoding='utf-8'), help='Tools JSON file')
@click.option('--model', '-m', help='Model to use')
@click.option('--temperature', type=float, help='Temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens')
@click.option('--system', '-s', help='System message')
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Write output to file')
def tools(prompt: str, tools: Optional, model: Optional[str], temperature: Optional[float], 
          max_tokens: Optional[int], system: Optional[str], output: Optional):
    """Chat with Claude using tools/function calling"""
    config = Config()
    try:
        provider = get_provider('anthropic', config)
        if not hasattr(provider, 'chat_with_tools'):
            click.echo("Error: Tools not supported by this provider", err=True)
            sys.exit(1)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        tools_list = []
        if tools:
            tools_list = json.load(tools)
        
        params = {}
        if model:
            params['model'] = model
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens:
            params['max_tokens'] = max_tokens
        
        result = provider.chat_with_tools(messages, tools_list, **params)
        
        output_text = json.dumps(result, indent=2)
        click.echo(output_text)
        if output:
            output.write(output_text)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


# ========== Agent commands ==========

@cli.group()
def agent():
    """Create, manage, and run agents."""
    pass


@agent.command('create')
@click.argument('name')
@click.option('--provider', '-p', default='openai', type=click.Choice(['openai', 'anthropic', 'gemini', 'groq', 'deepseek', 'mistral', 'together', 'cohere', 'perplexity']), help='Provider name')
@click.option('--model', '-m', required=True, help='Default model for this agent')
@click.option('--instructions', '-i', help='System prompt instructions (inline text)')
@click.option('--instructions-file', '-f', type=click.File('r', encoding='utf-8'), help='Read instructions from file')
@click.option('--brain', help='Optional brain name for memory/search')
@click.option('--prop', 'props', multiple=True, help='Set property key=value (repeatable)')
@click.option('--web/--no-web', default=True, help='Enable web_fetch action')
@click.option('--image-gen/--no-image-gen', default=True, help='Enable generate_image action')
@click.option('--vision-urls/--no-vision-urls', default=True, help='Enable analyze_image_urls action')
@click.option('--embeddings/--no-embeddings', default=True, help='Enable create_embedding action')
@click.option('--brain-search/--no-brain-search', default=True, help='Enable brain_document_search action')
def agent_create(name: str, provider: str, model: str, instructions: Optional[str], instructions_file: Optional, brain: Optional[str], props: tuple,
                 web: bool, image_gen: bool, vision_urls: bool, embeddings: bool, brain_search: bool):
    """Create a new agent and set it active."""
    config = Config()
    try:
        # Handle instructions from file or inline
        final_instructions = instructions
        if instructions_file:
            if instructions:
                click.echo("Warning: Both --instructions and --instructions-file provided. Using --instructions-file.", err=True)
            final_instructions = instructions_file.read()
        
        properties = {}
        for p in props or []:
            if '=' in p:
                k, v = p.split('=', 1)
                properties[k] = v
        actions = {}
        if web:
            actions['web_fetch'] = {}
        if image_gen:
            actions['generate_image'] = {}
        if vision_urls:
            actions['analyze_image_urls'] = {}
        if embeddings:
            actions['create_embedding'] = {}
        if brain_search:
            actions['brain_document_search'] = {}
        config.create_agent(
            name,
            provider=provider,
            model=model,
            instructions=final_instructions,
            brain=brain,
            properties=properties,
            actions=actions,
        )
        click.echo(f"Agent created: {name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent.command('list')
def agent_list():
    """List agents."""
    config = Config()
    agents = config.list_agents()
    active = config.get_active_agent()
    for a in agents:
        marker = ' *' if a.get('name') == active else ''
        click.echo(f"{a.get('name')}{marker}")


@agent.command('use')
@click.argument('name')
def agent_use(name: str):
    """Set active agent."""
    config = Config()
    try:
        config.set_active_agent(name)
        click.echo(f"Active agent: {name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent.command('current')
def agent_current():
    """Show active agent."""
    config = Config()
    curr = config.get_active_agent()
    if curr:
        click.echo(curr)
    else:
        click.echo("No active agent")


@agent.command('show')
@click.argument('name', required=False)
def agent_show(name: Optional[str]):
    """Show agent details (defaults to active agent)."""
    config = Config()
    if not name:
        name = config.get_active_agent()
    if not name:
        click.echo("Error: No agent specified and no active agent set.", err=True)
        sys.exit(1)
    data = config.get_agent(name)
    if not data:
        click.echo(f"Error: Unknown agent '{name}'", err=True)
        sys.exit(1)
    click.echo(json.dumps({"name": name, **data}, indent=2))


@agent.command('delete')
@click.argument('name')
def agent_delete(name: str):
    """Delete an agent."""
    config = Config()
    config.delete_agent(name)
    click.echo(f"Deleted agent: {name}")


@agent.group('prop')
def agent_prop():
    """Manage agent properties."""
    pass


@agent_prop.command('set')
@click.argument('name')
@click.argument('key')
@click.argument('value')
def agent_prop_set(name: str, key: str, value: str):
    config = Config()
    try:
        config.set_agent_property(name, key, value)
        click.echo("OK")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_prop.command('unset')
@click.argument('name')
@click.argument('key')
def agent_prop_unset(name: str, key: str):
    config = Config()
    try:
        config.remove_agent_property(name, key)
        click.echo("OK")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent.group('action')
def agent_action():
    """Enable/disable agent actions."""
    pass


@agent_action.command('enable')
@click.argument('name')
@click.argument('action')
@click.option('--config', 'config_file', type=click.File('r', encoding='utf-8'), help='Optional JSON config for action')
def agent_action_enable(name: str, action: str, config_file):
    cfg = None
    if config_file:
        try:
            cfg = json.load(config_file)
        except Exception as e:
            click.echo(f"Error reading JSON: {e}", err=True)
            sys.exit(1)
    config = Config()
    try:
        config.enable_agent_action(name, action, cfg)
        click.echo("OK")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_action.command('disable')
@click.argument('name')
@click.argument('action')
def agent_action_disable(name: str, action: str):
    config = Config()
    try:
        config.disable_agent_action(name, action)
        click.echo("OK")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent.group('thread')
def agent_thread():
    """Manage agent threads (conversation history)."""
    pass


@agent_thread.command('create')
@click.argument('agent_name')
@click.argument('thread_name')
def agent_thread_create(agent_name: str, thread_name: str):
    """Create a new thread for an agent."""
    config = Config()
    try:
        config.create_thread(agent_name, thread_name)
        click.echo(f"Thread created: {thread_name} (active for {agent_name})")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_thread.command('list')
@click.argument('agent_name')
def agent_thread_list(agent_name: str):
    """List threads for an agent."""
    config = Config()
    try:
        threads = config.list_threads(agent_name)
        if not threads:
            click.echo(f"No threads found for agent '{agent_name}'")
            return
        for thread in threads:
            marker = ' *' if thread.get('active') else ''
            msg_count = thread.get('message_count', 0)
            created = thread.get('created_at', 'unknown')
            click.echo(f"{thread['name']}{marker} ({msg_count} messages, created: {created})")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_thread.command('use')
@click.argument('agent_name')
@click.argument('thread_name')
def agent_thread_use(agent_name: str, thread_name: str):
    """Set active thread for an agent."""
    config = Config()
    try:
        config.set_active_thread(agent_name, thread_name)
        click.echo(f"Active thread for {agent_name}: {thread_name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_thread.command('current')
@click.argument('agent_name')
def agent_thread_current(agent_name: str):
    """Show active thread for an agent."""
    config = Config()
    try:
        thread_name = config.get_active_thread(agent_name)
        if thread_name:
            click.echo(thread_name)
        else:
            click.echo(f"No active thread for agent '{agent_name}'")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_thread.command('clear')
@click.argument('agent_name')
@click.argument('thread_name')
def agent_thread_clear(agent_name: str, thread_name: str):
    """Clear all messages from a thread."""
    config = Config()
    try:
        config.clear_thread(agent_name, thread_name)
        click.echo(f"Thread cleared: {thread_name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent_thread.command('delete')
@click.argument('agent_name')
@click.argument('thread_name')
def agent_thread_delete(agent_name: str, thread_name: str):
    """Delete a thread."""
    config = Config()
    try:
        config.delete_thread(agent_name, thread_name)
        click.echo(f"Thread deleted: {thread_name}")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@agent.command('run')
@click.argument('prompt', required=False)
@click.option('--agent', 'agent_name', help='Agent name (defaults to active agent)')
@click.option('--thread', 'thread_name', help='Thread name (defaults to active thread)')
@click.option('--image', 'images', multiple=True, type=click.Path(exists=True), help='Local image file(s) to include')
def agent_run(prompt: Optional[str], agent_name: Optional[str], thread_name: Optional[str], images: tuple):
    """Run an agent with a prompt (reads stdin if omitted). Uses active thread if available."""
    config = Config()
    if not prompt:
        prompt = sys.stdin.read()
    if not prompt:
        click.echo("Error: No prompt provided", err=True)
        sys.exit(1)
    if not agent_name:
        agent_name = config.get_active_agent()
    if not agent_name:
        click.echo("Error: No agent specified and no active agent set.", err=True)
        sys.exit(1)
    spec = config.get_agent(agent_name)
    if not spec:
        click.echo(f"Error: Unknown agent '{agent_name}'", err=True)
        sys.exit(1)
    
    # If no thread specified, try to use active thread
    if not thread_name:
        thread_name = config.get_active_thread(agent_name)
    
    try:
        ag = Agent(
            config=config,
            name=agent_name,
            provider=spec.get('provider'),
            model=spec.get('model'),
            instructions=spec.get('instructions'),
            brain=spec.get('brain'),
            properties=spec.get('properties') or {},
            actions_config=spec.get('actions') or {},
        )
        result = ag.run(input_text=prompt, images=list(images) if images else None, thread_name=thread_name)
        click.echo(result)
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@assistant.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), help='Save thread ID to file')
def thread(output: Optional):
    """Create a new conversation thread"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        result = provider.create_thread()
        
        click.echo(f"Thread created: {result['id']}")
        click.echo(json.dumps(result, indent=2))
        if output:
            output.write(result['id'])
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@assistant.command()
@click.argument('thread_id')
@click.argument('assistant_id')
@click.option('--instructions', '-i', help='Override instructions')
@click.option('--stream', '-s', is_flag=True, help='Stream the response')
def run(thread_id: str, assistant_id: str, instructions: Optional[str], stream: bool):
    """Run an assistant on a thread"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        
        params = {'stream': stream}
        if instructions:
            params['instructions'] = instructions
        
        if stream:
            for event in provider.run_assistant(thread_id, assistant_id, **params):
                click.echo(json.dumps(event))
        else:
            result = provider.run_assistant(thread_id, assistant_id, **params)
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@assistant.command()
@click.argument('thread_id')
@click.argument('content')
@click.option('--role', '-r', default='user', type=click.Choice(['user', 'assistant']), help='Message role')
@click.option('--file-ids', '-f', multiple=True, help='File IDs to attach')
def message(thread_id: str, content: str, role: str, file_ids: tuple):
    """Add a message to a thread"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        result = provider.add_message_to_thread(
            thread_id,
            role,
            content,
            file_ids=list(file_ids) if file_ids else []
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@assistant.command()
@click.argument('thread_id')
@click.option('--limit', '-l', default=20, help='Number of messages to retrieve')
def messages(thread_id: str, limit: int):
    """Get messages from a thread"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        result = provider.get_thread_messages(thread_id, limit)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


@assistant.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--purpose', '-p', default='assistants', help='File purpose')
def upload(file_path: str, purpose: str):
    """Upload a file for use with assistants"""
    config = Config()
    try:
        provider = get_provider('openai', config)
        result = provider.upload_file(file_path, purpose)
        click.echo(f"File uploaded: {result['id']}")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    try:
        cli()
    except UnicodeEncodeError as e:
        # Fallback for encoding errors
        error_bytes = str(e).encode('ascii', errors='replace')
        sys.stderr.buffer.write(b'Error: ')
        sys.stderr.buffer.write(error_bytes)
        sys.stderr.buffer.write(b'\n')
        sys.exit(1)
    except Exception as e:
        # Catch any other encoding-related issues
        try:
            error_msg = str(e)
            sys.stderr.buffer.write(error_msg.encode('utf-8'))
            sys.stderr.buffer.write(b'\n')
        except:
            sys.stderr.buffer.write(b'An error occurred\n')
        sys.exit(1)

