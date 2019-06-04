from appJar import gui
from const import DB_NAME
# from session import Session
from collection import Loader

class App:
    def __init__(self):
        self.app = gui('Memorize')
        # self.session = Session()
        self.col = Loader(DB_NAME).load()
        self.questions = [f'question {i}' for i in range(10)]
        
        self.create_main_menu_window()
        self.create_rename_deck_winodw()
        self.create_add_deck_winodw()
        self.create_cards_window()
        self.create_add_card_winodw()

    
    ################################################################################
    # main window, showing the decks
    
    def create_main_menu_window(self):
        # drop down menu
        self.app.setTitle('decks')
        self.app.addListBox('decks-list-box', self.col.dotted_names_list)

        self.app.startFrame('deck-buttons', row=1, column=0)
        self.app.addButton('cards', self.show_cards, row=0, column=0)
        self.app.addButton('study', self.study_deck, row=0, column=1)
        self.app.addButton('add-deck', self.add_deck, row=0, column=2)
        self.app.setButton('add-deck', 'add')
        self.app.addButton('remove-deck', self.remove_deck, row=0, column=3)
        self.app.setButton('remove-deck', 'remove')
        self.app.addButton('rename-deck', self.rename_deck, row=0, column=4)
        self.app.setButton('rename-deck', 'rename')
        self.app.stopFrame()

    def decks_updated(self):
        # called when decks are added or removed or renamed
        self.app.updateListBox('decks-list-box', self.col.dotted_names_list)

    def show_cards(self, button):
        self.app.showSubWindow("cards-window")

    def study_deck(self, button):
        pass

    def add_deck(self, button):
        self.app.showSubWindow('add-deck-window')
        self.app.setFocus('add-deck-name-entry')
    
    def remove_deck(self, button):
        deck_name = self.app.getListBox('decks-list-box')[0]
        self.col.remove_deck(deck_name)
        self.decks_updated()

    def rename_deck(self, button):
        dotted_name = self.app.getListBox('decks-list-box')[0]
        name = dotted_name.split('::')[-1]
        self.app.setEntry('rename-deck-entry', name)
        self.app.showSubWindow('rename-deck-window')
        self.app.setFocus('rename-deck-entry')


    ################################################################################
    # add deck window
    
    def add_deck_save(self, button):
        deck_name = self.app.getEntry('add-deck-name-entry')
        self.col.create_decks(deck_name)
        self.decks_updated()
        self.app.hideSubWindow('add-deck-window')
    
    def create_add_deck_winodw(self):
        self.app.startSubWindow('add-deck-window')
        self.app.setTitle('add deck')
        self.app.setSize('300x80')
        self.app.addEntry('add-deck-name-entry')
        self.app.addButton('add-deck-save-button', self.add_deck_save)
        self.app.setButton('add-deck-save-button', 'save')
        self.app.stopSubWindow()

    ################################################################################
    # cards window

    def delete_card(self, button):
        chosen = self.app.getListBox("cards-questions-list")
        self.app.removeListItem("cards-questions-list", chosen)

    def add_card(self, button):
        self.app.showSubWindow("add-card-window")

    def edit_card(self, button):
        pass

    def create_cards_window(self):
        self.app.startSubWindow("cards-window", modal=True)
        self.app.setTitle("cards")

        self.app.startFrame("cards-questions-frame", row=0, column=0)
        self.app.addListBox("cards-questions-list", self.questions)
        self.app.stopFrame()

        self.app.startFrame("cards-buttons", row=0, column=1)

        self.app.addButton("cards-edit-button", self.edit_card)
        self.app.setButton("cards-edit-button", "edit")

        self.app.addButton("cards-delete-button", self.delete_card)
        self.app.setButton("cards-delete-button", "delete")

        self.app.addButton("cards-add-button", self.add_card)
        self.app.setButton("cards-add-button", "add")

        self.app.stopFrame() # card-buttons
        self.app.stopSubWindow() # cards-window

    ################################################################################
    # rename deck window

    def rename_deck_save(self, button):
        dotted_name = self.app.getListBox('decks-list-box')[0]
        current_deck = self.col.find_deck(dotted_name)
        new_name = self.app.getEntry('rename-deck-entry')
        current_deck.name = new_name
        current_deck.flush() # TODO: this should not leak
        self.decks_updated()
        self.app.hideSubWindow('rename-deck-window')    
    
    def create_rename_deck_winodw(self):
        self.app.startSubWindow('rename-deck-window')
        self.app.setTitle('rename deck')
        self.app.addEntry('rename-deck-entry')
        self.app.addButton('rename-deck-save', self.rename_deck_save)
        self.app.setButton('rename-deck-save', 'save')
        self.app.stopSubWindow()

    ################################################################################
    # add card window

    def add_card_save(self, button):
        newQ = self.app.getTextArea("add-card-front-text")
        self.questions.append(newQ)
        self.app.updateListBox("cards-questions-list", self.questions)

    def create_add_card_winodw(self):
        self.app.startSubWindow("add-card-window", modal=True)
        self.app.addTextArea("add-card-front-text", text=None)
        self.app.addTextArea("add-card-back-text", text=None)
        self.app.addButton("add-card-save-button", self.add_card_save)
        self.app.setButton("add-card-save-button", "save")
        self.app.stopSubWindow()

    def go(self):
        self.app.go()

if __name__ == "__main__":
    app = App()
    app.go()
