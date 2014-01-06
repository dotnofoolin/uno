""" 
Terminal based Uno
v1.0.20140102
Josh Burks - dotnofoolin@gmail.com
1/2/2014
http://en.wikipedia.org/wiki/Uno_%28card_game%29
"""

from collections import deque
import random
import re
import time

from colorama import init, Fore, Back, Style

# colorama init
init()

def help():
    """
    Prints a help message
    """
    s  = ("+---------------------------------------------------------------+\n")
    s += ("| UNO Help:                                                     |\n")
    s += ("| D to draw, P to pass, S for stats, Q to quit                  |\n")
    s += ("| Type the card you want to play. Add R,G,B, or Y to WILD cards |\n")
    s += ("| Type UNO at the end of the card you are playing to say UNO    |\n")
    s += ("+---------------------------------------------------------------+\n")
    return s


class Player():
    """
    Player class. Manages the players name, hand, drawing, and playing cards
    """

    def __init__(self, name="Player", brain="CPU"):
        """
        Player init
        """
        self.name = name
        self.hand = []
        self.brain = brain
        self.said_uno = False

    def num_cards(self):
        """
        Returns number of cards in players hand
        """
        return len(self.hand)

    def draw_card(self, card):
        """
        Appends (draws) a card to the players hand
        """
        self.hand.append(card)

    def play_card(self, card):
        """
        Removes (plays) the card from the players hand
        """
        # We only want the first 4 chars, hence the 0:4 slicing
        try:
            c = self.hand.pop(self.hand.index(card[0:4]))
            return True
        except:
            return False

    def show_hand(self):
        """
        Returns the players hand, in color!
        """
        h = ""
        for card in self.hand:
            h += "|" + colorize_card(card) + "| "

        return h

    def score_hand(self):
        """
        Returns the score of the players hand
        """
        score = 0
        for c in self.hand:
            # Number cards are face value
            if re.search("\d", c[1:2]):
                score += int(c[1:2])
            # Action cards are 20 points
            if re.search("[R|S|-]", c[1:2]) and c[0:1] <> "W":
                score += 20
            # Wild cards are 50 points
            if re.search("^W", c):
                score += 50

        return score


def colorize_card(card):
    """
    Returns the card with special color formatting for printing to the screen
    """
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
    """
    Builds and returns a standard 108-card UNO deck
    """
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


def shuffle_deck(deck):
    """
    Shuffles and returns a deck
    """
    # Shuffle the deck at least 3 but no more than 10 times
    for i in range(random.randint(3, 10)):
        random.shuffle(deck)

    return deck


def draw_from_deck(deck, discard_deck):
    """
    Draws (pops) a card from the deck and returns it.
    Also reshuffles the decks if needed
    """
    # Reshuffle discard deck if main deck is empty.
    if len(deck) == 0:
        print(Fore.YELLOW + "Reshuffling the discard deck since the main deck is empty..." + Fore.RESET)
        top_card = discard_deck.pop()
        deck = shuffle_deck(discard_deck)
        discard_deck = []
        discard_deck.append(top_card)
        card = deck.pop()
    else:
        card = deck.pop()

    return card, deck, discard_deck
 

def valid_start_card(card):
    """
    Checks the card passed to see if it is a valid game start card
    """
    if re.search("^[SRI-]", card[1:2]):
        return False
    else:
        return True


def check_played_card(card, discard_card):
    """
    Checks the card passed against the active discard card to determine if play is valid
    """
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


