"""ElevenLabs TTS provider implementation"""
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
except ImportError:
    ElevenLabs = None
    Voice = None
    VoiceSettings = None

from typing import List, Dict, Any, Optional
from pathlib import Path
from ffmcp.voiceover.base import BaseTTSProvider


class ElevenLabsProvider(BaseTTSProvider):
    """ElevenLabs TTS provider"""
    
    def __init__(self, config):
        if ElevenLabs is None:
            raise ImportError("elevenlabs package not installed. Install with: pip install elevenlabs")
        super().__init__(config)
        self.client = ElevenLabs(api_key=self.api_key)
    
    def get_provider_name(self) -> str:
        return 'elevenlabs'
    
    def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice_id: str,
        **kwargs
    ) -> str:
        """Convert text to speech using ElevenLabs"""
        model_id = kwargs.get('model_id', 'eleven_multilingual_v2')
        stability = kwargs.get('stability', 0.5)
        similarity_boost = kwargs.get('similarity_boost', 0.75)
        style = kwargs.get('style', 0.0)
        use_speaker_boost = kwargs.get('use_speaker_boost', True)
        output_format = kwargs.get('output_format', 'mp3_44100_128')
        
        # Create voice settings
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost
        )
        
        # Generate audio
        audio = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=model_id,
            voice_settings=voice_settings,
            output_format=output_format,
        )
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            for chunk in audio:
                f.write(chunk)
        
        return str(output_file.absolute())
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices from ElevenLabs"""
        try:
            voices_response = self.client.voices.get_all()
            voices = []
            
            for voice in voices_response.voices:
                voice_dict = {
                    'id': voice.voice_id,
                    'name': voice.name,
                    'category': getattr(voice, 'category', None),
                    'description': getattr(voice, 'description', None),
                    'preview_url': getattr(voice, 'preview_url', None),
                    'labels': getattr(voice, 'labels', {}),
                }
                voices.append(voice_dict)
            
            return voices
        except Exception as e:
            # If API call fails, return empty list or re-raise
            raise Exception(f"Failed to list voices: {str(e)}")
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get details about a specific voice"""
        try:
            voice = self.client.voices.get(voice_id=voice_id)
            return {
                'id': voice.voice_id,
                'name': voice.name,
                'category': getattr(voice, 'category', None),
                'description': getattr(voice, 'description', None),
                'preview_url': getattr(voice, 'preview_url', None),
                'labels': getattr(voice, 'labels', {}),
            }
        except Exception:
            return None
    
    def create_voice(
        self,
        name: str,
        description: Optional[str] = None,
        files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a custom voice (requires files)"""
        if not files:
            raise ValueError("Files are required to create a voice")
        
        voice = self.client.voices.add(
            name=name,
            description=description,
            files=[Path(f) for f in files],
        )
        
        return {
            'id': voice.voice_id,
            'name': voice.name,
            'description': getattr(voice, 'description', None),
        }
    
    def delete_voice(self, voice_id: str) -> bool:
        """Delete a custom voice"""
        try:
            self.client.voices.delete(voice_id=voice_id)
            return True
        except Exception:
            return False
    
    def edit_voice(
        self,
        voice_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Edit a custom voice"""
        updates = {}
        if name is not None:
            updates['name'] = name
        if description is not None:
            updates['description'] = description
        if files is not None:
            updates['files'] = [Path(f) for f in files]
        
        if not updates:
            raise ValueError("At least one field must be provided to update")
        
        voice = self.client.voices.edit(
            voice_id=voice_id,
            **updates
        )
        
        return {
            'id': voice.voice_id,
            'name': voice.name,
            'description': getattr(voice, 'description', None),
        }

