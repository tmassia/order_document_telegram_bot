from aiogram.fsm.state import State, StatesGroup


# Define a state machine for the client's form
class ClientForm(StatesGroup):
    Client_name = State()  # State for entering client's name
    Shem_hevra = State()  # State for entering company name
    Telefon = State()  # State for entering phone number
    ChooseTest = State()  # State for choosing a test (not specified)


# Define a state machine for the BdikaGilui form
class BdikaGiluiForm(StatesGroup):
    MakomShemBG = State()  # State for entering location name
    MakomYehudBG = State()  # State for entering Yehud
    MakomKtovetBG = State()  # State for entering detailed address
    MakomLocationBG = State()  # State for entering location details
    KamutGalaimBG = State()  # State for entering quantity of items
    FileUploadBG = State()  # State for uploading a file
    CheckDateBG = State()  # State for entering check date