def autoplay(hand, discard_card, draw1_status):
    """
    Picks a card from the players hand that will make a valid play
    """
    # Build list of eligible cards, and randomly pick one from it
    elig_cards = []
    wild_cards = []

    # Count up the colors in the hand, in case we play a Wild
    colors = {"R": 0, "G": 0, "B": 0, "Y": 0}
    for c in hand:
        if re.search("^[RGBY]", c[0:1]):
            colors[c[0:1]] += 1

    # Pick the most frequent color
    max_color = max(colors, key=lambda k: colors[k])

    # This process can add the card to the elig_cards list twice. I'm cool with that.
    for c in hand:
        # If the color matches...
        if re.search("^[RGBY]", discard_card[0:1]) and c[0:1] == discard_card[0:1]:
            elig_cards.append(c)
        
        # If the number or action matches...
        if re.search("[\d|R|S]", discard_card[1:2]) and c[1:2] == discard_card[1:2]:
            elig_cards.append(c)

        # If the hand contains a Wild...
        if re.search("^W", c):
            wild_cards.append(c)

        # If discard is a Wild, and the hand contains a matching color...
        if (discard_card[0:1] == "W" and re.search("^[RGBY]", discard_card[4:5])) and c[0:1] == discard_card[4:5]:
            elig_cards.append(c)
    
    # May refine this a bit later, but it works
    # Regular cards take priority over wilds, which means the CPU will probably play the wilds last after UNO'ing
    try:
        card = random.choice(elig_cards)
    except:
        try:
            card = random.choice(wild_cards)
            card += max_color
        except:
            if draw1_status:
                card = "P"
            else:
                card = "D"

    # Don't forget to say UNO
    if len(hand) == 2 and card <> "D" and card <> "P":
        card += "UNO"

    return card


def print_message(message, audience=None):
    """
    Prints formatted messages to the screen depending on the audience passed in
    """
    if audience == "Human":
        print(Fore.CYAN + message + Fore.RESET)
    else:
        print(message)


