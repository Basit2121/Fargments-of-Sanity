import eel
import vlc
import google.generativeai as genai
import re
import random
import os
import logging
from pydub import AudioSegment
from pydub.playback import play
import psutil
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
class Config:
    API_KEY = 'YOUR API KEY'
    AUDIO_FILE = "assets\\audBG.mp3"
    AUDIO_VOLUME = 30
    WINDOW_SIZE = (1280, 720)
    MAX_MOVES = 50
    
    # Game settings
    MAX_RESPONSE_LINES = 2
    MAX_RESPONSE_WORDS = 20
    
    # Safety settings
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    # Fallback responses when AI fails
    FALLBACK_RESPONSES = [
        "*Ignores you.*",
        "*Doesn't respond.*", 
        "*No response.*",
        "*Pretends to not hear you.*"
    ]
    
    # Words to check for victory condition
    VICTORY_WORDS = ["open", "door"]
    VICTORY_EXCLUDE_WORDS = [
        "not", "cant", "cannot", "can't", "wont", "will not", "unable", 
        "don't", "wouldn't", "couldn't", "shouldn't", "mustn't", "won't", 
        "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", 
        "hadn't", "doesn't", "didn't", "sealed", "closed", "remains", "unopened"
    ]

class AudioManager:
    def __init__(self):
        self.player: Optional[vlc.MediaPlayer] = None
        self.audio_file = Config.AUDIO_FILE
        
    def play_background_audio(self, audio_path: str = None) -> bool:
        """Play background audio with error handling"""
        try:
            if audio_path:
                self.audio_file = audio_path
                
            if not os.path.exists(self.audio_file):
                logger.error(f"Audio file not found: {self.audio_file}")
                return False
                
            self.player = vlc.MediaPlayer(self.audio_file)
            self.player.play()
            self.player.audio_set_volume(Config.AUDIO_VOLUME)
            
            # Set up event manager for looping
            event_manager = self.player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._restart_audio)
            
            logger.info(f"Playing background audio: {self.audio_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def _restart_audio(self, event):
        """Restart audio when it ends"""
        try:
            if self.player:
                self.player.stop()
                self.play_background_audio()
        except Exception as e:
            logger.error(f"Error restarting audio: {e}")
    
    def stop_audio(self):
        """Stop audio playback"""
        try:
            if self.player:
                self.player.stop()
                self.player = None
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")

class GameLogic:
    def __init__(self):
        self.chat: Optional[Any] = None
        self.username: Optional[str] = None
        self.move_count: int = 0
        self.audio_manager = AudioManager()
        
    def initialize_ai(self) -> bool:
        """Initialize the AI model with error handling"""
        try:
            genai.configure(api_key=Config.API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat = model.start_chat()
            logger.info("AI model initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            return False
    
    def start_game(self, username: str) -> bool:
        """Start a new game session"""
        try:
            self.username = username
            self.move_count = 0
            
            if not self.initialize_ai():
                return False
                
            game_prompt = self._create_game_prompt(username)
            
            # Retry logic for AI initialization
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.chat.send_message(game_prompt, safety_settings=Config.SAFETY_SETTINGS)
                    logger.info(f"Game started for user: {username}")
                    return True
                except Exception as e:
                    logger.warning(f"AI initialization attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        logger.error("Failed to initialize AI after all retries")
                        return False
                    continue
                    
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            return False
    
    def _create_game_prompt(self, username: str) -> str:
        """Create the game prompt for the AI"""
        return (
            f"Lets play a game. I want you to act like a Yandere (Never mention that you are a yandere), "
            f"Your name will be Maya. In my game, I (my name is {username}) will try to convince Maya to open a door. "
            f"Maya refuses. Responses: No more than {Config.MAX_RESPONSE_LINES} line, max {Config.MAX_RESPONSE_WORDS} words. "
            f"respond with the response that maya would give in a conversation, no extra information"
        )
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and return response with game state"""
        try:
            self.move_count += 1
            
            if self.move_count > Config.MAX_MOVES:
                return {
                    "response": "You've run out of moves. Game over.",
                    "game_won": False,
                    "moves_remaining": 0
                }
            
            if not self.chat:
                logger.error("Chat session not initialized")
                return {
                    "response": random.choice(Config.FALLBACK_RESPONSES),
                    "game_won": False,
                    "moves_remaining": Config.MAX_MOVES - self.move_count
                }
            
            # Get AI response
            response = self.chat.send_message(user_message, safety_settings=Config.SAFETY_SETTINGS)
            maya_response = response.text.replace("\"", "").strip()
            
            # Check for victory condition
            game_won = self._check_victory_condition(maya_response)
            
            return {
                "response": maya_response,
                "game_won": game_won,
                "moves_remaining": Config.MAX_MOVES - self.move_count
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": random.choice(Config.FALLBACK_RESPONSES),
                "game_won": False,
                "moves_remaining": Config.MAX_MOVES - self.move_count
            }
    
    def _check_victory_condition(self, response: str) -> bool:
        """Check if the response indicates victory"""
        try:
            include_pattern = "|".join(Config.VICTORY_WORDS)
            exclude_pattern = "|".join(Config.VICTORY_EXCLUDE_WORDS)
            
            include_regex = re.compile(include_pattern, re.IGNORECASE)
            exclude_regex = re.compile(exclude_pattern, re.IGNORECASE)
            
            return bool(include_regex.search(response) and not exclude_regex.search(response))
            
        except Exception as e:
            logger.error(f"Error checking victory condition: {e}")
            return False

# Global game instance
game_logic = GameLogic()

def is_chrome_running() -> bool:
    """Check if Chrome is currently running"""
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'chrome.exe':
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking Chrome status: {e}")
        return False

# Eel exposed functions
@eel.expose
def play_bg_audio(audio_path: str = None) -> bool:
    """Play background audio"""
    return game_logic.audio_manager.play_background_audio(audio_path)

@eel.expose
def game(username: str) -> bool:
    """Start a new game"""
    return game_logic.start_game(username)

@eel.expose
def main_chat(user_message: str) -> bool:
    """Process user message and return game state"""
    try:
        result = game_logic.process_message(user_message)
        
        # Display response to frontend
        eel.displayResponse(result["response"])
        
        # Update move counter if available
        try:
            eel.updateMoveCount(result["moves_remaining"])
        except:
            pass  # Frontend might not have this function
        
        return result["game_won"]
        
    except Exception as e:
        logger.error(f"Error in main_chat: {e}")
        eel.displayResponse(random.choice(Config.FALLBACK_RESPONSES))
        return False

def main():
    """Main application entry point"""
    try:
        logger.info("Starting Fragments of Sanity application")
        
        # Initialize Eel
        eel.init('assets')
        
        # Start the application
        if is_chrome_running():
            eel.start('index.html', size=Config.WINDOW_SIZE)
        else:
            eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])
            
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

if __name__ == "__main__":
    main()