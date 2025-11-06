"""Main CLI entry point for ffmcp"""
import click
import sys
import json
from typing import Optional

from ffmcp.providers import get_provider
from ffmcp.config import Config


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ffmcp - AI command-line tool for accessing AI services"""
    pass


@cli.command()
@click.argument('prompt', required=False)
@click.option('--provider', '-p', default='openai', help='AI provider to use (openai, anthropic)')
@click.option('--model', '-m', help='Model to use (overrides default)')
@click.option('--temperature', '-t', type=float, help='Temperature for generation')
@click.option('--max-tokens', type=int, help='Maximum tokens to generate')
@click.option('--stream', '-s', is_flag=True, help='Stream the response')
@click.option('--input', '-i', type=click.File('r'), help='Read prompt from file')
@click.option('--output', '-o', type=click.File('w'), help='Write output to file')
def generate(prompt: Optional[str], provider: str, model: Optional[str], 
             temperature: Optional[float], max_tokens: Optional[int], 
             stream: bool, input: Optional, output: Optional):
    """Generate text using AI"""
    config = Config()
    
    # Get prompt from argument, file, or stdin
    if input:
        prompt_text = input.read()
    elif prompt:
        prompt_text = prompt
    else:
        prompt_text = sys.stdin.read()
    
    if not prompt_text.strip():
        click.echo("Error: No prompt provided", err=True)
        sys.exit(1)
    
    # Get provider instance
    try:
        provider_instance = get_provider(provider, config)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
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
            for chunk in provider_instance.generate_stream(prompt_text, **params):
                click.echo(chunk, nl=False)
                if output:
                    output.write(chunk)
            click.echo()  # Newline after streaming
        else:
            result = provider_instance.generate(prompt_text, **params)
            click.echo(result)
            if output:
                output.write(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('prompt')
@click.option('--provider', '-p', default='openai', help='AI provider to use')
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def providers():
    """List available AI providers"""
    from ffmcp.providers import AVAILABLE_PROVIDERS
    click.echo("Available providers:")
    for name, provider_class in AVAILABLE_PROVIDERS.items():
        click.echo(f"  - {name}: {provider_class.__doc__ or 'No description'}")


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
@click.option('--output', '-o', type=click.File('w'), help='Write output to file')
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


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
            with open(output, 'w') as f:
                f.write(result['url'])
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--model', '-m', default='whisper-1', help='Model to use')
@click.option('--language', '-l', help='Language code (optional)')
@click.option('--prompt', '-p', help='Prompt to guide transcription')
@click.option('--output', '-o', type=click.File('w'), help='Write output to file')
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--model', '-m', default='whisper-1', help='Model to use')
@click.option('--prompt', '-p', help='Prompt to guide translation')
@click.option('--output', '-o', type=click.File('w'), help='Write output to file')
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
        click.echo(f"Error: {e}", err=True)
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('text')
@click.option('--model', '-m', default='text-embedding-3-small', help='Embedding model')
@click.option('--dimensions', '-d', type=int, help='Number of dimensions')
@click.option('--output', '-o', type=click.File('w'), help='Write output to file')
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@openai.command()
@click.argument('prompt')
@click.option('--tools', '-t', type=click.File('r'), help='Tools JSON file')
@click.option('--model', '-m', help='Model to use')
@click.option('--temperature', type=float, help='Temperature')
@click.option('--output', '-o', type=click.File('w'), help='Write output to file')
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@openai.group()
def assistant():
    """Manage OpenAI Assistants"""
    pass


@assistant.command()
@click.argument('name')
@click.argument('instructions')
@click.option('--model', '-m', default='gpt-4o-mini', help='Model to use')
@click.option('--tools', '-t', type=click.File('r'), help='Tools JSON file')
@click.option('--temperature', type=float, help='Temperature')
@click.option('--output', '-o', type=click.File('w'), help='Save assistant ID to file')
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@assistant.command()
@click.option('--output', '-o', type=click.File('w'), help='Save thread ID to file')
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
        click.echo(f"Error: {e}", err=True)
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
        click.echo(f"Error: {e}", err=True)
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
        click.echo(f"Error: {e}", err=True)
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
        click.echo(f"Error: {e}", err=True)
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
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