if __name__ == "__main__":
    """
    Main entry point of the program
    """
    # Create a global deck of Uno cards
    deck = shuffle_deck(build_deck())
    discard_deck = []

    # Setup Human players
    human_player_name = raw_input("Enter your name: ")
    players = deque([Player(human_player_name, "Human")])

    # Setup CPU players
    num_cpu_players = raw_input("Number of CPU players (1-9): ")
    if re.search("[123456789]", num_cpu_players) and (1 <= int(num_cpu_players) <= 9):
        for n in range(1, int(num_cpu_players)+1):
            players.append(Player("CPU" + str(n), "CPU"))
    else:
        print("You didn't enter 1-9 for the number of players! Game over.")
        exit()

    # Initial deal of 7 cards
    for i in range(7):
       for p in players:
         c, deck, discard_deck = draw_from_deck(deck, discard_deck)
         p.draw_card(c)

    # Play the first card to get the discard pile started
    c, deck, discard_deck = draw_from_deck(deck, discard_deck)
    discard_deck.append(c)

    # Certain cards can't start the discard pile. Check for them and draw until we're good
    while not valid_start_card(discard_deck[-1]):
        c, deck, discard_deck = draw_from_deck(deck, discard_deck)
        discard_deck.append(c)

    # Instructions
    print(help())

    # Some flags to keep track of states
    game_over = False
    reverse = False
    skipped = False
    draw24 = False

    # Main game loop
    while not game_over:
        # Manually handle the players list (instead of for p in players)
        # Needed to handle the reverse action card
        # Be sure to players.append(p) where required!
        # Also remember that the list is 1 less due to the pop
        p = players.popleft()

        print("-" * 80)
        print("Current Player: {} ({})").format(p.name, p.brain)

        # More state tracking flags
        turn_over = False
        draw1 = False

        # If there is only one player, they win by forfeit
        if len(players) == 0:
            print(Fore.GREEN + "{} WINS!!! Game Over." + Fore.RESET).format(p.name)
            turn_over = True
            game_over = True

        while not turn_over:
            # Do some checks for action cards before we ask the player for a card...
            # Reverse Action card (step 2)
            if discard_deck[-1][1:4] == "REV" and reverse and len(players) == 1:
                print_message("You were skipped (because Reverse works like Skip with 2 players). Turn over!", p.brain)
                players.append(p)
                reverse = False
                turn_over = True
                break

            # Skip Action card (step 2)
            if discard_deck[-1][1:4] == "SKP" and skipped:
                print_message("You were skipped. Turn over!", p.brain)
                players.append(p)
                skipped = False
                turn_over = True
                break
            
            # Draw 2/4 action cards (step 2)
            if discard_deck[-1][1:3] == "-D" and draw24:
                for i in range(int(discard_deck[-1][3:4])):
                    c, deck, discard_deck = draw_from_deck(deck, discard_deck)
                    p.draw_card(c)
                
                print_message("You have to draw " + discard_deck[-1][3:4] + ". Turn over!", p.brain)
                players.append(p)
                draw24 = False
                turn_over = True
                break

            # Ask player/cpu for a card
            # CPU player
            if p.brain == "CPU":
                card = autoplay(p.hand, discard_deck[-1], draw1)
                print_message(p.name + " played " + card)
                time.sleep(1)
            # Human player
            else:
                print("Your Hand: {}").format(p.show_hand())
                print("CURRENT: {}").format(colorize_card(discard_deck[-1]))
                #print("DEBUG Autoplay: {}").format(autoplay(p.hand, discard_deck[-1], draw1))
                card = raw_input("Your Play " + p.name + " OR PASS --> ").upper()

            # Pass
            if re.search("^P", card):
                players.append(p)
                turn_over = True
                break

            # Draw another card
            if re.search("^D", card):
                if not draw1:
                    c, deck, discard_deck = draw_from_deck(deck, discard_deck)
                    p.draw_card(c)
                    draw1 = True
                    turn_over = False
                elif draw1:
                    print(Fore.RED + "You've already drawn a card. You have to PLAY or PASS." + Fore.RESET)

            # Print help, and a suggestion from the autoplay function
            if re.search("^H", card):
                print(help())
                print("I suggest you play: {}\n").format(autoplay(p.hand, discard_deck[-1], draw1))
                turn_over = False

            # Print stats about the other players, decks, etc
            if re.search("^S", card):
                for piter in players:
                    print("Player: {}, Cards: {}").format(piter.name, piter.num_cards())
                
                print("Cards in Deck: {}, Cards in Discard: {}").format(str(len(deck)), str(len(discard_deck))) 

            # Quit the game, put players cards at bottom of discard deck
            if re.search("^Q", card):
                print(Fore.YELLOW + "{} quit the game!" + Fore.RESET).format(p.name)
                discard_deck = p.hand + discard_deck
                p.deck = []
                if len(players) == 0:
                    game_over = True

                turn_over = True

            # Process the played card
            if re.search("^[RGBYW]", card):
                # Check if player said UNO
                if re.search("UNO$", card):
                    p.said_uno = True
                    card = re.sub(r'UNO$', "", card)

                # Not a fan of this. Think about revamping
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

                    # If we got this far, then the card was valid, and the turn is over
                    players.append(p)

                    # Process any action cards now
                    # Reverse Action card (step 1)
                    if card[1:4] == "REV":
                        print_message(p.name + " played a reverse")
                        reverse = True
                        players.reverse()
                        players.rotate(-1)

                    # Skip Action card (step 1)
                    if card[1:4] == "SKP":
                        print_message(p.name + " played a skip")
                        skipped = True

                    # Draw 2/4 Action card (step 1)
                    if card[1:3] == "-D":
                        print_message(p.name + " played a Draw " + card[3:4])
                        draw24 = True
                        

                except:
                    print(Fore.RED + "Invalid card, try again. You played: {}" + Fore.RESET).format(card)
                    turn_over = False
                    p.said_uno = False

                # Check for UNO
                if p.num_cards() == 1:
                    if p.said_uno:
                        print(Fore.YELLOW + "{} says UNO!!!" + Fore.RESET).format(p.name)
                        p.said_uno = False
                    else:
                        print(Fore.YELLOW + "{} forgot to say UNO! Draw two!" + Fore.RESET).format(p.name)
                        c, deck, discard_deck = draw_from_deck(deck, discard_deck)
                        p.draw_card(c)
                        c, deck, discard_deck = draw_from_deck(deck, discard_deck)
                        p.draw_card(c)
                        p.said_uno = False

            # Player is out of cards, so the game is over
            if p.num_cards() == 0:
                print(Fore.GREEN + "{} WINS!!! Game Over." + Fore.RESET).format(p.name)
                game_over = True
                # Score the other players hands
                score = 0
                for loser in players:
                    if loser.num_cards() > 0:
                        print("Player: {} Score: {} Hand: {}").format(loser.name, loser.score_hand(), loser.show_hand())
                        score += loser.score_hand()
            
                print(Fore.GREEN + "Final Score: {}" + Fore.RESET).format(str(score))


    print("Thanks for playing!")
