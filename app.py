import pyaudio
import wave
import os
from pydub import AudioSegment
import numpy as np
import threading
import time

class MultiSpeakerPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.chunk_size = 1024
        self.active_streams = []
        self.is_playing = False
        self.play_thread = None
        
    def load_audio(self, mp3_file):
        """Load and prepare audio data"""
        print(f"Loading {mp3_file}...")
        audio = AudioSegment.from_mp3(mp3_file)
        print("Audio loaded successfully")
        return audio
    
    def create_stream(self, device_index, audio_format, channels, rate):
        """Create an audio stream for a specific device"""
        device_info = self.p.get_device_info_by_index(device_index)
        print(f"Creating stream for {device_info['name']}")
        
        stream = self.p.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=device_index,
            frames_per_buffer=self.chunk_size
        )
        return stream
    
    def play_chunk(self, streams, chunk):
        """Play a single chunk on all streams"""
        for stream in streams:
            if stream and not stream.is_stopped():
                try:
                    stream.write(chunk)
                except Exception as e:
                    print(f"Error writing to stream: {e}")
    
    def play_on_devices(self, mp3_file, device_indices):
        """Play audio on multiple devices"""
        try:
            # Load audio
            audio = self.load_audio(mp3_file)
            print("Converting audio format...")
            
            # Create streams for all devices
            streams = []
            for idx in device_indices:
                try:
                    stream = self.create_stream(
                        idx,
                        self.p.get_format_from_width(audio.sample_width),
                        audio.channels,
                        audio.frame_rate
                    )
                    streams.append(stream)
                    print(f"Stream created for device {idx}")
                except Exception as e:
                    print(f"Error creating stream for device {idx}: {e}")
                    continue
            
            if not streams:
                print("No streams could be created")
                return
            
            # Get audio data as raw bytes
            print("Preparing audio chunks...")
            samples = np.array(audio.get_array_of_samples())
            
            # Calculate total chunks for progress tracking
            total_chunks = len(samples) // self.chunk_size
            print(f"Total chunks to play: {total_chunks}")
            
            print("\nStarting playback...")
            start_time = time.time()
            
            # Play audio chunks
            for i in range(0, len(samples), self.chunk_size):
                chunk = samples[i:i + self.chunk_size].tobytes()
                self.play_chunk(streams, chunk)
                
                # Show progress every 10%
                if i % (total_chunks // 10 * self.chunk_size) == 0:
                    progress = (i / len(samples)) * 100
                    elapsed = time.time() - start_time
                    print(f"Progress: {progress:.1f}% (Time elapsed: {elapsed:.1f}s)")
            
            print("\nPlayback completed!")
            
            # Cleanup
            for stream in streams:
                stream.stop_stream()
                stream.close()
            
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            print("Cleaning up resources...")
            self.cleanup()
    
    def list_audio_devices(self):
        """List all available audio output devices"""
        print("\nAvailable Audio Output Devices:")
        valid_outputs = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                print(f"Index {i}: {device_info['name']}")
                valid_outputs.append(i)
        return valid_outputs
    
    def cleanup(self):
        """Clean up resources"""
        self.p.terminate()

def main():
    try:
        # Create player instance
        player = MultiSpeakerPlayer()
        
        # List available devices
        player.list_audio_devices()
        
        # Select devices for playback
        device_indices = [4, 5]  # Modify these indices based on your devices
        
        print(f"\nSelected devices: {device_indices}")
        player.play_on_devices("testMusic.mp3", device_indices)
        
    except Exception as e:
        print(f"Error in main: {e}")
        
if __name__ == "__main__":
    main()

import pyaudio
import wave
import os
from pydub import AudioSegment
import numpy as np
import time

class MultiSpeakerPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.chunk_size = 1024
        
    def load_audio(self, mp3_file):
        """Load and prepare audio data"""
        print(f"Loading {mp3_file}...")
        audio = AudioSegment.from_mp3(mp3_file)
        print("Audio loaded successfully")
        return audio
    
    def create_stream(self, device_index, audio_format, channels, rate):
        """Create an audio stream for a specific device"""
        device_info = self.p.get_device_info_by_index(device_index)
        print(f"Creating stream for {device_info['name']}")
        
        stream = self.p.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=device_index,
            frames_per_buffer=self.chunk_size
        )
        return stream
    
    def play_chunk(self, streams, chunk):
        """Play a single chunk on all streams"""
        for stream in streams:
            if stream:
                try:
                    stream.write(chunk)
                except Exception as e:
                    print(f"Error writing to stream: {e}")
    
    def play_on_devices(self, mp3_file, device_indices):
        """Play audio on multiple devices"""
        try:
            # Load audio
            audio = self.load_audio(mp3_file)
            print("Converting audio format...")
            
            # Create streams for all devices
            streams = []
            for idx in device_indices:
                try:
                    stream = self.create_stream(
                        idx,
                        self.p.get_format_from_width(audio.sample_width),
                        audio.channels,
                        audio.frame_rate
                    )
                    streams.append(stream)
                    print(f"Stream created for device {idx}")
                except Exception as e:
                    print(f"Error creating stream for device {idx}: {e}")
                    streams.append(None)
                    continue
            
            # Check if any streams were created successfully
            active_streams = [s for s in streams if s is not None]
            if not active_streams:
                print("No streams could be created")
                return
            
            # Get audio data as raw bytes
            print("Preparing audio chunks...")
            samples = np.array(audio.get_array_of_samples())
            
            # Calculate total chunks
            total_chunks = len(samples) // self.chunk_size
            print(f"Total chunks to play: {total_chunks}")
            
            print("\nStarting playback...")
            start_time = time.time()
            
            # Play audio chunks
            for i in range(0, len(samples), self.chunk_size):
                chunk = samples[i:i + self.chunk_size].tobytes()
                self.play_chunk(active_streams, chunk)
                
                # Show progress every 10%
                if i % (total_chunks // 10 * self.chunk_size) == 0:
                    progress = (i / len(samples)) * 100
                    elapsed = time.time() - start_time
                    print(f"Progress: {progress:.1f}% (Time elapsed: {elapsed:.1f}s)")
            
            print("\nPlayback completed!")
            
            # Cleanup
            for stream in active_streams:
                if stream:
                    stream.stop_stream()
                    stream.close()
            
        except Exception as e:
            print(f"Error during playback: {e}")
            print(f"Error details: {type(e).__name__}")
        finally:
            print("Cleaning up resources...")
            self.cleanup()
    
    def list_audio_devices(self):
        """List all available audio output devices"""
        print("\nAvailable Audio Output Devices:")
        valid_outputs = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                print(f"Index {i}: {device_info['name']}")
                valid_outputs.append(i)
        return valid_outputs
    
    def cleanup(self):
        """Clean up resources"""
        self.p.terminate()

def main():
    try:
        # Create player instance
        player = MultiSpeakerPlayer()
        
        # List available devices
        valid_devices = player.list_audio_devices()
        
        print("\nEnter the device indices you want to use (comma-separated):")
        device_indices = input().strip().split(',')
        device_indices = [int(idx) for idx in device_indices]
        
        print(f"\nSelected devices: {device_indices}")
        player.play_on_devices("testMusic.mp3", device_indices)
        
    except Exception as e:
        print(f"Error in main: {e}")
        
if __name__ == "__main__":
    main()