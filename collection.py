import sqlite3

import const
import utils

from decks import Deck
from cards import Card

class Loader:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    @property
    def deck_rows(self):
        # just a utility function
        # returns a list of rows (<deck-id>, <deck-name>, <deck-parent-id>)
        
        query ="""\
            SELECT * FROM Deck;
        """
        
        cursor = self.conn.execute(query)

        data = cursor.fetchall()
        self.conn.commit()
        return data

    
    def card_rows(self, deck_id):
        # just a utility function
        # returns a list of card rows, which have the form
        # (id, EF, front, back, due_time, last_interval)
        
        query = """\
            SELECT Card.id, EF, front, back, due, last_interval FROM Card
            	INNER JOIN Deck
            		ON Card.deck_id = Deck.id
            WHERE Deck.id = ?;
        """

        cursor = self.conn.execute(query, (deck_id, ))
        cards = cursor.fetchall()
        self.conn.commit()
        return cards

    def load(self):
        # creates the Collection determined by the database at self.conn
        def create():
            roots = []
            decks = {} # maps ids to decks            
            deck_rows = self.deck_rows
            for deck_row in deck_rows:
                id, name, parent_id = deck_row
                if parent_id is None:
                    # the row represents a root deck
                    deck = Deck(id=id, name=name, conn=self.conn)
                    decks[id] = deck
                    roots.append(deck)
                elif parent_id in decks:
                    parent = decks[parent_id]
                    deck = Deck(id=id, name=name, conn=self.conn)
                    parent.subdecks[name] = deck
                    decks[id] = deck
            return roots, decks
        
        def populate(created_decks):
            for deck_id, deck in created_decks.items():
                for card_row in self.card_rows(deck_id):
                    card_id, EF, front, back, due, last_interval = card_row
                    deck.add_card((Card(deck=deck, id=card_id, EF=EF, front=front,
                                        back=back, due=due,
                                        last_interval=last_interval, conn=self.conn)))
            return created_decks
        
        roots, decks = create()
        populate(decks)
        deck_table = {deck.name: deck for deck in roots}
        return Collection(self.conn, deck_table)

class Collection:
    """
    Collections are factories for decks and cards

    * attributes:
    - conn: the connection to the database containing the collection
    - decks: a dict of the form {<name>: <deck>}
    """

    def __init__(self, conn, decks):
        self.conn = conn
        self.decks = decks
        
    def create_decks(self, name):
        # a name has the form <name> or <name1>::<name2>::...
        # no decks are created for names that already exist
        
        names = name.split('::')
        division = self._divide(names)
        if division is None:
            # all names exist
            return
        deck, names = division
        if deck is None:
            # create a top level deck
            self.decks[names[0]] = self._create_deck_path(names, parent=None)
        else:
            self._create_deck_path(names, parent=deck)

    def _divide(self, names):
        """
        Just a utility for self.create_decks.
        Returns a pair (deck, sublist) where deck exists in the
        collection, sublist is not empty and sublist[0] is
        supposed to the name of a subdeck of deck, but deck has
        no such subdeck. If names[0] does not exist, returns
        (None, names). If @names determines an existing path in
        the deck hierarchy, this function returns None
        """
        
        if not names:
            return None
        deck = self.decks.get(names[0])
        if not deck:
            return (None, names)
        ni = 1 # name index
        while ni < len(names):
            name = names[ni]
            subdeck = deck.subdecks.get(name)
            if subdeck is None:
                return (deck, names[ni:])
            else:
                deck = subdeck
                ni += 1
        else:
            # names are exhausted and all decks exist
            return None            
                    
    def _create_deck_path(self, names, parent):
        """
        Just a utility for self.create_decks.
        @names must be a non-empty list of deck names.
        @parent must be a deck or None.
        This function creates a deck for each name, with names[-1]
        being a child of names[-2] being a child of names[-3] and so
        on. The deck determined by names[0] will have @parent as a
        parent. This function returns the deck associated with
        names[0]
        """
        result = None
        for name in names:
            deck = self._create_deck(name, parent)
            parent = deck
            if result is None: # will return the first deck 
                result = deck
        return result
    
    def _create_deck(self, name, parent):
        """Just a utility for self._create_deck_path."""
        deck = Deck(id=utils.getid(self.conn, 'deck'), name=name, conn=self.conn)
        if parent is None:
            parent_id = None
        else:
            parent_id = parent.id
            parent.subdecks[name] = deck
        parent_id = None if parent is None else parent.id
        deck.conn.execute('INSERT INTO deck(id, name, parent_id) VALUES (?, ?, ?)',
                          (deck.id, deck.name, parent_id))
        deck.conn.commit()
        return deck
                    
    def remove_deck(self, deck_name):
        deck = self.decks[deck_name]

        # from the database remove all cards from the deck
        self.conn.execute('DELETE FROM card WHERE deck_id = ?', (deck.id,))
        self.conn.commit()

        # remove the deck from the database
        self.conn.execute('DELTE FROM deck WHERE deck_id = ?', (deck.id,))
        self.conn.commit()
    
    def create_card(self, front, back, deck_name):
        deck = self.decks[deck_name]
        dct = dict(id=utils.getid(self.conn, 'card'), front=front, back=back,
                   deck=deck, due=utils.today(), last_interval=None,
                   EF=2.5, conn=self.conn)
        
        card = Card(**dct)

        ##################################################
        # insert the card into the database
        
        # dct contains almost all attributes needed for inserting
        # a row into the database, except deck_id
        dct['deck_id'] = deck.id
        
        card.conn.execute("""
            INSERT INTO card (id, front, back, deck_id, due, last_interval, EF)
            VALUES (:id, :front, :back, :deck_id, :due, :last_interval, :EF)""",
                          dct)        
        card.conn.commit()
        deck.add_card(card)
        return card
            
    def remove_card(self, card):
        deck = card.deck
        del deck.cards[card.id]
        card.conn.execute('DELETE FROM card WHERE id = ?', (self.id,))
        card.conn.commit()