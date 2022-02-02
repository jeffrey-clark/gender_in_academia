class Researcher:
    # upon creation we take all inital data as arguments
    def __init__(self, id, app_id, name, surname, financier, keywords):
        self.id = id
        self.app_id = app_id
        self.name = name
        self.surname = surname
        self.fullname = name + " " + surname
        self.financier = financier
        self.keywords = keywords

