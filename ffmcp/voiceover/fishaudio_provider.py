"""FishAudio TTS provider implementation"""
try:
    from fish_audio_sdk import Session, TTSRequest, ReferenceAudio
except ImportError:
    Session = None
    TTSRequest = None
    ReferenceAudio = None

from typing import List, Dict, Any, Optional
from pathlib import Path
from ffmcp.voiceover.base import BaseTTSProvider


class FishAudioProvider(BaseTTSProvider):
    """FishAudio TTS provider"""
    
    def __init__(self, config):
        if Session is None:
            raise ImportError("fish-audio-sdk package not installed. Install with: pip install fish-audio-sdk")
        super().__init__(config)
        # FishAudio Session initialization
        self.session = Session(self.api_key)
    
    def get_provider_name(self) -> str:
        return 'fishaudio'
    
    def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice_id: str = None,
        **kwargs
    ) -> str:
        """Convert text to speech using FishAudio
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice_id: Model/reference_id (optional)
            **kwargs: Additional parameters:
                - model: Model name (alternative to voice_id)
                - reference_id: Voice model ID
                - reference_audio: Path to reference audio file for voice cloning
                - reference_text: Text corresponding to reference audio
                - format: Output format (mp3, wav, pcm, opus) - default: mp3
                - prosody: Dict with speed and volume (e.g., {"speed": 1.0, "volume": 0})
                - base_url: Custom API endpoint (for Session initialization)
        """
        model = kwargs.get('model') or voice_id
        reference_id = kwargs.get('reference_id') or model
        reference_audio_path = kwargs.get('reference_audio')
        reference_text = kwargs.get('reference_text')
        output_format = kwargs.get('format') or kwargs.get('output_format', 'mp3')
        prosody = kwargs.get('prosody')
        
        # Build TTS request
        tts_request_kwargs = {
            'text': text,
            'format': output_format,
        }
        
        # Add reference_id/model if specified
        if reference_id:
            tts_request_kwargs['reference_id'] = reference_id
        
        # Add prosody settings if provided
        if prosody:
            tts_request_kwargs['prosody'] = prosody
        
        # Add reference audio for voice cloning if provided
        references = []
        if reference_audio_path:
            ref_path = Path(reference_audio_path)
            if not ref_path.exists():
                raise FileNotFoundError(f"Reference audio file not found: {reference_audio_path}")
            
            with open(ref_path, 'rb') as f:
                audio_data = f.read()
            
            ref_audio = ReferenceAudio(
                audio=audio_data,
                text=reference_text or text[:100]  # Use provided text or first 100 chars
            )
            references.append(ref_audio)
            tts_request_kwargs['references'] = references
        
        tts_request = TTSRequest(**tts_request_kwargs)
        
        # Generate audio and save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            for chunk in self.session.tts(tts_request):
                f.write(chunk)
        
        return str(output_file.absolute())
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """List available models/voices from FishAudio"""
        try:
            models = self.session.list_models()
            voices = []
            
            # Handle different response formats
            if isinstance(models, list):
                for model in models:
                    if isinstance(model, str):
                        voices.append({
                            'id': model,
                            'name': model,
                            'model': model,
                        })
                    elif isinstance(model, dict):
                        voices.append({
                            'id': model.get('id') or model.get('name') or model.get('model') or model.get('reference_id'),
                            'name': model.get('name') or model.get('id') or model.get('model') or model.get('reference_id'),
                            'model': model.get('model') or model.get('id') or model.get('name') or model.get('reference_id'),
                            'description': model.get('description'),
                        })
            elif isinstance(models, dict):
                # If it's a dict with models list
                model_list = models.get('models', [])
                for model in model_list:
                    voices.append({
                        'id': model.get('id') or model.get('name') or model.get('reference_id'),
                        'name': model.get('name') or model.get('id') or model.get('reference_id'),
                        'model': model.get('model') or model.get('id') or model.get('reference_id'),
                        'description': model.get('description'),
                    })
            
            return voices if voices else [{'id': 'default', 'name': 'Default Model', 'model': 'default'}]
        except Exception as e:
            raise Exception(f"Failed to list models: {str(e)}")
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get details about a specific model/voice"""
        try:
            models = self.session.list_models()
            
            # Search for the voice_id in models
            if isinstance(models, list):
                for model in models:
                    if isinstance(model, str):
                        if model == voice_id:
                            return {'id': model, 'name': model, 'model': model}
                    elif isinstance(model, dict):
                        model_id = model.get('id') or model.get('name') or model.get('model') or model.get('reference_id')
                        if model_id == voice_id:
                            return {
                                'id': model_id,
                                'name': model.get('name') or model_id,
                                'model': model.get('model') or model_id,
                                'description': model.get('description'),
                            }
            elif isinstance(models, dict):
                model_list = models.get('models', [])
                for model in model_list:
                    model_id = model.get('id') or model.get('name') or model.get('reference_id')
                    if model_id == voice_id:
                        return {
                            'id': model_id,
                            'name': model.get('name') or model_id,
                            'model': model.get('model') or model_id,
                            'description': model.get('description'),
                        }
            
            return None
        except Exception:
            return None

