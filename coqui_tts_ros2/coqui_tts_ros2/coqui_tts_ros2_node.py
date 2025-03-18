#!/usr/bin/env python3
import tempfile
import subprocess
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
import torch
import time

# Patch torch.load to disable weights_only
_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from TTS.api import TTS
from coqui_tts_ros2_interfaces.action import TTS as TTSAction
from std_msgs.msg import Bool

import builtins
# Automatically confirm license prompt by returning 'y' for any input call.
builtins.input = lambda prompt='': 'y'

class TTSNode(Node):
    def __init__(self):
        super().__init__('coqui_tts_ros2')
        # Declare parameters.
        self.declare_parameter('model', 'tts_models/en/ljspeech/glow-tts')
        self.declare_parameter('device', 'cuda')

        # Get parameter values.
        model = self.get_parameter('model').get_parameter_value().string_value
        device = self.get_parameter('device').get_parameter_value().string_value

        # Check device.
        if device == 'cuda' and not torch.cuda.is_available():
            raise RuntimeError('CUDA is not available, please set device=cpu')
        elif device != 'cpu' and device != 'cuda':
            raise ValueError(f'Unknown device: {device}\nSupported devices: [cpu, cuda]')

        self.get_logger().info(f'Using device: {device}')
        self.get_logger().info(f'Using model: {model}')
        
        # Initialize TTS
        self.tts = TTS(model).to(device)

        # Initialize TTS State Publisher
        self.tts_state_publisher = self.create_publisher(Bool, '~/tts_state', 10)

        # Initialize ActionServer
        self.action_server = ActionServer(
            self,
            TTSAction,
            '~/tts',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        self.get_logger().info('Coqui TTS ROS2 started')

    def execute_callback(self, goal_handle):
        # Send initial feedback: STARTED
        feedback_msg = TTSAction.Feedback()
        feedback_msg.stage = TTSAction.Feedback.STARTED
        goal_handle.publish_feedback(feedback_msg)

        # Handle parameters
        text = goal_handle.request.text
        if text == '': # If text is empty, abort
            goal_handle.abort()
            return
        self.get_logger().info(f'Generating audio for text: {text}')

        speaker = goal_handle.request.speaker
        if speaker == '':
            speaker = None
        
        language = goal_handle.request.language
        if language == '':
            language = None

        speaker_wave = goal_handle.request.speaker_wave
        if speaker_wave == '':
            speaker_wave = None

        emotion = goal_handle.request.emotion
        if emotion == '':
            emotion = None
        speed = goal_handle.request.speed
        if speed == 0.0:
            speed = None #defaults to 1.0 later
        split_sentences = not goal_handle.request.dont_split_sentences
        wait_before_speaking = goal_handle.request.wait_before_speaking

        # Record time before generating audio.
        start_time = time.time()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp_file:
            wav_path = tmp_file.name
            try: # Generate audio
                self.tts.tts_to_file(text=text, 
                                     speaker=speaker,
                                     language=language,
                                     speaker_wav=speaker_wave,
                                     emotion=emotion,
                                     speed=speed,
                                     split_sentences=split_sentences,
                                     file_path=wav_path)
                self.get_logger().info(f'Audio written to {wav_path}')
                # Send feedback: GENERATED_AUDIO
                feedback_msg.stage = TTSAction.Feedback.GENERATED_AUDIO
                goal_handle.publish_feedback(feedback_msg)

            except Exception as e:
                error_msg = f"Failed to generate audio: {e}"
                self.get_logger().error(error_msg)
                goal_handle.abort()
                result = TTSAction.Result()
                result.success = False
                result.message = error_msg
                return result
            
            # Calculate generation time and wait for the remaining time if needed.
            generation_time = time.time() - start_time
            remaining_wait = wait_before_speaking - generation_time
            if remaining_wait > 0:
                self.get_logger().info(f'Waiting {remaining_wait:.2f} seconds before speaking.')
                time.sleep(remaining_wait)
            # Send feedback: WAIT_DONE
            feedback_msg.stage = TTSAction.Feedback.WAIT_DONE
            goal_handle.publish_feedback(feedback_msg)
            
            try: # Play audio using aplay
                self.get_logger().info("Playing audio...")
                self.tts_state_publisher.publish(Bool(data=True))
                subprocess.run(["aplay", wav_path], check=True)
                self.tts_state_publisher.publish(Bool(data=False))
                self.get_logger().info("Audio played successfully.")
                # Send feedback: AUDIO_PLAYED
                feedback_msg.stage = TTSAction.Feedback.AUDIO_PLAYED
                goal_handle.publish_feedback(feedback_msg)
        
            except Exception as e:
                error_msg = f"Failed to play audio: {e}"
                self.get_logger().error(error_msg)
                goal_handle.abort()
                result = TTSAction.Result()
                result.success = False
                result.message = error_msg
                return result
            
            goal_handle.succeed()
            result = TTSAction.Result()
            result.success = True
            result.message = "TTS conversion and playback completed."
            return result

    def goal_callback(self, goal_request):
        self.get_logger().info('Received new TTS goal.')
        return rclpy.action.GoalResponse.ACCEPT
    
    def cancel_callback(self, goal_handle):
        self.get_logger().info('Canceling TTS goal.')
        return CancelResponse.ACCEPT

def main(args=None):
    rclpy.init(args=args)
    node = TTSNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
