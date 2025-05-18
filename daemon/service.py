#!/usr/bin/env python3
import os
import random
import subprocess
import tempfile
import time
from pathlib import Path

COMMERCIALS_PER_BREAK = 3
AUDIO_DEVICE = "hdmi:CARD=vc4hdmi,DEV=0"

def create_alternating_playlist(source_dirs, output_file, commercials_per_break=3):
    """
    Creates an M3U playlist with random videos from multiple sources.
    Each video played is randomly selected from a source that's different
    from the source of the previously played video.
    If the commercials directory exists, multiple commercials are inserted
    between each regular video.
    
    Args:
        source_dirs: List of directory paths, each containing videos from a different source
        output_file: Path to save the M3U playlist
        commercials_per_break: Number of commercials to insert between shows (default: 3)
    """
    # Get all video files from each source
    source_videos = []
    for source_dir in source_dirs:
        videos = [os.path.join(source_dir, f) for f in os.listdir(source_dir)
                 if f.lower().endswith('.mp4')]
        # Only add sources that have videos
        if videos:
            source_videos.append(videos)
    
    # Check for commercials directory
    commercials_dir = '/media/commercials'
    commercials = []
    has_commercials = False
    
    if os.path.exists(commercials_dir) and os.path.isdir(commercials_dir):
        commercials = [os.path.join(commercials_dir, f) for f in os.listdir(commercials_dir)
                      if f.lower().endswith('.mp4')]
        if commercials:
            has_commercials = True
            print(f"Found {len(commercials)} commercials to insert between shows")
            # Shuffle commercials
            random.shuffle(commercials)
    
    # Check if we have enough sources with videos
    if len(source_videos) < 2:
        print("Need at least 2 sources with videos for alternating playback.")
        if len(source_videos) == 1:
            # Just create a regular shuffled playlist from the one source
            playlist = source_videos[0].copy()
            random.shuffle(playlist)
            print("Creating a regular shuffled playlist from the only available source.")
        else:
            print("No sources with videos found.")
            return None
    else:
        # Shuffle each list of videos
        for videos in source_videos:
            random.shuffle(videos)
        
        # Create a playlist with random alternating sources
        base_playlist = []
        
        # Keep track of videos used from each source
        used_videos = [0] * len(source_videos)
        
        # Start with a random source
        current_source = random.randint(0, len(source_videos) - 1)
        
        # Add the first video
        base_playlist.append(source_videos[current_source][0])
        used_videos[current_source] += 1
        
        # Keep adding videos until we've used all available videos
        while True:
            # Find sources that still have unused videos
            available_sources = [i for i in range(len(source_videos)) 
                               if used_videos[i] < len(source_videos[i]) and i != current_source]
            
            # If no more available sources (different from current), break
            if not available_sources:
                break
            
            # Choose a random source different from the current one
            current_source = random.choice(available_sources)
            
            # Add the next video from this source
            base_playlist.append(source_videos[current_source][used_videos[current_source]])
            used_videos[current_source] += 1
        
        # Insert commercials between videos if available
        if has_commercials:
            playlist = []
            commercial_index = 0
            
            for video in base_playlist:     
                # Add commercials_per_break commercials (if we have any)
                for _ in range(commercials_per_break):
                    # Only add a commercial if we have at least one
                    if len(commercials) > 0:
                        # Add a commercial
                        playlist.append(commercials[commercial_index])
                        commercial_index += 1
                        # If we run out of commercials, cycle back to the beginning
                        if commercial_index >= len(commercials):
                            commercial_index = 0
                            # Optionally shuffle again for more randomness
                            random.shuffle(commercials)
            	 
            	 # Add the main show video
                playlist.append(video)
        else:
            # No commercials to insert
            playlist = base_playlist
    
    # Write the M3U playlist
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for video_path in playlist:
            # Convert to absolute path and escape spaces
            abs_path = os.path.abspath(video_path)
            f.write(f"{abs_path}\n")
    
    print(f"Created playlist with {len(playlist)} videos at {output_file}")
    return output_file

def launch_vlc_with_playlist(playlist_path):
    """Launches VLC with the specified playlist using specific audio device settings.
    Returns the process object so we can monitor when it ends.
    """
    try:
        # Use cvlc with the specific audio settings for Linux
        cmd = [
            "cvlc",
            "--play-and-exit",     # Exit VLC when the playlist ends
            "--no-repeat",         # Don't repeat the playlist
            "--no-loop",           # Don't loop the playlist
            "--aout=alsa",
            "--no-osd",
            f"--alsa-audio-device={AUDIO_DEVICE}",
            playlist_path
        ]
        
        # Launch VLC and keep the process object
        vlc_process = subprocess.Popen(cmd)
        print(f"Launched cvlc with playlist: {playlist_path}")
        print(f"Using audio device: {AUDIO_DEVICE}")
        return vlc_process
    except Exception as e:
        print(f"Error launching VLC: {e}")
        return None

def main():
    """Create m3u playlists and play them continuously with vlc"""
     
    while True:
        # Find all subdirectories in the /media/shows/ directory to use as sources
        base_dir = "/media/shows/"
        try:
            source_dirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) 
                          if os.path.isdir(os.path.join(base_dir, d))]
            
            if not source_dirs:
                print(f"No directories found in {base_dir}. Please check the path.")
                return
                
            print(f"\n{'-'*60}")
            print(f"Found {len(source_dirs)} show directories to use as sources:")
            for i, dir_path in enumerate(source_dirs, 1):
                print(f"  {i}. {os.path.basename(dir_path)}")
        except FileNotFoundError:
            print(f"Directory {base_dir} not found. Please check the path.")
            return
        except PermissionError:
            print(f"Permission denied when accessing {base_dir}.")
            return
        
        # Create a temporary file for the playlist
        with tempfile.NamedTemporaryFile(suffix='.m3u', delete=False) as temp:
            playlist_path = temp.name
        
        # Create the playlist with 3 commercials per break
        create_alternating_playlist(source_dirs, playlist_path, COMMERCIALS_PER_BREAK)
        
        # Launch VLC with the playlist and wait for it to finish
        print(f"Starting playlist playback...")
        vlc_process = launch_vlc_with_playlist(playlist_path)
        
        if vlc_process:
            # Wait for the VLC process to finish
            print("Waiting for playback to complete...")
            vlc_process.wait()
            print("Playback finished. Creating a new playlist...")
        else:
            # If VLC failed to start, wait a bit before trying again
            print("Failed to start VLC. Trying again in 30 seconds...")
            time.sleep(30)
        
        # Clean up the temporary file
        try:
            os.remove(playlist_path)
            print(f"Removed temporary playlist file: {playlist_path}")
        except Exception as e:
            print(f"Failed to remove temporary file: {e}")
            pass

if __name__ == "__main__":
    main()