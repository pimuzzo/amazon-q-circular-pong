#!/usr/bin/env python3
"""
Circular Pong Game
A retro-style single-player game where the paddle moves along a semicircle
and the ball bounces within a full circle.
"""

import pygame
import math
import sys
import random
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (retro green theme)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (50, 255, 50)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)
BLUE = (0, 0, 255)
BRIGHT_BLUE = (50, 50, 255)

# Game settings
CIRCLE_RADIUS = 250
CIRCLE_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
PADDLE_LENGTH = 60
PADDLE_THICKNESS = 8
BALL_RADIUS = 8
BALL_SPEED = 5
PADDLE_SPEED = 3


def generate_beep_sound(frequency, duration, sample_rate=22050):
    """Generate a simple beep sound"""
    frames = int(duration * sample_rate)
    arr = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
    arr = (arr * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)  # Make stereo
    sound = pygame.sndarray.make_sound(arr)
    return sound

def generate_noise_sound(duration, sample_rate=22050):
    """Generate a noise sound for game over"""
    frames = int(duration * sample_rate)
    arr = np.random.randint(-2000, 2000, (frames, 2), dtype=np.int16)
    sound = pygame.sndarray.make_sound(arr)
    return sound


class Ball:
    """Ball class that handles ball physics and rendering"""
    
    def __init__(self, x, y, game=None):
        self.x = x
        self.y = y
        # Always start moving towards red semicircle (180°-360°)
        self.dx = random.choice([-1, 1]) * BALL_SPEED * random.uniform(0.7, 1.0)
        self.dy = -abs(random.uniform(0.7, 1.0)) * BALL_SPEED  # Always negative (upward)
        self.radius = BALL_RADIUS
        self.game = game  # Reference to game for sound effects
        
    def update(self):
        """Update ball position and handle circular boundary collision"""
        # Move ball
        self.x += self.dx
        self.y += self.dy
        
        # Check collision with circular boundary
        center_x, center_y = CIRCLE_CENTER
        distance_from_center = math.sqrt((self.x - center_x)**2 + (self.y - center_y)**2)
        
        if distance_from_center + self.radius >= CIRCLE_RADIUS:
            # Play wall bounce sound
            if self.game and self.game.sounds_enabled:
                self.game.wall_sound.play()
            
            # Calculate reflection off circular boundary
            # Vector from center to ball
            normal_x = (self.x - center_x) / distance_from_center
            normal_y = (self.y - center_y) / distance_from_center
            
            # Reflect velocity vector
            dot_product = self.dx * normal_x + self.dy * normal_y
            self.dx = self.dx - 2 * dot_product * normal_x
            self.dy = self.dy - 2 * dot_product * normal_y
            
            # Move ball back inside circle
            self.x = center_x + normal_x * (CIRCLE_RADIUS - self.radius)
            self.y = center_y + normal_y * (CIRCLE_RADIUS - self.radius)
    
    def draw(self, screen):
        """Draw the ball"""
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        # Add a small glow effect
        pygame.draw.circle(screen, BRIGHT_GREEN, (int(self.x), int(self.y)), self.radius + 2, 1)


class Paddle:
    """Paddle class that moves along the semicircle"""
    
    def __init__(self):
        self.angle = math.pi / 2  # Always start at 90 degrees (green)
        self.length = PADDLE_LENGTH
        self.thickness = PADDLE_THICKNESS
        
    def update(self, keys):
        """Update paddle position based on input"""
        if keys[pygame.K_LEFT]:
            self.angle += PADDLE_SPEED * 0.02  # Convert to radians
        if keys[pygame.K_RIGHT]:
            self.angle -= PADDLE_SPEED * 0.02
            
        # Constrain paddle to green semicircle (0° to 180°) that it protects
        if self.angle > math.pi:
            self.angle = math.pi
        elif self.angle < 0:
            self.angle = 0
    
    def get_position(self):
        """Get paddle center position"""
        center_x, center_y = CIRCLE_CENTER
        paddle_radius = CIRCLE_RADIUS - self.thickness // 2
        x = center_x + paddle_radius * math.cos(self.angle)
        y = center_y + paddle_radius * math.sin(self.angle)
        return x, y
    
    def get_endpoints(self):
        """Get paddle start and end points for collision detection"""
        center_x, center_y = CIRCLE_CENTER
        paddle_radius = CIRCLE_RADIUS - self.thickness // 2
        
        # Calculate half-length in radians
        half_length_radians = (self.length / 2) / paddle_radius
        
        # Start and end angles
        start_angle = self.angle - half_length_radians
        end_angle = self.angle + half_length_radians
        
        # Calculate positions
        start_x = center_x + paddle_radius * math.cos(start_angle)
        start_y = center_y + paddle_radius * math.sin(start_angle)
        end_x = center_x + paddle_radius * math.cos(end_angle)
        end_y = center_y + paddle_radius * math.sin(end_angle)
        
        return (start_x, start_y), (end_x, end_y)
    
    def draw(self, screen):
        """Draw the paddle"""
        start_pos, end_pos = self.get_endpoints()
        pygame.draw.line(screen, GREEN, start_pos, end_pos, self.thickness)
        # Add glow effect
        pygame.draw.line(screen, BRIGHT_GREEN, start_pos, end_pos, self.thickness + 2)


