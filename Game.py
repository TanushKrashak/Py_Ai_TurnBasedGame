import random
import time
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

# Animation settings
TEXT_DELAY = 0.01  # Delay between characters in seconds
LINE_DELAY = 0.5   # Delay between lines in seconds

def print_animated(text: str, delay: float = TEXT_DELAY, end: str = '\n'):
    """Print text with animated effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print(end=end)

def print_line_delay(delay: float = LINE_DELAY):
    """Add delay between lines"""
    time.sleep(delay)

class Character(ABC):
    def __init__(self, name: str, character_class: str):
        self.name = name
        self.character_class = character_class
        self.max_health = 100
        self.health = self.max_health
        self.defense = 10
        self.attack = 15
        self.dodge_chance = 20
        self.stamina = 100
        self.max_stamina = 100
        self.critical_hit_chance = 15
        self.speed = 10
        self.ultimate_cooldown = 0
        self.ultimate_cooldown_max = 3
        self.defend_bonus = 0
        self.dodge_bonus = 0
        self.is_defeated = False
        self.team = None
        
    def reset_bonuses(self):
        """Reset temporary bonuses at the start of turn"""
        self.defend_bonus = 0
        self.dodge_bonus = 0
        
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage dealt"""
        if self.is_defeated:
            return 0
            
        # Check dodge
        total_dodge = min(90, self.dodge_chance + self.dodge_bonus)
        if random.randint(1, 100) <= total_dodge:
            return 0
            
        # Calculate damage with defense
        actual_damage = max(1, damage - self.defense - self.defend_bonus)
        self.health = max(0, self.health - actual_damage)
        
        if self.health == 0:
            self.is_defeated = True
            
        return actual_damage
        
    def heal(self, amount: int):
        """Heal character"""
        if not self.is_defeated:
            self.health = min(self.max_health, self.health + amount)
            
    def restore_stamina(self, amount: int):
        """Restore stamina"""
        self.stamina = min(self.max_stamina, self.stamina + amount)
        
    def use_stamina(self, amount: int) -> bool:
        """Use stamina, return False if not enough"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
        
    def can_use_ultimate(self) -> bool:
        """Check if ultimate can be used"""
        return self.ultimate_cooldown == 0 and self.stamina >= 30
        
    def start_ultimate_cooldown(self):
        """Start ultimate cooldown"""
        self.ultimate_cooldown = self.ultimate_cooldown_max
        
    def update_cooldowns(self):
        """Update cooldowns at end of turn"""
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1
            
    def restore_stamina_per_turn(self):
        """Restore stamina at the end of each turn"""
        if not self.is_defeated:
            self.restore_stamina(5)
            
    @abstractmethod
    def get_ultimate_description(self) -> str:
        pass
        
    @abstractmethod
    def use_ultimate(self, allies: List['Character'], enemies: List['Character']) -> str:
        pass

class Knight(Character):
    def __init__(self, name: str):
        super().__init__(name, "Knight")
        self.max_health = 120
        self.health = self.max_health
        self.defense = 20
        self.attack = 18
        self.dodge_chance = 10
        self.speed = 8
        
    def get_ultimate_description(self) -> str:
        return "Shield Wall - Defend both allies for 1 turn"
        
    def use_ultimate(self, allies: List[Character], enemies: List[Character]) -> str:
        if not self.use_stamina(30):
            return f"{self.name} doesn't have enough stamina for Ultimate!"
            
        self.start_ultimate_cooldown()
        
        # Apply defend bonus to all allies
        for ally in allies:
            if ally != self and not ally.is_defeated:
                ally.defend_bonus = 15
                
        return f"{self.name} uses Shield Wall! All allies gain +15 defense for 1 turn."

class Assassin(Character):
    def __init__(self, name: str):
        super().__init__(name, "Assassin")
        self.max_health = 80
        self.health = self.max_health
        self.defense = 8
        self.attack = 25
        self.dodge_chance = 35
        self.critical_hit_chance = 30
        self.speed = 15
        
    def get_ultimate_description(self) -> str:
        return "Shadow Strike - Guaranteed critical hits for 2 turns"
        
    def use_ultimate(self, allies: List[Character], enemies: List[Character]) -> str:
        if not self.use_stamina(30):
            return f"{self.name} doesn't have enough stamina for Ultimate!"
            
        self.start_ultimate_cooldown()
        self.critical_hit_chance = 100  # Will be reset after 2 turns
        
        return f"{self.name} uses Shadow Strike! Guaranteed critical hits for 2 turns."

class Mage(Character):
    def __init__(self, name: str):
        super().__init__(name, "Mage")
        self.max_health = 70
        self.health = self.max_health
        self.defense = 5
        self.attack = 22
        self.dodge_chance = 15
        self.speed = 12
        
    def get_ultimate_description(self) -> str:
        return "Arcane Storm - AOE spell hitting all enemies"
        
    def use_ultimate(self, allies: List[Character], enemies: List[Character]) -> str:
        if not self.use_stamina(30):
            return f"{self.name} doesn't have enough stamina for Ultimate!"
            
        self.start_ultimate_cooldown()
        
        total_damage = 0
        for enemy in enemies:
            if not enemy.is_defeated:
                damage = enemy.take_damage(35)
                total_damage += damage
                
        return f"{self.name} uses Arcane Storm! Deals 35 damage to all enemies (Total: {total_damage})"

class Healer(Character):
    def __init__(self, name: str):
        super().__init__(name, "Healer")
        self.max_health = 90
        self.health = self.max_health
        self.defense = 12
        self.attack = 12
        self.dodge_chance = 20
        self.speed = 10
        
    def get_ultimate_description(self) -> str:
        return "Divine Blessing - Heal both allies and revive one dead ally"
        
    def use_ultimate(self, allies: List[Character], enemies: List[Character]) -> str:
        if not self.use_stamina(30):
            return f"{self.name} doesn't have enough stamina for Ultimate!"
            
        self.start_ultimate_cooldown()
        
        # Heal all allies
        for ally in allies:
            if ally != self:
                if ally.is_defeated:
                    # Revive dead ally
                    ally.is_defeated = False
                    ally.health = ally.max_health // 2
                    ally.stamina = ally.max_stamina // 2
                else:
                    # Heal living ally
                    ally.heal(40)
                    ally.restore_stamina(20)
                    
        return f"{self.name} uses Divine Blessing! Heals all allies and revives dead ones."

class Game:
    def __init__(self):
        self.characters = []
        self.turn_count = 0
        self.game_over = False
        self.winner = None
        
    def add_character(self, character: Character, team: int):
        """Add character to game with team assignment (0 or 1)"""
        character.team = team
        self.characters.append(character)
        
    def get_team_characters(self, team: int) -> List[Character]:
        """Get all characters on a team"""
        return [c for c in self.characters if c.team == team]
        
    def get_alive_characters(self, team: int) -> List[Character]:
        """Get alive characters on a team"""
        return [c for c in self.characters if c.team == team and not c.is_defeated]
        
    def get_enemy_characters(self, character: Character) -> List[Character]:
        """Get enemy characters for a given character"""
        return [c for c in self.characters if c.team != character.team and not c.is_defeated]
        
    def get_ally_characters(self, character: Character) -> List[Character]:
        """Get ally characters for a given character"""
        return [c for c in self.characters if c.team == character.team and c != character and not c.is_defeated]
        
    def get_turn_order(self) -> List[Character]:
        """Get characters in turn order (by speed, then random)"""
        alive_chars = [c for c in self.characters if not c.is_defeated]
        return sorted(alive_chars, key=lambda x: (-x.speed, random.random()))
        
    def check_game_over(self):
        """Check if game is over"""
        team0_alive = len(self.get_alive_characters(0))
        team1_alive = len(self.get_alive_characters(1))
        
        if team0_alive == 0:
            self.game_over = True
            self.winner = 1
        elif team1_alive == 0:
            self.game_over = True
            self.winner = 0
            
    def perform_action(self, character: Character, action: str, target: Optional[Character] = None) -> str:
        """Perform an action for a character"""
        if character.is_defeated:
            return f"{character.name} is defeated and cannot act!"
            
        character.reset_bonuses()
        
        if action == "light":
            if not character.use_stamina(10):
                return f"{character.name} doesn't have enough stamina for Light Attack!"
                
            if not target or target.is_defeated:
                return f"{character.name} has no valid target for Light Attack!"
                
            # Check for critical hit
            is_critical = random.randint(1, 100) <= character.critical_hit_chance
            damage = character.attack
            if is_critical:
                damage *= 2
                
            actual_damage = target.take_damage(damage)
            crit_text = " (CRITICAL!)" if is_critical else ""
            
            return f"{character.name} uses Light Attack on {target.name} - {actual_damage} damage{crit_text}"
            
        elif action == "heavy":
            if not character.use_stamina(20):
                return f"{character.name} doesn't have enough stamina for Heavy Attack!"
                
            if not target or target.is_defeated:
                return f"{character.name} has no valid target for Heavy Attack!"
                
            # Check for critical hit
            is_critical = random.randint(1, 100) <= character.critical_hit_chance
            damage = int(character.attack * 1.5)
            if is_critical:
                damage *= 2
                
            actual_damage = target.take_damage(damage)
            crit_text = " (CRITICAL!)" if is_critical else ""
            
            return f"{character.name} uses Heavy Attack on {target.name} - {actual_damage} damage{crit_text}"
            
        elif action == "ultimate":
            if not character.can_use_ultimate():
                return f"{character.name} cannot use Ultimate! (Cooldown: {character.ultimate_cooldown}, Stamina: {character.stamina})"
                
            allies = self.get_ally_characters(character)
            enemies = self.get_enemy_characters(character)
            return character.use_ultimate(allies, enemies)
            
        elif action == "defend":
            if not character.use_stamina(5):
                return f"{character.name} doesn't have enough stamina for Defend!"
                
            character.defend_bonus = 10
            return f"{character.name} uses Defend! +10 defense for 1 turn"
            
        elif action == "dodge":
            if not character.use_stamina(5):
                return f"{character.name} doesn't have enough stamina for Dodge!"
                
            character.dodge_bonus = 30
            return f"{character.name} uses Dodge! +30 dodge chance for 1 turn"
            
        elif action == "heal":
            if not character.use_stamina(15):
                return f"{character.name} doesn't have enough stamina for Heal!"
                
            heal_amount = 25
            stamina_restore = 15
            
            character.heal(heal_amount)
            character.restore_stamina(stamina_restore)
            
            return f"{character.name} uses Heal! +{heal_amount} HP, +{stamina_restore} Stamina"
            
        else:
            return f"Invalid action: {action}"
            
    def get_game_state(self) -> Dict:
        """Get current game state for AI bots"""
        return {
            "turn_count": self.turn_count,
            "game_over": self.game_over,
            "winner": self.winner,
            "characters": [
                {
                    "name": c.name,
                    "character_class": c.character_class,
                    "team": c.team,
                    "health": c.health,
                    "max_health": c.max_health,
                    "stamina": c.stamina,
                    "max_stamina": c.max_stamina,
                    "defense": c.defense,
                    "attack": c.attack,
                    "dodge_chance": c.dodge_chance,
                    "critical_hit_chance": c.critical_hit_chance,
                    "speed": c.speed,
                    "ultimate_cooldown": c.ultimate_cooldown,
                    "is_defeated": c.is_defeated,
                    "defend_bonus": c.defend_bonus,
                    "dodge_bonus": c.dodge_bonus
                }
                for c in self.characters
            ]
        }
        
    def display_status(self):
        """Display current status of all characters"""
        print_animated(f"\n{'='*60}")
        print_animated(f"TURN {self.turn_count}")
        print_animated(f"{'='*60}")
        
        for team in [0, 1]:
            team_name = "TEAM 1" if team == 0 else "TEAM 2"
            print_animated(f"\n{team_name}:")
            print_animated("-" * 30)
            
            for char in self.get_team_characters(team):
                status = "DEFEATED" if char.is_defeated else "ALIVE"
                ultimate_status = f" (Ult: {char.ultimate_cooldown})" if char.ultimate_cooldown > 0 else " (Ult: Ready)"
                print_animated(f"{char.name} ({char.character_class}) - HP: {char.health}/{char.max_health} | "
                      f"Stamina: {char.stamina}/{char.max_stamina} | {status}{ultimate_status}")
                      
    def run_turn(self, player1_action: str, player2_action: str, 
                 player1_target: Optional[Character] = None, player2_target: Optional[Character] = None):
        """Run a complete turn"""
        self.turn_count += 1
        turn_order = self.get_turn_order()
        
        print_animated(f"\n🎯 TURN {self.turn_count} STARTING 🎯")
        self.display_status()
        
        # Process actions in turn order
        for character in turn_order:
            if character.is_defeated:
                continue
                
            # Determine action based on character
            if character.name == "Player 1":
                action = player1_action
                target = player1_target
            elif character.name == "Player 2":
                action = player2_action
                target = player2_target
            else:
                # Bot character - use AI
                bot_id = 0 if character.name == "Bot 1" else 1
                action = get_bot_action(bot_id, self.get_game_state())
                target = self._get_bot_target(character, action)
                
            # Perform action
            result = self.perform_action(character, action, target)
            print_animated(f"\n⚔️  {result}")
            print_line_delay(0.3)  # Short delay after action
            
            # Update cooldowns
            character.update_cooldowns()
            
            # Check for game over
            self.check_game_over()
            if self.game_over:
                break
                
        # Restore stamina for all characters at end of turn
        print_animated("\n💪 Stamina restoration phase...")
        for character in self.characters:
            if not character.is_defeated:
                old_stamina = character.stamina
                character.restore_stamina_per_turn()
                if character.stamina > old_stamina:
                    print_animated(f"  {character.name} gains +5 stamina! ({old_stamina} → {character.stamina})")
        
        print_line_delay()
        
        # End of turn status
        print_animated(f"\n📊 END OF TURN {self.turn_count}")
        self.display_status()
        
    def _get_bot_target(self, bot: Character, action: str) -> Optional[Character]:
        """Get target for bot action"""
        if action in ["light", "heavy"]:
            enemies = self.get_enemy_characters(bot)
            if enemies:
                return random.choice(enemies)
        elif action == "heal":
            allies = self.get_ally_characters(bot)
            if allies:
                return random.choice(allies)
        return None
        
    def display_ultimate_info(self):
        """Display ultimate descriptions for all characters"""
        print_animated("\n🌟 ULTIMATE ABILITIES:")
        print_animated("=" * 50)
        for char in self.characters:
            print_animated(f"{char.name} ({char.character_class}): {char.get_ultimate_description()}")

def get_bot_action(bot_id: int, game_state: dict) -> str:
    """
    bot_id: 0 or 1 for bot1 or bot2
    game_state: full state of the game including stats of all characters
    return: one of ["light", "heavy", "ultimate", "defend", "dodge", "heal"]
    """
    # Simple AI: random action with stamina consideration
    actions = ["light", "heavy", "defend", "dodge", "heal", "ultimate"]
    
    # Get bot character info
    bot_char = None
    for char in game_state["characters"]:
        if char["name"] == f"Bot {bot_id + 1}":
            bot_char = char
            break
            
    if not bot_char:
        return "light"  # Fallback
        
    # Filter actions based on stamina
    available_actions = []
    for action in actions:
        if action == "light" and bot_char["stamina"] >= 10:
            available_actions.append(action)
        elif action == "heavy" and bot_char["stamina"] >= 20:
            available_actions.append(action)
        elif action == "ultimate" and bot_char["stamina"] >= 30 and bot_char["ultimate_cooldown"] == 0:
            available_actions.append(action)
        elif action in ["defend", "dodge"] and bot_char["stamina"] >= 5:
            available_actions.append(action)
        elif action == "heal" and bot_char["stamina"] >= 15:
            available_actions.append(action)
            
    if not available_actions:
        return "light"  # Fallback
        
    return random.choice(available_actions)

def create_character_by_class(name: str, character_class: str) -> Character:
    """Create a character instance based on class name"""
    if character_class.lower() == "knight":
        return Knight(name)
    elif character_class.lower() == "assassin":
        return Assassin(name)
    elif character_class.lower() == "mage":
        return Mage(name)
    elif character_class.lower() == "healer":
        return Healer(name)
    else:
        raise ValueError(f"Unknown character class: {character_class}")

def select_character_class(player_name: str) -> str:
    """Let player select their character class"""
    print_animated(f"\n{player_name} - Choose your character class:")
    print_animated("1. Knight - High health/defense, Shield Wall ultimate")
    print_animated("2. Assassin - High attack/dodge, Shadow Strike ultimate")
    print_animated("3. Mage - High attack, Arcane Storm ultimate")
    print_animated("4. Healer - Balanced, Divine Blessing ultimate")
    
    while True:
        try:
            choice = int(input("Enter choice (1-4): "))
            if choice == 1:
                return "Knight"
            elif choice == 2:
                return "Assassin"
            elif choice == 3:
                return "Mage"
            elif choice == 4:
                return "Healer"
            else:
                print_animated("Invalid choice! Enter 1-4.")
        except ValueError:
            print_animated("Invalid input! Enter a number.")

def select_ai_class(bot_name: str) -> str:
    """Let player select AI bot character class"""
    print_animated(f"\nSelect class for {bot_name}:")
    print_animated("1. Knight - High health/defense, Shield Wall ultimate")
    print_animated("2. Assassin - High attack/dodge, Shadow Strike ultimate")
    print_animated("3. Mage - High attack, Arcane Storm ultimate")
    print_animated("4. Healer - Balanced, Divine Blessing ultimate")
    
    while True:
        try:
            choice = int(input("Enter choice (1-4): "))
            if choice == 1:
                return "Knight"
            elif choice == 2:
                return "Assassin"
            elif choice == 3:
                return "Mage"
            elif choice == 4:
                return "Healer"
            else:
                print_animated("Invalid choice! Enter 1-4.")
        except ValueError:
            print_animated("Invalid input! Enter a number.")

def main():
    """Main game function"""
    print_animated("🎮 2v2 BATTLE GAME 🎮")
    print_animated("=" * 50)
    
    # Create game
    game = Game()
    
    # Let players choose their classes
    print_animated("\n🎯 CHARACTER SELECTION 🎯")
    print_animated("=" * 30)
    
    player1_class = select_character_class("Player 1")
    player2_class = select_character_class("Player 2")
    
    # Let players choose AI bot classes
    print_animated(f"\n🤖 AI BOT SELECTION 🤖")
    print_animated("=" * 30)
    
    bot1_class = select_ai_class("Bot 1")
    bot2_class = select_ai_class("Bot 2")
    
    # Create characters with selected classes
    player1 = create_character_by_class("Player 1", player1_class)
    player2 = create_character_by_class("Player 2", player2_class)
    bot1 = create_character_by_class("Bot 1", bot1_class)
    bot2 = create_character_by_class("Bot 2", bot2_class)
    
    # Add to game
    game.add_character(player1, 0)  # Team 0
    game.add_character(player2, 0)  # Team 0
    game.add_character(bot1, 1)     # Team 1
    game.add_character(bot2, 1)     # Team 1
    
    # Display team composition
    print_animated(f"\n📋 TEAM COMPOSITION 📋")
    print_animated("=" * 30)
    print_animated("TEAM 1:")
    print_animated(f"  Player 1: {player1_class}")
    print_animated(f"  Player 2: {player2_class}")
    print_animated("TEAM 2:")
    print_animated(f"  Bot 1: {bot1_class}")
    print_animated(f"  Bot 2: {bot2_class}")
    
    # Display ultimate info
    game.display_ultimate_info()
    
    # Game loop
    while not game.game_over:
        print_animated(f"\n🎯 TURN {game.turn_count + 1}")
        print_animated("=" * 50)
        
        # Get player actions
        print_animated(f"\nPlayer 1 ({player1.character_class}) - Choose your action:")
        print_animated("1. Light Attack (10 stamina)")
        print_animated("2. Heavy Attack (20 stamina)")
        print_animated("3. Ultimate Attack (30 stamina)")
        print_animated("4. Defend (5 stamina)")
        print_animated("5. Dodge (5 stamina)")
        print_animated("6. Heal (15 stamina)")
        
        while True:
            try:
                choice1 = int(input("Enter choice (1-6): "))
                if 1 <= choice1 <= 6:
                    break
                print_animated("Invalid choice! Enter 1-6.")
            except ValueError:
                print_animated("Invalid input! Enter a number.")
                
        actions = ["light", "heavy", "ultimate", "defend", "dodge", "heal"]
        player1_action = actions[choice1 - 1]
        
        # Get target if needed
        player1_target = None
        if player1_action in ["light", "heavy"]:
            enemies = game.get_enemy_characters(player1)
            if enemies:
                print_animated(f"\nChoose target for {player1_action}:")
                for i, enemy in enumerate(enemies, 1):
                    print_animated(f"{i}. {enemy.name} ({enemy.character_class}) - HP: {enemy.health}")
                while True:
                    try:
                        target_choice = int(input("Enter target (1-2): "))
                        if 1 <= target_choice <= len(enemies):
                            player1_target = enemies[target_choice - 1]
                            break
                        print_animated("Invalid choice!")
                    except ValueError:
                        print_animated("Invalid input!")
                        
        print_animated(f"\nPlayer 2 ({player2.character_class}) - Choose your action:")
        print_animated("1. Light Attack (10 stamina)")
        print_animated("2. Heavy Attack (20 stamina)")
        print_animated("3. Ultimate Attack (30 stamina)")
        print_animated("4. Defend (5 stamina)")
        print_animated("5. Dodge (5 stamina)")
        print_animated("6. Heal (15 stamina)")
        
        while True:
            try:
                choice2 = int(input("Enter choice (1-6): "))
                if 1 <= choice2 <= 6:
                    break
                print_animated("Invalid choice! Enter 1-6.")
            except ValueError:
                print_animated("Invalid input! Enter a number.")
                
        player2_action = actions[choice2 - 1]
        
        # Get target if needed
        player2_target = None
        if player2_action in ["light", "heavy"]:
            enemies = game.get_enemy_characters(player2)
            if enemies:
                print_animated(f"\nChoose target for {player2_action}:")
                for i, enemy in enumerate(enemies, 1):
                    print_animated(f"{i}. {enemy.name} ({enemy.character_class}) - HP: {enemy.health}")
                while True:
                    try:
                        target_choice = int(input("Enter target (1-2): "))
                        if 1 <= target_choice <= len(enemies):
                            player2_target = enemies[target_choice - 1]
                            break
                        print_animated("Invalid choice!")
                    except ValueError:
                        print_animated("Invalid input!")
                        
        # Run the turn
        game.run_turn(player1_action, player2_action, player1_target, player2_target)
        
        if game.game_over:
            break
            
        # Brief pause
        input("\nPress Enter to continue to next turn...")
        
    # Game over
    print_animated(f"\n🏆 GAME OVER! 🏆")
    print_animated("=" * 50)
    if game.winner == 0:
        print_animated("🎉 TEAM 1 WINS! 🎉")
    else:
        print_animated("🎉 TEAM 2 WINS! 🎉")
        
    print_animated(f"\nFinal Stats:")
    game.display_status()

if __name__ == "__main__":
    main()
