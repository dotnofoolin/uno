""" 
Terminal based Uno
Josh Burks
12/23/2013
http://en.wikipedia.org/wiki/Uno_%28card_game%29
"""

# TODO: if out of cards, shuffle discard_deck and reset deck
# TODO: check action cards (skip, rev, draw 2/4)
#       skip --> +1 the player list iter
#       rev --> flip player list
#       draw2/4 --> at start of player loop, look at discard
# TODO: computer player logic, implement play_card_guess()
#       play_card_guess will just try each card in hand, until no error, or will draw once and pass
# TODO: say uno on last card, or force draw two
# TODO: point tally when game is over

import random
import re
from colorama import init, Fore, Back, Style

# colorama init
init()

class Player():
    def __init__(self, name="Player", brain="CPU"):
        self.name = name
        self.hand = []
        self.brain = brain
        self.said_uno = False

    def num_cards(self):
        return len(self.hand)

    def draw_card(self, card):
        self.hand.append(card)

    def play_card(self, card):
        # We only want the first 4 chars, hence the 0:4 slicing
        try:
            c = self.hand.pop(self.hand.index(card[0:4]))
            return True
        except:
            return False

    def show_hand(self):
        h = ""
        for card in self.hand:
            h += "|" + colorize_card(card) + "|  "

        return h

def help():
    s  = ("+---------------------------------------------------------------+\n")
    s += ("| UNO - v1.0.0                                                  |\n")
    s += ("| D to draw, PASS or nothing to pass, Q to quit                 |\n")
    s += ("| Type the card you want to play. Add R,G,B, or Y to WILD cards |\n")
    s += ("| Type UNO at the end of the card you are playing to call UNO   |\n")
    s += ("+---------------------------------------------------------------+\n")
    return s


def colorize_card(card):
    colored_card = card
    if card[0:1] == "R" or card[4:5] == "R":
        colored_card = Back.RED + Fore.WHITE + card + Fore.RESET + Back.RESET
    if card[0:1] == "G" or card[4:5] == "G":
        colored_card = Back.GREEN + Fore.BLACK + card + Fore.RESET + Back.RESET
    if card[0:1] == "B" or card[4:5] == "B":
        colored_card = Back.BLUE + Fore.WHITE + card + Fore.RESET + Back.RESET
    if card[0:1] == "Y" or card[4:5] == "Y":
        colored_card = Back.YELLOW + Fore.BLACK + card + Fore.RESET + Back.RESET
    if card[0:1] == "W" and len(card) == 4:
        colored_card = Back.RED + Fore.WHITE + card[0:1] \
            + Back.GREEN + Fore.BLACK + card[1:2] \
            + Back.BLUE + Fore.WHITE + card[2:3] \
            + Back.YELLOW + Fore.BLACK + card[3:4] \
            + Fore.RESET + Back.RESET
        
    return colored_card


def build_deck():
    # Wild cards
    deck = ["WILD", "WILD", "WILD", "WILD", "W-D4", "W-D4", "W-D4", "W-D4"]
    # Red cards
    deck += ["R" + str(n) for n in range(10)]
    deck += ["R" + str(n) for n in range(1,10)]
    deck += ["RSKP", "RSKP", "R-D2", "R-D2", "RREV", "RREV"]
    # Green cards
    deck += ["G" + str(n) for n in range(10)]
    deck += ["G" + str(n) for n in range(1,10)]
    deck += ["GSKP", "GSKP", "G-D2", "G-D2", "GREV", "GREV"]
    # Blue cards
    deck += ["B" + str(n) for n in range(10)]
    deck += ["B" + str(n) for n in range(1,10)]
    deck += ["BSKP", "BSKP", "B-D2", "B-D2", "BREV", "BREV"]
    # Yellow cards
    deck += ["Y" + str(n) for n in range(10)]
    deck += ["Y" + str(n) for n in range(1,10)]
    deck += ["YSKP", "YSKP", "Y-D2", "Y-D2", "YREV", "YREV"]

    return deck


def valid_start_card(card):
    if re.search("^[SRI-]", card[1:2]):
        return False
    else:
        return True


