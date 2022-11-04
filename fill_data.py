from models import *

petro = User(
    id = 1,
    firstName = "Petro",
    lastName = "Melnyk",
    email = "petropetro@gmail.com",
    password = "petrotop1",
    birthDate = "2004-01-01",
    wallet = 0,
    userStatus = 0
)

maksym = User(
    id = 2,
    firstName = "Maksym",
    lastName = "Koval",
    email = "KovalMaks@gmail.com",
    password = "k0valmaks",
    birthDate = "2003-05-01",
    wallet = 10,
    userStatus = 0
)

denys = User(
    id = 3,
    firstName = "Denys",
    lastName = "Malyar",
    email = "MalyarDenys@gmail.com",
    password = "Denys2002",
    birthDate = "2002-04-02",
    wallet = 7,
    userStatus = 0
)

tr1 = Transaction(
    id = 1,
    value = 3,
    datePerformed = "2022-01-01 12:12:12",
    sentByUser = 1,
    sentToUser = 2
)
tr2 = Transaction(
    id = 2,
    value = 2,
    datePerformed = "2022-01-02 12:12:12",
    sentByUser = 3,
    sentToUser = 1
)
tr3 = Transaction(
    id = 3,
    value = 5,
    datePerformed = "2022-01-03 12:12:12",
    sentByUser = 1,
    sentToUser = 2
)

Session.add_all([petro,maksym,denys])
Session.commit()
Session.add_all([tr1,tr2,tr3])
Session.commit()