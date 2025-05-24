import torch
import torch.backends.cudnn
from spleeter.separator import Separator
from pathlib import Path
from typing import Dict, List
from src.utils.gpu_utils import get_gpu_device

class StemSeparator:
    def __init__(self):
        self.device = get_gpu_device()
        self.separator = Separator('spleeter:5stems', stft_backend='torch', device=self.device)

    async def separate_stems(self, audio_path: Path) -> Dict[str, Path]:
        """Separate audio into stems using spleeter"""
        try:
            # Create output directory
            output_dir = audio_path.parent / "stems"
            output_dir.mkdir(exist_ok=True)

            # Separate stems
            self.separator.separate_to_file(
                str(audio_path),
                str(output_dir),
                synchronous=False
            )

            # Wait for separation to complete
            while not (output_dir / f"{audio_path.stem}_vocals.wav").exists():
                await asyncio.sleep(1)

            # Return paths to separated stems
            stems = {
                'vocals': output_dir / f"{audio_path.stem}_vocals.wav",
                'bass': output_dir / f"{audio_path.stem}_bass.wav",
                'drums': output_dir / f"{audio_path.stem}_drums.wav",
                'guitar1': output_dir / f"{audio_path.stem}_other.wav",
                'guitar2': output_dir / f"{audio_path.stem}_piano.wav"
            }

            return stems

        except Exception as e:
            raise Exception(f"Error separating stems: {str(e)}")