def check_played_card(card, discard_card):
    # Wild cards are always valid, as long as they picked the color
    if card[0:1] == "W" and re.search("^[RGBY]", card[4:5]):
        return True
    
    # Check the color. Matches are valid
    if card[0:1] == discard_card[0:1]:
        return True

    # Check card color against discarded Wild card
    if card[0:1] == discard_card[4:5]:
        return True

    # Check the number/action. Matches are valid
    if card[1:2] == discard_card[1:2]:
        return True

    return False


if __name__ == "__main__":
    # Create a deck of Uno cards
    deck = build_deck()
    discard_deck = []

    # Shuffle the deck a random number of times
    for i in range(random.randint(1, 5)):
        random.shuffle(deck)

    # Setup the players
    players = [Player("Josh", "Human"), Player("CPU1", "CPU"), Player("CPU2", "CPU")] 
    #human_player = Player("Josh", "Human")
    #cpu_player = Player("CPU", "CPU")

    # TODO: set initial order of play

    # Initial deal of 7 cards
    for i in range(7):
       for p in players:
         p.draw_card(deck.pop())

    # Play the first card to get the discard pile started
    discard_deck.append(deck.pop())

    # Certain cards can't start the discard pile. Check for them and draw until we're good
    while not valid_start_card(discard_deck[-1]):
        discard_deck.append(deck.pop())

    # Instructions
    print(help())

    # Main game loop
    game_over = False
    skipped = False
    reverse = False
    while not game_over:
        for p in players:
            print("Current Player: {} ({})").format(p.name, p.brain)
            turn_over = False
            while not turn_over:
                # Do some checks for action cards before we as the player for a card...
                if discard_deck[-1][1:4] == "REV" and reverse:
                    # Reverse Action card (step 2)
                    reverse = False
                    #turn_over = True
                    #break

                if discard_deck[-1][1:4] == "SKP" and skipped:
                    # Skip Action card (step 2)
                    print("Found a skip. Turn over!")
                    skipped = False
                    turn_over = True
                    break
                
                if discard_deck[-1][1:3] == "-D":
                    # Draw 2/4 action cards
                    for i in range(int(discard_deck[-1][3:4])):
                        p.draw_card(deck.pop())
                    
                    print("You have to draw {}. Turn over!").format(discard_deck[-1][3:4])
                    turn_over = True
                    break
    
                # Ask player for card, or other command...
                print("Your Hand: {}").format(p.show_hand())
                print("CURRENT: {}").format(colorize_card(discard_deck[-1]))
                card = raw_input("Your Play " + p.name + " OR PASS --> ").upper()

                if re.search("^P", card):
                    # Pass
                    turn_over = True
                    break

                if re.search("^D", card):
                    # Draw another card
                    p.draw_card(deck.pop())
                    turn_over = False

                if re.search("^H", card):
                    # Print help
                    print(help())
                    turn_over = False

                if re.search("^Q", card):
                    # Quit the game
                    game_over = True
                    turn_over = True
                    exit()

                if re.search("^[RGBYW]", card):
                    # Process the played card
                    try:
                        # Validate the card played
                        if check_played_card(card, discard_deck[-1]):
                            # Locate the card, pop it and append it to the discard pile
                            if p.play_card(card):
                                discard_deck.append(card)
                                turn_over = True
                            else:
                                raise
                        else:
                            raise

                        if card[1:4] == "REV":
                            # Reverse Action card (step 1)
                            reverse = True
                            players.reverse()

                        if card[1:4] == "SKP":
                            # Skip Action card (step 1)
                            print("{} played a skip").format(p.name)
                            skipped = True

                    except:
                        print(Fore.RED + "Invalid card, try again. You played: {}" + Fore.RESET).format(card)
                        turn_over = False

                if p.num_cards() == 1:
                    print(Fore.YELLOW + "{} says UNO!!!" + Fore.RESET).format(p.name)

                if p.num_cards() == 0:
                    print(Fore.GREEN + "{} WINS!!! Game Over." + Fore.RESET).format(p.name)
                    game_over = True


    print("Thanks for playing!")