class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Circular Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize sounds
        try:
            # Check if pygame mixer is properly initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            print("Generating sounds...")
            self.paddle_sound = generate_beep_sound(800, 0.1)  # High pitch beep for paddle
            self.wall_sound = generate_beep_sound(400, 0.15)   # Lower pitch for wall bounce
            self.life_lost_sound = generate_beep_sound(200, 0.3)  # Low pitch for life loss
            self.game_over_sound = generate_noise_sound(0.5)   # Noise for game over
            self.sounds_enabled = True
            print("Sound initialization successful!")
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            print("Continuing without sound...")
            self.sounds_enabled = False
        
        # Game objects
        self.ball = Ball(CIRCLE_CENTER[0], CIRCLE_CENTER[1] - 50, self)
        self.paddle = Paddle()
        
        # Game state
        self.score = 0
        self.bounces = 0
        self.lives = 3
        self.life_lost = False  # Flag to prevent multiple life losses
        self.paddle_collision_cooldown = 0  # Prevent multiple paddle hits
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
        
    def check_paddle_collision(self):
        """Check if ball collides with paddle - returns True if collision occurred"""
        # Decrease cooldown timer
        if self.paddle_collision_cooldown > 0:
            self.paddle_collision_cooldown -= 1
            return False  # Skip collision check during cooldown
        
        # Get paddle endpoints
        start_pos, end_pos = self.paddle.get_endpoints()
        
        # Check distance from ball to paddle line segment
        ball_pos = (self.ball.x, self.ball.y)
        distance = self.point_to_line_distance(ball_pos, start_pos, end_pos)
        
        if distance <= self.ball.radius + self.paddle.thickness // 2:
            # Play paddle hit sound
            if self.sounds_enabled:
                self.paddle_sound.play()
            
            # Collision detected - reflect ball
            # Calculate normal vector of paddle
            paddle_dx = end_pos[0] - start_pos[0]
            paddle_dy = end_pos[1] - start_pos[1]
            paddle_length = math.sqrt(paddle_dx**2 + paddle_dy**2)
            
            # Normal vector (perpendicular to paddle)
            normal_x = -paddle_dy / paddle_length
            normal_y = paddle_dx / paddle_length
            
            # Reflect ball velocity
            dot_product = self.ball.dx * normal_x + self.ball.dy * normal_y
            self.ball.dx = self.ball.dx - 2 * dot_product * normal_x
            self.ball.dy = self.ball.dy - 2 * dot_product * normal_y
            
            # Add some randomness to prevent predictable patterns
            self.ball.dx += random.uniform(-0.5, 0.5)
            self.ball.dy += random.uniform(-0.5, 0.5)
            
            # Normalize speed
            speed = math.sqrt(self.ball.dx**2 + self.ball.dy**2)
            self.ball.dx = (self.ball.dx / speed) * BALL_SPEED
            self.ball.dy = (self.ball.dy / speed) * BALL_SPEED
            
            self.bounces += 1
            self.paddle_collision_cooldown = 10  # Set cooldown (10 frames)
            return True  # Collision occurred
        return False  # No collision
    
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line start to end
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            # Line is a point
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Parameter t for closest point on line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))
        
        # Closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Distance from point to closest point
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    
    def check_game_over(self):
        """Check if ball crossed the green area without hitting paddle"""
        center_x, center_y = CIRCLE_CENTER
        
        # Calculate distance from center and angle
        distance_from_center = math.sqrt((self.ball.x - center_x)**2 + (self.ball.y - center_y)**2)
        ball_angle = math.atan2(self.ball.y - center_y, self.ball.x - center_x)
        if ball_angle < 0:
            ball_angle += 2 * math.pi
        
        # Check if ball is very close to the circular boundary in the green semicircle
        if distance_from_center >= CIRCLE_RADIUS - self.ball.radius - 5:  # Close to boundary
            # Check if ball is trying to enter the green semicircle (0° to 180°) that paddle protects
            if 0 <= ball_angle <= math.pi and not self.life_lost:
                print(f"Ball hit green boundary at {math.degrees(ball_angle):.1f}° - losing life!")
                # Player missed the ball - lose a life
                self.lives -= 1
                self.life_lost = True  # Prevent multiple life losses
                
                # Play appropriate sound
                if self.sounds_enabled:
                    if self.lives <= 0:
                        self.game_over_sound.play()
                    else:
                        self.life_lost_sound.play()
                
                if self.lives <= 0:
                    self.game_over = True
                else:
                    # Reset ball position for next life after a short delay
                    pygame.time.wait(500)  # Brief pause
                    self.reset_ball()
                    self.life_lost = False  # Reset flag for next round
    
    def reset_ball(self):
        """Reset ball to center position with velocity directed towards red semicircle"""
        self.ball = Ball(CIRCLE_CENTER[0], CIRCLE_CENTER[1] - 50, self)
        # Direct ball towards red semicircle (180° to 360°)
        # Set velocity to go upward and slightly to one side
        self.ball.dx = random.choice([-1, 1]) * BALL_SPEED * random.uniform(0.5, 0.8)
        self.ball.dy = -abs(random.uniform(0.6, 1.0)) * BALL_SPEED  # Always negative (upward)
    
    def update(self):
        """Update game state"""
        if not self.game_over:
            keys = pygame.key.get_pressed()
            
            # Update game objects
            self.paddle.update(keys)
            self.ball.update()
            
            # Check paddle collision first - if ball hits paddle, don't lose life
            paddle_hit = self.check_paddle_collision()
            
            # Only check for life loss if paddle was NOT hit
            if not paddle_hit:
                self.check_game_over()
            
            # Update score (time survived)
            current_time = pygame.time.get_ticks()
            self.score = (current_time - self.start_time) // 1000
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        # Draw circular boundary
        pygame.draw.circle(self.screen, DARK_GREEN, CIRCLE_CENTER, CIRCLE_RADIUS, 3)
        
        # Draw center line to show the boundary
        pygame.draw.line(self.screen, (100, 100, 0), 
                        (CIRCLE_CENTER[0] - CIRCLE_RADIUS, CIRCLE_CENTER[1]),
                        (CIRCLE_CENTER[0] + CIRCLE_RADIUS, CIRCLE_CENTER[1]), 2)
        
        # Draw red upper semicircle (180° to 360°) - safe zone for ball
        pygame.draw.arc(self.screen, RED, 
                       (CIRCLE_CENTER[0] - CIRCLE_RADIUS, CIRCLE_CENTER[1] - CIRCLE_RADIUS,
                        CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2),
                       0, math.pi, 4)
        
        # Highlight the bottom semicircle in green (0° to 180°) where paddle moves and protects
        pygame.draw.arc(self.screen, BRIGHT_GREEN, 
                       (CIRCLE_CENTER[0] - CIRCLE_RADIUS, CIRCLE_CENTER[1] - CIRCLE_RADIUS,
                        CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2),
                       math.pi, 2 * math.pi, 1)
        
        # Draw game objects
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw UI
        score_text = self.font.render(f"Time: {self.score}s", True, GREEN)
        bounces_text = self.font.render(f"Bounces: {self.bounces}", True, GREEN)
        lives_text = self.font.render(f"Lives: {self.lives}", True, GREEN)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(bounces_text, (10, 50))
        self.screen.blit(lives_text, (10, 90))
        
        # Draw instructions
        if self.score < 3:  # Show instructions for first 3 seconds
            instructions = [
                "Use LEFT/RIGHT arrows to move paddle",
                "Keep the ball from entering the green semicircle!",
                "Survive as long as possible!"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 25))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            final_score_text = self.font.render(f"Final Time: {self.score}s", True, GREEN)
            final_bounces_text = self.font.render(f"Total Bounces: {self.bounces}", True, GREEN)
            final_lives_text = self.font.render(f"Lives Used: {3 - self.lives}/3", True, GREEN)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            
            # Center the text
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            bounces_rect = final_bounces_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            lives_rect = final_lives_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(final_score_text, score_rect)
            self.screen.blit(final_bounces_text, bounces_rect)
            self.screen.blit(final_lives_text, lives_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def restart(self):
        """Restart the game"""
        self.ball = Ball(CIRCLE_CENTER[0], CIRCLE_CENTER[1] - 50, self)  # Pass game reference
        self.paddle = Paddle()
        self.score = 0
        self.bounces = 0
        self.lives = 3
        self.life_lost = False
        self.paddle_collision_cooldown = 0
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.restart()
            
            # Update and draw
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
